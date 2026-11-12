"""Astra production chain with independent jev gates and bounded backward repair."""
from contextlib import contextmanager
from datetime import datetime, timezone
import json
from pathlib import Path
import shutil
import sys
import traceback

from astra.actions import select_action, execute_action
from astra.client import CodexSDK, MODEL
from astra.design import review_design, design_summary
from astra.evidence import text_evidence
from astra.jev import JevClient, GateDecision, evaluator_name, policy_name
from astra.models import Artifact, Assessment, Request, STAGES, SOURCE_STAGE, REPAIR_OWNER, SEARCHES_WEB
from astra.prompts import specialist_prompt, judge_prompt
from astra.render_worker import PROFILES
from astra.rendering import DeliveryError, render, probe, validate_source
from astra.runs import attempt_index, attempt_path, create_run, digest, runs_root, save

AUDITOR_ROLE = 'astra-evidence-auditor'
REVIEW_STATUS = {'advisory': 'advisory', 'gated': 'approved', 'off': 'astra_only'}


def progress(message):
    """Operator progress goes to stderr; stdout carries the CLI's JSON result."""
    print(message, file=sys.stderr, flush=True)


def relative(folder, path):
    return Path(path).relative_to(folder).as_posix()


def disabled_decision(stage, feedback, evaluator):
    return GateDecision(approved=False, repair_stage=REPAIR_OWNER[stage], feedback=feedback,
                        defects=[], evaluator=evaluator, model=evaluator, answers={})


class Pipeline:
    """A reviewer (``jev``) offers ``review`` for the gate and ``ask`` for raw questions.

    Injected collaborators are seams for tests and operators; ``jev=None`` means a real
    TypeSafe client is opened per run and closed afterwards.
    """
    def __init__(self, client=None, runs_dir=None, renderer=None, jev=None, prober=None):
        self.client = client or CodexSDK()
        self.runs_dir = Path(runs_dir or runs_root())
        self.renderer = renderer or render
        self.jev = jev
        self.prober = prober or probe

    @contextmanager
    def _reviewer(self, request):
        if request.review_mode == 'off' or self.jev is not None:
            yield self.jev
            return
        # Fail before consuming Codex usage if the real Jev credentials are absent.
        jev = JevClient()
        try:
            yield jev
        finally:
            jev.close()

    def _judge(self, jev, folder, request, stage, paths, images, index):
        hashes = {relative(folder, p): digest(p) for p in paths}
        context = '\n'.join(hashes)
        output = attempt_path(folder, index, stage, 'astra-audit')
        result = self.client.call(judge_prompt(stage,request,context,list(hashes)),
                                  cwd=folder,output=output,schema=Assessment,images=images,
                                  effort=request.effort,search=stage in SEARCHES_WEB,
                                  evidence_paths=list(hashes))
        save(output, result.model_dump())
        if any(digest(folder/name)!=value for name,value in hashes.items()):
            raise RuntimeError('Evidence changed during Astra audit')
        if not set(result.evidence).issubset(hashes):
            raise RuntimeError('Astra auditor cited evidence outside the supplied bundle')
        if stage=='render' and not set(result.evidence).intersection(relative(folder, p) for p in images):
            raise RuntimeError('Render review must cite actual frames')
        save(output.with_suffix('.record.json'),dict(model=MODEL,input_hashes=hashes,
             role=AUDITOR_ROLE,score_kind='uncalibrated_model_judgment'))
        if request.review_mode == 'off':
            decision = disabled_decision(stage, 'TypeSafe Jev disabled by request. Astra evidence audit retained; no Jev approval claimed.', 'disabled')
            save(attempt_path(folder, index, stage, 'review-disabled'), decision.model_dump())
            return decision
        state={'checkpoint':stage,'original_request':request.prompt,
               'artifacts':text_evidence(folder,paths),
               'astra_evidence_audit':result.model_dump(),
               'image_handling':'Jev receives only Astra text observations of images, never pixels.',
               'input_hashes':hashes}
        try:
            decision=jev.review(state=state,stage=stage,audit=result,
                                output=attempt_path(folder, index, stage, 'jev'))
        except Exception as exc:
            if request.review_mode=='gated':raise
            traceback.print_exc()
            decision=disabled_decision(stage, f'Advisory review unavailable: {type(exc).__name__}. No retry or approval inferred.', 'unavailable')
            save(attempt_path(folder, index, stage, 'advisory-unavailable'),decision.model_dump())
        if request.review_mode=='advisory':
            # Preserve Jev's actual verdict, but do not dispatch investigations,
            # repeat evaluations, or regenerate work because of that verdict.
            return decision
        # Gated: retain design advice, then allow one Jev-selected investigation over new evidence.
        design_path=attempt_path(folder, index, stage, 'design')
        design=review_design(jev,state,stage,design_path)
        state=dict(state,design_advice=design_summary(design))
        paths=paths+[design_path]
        hashes[relative(folder, design_path)]=digest(design_path)
        if not decision.approved:
            action = select_action(jev, dict(state, gate_decision=decision.model_dump()),
                                   stage, attempt_path(folder, index, stage, 'action'))
            investigation_path=attempt_path(folder, index, stage, 'investigation')
            report = execute_action(self.client, action, stage=stage, request=request,
                                    folder=folder, paths=paths, images=images, output=investigation_path)
            if report is not None:
                decision.feedback += '\nJev-selected Astra investigation: ' + action.action + '\n' + report.feedback
                hashes[relative(folder, investigation_path)]=digest(investigation_path)
                combined=result.model_copy(update={
                    'verified':result.verified and report.verified,
                    'defects':list(dict.fromkeys(result.defects+report.defects)),
                    'feedback':result.feedback+'\nAdditional investigation:\n'+report.feedback,
                })
                enriched=dict(state,additional_astra_investigation=report.model_dump(),
                              astra_evidence_audit=combined.model_dump())
                # One new decision over genuinely new evidence, not repeated sampling.
                # The original audit's unresolved blockers still cannot be overruled.
                decision=jev.review(state=enriched,stage=stage,audit=combined,
                                    output=attempt_path(folder, index, stage, 'jev-after-tool'))
                if not decision.approved:
                    decision.feedback += '\nJev-selected Astra investigation: ' + action.action + '\n' + report.feedback
            else:
                decision.feedback += '\nNo additional investigation executed: ' + action.action
            save(attempt_path(folder, index, stage, 'final-decision'), decision.model_dump())
        if any(digest(folder/name)!=value for name,value in hashes.items()):
            raise RuntimeError('Evidence changed during TypeSafe Jev evaluation')
        return decision

    def run(self, request, *, folder=None, feedback='', render_quality=None):
        if folder is not None:
            folder=Path(folder).resolve()
            request=Request.model_validate_json((folder/'request.json').read_text(encoding='utf-8'))
        with self._reviewer(request) as jev:
            if folder is None:
                folder,_=create_run(request, self.runs_dir)
            return self._produce(jev, folder, request, feedback, render_quality)

    def _produce(self, jev, folder, request, feedback, render_quality):
        (folder/'attempts').mkdir(exist_ok=True)
        # A local resume reuses only accepted artifacts whose exact hashes still match.
        ledger_path=folder/'manifest.json'
        ledger=json.loads(ledger_path.read_text(encoding='utf-8')) if ledger_path.exists() else dict(model=MODEL,stages={},events=[])
        policy = policy_name(request.review_mode)
        if ledger.get('evaluator_policy') != policy:
            ledger['stages'] = {}
        delivery_path=folder/'delivery.json'
        if render_quality is not None:
            if render_quality not in PROFILES:raise ValueError('Invalid render quality')
            delivery={'quality':render_quality}
            if not delivery_path.exists() or json.loads(delivery_path.read_text(encoding='utf-8'))!=delivery:
                save(delivery_path,delivery)
                ledger['stages'].pop(SOURCE_STAGE,None)
                ledger['events'].append(dict(stage='delivery',attempt=0,quality=render_quality,
                    reason='User changed delivery quality; scene and render require fresh review.'))
        if delivery_path.exists():
            quality=json.loads(delivery_path.read_text(encoding='utf-8'))['quality']
            width,height,fps=PROFILES[quality]
            request=request.model_copy(update={'quality':quality,'prompt':request.prompt+
                f'\nLatest user delivery override: {width}x{height} at {fps} fps supersedes all earlier resolution/fps requirements. Preserve the mathematical content and visual design.'})
        ledger.update(status='running',error=None,run_dir=str(folder),evaluator_policy=policy,
                      evaluator=evaluator_name(request.review_mode))
        save(ledger_path,ledger)
        revisions=0; i=0
        attempt=max([index for index in map(attempt_index,(folder/'attempts').iterdir()) if index is not None]
                    + [event['attempt'] for event in ledger['events']] + [0])
        try:
            while True:
                while i < len(STAGES):
                    stage=STAGES[i]
                    accepted=ledger['stages'].get(stage)
                    if accepted and all((folder/p).is_file() and digest(folder/p)==h for p,h in accepted['hashes'].items()):
                        progress(f'cached: {stage}'); i+=1; continue
                    # Invalidate this stage and every downstream stage before writing anything.
                    for name in STAGES[i:]: ledger['stages'].pop(name,None)
                    save(ledger_path,ledger)
                    attempt+=1
                    progress(f'Astra {stage}, attempt {attempt}')
                    context='\n'.join(f'{name}.json' for name in STAGES[:i])
                    candidate_path=attempt_path(folder, attempt, stage, 'candidate')
                    artifact=self.client.call(specialist_prompt(stage,request,context,feedback),cwd=folder,
                         output=candidate_path,schema=Artifact,effort=request.effort,search=stage in SEARCHES_WEB)
                    save(candidate_path,artifact.model_dump())
                    if stage==SOURCE_STAGE:
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
                    if stage==SOURCE_STAGE and delivery_path.exists():paths.append(delivery_path)
                    images=[]
                    if stage==SOURCE_STAGE and request.render:
                        try:
                            execution,frame=self.prober(folder,artifact.content,attempt,request.quality)
                        except RuntimeError as exc:
                            revisions+=1
                            ledger['events'].append(dict(stage='scene_probe',attempt=attempt,error=str(exc)))
                            if revisions>request.max_revisions:raise
                            feedback=str(exc);save(ledger_path,ledger);continue
                        paths.extend([execution,frame]);images=[frame]
                    progress(f'Astra evidence audit{ " (Jev off)" if request.review_mode=="off" else " -> TypeSafe Jev" }: {stage}')
                    review=self._judge(jev,folder,request,stage,paths,images,attempt)
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
                    if stage==SOURCE_STAGE and delivery_path.exists():deps.append(delivery_path)
                    ledger['stages'][stage]={'hashes':{relative(folder, p):digest(p) for p in deps}}
                    save(ledger_path,ledger); i+=1;feedback=''
                if not request.render: break
                attempt+=1
                source=Artifact.model_validate_json((folder/f'{SOURCE_STAGE}.json').read_text(encoding='utf-8')).content
                (folder/'scene.py').write_text(source,encoding='utf-8')
                progress(f'Rendering {request.quality}, attempt {attempt}')
                try:
                    video,frames,sheet=self.renderer(folder,source,request.quality,attempt)
                except DeliveryError:
                    raise  # A renderer fault; repairing the scene source cannot fix it.
                except (RuntimeError, ValueError) as exc:
                    revisions+=1
                    ledger['events'].append(dict(stage='render',attempt=attempt,error=str(exc)))
                    if revisions>request.max_revisions: raise
                    feedback='Render failed. Repair source: '+str(exc);i=STAGES.index(REPAIR_OWNER['render'])
                    ledger['stages'].pop(REPAIR_OWNER['render'],None);save(ledger_path,ledger);continue
                paths=[folder/f'{name}.json' for name in STAGES]+[folder/'scene.py']+frames+[sheet]
                metadata=sheet.parent/'metadata.json'
                if metadata.exists():paths.append(metadata)
                if delivery_path.exists():paths.append(delivery_path)
                progress('Astra frame inspection' + (' (Jev off)' if request.review_mode=='off' else ' -> TypeSafe Jev decision'))
                review=self._judge(jev,folder,request,'render',paths,frames+[sheet],attempt)
                ledger['events'].append(dict(stage='render',attempt=attempt,approved=review.approved,
                                           review=review.model_dump()))
                save(ledger_path,ledger)
                if review.approved or request.review_mode!='gated':
                    ledger.update(video=str(video.relative_to(folder)),contact_sheet=str(sheet.relative_to(folder)),
                                  video_sha256=digest(video))
                    break
                revisions+=1
                if revisions>request.max_revisions:raise RuntimeError('Render review revision budget exhausted')
                i=STAGES.index(review.repair_stage);feedback=review.model_dump_json()
                for name in STAGES[i:]:ledger['stages'].pop(name,None)
            ledger.update(status='completed',review_mode=request.review_mode,
                          review_status=REVIEW_STATUS[request.review_mode],
                          completed_utc=datetime.now(timezone.utc).isoformat())
        except Exception as exc:
            ledger.update(status='failed',error=f'{type(exc).__name__}: {exc}')
            raise
        finally:save(ledger_path,ledger)
        return ledger
