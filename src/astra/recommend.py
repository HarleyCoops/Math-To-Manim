"""Standalone `recommend`: real Jev selects one Astra investigation over a run's retained evidence."""
from datetime import datetime, timezone
import json
from pathlib import Path

from astra.actions import select_action, execute_action
from astra.client import CodexSDK
from astra.design import review_design, design_summary
from astra.evidence import text_evidence
from astra.jev import JevClient
from astra.models import Request, STAGES
from astra.runs import attempt_path, attempt_paths, digest, parse_attempt


def recommend(folder, stage, attempt=None, execute=False, design=False):
    folder=Path(folder).resolve()
    request=Request.model_validate_json((folder/'request.json').read_text(encoding='utf-8'))
    limit=STAGES.index(stage) if stage in STAGES else len(STAGES)
    paths=[folder/f'{s}.json' for s in STAGES[:limit] if (folder/f'{s}.json').is_file()]
    candidates=attempt_paths(folder,'candidate',stage=stage,index=attempt)
    if candidates:
        candidate=candidates[-1];paths.append(candidate)
        index=parse_attempt(candidate)[0]
        paths.extend(p for p in [attempt_path(folder,index,stage,'astra-audit'),
                                 attempt_path(folder,index,stage,'jev')] if p.is_file())
    elif stage!='render':raise ValueError('No candidate for selected checkpoint')
    images=[]
    if stage=='render':
        renders=sorted((folder/'renders').glob('*/contact_sheet.png'))
        if not renders:raise ValueError('No rendered frame evidence')
        images=sorted(renders[-1].parent.glob('frame_*.png'))+[renders[-1]]
        paths+=images
        if (folder/'scene.py').is_file():paths.append(folder/'scene.py')
        for kind in ['astra-audit','jev']:
            reports=attempt_paths(folder,kind,stage='render')
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
