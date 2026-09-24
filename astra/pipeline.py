"""Astra production chain with independent jev gates and bounded backward repair."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import uuid

from astra.client import CodexSDK, MODEL
from astra.jev import JevClient, GateDecision, POLICY_VERSION
from astra.evidence import text_evidence, design_summary
from astra.models import Artifact, Assessment, Request, STAGES
from astra.prompts import specialist_prompt, judge_prompt
from astra.rendering import render, probe, validate_source

ROOT = Path(__file__).resolve().parents[1]

def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def save(path, value):
    path = Path(path)
    temp = path.with_suffix('.tmp')
    temp.write_text(json.dumps(value,indent=2,ensure_ascii=False),encoding='utf-8')
    temp.replace(path)

class Pipeline:
    def __init__(self, client=None, runs_dir=None, renderer=None, jev=None, prober=None):
        self.client = client or CodexSDK()
        self.runs_dir = Path(runs_dir or ROOT/'runs/astra')
        self.renderer = renderer or render
        self.jev = jev
        self.prober = prober or probe

    def _judge(self, folder, request, stage, paths, images, index):
        hashes = {str(p.relative_to(folder)).replace('\\','/'): digest(p) for p in paths}
        context = '\n'.join(hashes)
        output = folder/f'attempts/{index:03d}-{stage}-astra-audit.json'
        result = self.client.call(judge_prompt(stage,request,context,list(hashes)),
                                  cwd=folder,output=output,schema=Assessment,images=images,
                                  effort=request.effort,search=stage=='mathematics',
                                  evidence_paths=list(hashes))
        save(output, result.model_dump())
        if any(digest(folder/name)!=value for name,value in hashes.items()):
            raise RuntimeError('Evidence changed during Astra audit')
        if not set(result.evidence).issubset(hashes):
            raise RuntimeError('Astra auditor cited evidence outside the supplied bundle')
        if stage=='render' and not set(result.evidence).intersection(
                str(p.relative_to(folder)).replace('\\','/') for p in images):
            raise RuntimeError('Render review must cite actual frames')
        save(output.with_suffix('.record.json'),dict(model=MODEL,input_hashes=hashes,
             role='astra-evidence-auditor',score_kind='uncalibrated_model_judgment'))
        state={'checkpoint':stage,'original_request':request.prompt,
               'artifacts':text_evidence(folder,paths),
               'astra_evidence_audit':result.model_dump(),
               'image_handling':'Jev receives only Astra text observations of images, never pixels.',
               'input_hashes':hashes}
        try:
            decision=self.jev.review(state=state,stage=stage,audit=result,
                                     output=folder/f'attempts/{index:03d}-{stage}-jev.json')
        except Exception as exc:
            if request.review_mode=='gated':raise
            decision=GateDecision(approved=False,repair_stage='scene' if stage=='render' else stage,
                feedback=f'Advisory review unavailable: {type(exc).__name__}. No retry or approval inferred.',
                defects=[],evaluator='unavailable',model='unavailable',answers={})
            save(folder/f'attempts/{index:03d}-{stage}-advisory-unavailable.json',decision.model_dump())
        if request.review_mode=='advisory':
            # Preserve Jev's actual verdict, but do not dispatch investigations,
            # repeat evaluations, or regenerate work because of that verdict.
            return decision
        if isinstance(self.jev, JevClient):
            from astra.design import review_design
            design=review_design(self.jev,state,stage,folder/f'attempts/{index:03d}-{stage}-design.json')
            state=dict(state,design_advice=design_summary(design))
            design_path=folder/f'attempts/{index:03d}-{stage}-design.json'
            paths=paths+[design_path]
            hashes[design_path.relative_to(folder).as_posix()]=digest(design_path)
        if not decision.approved and isinstance(self.jev, JevClient):
            from astra.actions import select_action, execute_action
            action = select_action(self.jev, dict(state, gate_decision=decision.model_dump()),
                                   stage, folder/f'attempts/{index:03d}-{stage}-action.json')
            report = execute_action(self.client, action, stage=stage, request=request,
                                    folder=folder, paths=paths, images=images,
                                    output=folder/f'attempts/{index:03d}-{stage}-investigation.json')
            if report is not None:
                decision.feedback += '\nJev-selected Astra investigation: ' + action.action + '\n' + report.feedback
                investigation_path=folder/f'attempts/{index:03d}-{stage}-investigation.json'
                hashes[investigation_path.relative_to(folder).as_posix()]=digest(investigation_path)
                combined=result.model_copy(update={
                    'verified':result.verified and report.verified,
                    'defects':list(dict.fromkeys(result.defects+report.defects)),
                    'feedback':result.feedback+'\nAdditional investigation:\n'+report.feedback,
                })
                enriched=dict(state,additional_astra_investigation=report.model_dump(),
                              astra_evidence_audit=combined.model_dump())
                # One new decision over genuinely new evidence, not repeated sampling.
                # The original audit's unresolved blockers still cannot be overruled.
                decision=self.jev.review(state=enriched,stage=stage,audit=combined,
                    output=folder/f'attempts/{index:03d}-{stage}-jev-after-tool.json')
                if not decision.approved:
                    decision.feedback += '\nJev-selected Astra investigation: ' + action.action + '\n' + report.feedback
            else:
                decision.feedback += '\nNo additional investigation executed: ' + action.action
            save(folder/f'attempts/{index:03d}-{stage}-final-decision.json', decision.model_dump())
        if any(digest(folder/name)!=value for name,value in hashes.items()):
            raise RuntimeError('Evidence changed during TypeSafe Jev evaluation')
        return decision

    def run(self, request, *, folder=None, feedback='', render_quality=None):
        # Fail before consuming Codex usage if the real Jev credentials are absent.
        if self.jev is None:
            self.jev = JevClient()
        if folder is None:
            folder=self.runs_dir/(datetime.now(timezone.utc).strftime('%Y%m%d-%H%M%S')+'-'+uuid.uuid4().hex[:6])
            folder.mkdir(parents=True)
            save(folder/'request.json',request.model_dump())
        else:
            folder=Path(folder).resolve()
            request=Request.model_validate_json((folder/'request.json').read_text(encoding='utf-8'))
        (folder/'attempts').mkdir(exist_ok=True)
        # A local resume reuses only accepted artifacts whose exact hashes still match.
        ledger_path=folder/'manifest.json'
        ledger=json.loads(ledger_path.read_text()) if ledger_path.exists() else dict(model=MODEL,stages={},events=[])
        if ledger.get('evaluator_policy') != POLICY_VERSION:
            ledger['stages'] = {}
        delivery_path=folder/'delivery.json'
        if render_quality is not None:
            if render_quality not in {'l','m','h'}:raise ValueError('Invalid render quality')
            delivery={'quality':render_quality}
            if not delivery_path.exists() or json.loads(delivery_path.read_text())!=delivery:
                save(delivery_path,delivery)
                ledger['stages'].pop('scene',None)
                ledger['events'].append(dict(stage='delivery',attempt=0,quality=render_quality,
                    reason='User changed delivery quality; scene and render require fresh review.'))
        if delivery_path.exists():
            quality=json.loads(delivery_path.read_text())['quality']
            from astra.render_worker import PROFILES
            width,height,fps=PROFILES[quality]
            request=request.model_copy(update={'quality':quality,'prompt':request.prompt+
                f'\nLatest user delivery override: {width}x{height} at {fps} fps supersedes all earlier resolution/fps requirements. Preserve the mathematical content and visual design.'})
        ledger.update(status='running',error=None,run_dir=str(folder),evaluator_policy=POLICY_VERSION)
        save(ledger_path,ledger)
        revisions=0; i=0
        attempt=max([int(p.name.split('-')[0]) for p in (folder/'attempts').iterdir()
                     if p.name.split('-')[0].isdigit()]
                    + [event['attempt'] for event in ledger['events']] + [0])
        try:
            while True:
                while i < len(STAGES):
                    stage=STAGES[i]
                    accepted=ledger['stages'].get(stage)
                    if accepted and all((folder/p).is_file() and digest(folder/p)==h for p,h in accepted['hashes'].items()):
                        print(f'cached: {stage}',flush=True); i+=1; continue
                    # Invalidate this stage and every downstream stage before writing anything.
                    for name in STAGES[i:]: ledger['stages'].pop(name,None)
                    save(ledger_path,ledger)
                    attempt+=1
                    print(f'Astra {stage}, attempt {attempt}',flush=True)
                    context='\n'.join(f'{name}.json' for name in STAGES[:i])
                    candidate_path=folder/f'attempts/{attempt:03d}-{stage}-candidate.json'
                    artifact=self.client.call(specialist_prompt(stage,request,context,feedback),cwd=folder,
                         output=candidate_path,schema=Artifact,effort=request.effort,search=stage=='mathematics')
                    save(candidate_path,artifact.model_dump())
                    if stage=='scene':
                        try:
                            validate_source(artifact.content)
                        except (ValueError, SyntaxError) as exc:
                            revisions += 1
                            ledger['events'].append(dict(stage=stage,attempt=attempt,error=str(exc)))
                            if revisions > request.max_revisions:
                                raise RuntimeError('Static repair budget exhausted') from exc
                            feedback = 'Static source validation failed: ' + str(exc)
                            save(ledger_path,ledger)
                            continue
                    paths=[folder/f'{name}.json' for name in STAGES[:i]]+[candidate_path]
                    if stage=='scene' and delivery_path.exists():paths.append(delivery_path)
                    images=[]
                    if stage=='scene' and request.render:
                        try:
                            execution,frame=self.prober(folder,artifact.content,attempt)
                        except RuntimeError as exc:
                            revisions+=1
                            ledger['events'].append(dict(stage='scene_probe',attempt=attempt,error=str(exc)))
                            if revisions>request.max_revisions:raise
                            feedback=str(exc);save(ledger_path,ledger);continue
                        paths.extend([execution,frame]);images=[frame]
                    print(f'Astra evidence audit -> TypeSafe Jev: {stage}',flush=True)
                    review=self._judge(folder,request,stage,paths,images,attempt)
                    ledger['events'].append(dict(stage=stage,attempt=attempt,approved=review.approved,
                                               review=review.model_dump()))
                    if not review.approved and request.review_mode=='gated':
                        revisions+=1
                        if revisions>request.max_revisions: raise RuntimeError('Jev revision budget exhausted')
                        i=min(i,STAGES.index(review.repair_stage));feedback=review.model_dump_json()
                        for name in STAGES[i:]:ledger['stages'].pop(name,None)
                        save(ledger_path,ledger);continue
                    shutil.copyfile(candidate_path,folder/f'{stage}.json')
                    # Bind cached approval to the request and all upstream inputs, not just output.
                    deps=[folder/'request.json']+[folder/f'{name}.json' for name in STAGES[:i+1]]
                    if stage=='scene' and delivery_path.exists():deps.append(delivery_path)
                    ledger['stages'][stage]={'hashes':{p.relative_to(folder).as_posix():digest(p) for p in deps}}
                    save(ledger_path,ledger); i+=1;feedback=''
                if not request.render: break
                attempt+=1
                source=Artifact.model_validate_json((folder/'scene.json').read_text()).content
                (folder/'scene.py').write_text(source,encoding='utf-8')
                print(f'Rendering {request.quality}, attempt {attempt}',flush=True)
                try:
                    video,frames,sheet=self.renderer(folder,source,request.quality,attempt)
                except (RuntimeError, ValueError) as exc:
                    revisions+=1
                    ledger['events'].append(dict(stage='render',attempt=attempt,error=str(exc)))
                    if revisions>request.max_revisions: raise
                    feedback='Render failed. Repair source: '+str(exc);i=3
                    ledger['stages'].pop('scene',None);save(ledger_path,ledger);continue
                paths=[folder/f'{name}.json' for name in STAGES]+[folder/'scene.py']+frames+[sheet]
                metadata=sheet.parent/'metadata.json'
                if metadata.exists():paths.append(metadata)
                if delivery_path.exists():paths.append(delivery_path)
                print('Astra frame inspection -> TypeSafe Jev decision',flush=True)
                review=self._judge(folder,request,'render',paths,frames+[sheet],attempt)
                ledger['events'].append(dict(stage='render',attempt=attempt,approved=review.approved,
                                           review=review.model_dump()))
                save(ledger_path,ledger)
                if review.approved or request.review_mode=='advisory':
                    ledger.update(video=str(video.relative_to(folder)),contact_sheet=str(sheet.relative_to(folder)),
                                  video_sha256=digest(video))
                    break
                revisions+=1
                if revisions>request.max_revisions:raise RuntimeError('Render review revision budget exhausted')
                i=STAGES.index(review.repair_stage);feedback=review.model_dump_json()
                for name in STAGES[i:]:ledger['stages'].pop(name,None)
            ledger.update(status='completed',review_mode=request.review_mode,
                          review_status='advisory' if request.review_mode=='advisory' else 'approved',
                          completed_utc=datetime.now(timezone.utc).isoformat())
        except Exception as exc:
            ledger.update(status='failed',error=f'{type(exc).__name__}: {exc}')
            raise
        finally:save(ledger_path,ledger)
        return ledger
