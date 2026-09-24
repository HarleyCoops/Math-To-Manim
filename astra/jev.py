"""Real TypeSafe Jev integration. No Codex or LLM substitute on failure."""
import json
import math
import os
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal
from pydantic import BaseModel, ConfigDict

JEV_MODEL = 'jev-1.13.0'
POLICY_VERSION = 'typesafe-jev-v1'

class GateDecision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    approved: bool
    repair_stage: Literal['brief','mathematics','storyboard','scene']
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
    questions.update({
        'evidence_sufficient':{'type':'noul','instructions':'Does the state contain concrete evidence sufficient to evaluate this checkpoint at its current scope, without assuming later stages are already implemented?'},
        'blocking_defect':{'type':'noul','instructions':'Does the evidence audit identify an unresolved blocking defect supported by the supplied candidate or observations? Nonblocking limitations do not count.'},
        'repair_target':{'type':'choice','instructions':'If revision is required, which earliest role owns the issue identified by the evidence? Select the current role when the only issue is insufficient evidence.',
                         'criteria':{'brief':'Learner, scope or prerequisites','mathematics':'Equations, assumptions, derivations or topology','storyboard':'Teaching sequence, camera, color or notation plan','scene':'Implementation, rendering or visible layout'}},
    })
    return questions


def _unit(value):
    if isinstance(value,bool) or not isinstance(value,(float,int)) or not math.isfinite(value) or not 0<=value<=1:
        raise ValueError('Invalid TypeSafe probability or confidence')
    return float(value)


def evaluate_response(response, *, stage, audit):
    if not str(response.get('model','')).startswith('jev-'):
        raise ValueError('Evaluation response is not a Jev model')
    answers=response['answers']; reasons=[]
    required=questions_for(stage)
    if set(answers)!=set(required):raise ValueError('Missing or unexpected Jev answers')
    for key in ['criterion_1','criterion_2']:
        a=answers[key]
        if a.get('type')!='score':raise ValueError('Expected Jev Score')
        score=a['score'];confidence=_unit(a['confidence'])
        if isinstance(score,bool) or not isinstance(score,(float,int)) or not math.isfinite(score) or not 0<=score<=4:
            raise ValueError('Invalid Jev rubric score')
        probs=a['probabilities']
        if set(probs)!={'0','1','2','3','4'}:raise ValueError('Invalid score distribution levels')
        values=[_unit(probs[str(i)]) for i in range(5)]
        if abs(sum(values)-1)>0.02:raise ValueError('Invalid score distribution total')
        if abs(sum(i*p for i,p in enumerate(values))-score)>0.06:raise ValueError('Score differs from expected value')
        if score<3.2 or confidence<0.65:reasons.append(f"{key}: score={score:.3f}/4, confidence={confidence:.3f}; {required[key]['instructions']}")
    for key in ['evidence_sufficient','blocking_defect']:
        if answers[key].get('type')!='noul':raise ValueError('Expected Jev Noul')
    enough=_unit(answers['evidence_sufficient']['noul']);blocked=_unit(answers['blocking_defect']['noul'])
    if enough<0.8:reasons.append(f'Insufficient evidence: probability={enough:.3f}; gather concrete checks')
    if blocked>0.2:reasons.append(f'Blocking defect probability={blocked:.3f}; resolve the evidence audit defects')
    route=answers['repair_target']
    if route.get('type')!='choice' or route['choice'] not in required['repair_target']['criteria']:
        raise ValueError('Invalid Jev repair choice')
    route_confidence=_unit(route['confidence'])
    if set(route['probabilities'])!=set(required['repair_target']['criteria']):raise ValueError('Invalid repair distribution')
    if abs(sum(_unit(v) for v in route['probabilities'].values())-1)>0.02:raise ValueError('Invalid repair distribution total')
    # An Astra audit with unresolved blockers cannot be overruled by a probabilistic approval.
    if not audit.verified or audit.defects:reasons.append('Astra evidence audit has unresolved blockers or insufficient verification')
    current='scene' if stage=='render' else stage
    target=route['choice'] if route_confidence>=0.65 else current
    if reasons and route_confidence<0.65:reasons.append('Repair routing uncertain; gather evidence at the current stage')
    return GateDecision(approved=not reasons,repair_stage=target,defects=reasons,
                        feedback='\n'.join(reasons)+('\nAstra evidence audit (not Jev-generated prose):\n'+audit.feedback if reasons else ''),
                        model=response['model'],answers=answers)


def load_api_key(root=None):
    """Read only the TypeSafe credential; never export it to child processes."""
    if os.environ.get('TYPESAFE_API_KEY'):
        return os.environ['TYPESAFE_API_KEY']
    path = Path(root or Path(__file__).resolve().parents[1]) / '.env.local'
    if path.is_file():
        for line in path.read_text(encoding='utf-8-sig').splitlines():
            name, separator, value = line.strip().removeprefix('export ').partition('=')
            if separator and name.strip() == 'TYPESAFE_API_KEY':
                value = value.strip()
                if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                    value = value[1:-1]
                if value:
                    return value
    raise RuntimeError('Save TYPESAFE_API_KEY in the repository .env.local or process environment')


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
        """Retain actual HTTP receipts, including retries, without secret headers."""
        start=len(self.http_events)
        try:
            response=self.client.system_one(state=state,questions=questions,model=JEV_MODEL)
            raw=response.model_dump(mode='json')
            Path(output).with_suffix('.response.json').write_text(json.dumps(raw,indent=2),encoding='utf-8')
            return raw
        finally:
            Path(output).with_suffix('.http.json').write_text(
                json.dumps(self.http_events[start:],indent=2),encoding='utf-8')

    def review(self, *, state, stage, audit, output):
        # Avoid silently truncating mathematical state. Split upstream artifacts deliberately instead.
        if len(json.dumps(state,ensure_ascii=False).encode('utf-8'))>90000:
            raise ValueError('Jev state exceeds local evidence budget; reduce the checkpoint scope')
        questions=questions_for(stage)
        output=Path(output)
        payload={'model':JEV_MODEL,'state':state,'questions':questions,'policy_version':POLICY_VERSION}
        output.with_suffix('.request.json').write_text(json.dumps(payload,indent=2,ensure_ascii=False),encoding='utf-8')
        raw=self.ask(state=state,questions=questions,output=output)
        decision=evaluate_response(raw,stage=stage,audit=audit)
        output.write_text(decision.model_dump_json(indent=2),encoding='utf-8')
        return decision

    def close(self):
        self.client.close()
