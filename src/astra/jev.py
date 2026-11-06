"""Real TypeSafe Jev integration. No Codex or LLM substitute on failure.

A reviewer offers two calls. ``review`` applies the gate contract to one
checkpoint; ``ask`` answers raw typed questions (design advice, action
selection). Answers are validated here; every caller shares one parser and
one set of thresholds.
"""
import json
import math
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from astra.models import Stage, STAGES, REPAIR_OWNER

JEV_MODEL = 'jev-1.13.0'
POLICY_VERSION = 'typesafe-jev-v1'
ASTRA_ONLY_POLICY = 'astra-only-v1'
# Provisional engineering policy, not calibrated accuracy (docs/JEV.md).
CONFIDENCE_FLOOR = 0.65   # below this an answer requests evidence instead of acting
SCORE_FLOOR = 3.2         # rubric score (0-4) required to count as supported
STATE_BUDGET_BYTES = 90000
SCORE_LEVELS = ('0', '1', '2', '3', '4')


def evaluator_name(review_mode):
    return 'disabled' if review_mode == 'off' else JEV_MODEL


def policy_name(review_mode):
    return ASTRA_ONLY_POLICY if review_mode == 'off' else POLICY_VERSION


class GateDecision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    approved: bool
    repair_stage: Stage
    feedback: str
    defects: list[str]
    evaluator: str = 'typesafe-jev'
    model: str
    answers: dict
    policy_version: str = POLICY_VERSION


def questions_for(stage):
    # Every question addresses one bounded issue. Jev is not asked to prove a theorem.
    focus = {
        'brief': ('Does the brief state a concrete learner and prerequisite baseline?',
                  'Does the brief specify observable acceptance criteria for the requested film?'),
        'mathematics': ('Are domains and hypotheses explicitly attached to the main mathematical claims?',
                        'Are numerical or symbolic checks documented for the central formula?'),
        'storyboard': ('Does the shot sequence introduce definitions before using them?',
                       'Does the storyboard assign exact formulas to specific shots?'),
        'scene': ('Does the audit support that the scene implements the approved mathematical formulas?',
                  'Does the audit support that the source implements the planned geometric transitions?'),
        'render': ('Do the supplied frame observations support readable on-screen formulas?',
                   'Do the supplied frame observations support the intended geometric states?'),
    }[stage]
    criteria=['Absent or contradicted','Major omissions','Partly supported, needs repair',
              'Supported with minor limitations','Clearly supported by specific evidence']
    questions={f'criterion_{i}':{'type':'score','instructions':q+' Evaluate only the supplied text state; do not infer unseen images or unperformed checks.',
                                 'criteria':criteria} for i,q in enumerate(focus,1)}
    owners={'brief':'Learner, scope or prerequisites','mathematics':'Equations, assumptions, derivations or topology',
            'storyboard':'Teaching sequence, camera, color or notation plan','scene':'Implementation, rendering or visible layout'}
    assert set(owners) == set(STAGES)
    questions.update({
        'evidence_sufficient':{'type':'noul','instructions':'Does the state contain concrete evidence sufficient to evaluate this checkpoint at its current scope, without assuming later stages are already implemented?'},
        'blocking_defect':{'type':'noul','instructions':'Does the evidence audit identify an unresolved blocking defect supported by the supplied candidate or observations? Nonblocking limitations do not count.'},
        'repair_target':{'type':'choice','instructions':'If revision is required, which earliest role owns the issue identified by the evidence? Select the current role when the only issue is insufficient evidence.',
                         'criteria':owners},
    })
    return questions


def unit_interval(value):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not 0<=value<=1:
        raise ValueError('Invalid TypeSafe probability or confidence')
    return float(value)


def answers_from(response, questions):
    """The answers of a Jev response, which must address exactly the questions asked."""
    if not str(response.get('model','')).startswith('jev-'):
        raise ValueError('Evaluation response is not a Jev model')
    answers=response.get('answers',{})
    if set(answers)!=set(questions):raise ValueError('Missing or unexpected Jev answers')
    return answers


def parse_score(answer):
    """(score, confidence) of a Score answer; its 0-4 distribution must agree with the score."""
    if answer.get('type')!='score':raise ValueError('Expected Jev Score')
    score=answer['score'];confidence=unit_interval(answer['confidence'])
    if isinstance(score,bool) or not isinstance(score,(float,int)) or not math.isfinite(score) or not 0<=score<=4:
        raise ValueError('Invalid Jev rubric score')
    probabilities=answer['probabilities']
    if set(probabilities)!=set(SCORE_LEVELS):raise ValueError('Invalid score distribution levels')
    values=[unit_interval(probabilities[level]) for level in SCORE_LEVELS]
    if abs(sum(values)-1)>0.02:raise ValueError('Invalid score distribution total')
    if abs(sum(i*p for i,p in enumerate(values))-score)>0.06:raise ValueError('Score differs from expected value')
    return score,confidence


def parse_noul(answer):
    if answer.get('type')!='noul':raise ValueError('Expected Jev Noul')
    return unit_interval(answer['noul'])


def parse_choice(answer, options):
    """(choice, confidence, probabilities) of a Choice answer over exactly these options."""
    if answer.get('type')!='choice' or answer.get('choice') not in options:
        raise ValueError('Invalid Jev choice')
    probabilities=answer.get('probabilities',{})
    if set(probabilities)!=set(options):raise ValueError('Invalid choice distribution')
    probabilities={k:unit_interval(v) for k,v in probabilities.items()}
    if abs(sum(probabilities.values())-1)>0.02:raise ValueError('Invalid choice distribution total')
    return answer['choice'],unit_interval(answer['confidence']),probabilities


def evaluate_response(response, *, stage, audit):
    required=questions_for(stage)
    answers=answers_from(response,required); reasons=[]
    for key in ['criterion_1','criterion_2']:
        score,confidence=parse_score(answers[key])
        if score<SCORE_FLOOR or confidence<CONFIDENCE_FLOOR:
            reasons.append(f"{key}: score={score:.3f}/4, confidence={confidence:.3f}; {required[key]['instructions']}")
    enough=parse_noul(answers['evidence_sufficient']);blocked=parse_noul(answers['blocking_defect'])
    if enough<0.8:reasons.append(f'Insufficient evidence: probability={enough:.3f}; gather concrete checks')
    if blocked>0.2:reasons.append(f'Blocking defect probability={blocked:.3f}; resolve the evidence audit defects')
    route,route_confidence,_=parse_choice(answers['repair_target'],required['repair_target']['criteria'])
    # An Astra audit with unresolved blockers cannot be overruled by a probabilistic approval.
    if not audit.verified or audit.defects:reasons.append('Astra evidence audit has unresolved blockers or insufficient verification')
    current=REPAIR_OWNER[stage]
    target=route if route_confidence>=CONFIDENCE_FLOOR else current
    if reasons and route_confidence<CONFIDENCE_FLOOR:reasons.append('Repair routing uncertain; gather evidence at the current stage')
    return GateDecision(approved=not reasons,repair_stage=target,defects=reasons,
                        feedback='\n'.join(reasons)+('\nAstra evidence audit (not Jev-generated prose):\n'+audit.feedback if reasons else ''),
                        model=response['model'],answers=answers)


def load_api_key(root=None):
    """Read only the TypeSafe credential; never export it to child processes."""
    if os.environ.get('TYPESAFE_API_KEY'):
        return os.environ['TYPESAFE_API_KEY']
    path = Path(root or Path.cwd()) / '.env.local'
    if path.is_file():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            name, separator, value = line.strip().removeprefix('export ').partition('=')
            if separator and name.strip() == 'TYPESAFE_API_KEY':
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                if value:
                    return value
    raise RuntimeError('Save TYPESAFE_API_KEY in the working directory .env.local or process environment')


class JevClient:
    def __init__(self, api_key=None):
        import httpx2
        from typesafe_sdk import TypeSafeClient
        self.http_events=[]
        def record(response):
            self.http_events.append({
                'utc':datetime.now(timezone.utc).isoformat(),
                'method':response.request.method,'url':str(response.request.url),
                'status':response.status_code,
                'request_body_sha256':hashlib.sha256(response.request.content).hexdigest(),
                'response_headers':{k:response.headers[k] for k in
                    ['date','x-request-id','request-id','x-correlation-id'] if k in response.headers},
            })
        http=httpx2.Client(timeout=90,event_hooks={'response':[record]})
        self.client=TypeSafeClient(api_key=api_key or load_api_key(),
                                   model=JEV_MODEL,base_url='https://api.typesafe.ai',http_client=http)

    def ask(self, *, state, questions, output):
        """Ask raw typed questions; retain the request, response and HTTP receipts (no secrets)."""
        # Avoid silently truncating mathematical state. Split upstream artifacts deliberately instead.
        if len(json.dumps(state,ensure_ascii=False).encode('utf-8'))>STATE_BUDGET_BYTES:
            raise ValueError('Jev state exceeds local evidence budget; reduce the checkpoint scope')
        output=Path(output)
        output.with_suffix('.request.json').write_text(json.dumps(
            {'model':JEV_MODEL,'state':state,'questions':questions},indent=2,ensure_ascii=False),encoding='utf-8')
        start=len(self.http_events)
        try:
            response=self.client.system_one(state=state,questions=questions,model=JEV_MODEL)
            raw=response.model_dump(mode='json')
            output.with_suffix('.response.json').write_text(json.dumps(raw,indent=2),encoding='utf-8')
            return raw
        finally:
            output.with_suffix('.http.json').write_text(
                json.dumps(self.http_events[start:],indent=2),encoding='utf-8')

    def review(self, *, state, stage, audit, output):
        """Apply the gate contract at one checkpoint and retain the deterministic decision."""
        raw=self.ask(state=state,questions=questions_for(stage),output=output)
        decision=evaluate_response(raw,stage=stage,audit=audit)
        Path(output).write_text(decision.model_dump_json(indent=2),encoding='utf-8')
        return decision

    def close(self):
        self.client.close()
