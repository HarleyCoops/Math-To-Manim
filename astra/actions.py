"""Jev selects an allowlisted investigation; the host executes it with Astra."""
import json
from pathlib import Path
from pydantic import BaseModel, ConfigDict
from astra.jev import JEV_MODEL, _unit
from astra.evidence import text_evidence, design_summary
from astra.models import Assessment, Request
from astra.prompts import judge_prompt

ACTIONS = {
    'check_math': 'Independently calculate the disputed formulas, domains, critical values or topology. Report actual tool results and specific corrections.',
    'clarify_definitions': 'Trace first use of every term against its definition. Recommend exact wording and shot ordering for the identified gaps.',
    'inspect_scene': 'Inspect Manim source and installed APIs for the identified implementation defect. Recommend exact source locations and changes; do not edit or render.',
    'inspect_frames': 'Inspect supplied actual frames for the identified uncertainty. Cite frame filenames and exact visible geometry or notation problems.',
    'replan_camera': 'Inspect shot layout and available frames. Recommend concrete camera targets, zoom values, label positions, colors and holds supported by evidence.',
    'no_action': 'No further investigation is warranted by this evidence.',
}
STAGE_ACTIONS = {
    'brief': ['clarify_definitions','no_action'],
    'mathematics': ['check_math','clarify_definitions','no_action'],
    'storyboard': ['clarify_definitions','check_math','replan_camera','no_action'],
    'scene': ['inspect_scene','check_math','clarify_definitions','replan_camera','no_action'],
    'render': ['inspect_frames','inspect_scene','check_math','clarify_definitions','replan_camera','no_action'],
}

class ActionDecision(BaseModel):
    model_config = ConfigDict(extra='forbid')
    action: str
    confidence: float
    execute: bool
    model: str
    probabilities: dict[str,float]


def parse_action(raw, stage):
    if raw.get('model') != JEV_MODEL or set(raw.get('answers',{})) != {'next_action'}:
        raise ValueError('Invalid Jev action response')
    a=raw['answers']['next_action']; allowed=STAGE_ACTIONS[stage]
    if a.get('type')!='choice' or a.get('choice') not in allowed or set(a.get('probabilities',{}))!=set(allowed):
        raise ValueError('Jev selected an unavailable action')
    probs={k:_unit(v) for k,v in a['probabilities'].items()}
    if abs(sum(probs.values())-1)>.02:raise ValueError('Invalid action distribution')
    confidence=_unit(a['confidence'])
    return ActionDecision(action=a['choice'],confidence=confidence,
        execute=confidence>=.65 and a['choice']!='no_action',model=raw['model'],probabilities=probs)


def select_action(jev, state, stage, output):
    output=Path(output)
    if len(json.dumps(state,ensure_ascii=False).encode('utf-8'))>90000:
        raise ValueError('Jev action state exceeds local evidence budget')
    questions={'next_action':{'type':'choice',
        'instructions':'Which ONE available investigation would most directly resolve the specific uncertainty or defect in this state? Choose no_action if evidence supports proceeding without further investigation. You select an action; the host executes it.',
        'criteria':{k:ACTIONS[k] for k in STAGE_ACTIONS[stage]}}}
    output.with_suffix('.request.json').write_text(json.dumps({'model':JEV_MODEL,'state':state,'questions':questions},indent=2),encoding='utf-8')
    raw=jev.ask(state=state,questions=questions,output=output)
    decision=parse_action(raw,stage)
    output.write_text(decision.model_dump_json(indent=2),encoding='utf-8')
    return decision


def execute_action(client, decision, *, stage, request, folder, paths, images, output):
    if not decision.execute:return None
    if decision.action not in STAGE_ACTIONS[stage]:raise ValueError('Action unavailable at checkpoint')
    if decision.action=='inspect_frames' and not images:raise ValueError('Frame inspection requires actual images')
    names=[Path(p).relative_to(folder).as_posix() for p in paths]
    prompt=judge_prompt(stage,request,'\n'.join(names),names)
    prompt+='\nJev selected this investigation: '+decision.action+'\n'+ACTIONS[decision.action]
    prompt+='\nReturn concrete recommendations in feedback, supported by exact evidence. Do not claim Jev authored your prose.'
    report=client.call(prompt,cwd=folder,output=output,schema=Assessment,images=images,
                       effort=request.effort,search=decision.action=='check_math',evidence_paths=names)
    if not set(report.evidence).issubset(names):raise ValueError('Action cited unavailable evidence')
    if decision.action=='inspect_frames' and not set(report.evidence).intersection(
            Path(p).relative_to(folder).as_posix() for p in images):
        raise ValueError('Frame investigation must cite an actual frame')
    Path(output).write_text(report.model_dump_json(indent=2),encoding='utf-8')
    return report


def recommend(folder, stage, attempt=None, execute=False, design=False):
    from datetime import datetime, timezone
    from astra.client import CodexSDK
    from astra.jev import JevClient
    from astra.models import STAGES
    from astra.pipeline import digest
    folder=Path(folder).resolve()
    request=Request.model_validate_json((folder/'request.json').read_text(encoding='utf-8'))
    limit=STAGES.index(stage) if stage in STAGES else len(STAGES)
    paths=[folder/f'{s}.json' for s in STAGES[:limit] if (folder/f'{s}.json').is_file()]
    pattern=f'{attempt:03d}-{stage}-candidate.json' if attempt is not None else f'*-{stage}-candidate.json'
    candidates=sorted((folder/'attempts').glob(pattern))
    if candidates:
        candidate=candidates[-1];paths.append(candidate)
        audit=candidate.with_name(candidate.name.replace('-candidate.json','-astra-audit.json'))
        gate=candidate.with_name(candidate.name.replace('-candidate.json','-jev.json'))
        paths.extend(p for p in [audit,gate] if p.is_file())
    elif stage!='render':raise ValueError('No candidate for selected checkpoint')
    images=[]
    if stage=='render':
        renders=sorted((folder/'renders').glob('*/contact_sheet.png'))
        if not renders:raise ValueError('No rendered frame evidence')
        images=sorted(renders[-1].parent.glob('frame_*.png'))+[renders[-1]]
        paths+=images
        if (folder/'scene.py').is_file():paths.append(folder/'scene.py')
        for suffix in ['astra-audit','jev']:
            reports=sorted((folder/'attempts').glob(f'*-render-{suffix}.json'))
            if reports:paths.append(reports[-1])
    hashes={p.relative_to(folder).as_posix():digest(p) for p in paths}
    state={'checkpoint':stage,'original_request':request.prompt,
        'artifacts':text_evidence(folder,paths),
        'image_handling':'Jev sees text reports only. The selected Astra tool can inspect the listed images.',
        'input_hashes':hashes}
    output_dir=folder/'recommendations'/datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S-%f')
    output_dir.mkdir(parents=True)
    jev=JevClient()
    try:
        design_report=None
        if design:
            from astra.design import review_design
            design_report=review_design(jev,state,stage,output_dir/'design.json')
            state=dict(state,design_advice=design_summary(design_report))
            paths.append(output_dir/'design.json')
            hashes[(output_dir/'design.json').relative_to(folder).as_posix()]=digest(output_dir/'design.json')
        decision=select_action(jev,state,stage,output_dir/'action.json')
        report=execute_action(CodexSDK(),decision,stage=stage,request=request,folder=folder,
            paths=paths,images=images,output=output_dir/'investigation.json') if execute else None
        if any(digest(folder/name)!=value for name,value in hashes.items()):
            raise RuntimeError('Evidence changed during recommendation')
        result={'selection':decision.model_dump(),'executed':report is not None,
                'design_report':str(output_dir/'design.json') if design_report else None,
                'report':str(output_dir/'investigation.json') if report else None,
                'feedback':report.feedback if report else None,'input_hashes':hashes}
        (output_dir/'result.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
        return result
    finally:jev.close()
