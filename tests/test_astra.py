"""Behavioral tests for gated advancement, rollback, evidence, and safe resumption."""
import json
from pathlib import Path
import pytest
from astra.models import Artifact, Assessment, Request
from astra.pipeline import Pipeline
from astra.rendering import validate_source
from astra.client import clean_environment
from astra.jev import GateDecision

SOURCE='from manim import *\nclass AstraFilm(ThreeDScene):\n    def construct(self):\n        self.wait(30)\n'

def verdict(evidence, reject=False, target='scene'):
    return Assessment(mathematics=.5 if reject else .95,pedagogy=.95,visual_design=.95,
                      implementation=.95,verified=True,defects=['fix'] if reject else [],
                      feedback='repair the named defect',evidence=evidence,
                      limitations=['model judgment'],repair_stage=target)

class FakeJev:
    def review(self, *, state, stage, audit, output):
        assert state['astra_evidence_audit'] == audit.model_dump()
        return GateDecision(approved=audit.verified and not audit.defects,
            repair_stage=audit.repair_stage, feedback=audit.feedback,
            defects=audit.defects, model='jev-test-fake', answers={})

class FakeSDK:
    def __init__(self, rejected_stage=None):
        self.calls=[];self.rejected_stage=rejected_stage
    def call(self,prompt,**kw):
        self.calls.append(kw['output'].name)
        if kw['schema'] is Artifact:
            return Artifact(summary='complete',content=SOURCE if 'scene-candidate' in kw['output'].name else 'checked plan',checks=['done'],sources=[])
        # The manifest names exact supplied artifacts; use candidate or attached frame.
        candidates=sorted(kw['cwd'].glob('attempts/*-candidate.json'))
        evidence=[kw['images'][0].relative_to(kw['cwd']).as_posix()] if kw['images'] else [candidates[-1].relative_to(kw['cwd']).as_posix()]
        reject=self.rejected_stage and self.rejected_stage in kw['output'].name
        self.rejected_stage=None if reject else self.rejected_stage
        return verdict(evidence,reject=bool(reject),target='mathematics')

def fake_render(folder,source,quality,attempt):
    p=folder/f'renders/{attempt:03d}';p.mkdir(parents=True)
    paths=[p/n for n in ('film.mp4','frame.png','sheet.png')]
    for path in paths:path.write_bytes(b'test')
    return paths[0],[paths[1]],paths[2]

def test_all_stages_and_render_require_jev(tmp_path):
    client=FakeSDK();result=Pipeline(client,tmp_path,fake_render,jev=FakeJev()).run(Request(prompt='Explain topology'))
    assert result['status']=='completed'
    assert len(result['events'])==5
    assert all(e['approved'] for e in result['events'])
    assert len(client.calls)==9
    assert result['video_sha256']

def test_rejection_invalidates_downstream_and_repairs_upstream(tmp_path):
    client=FakeSDK('storyboard');result=Pipeline(client,tmp_path,fake_render,jev=FakeJev()).run(Request(prompt='Explain topology'))
    assert result['status']=='completed'
    assert sum('mathematics-candidate' in c for c in client.calls)==2
    assert sum('storyboard-candidate' in c for c in client.calls)==2
    assert sum('brief-candidate' in c for c in client.calls)==1

def test_exhausted_gate_fails_without_render(tmp_path):
    client=FakeSDK('brief')
    with pytest.raises(RuntimeError,match='budget'):
        Pipeline(client,tmp_path,lambda *a:pytest.fail('must not render'),jev=FakeJev()).run(Request(prompt='Explain topology',max_revisions=0))
    assert json.loads(next(tmp_path.glob('*/manifest.json')).read_text())['status']=='failed'

def test_resume_rechecks_render_and_changed_artifacts(tmp_path):
    client=FakeSDK();pipe=Pipeline(client,tmp_path,fake_render,jev=FakeJev())
    first=pipe.run(Request(prompt='Explain topology'));folder=Path(first['run_dir'])
    client.calls.clear();pipe.run(None,folder=folder)
    assert len(client.calls)==1 and 'render-astra-audit' in client.calls[0]
    (folder/'mathematics.json').write_text('{}')
    client.calls.clear();pipe.run(None,folder=folder)
    assert sum('candidate' in c for c in client.calls)==3

def test_credentials_not_inherited(monkeypatch):
    monkeypatch.setenv('OPENAI_API_KEY','test-secret');monkeypatch.setenv('CODEX_API_KEY','test')
    monkeypatch.setenv('XAI_API_KEY','test');monkeypatch.setenv('GH_TOKEN','test')
    env=clean_environment()
    assert not {'OPENAI_API_KEY','CODEX_API_KEY','XAI_API_KEY','GH_TOKEN'} & env.keys()

@pytest.mark.parametrize('code',['import os\n'+SOURCE,SOURCE+'\nopen("x")',SOURCE+'\neval("x")'])
def test_scene_static_screen_rejects_file_or_dynamic_execution(code):
    with pytest.raises(ValueError):validate_source(code)

def test_invalid_citations_and_mutations_fail_closed(tmp_path):
    class BadSDK(FakeSDK):
        def call(self,prompt,**kw):
            result=super().call(prompt,**kw)
            if isinstance(result,Assessment):result.evidence=['made-up.txt']
            return result
    with pytest.raises(RuntimeError,match='outside'):
        Pipeline(BadSDK(),tmp_path,fake_render,jev=FakeJev()).run(Request(prompt='Explain topology'))


def test_one_reevaluation_requires_new_investigation_evidence(tmp_path,monkeypatch):
    import astra.pipeline as module
    from astra.actions import ActionDecision
    folder=tmp_path/'run';(folder/'attempts').mkdir(parents=True)
    candidate=folder/'attempts/001-brief-candidate.json'
    candidate.write_text('{}')
    states=[]
    class FakeLiveJev:
        def review(self,*,state,stage,audit,output):
            states.append(state)
            return GateDecision(approved='additional_astra_investigation' in state,
                repair_stage='brief',feedback='Need evidence',defects=[],model='jev-test-fake',answers={})
    def design(jev,state,stage,output):
        result={'policy':'test','advisory_only':True,'priority':[],'findings':[]}
        Path(output).write_text(json.dumps(result));return result
    def investigate(client,decision,**kw):
        report=verdict(['attempts/001-brief-candidate.json'])
        report.feedback='New independent evidence'
        Path(kw['output']).write_text(report.model_dump_json());return report
    monkeypatch.setattr(module,'JevClient',FakeLiveJev)
    monkeypatch.setattr('astra.design.review_design',design)
    monkeypatch.setattr('astra.actions.select_action',lambda *a:ActionDecision(
        action='clarify_definitions',confidence=.9,execute=True,model='jev-test-fake',probabilities={}))
    monkeypatch.setattr('astra.actions.execute_action',investigate)
    result=Pipeline(FakeSDK(),jev=FakeLiveJev())._judge(folder,Request(prompt='Explain topology'),
        'brief',[candidate],[],1)
    assert result.approved and len(states)==2
    assert 'additional_astra_investigation' not in states[0]
    assert states[1]['additional_astra_investigation']['feedback']=='New independent evidence'
    assert (folder/'attempts/001-brief-final-decision.json').is_file()
