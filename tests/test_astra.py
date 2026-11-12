"""Behavioral tests for gated advancement, rollback, evidence, and safe resumption."""
import json
from pathlib import Path
import pytest
from astra.models import Artifact, Assessment, Request
from astra.pipeline import Pipeline
from astra.rendering import validate_source
from astra.environment import clean_environment
from astra.jev import GateDecision

SOURCE='from manim import *\nclass AstraFilm(ThreeDScene):\n    def construct(self):\n        self.wait(30)\n'

def verdict(evidence, reject=False, target='scene'):
    return Assessment(mathematics=.5 if reject else .95,pedagogy=.95,visual_design=.95,
                      implementation=.95,verified=True,defects=['fix'] if reject else [],
                      feedback='repair the named defect',evidence=evidence,
                      limitations=['model judgment'],repair_stage=target)

def fake_answer(question, choice=None):
    """A confident, well-formed Jev answer of the question's type; choices default to the last option."""
    if question['type']=='score':
        return {'type':'score','score':4.,'confidence':.9,'probabilities':{'0':0.,'1':0.,'2':0.,'3':0.,'4':1.}}
    if question['type']=='noul':
        return {'type':'noul','noul':.99}
    options=list(question['criteria']);pick=choice if choice in options else options[-1]
    return {'type':'choice','choice':pick,'confidence':.9,'probabilities':{o:float(o==pick) for o in options}}

class FakeJev:
    """The reviewer protocol: a gate verdict mirroring the Astra audit, plus typed answers to raw questions."""
    def __init__(self, choice=None):
        self.choice=choice
    def review(self, *, state, stage, audit, output):
        assert state['astra_evidence_audit'] == audit.model_dump()
        return GateDecision(approved=audit.verified and not audit.defects,
            repair_stage=audit.repair_stage, feedback=audit.feedback,
            defects=audit.defects, model='jev-test-fake', answers={})
    def ask(self, *, state, questions, output):
        return {'model':'jev-test-fake','answers':{k:fake_answer(q,self.choice) for k,q in questions.items()}}

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

def fake_probe(folder,source,attempt,quality):
    p=folder/f'probes/{attempt:03d}';p.mkdir(parents=True)
    record=p/'execution.json';record.write_text('{}')
    frame=p/'frame.png';frame.write_bytes(b'test')
    return record,frame

def fake_render(folder,source,quality,attempt,**options):
    p=folder/f'renders/{attempt:03d}';p.mkdir(parents=True)
    paths=[p/n for n in ('film.mp4','frame.png','sheet.png')]
    for path in paths:path.write_bytes(b'test')
    (p/'metadata.json').write_text(json.dumps({'format':{'duration':'90.0'}}))
    return paths[0],[paths[1]],paths[2]

def test_all_stages_and_render_require_jev(tmp_path):
    client=FakeSDK();result=Pipeline(client,tmp_path,fake_render,jev=FakeJev(),prober=fake_probe).run(Request(review_mode='gated',prompt='Explain topology'))
    assert result['status']=='completed'
    assert len(result['events'])==5
    assert all(e['approved'] for e in result['events'])
    assert len(client.calls)==9
    assert result['video_sha256']


def test_advisory_rejection_does_not_retry_or_claim_approval(tmp_path):
    client=FakeSDK('scene')
    result=Pipeline(client,tmp_path,fake_render,jev=FakeJev(),prober=fake_probe).run(Request(prompt='Explain topology'))
    assert result['status']=='completed' and result['review_status']=='advisory'
    assert sum('scene-candidate' in c for c in client.calls)==1
    assert any(e.get('approved') is False for e in result['events'])


def test_jev_off_retains_astra_audits_without_constructing_jev(tmp_path,monkeypatch):
    monkeypatch.setattr('astra.pipeline.JevClient', lambda: pytest.fail('Jev must remain off'))
    client=FakeSDK()
    pipe=Pipeline(client,tmp_path,fake_render,prober=fake_probe)
    result=pipe.run(Request(prompt='Explain topology',review_mode='off'))
    assert result['status']=='completed' and result['review_status']=='astra_only'
    assert len(client.calls)==9 and result['video_sha256']
    assert all(e['review']['evaluator']=='disabled' and not e['approved'] for e in result['events'])
    client.calls.clear()
    resumed=pipe.run(None,folder=Path(result['run_dir']))
    assert resumed['review_status']=='astra_only' and len(client.calls)==1


def test_advisory_api_failure_is_recorded_without_retry(tmp_path):
    class UnavailableJev:
        calls=0
        def review(self,**kwargs):
            self.calls+=1
            raise ConnectionError('offline')
    jev=UnavailableJev()
    result=Pipeline(FakeSDK(),tmp_path,fake_render,jev=jev,prober=fake_probe).run(Request(prompt='Explain topology'))
    assert result['status']=='completed' and jev.calls==5
    assert all(e['review']['evaluator']=='unavailable' for e in result['events'])
    assert not any(e['approved'] for e in result['events'])


def test_local_render_never_constructs_model_clients(tmp_path,monkeypatch):
    import ast
    import astra.local_render as local
    # The render-only path does not even import the model or Jev client modules.
    imported={node.module for node in ast.walk(ast.parse(Path(local.__file__).read_text(encoding='utf-8')))
              if isinstance(node,ast.ImportFrom)}
    assert not imported & {'astra.pipeline','astra.client','astra.jev'}
    folder=tmp_path/'run';folder.mkdir()
    (folder/'manifest.json').write_text('{"events":[]}')
    scene=folder/'saved.py';scene.write_text(SOURCE)
    monkeypatch.setattr(local,'render',fake_render)
    result=local.render_existing(folder,scene)
    assert result['status']=='completed' and result['review_status']=='not_reviewed'
    assert result['review_mode']=='disabled_for_local_render'
    assert result['video_sha256'] and result['duration_seconds']==90.0

def test_rejection_invalidates_downstream_and_repairs_upstream(tmp_path):
    client=FakeSDK('storyboard');result=Pipeline(client,tmp_path,fake_render,jev=FakeJev(),prober=fake_probe).run(Request(review_mode='gated',prompt='Explain topology'))
    assert result['status']=='completed'
    assert sum('mathematics-candidate' in c for c in client.calls)==2
    assert sum('storyboard-candidate' in c for c in client.calls)==2
    assert sum('brief-candidate' in c for c in client.calls)==1

def test_exhausted_gate_fails_without_render(tmp_path):
    client=FakeSDK('brief')
    with pytest.raises(RuntimeError,match='budget'):
        Pipeline(client,tmp_path,lambda *a:pytest.fail('must not render'),jev=FakeJev(),prober=fake_probe).run(Request(review_mode='gated',prompt='Explain topology',max_revisions=0))
    assert json.loads(next(tmp_path.glob('*/manifest.json')).read_text())['status']=='failed'

def test_resume_rechecks_render_and_changed_artifacts(tmp_path):
    client=FakeSDK();pipe=Pipeline(client,tmp_path,fake_render,jev=FakeJev(),prober=fake_probe)
    first=pipe.run(Request(review_mode='gated',prompt='Explain topology'));folder=Path(first['run_dir'])
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


def test_resume_quality_preserves_planning_but_rechecks_scene(tmp_path):
    client=FakeSDK();qualities=[]
    def renderer(folder,source,quality,attempt):
        qualities.append(quality)
        return fake_render(folder,source,quality,attempt)
    pipe=Pipeline(client,tmp_path,renderer,jev=FakeJev(),prober=fake_probe)
    first=pipe.run(Request(review_mode='gated',prompt='Explain topology'));folder=Path(first['run_dir'])
    client.calls.clear()
    result=pipe.run(None,folder=folder,render_quality='m')
    assert result['status']=='completed' and qualities==['h','m']
    assert [c for c in client.calls if 'candidate' in c]==['006-scene-candidate.json']
    assert 'delivery.json' in result['stages']['scene']['hashes']
    client.calls.clear();pipe.run(None,folder=folder)
    assert qualities[-1]=='m' and not any('candidate' in c for c in client.calls)

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
        Pipeline(BadSDK(),tmp_path,fake_render,jev=FakeJev(),prober=fake_probe).run(Request(review_mode='gated',prompt='Explain topology'))


def test_one_reevaluation_requires_new_investigation_evidence(tmp_path):
    folder=tmp_path/'run';(folder/'attempts').mkdir(parents=True)
    candidate=folder/'attempts/001-brief-candidate.json'
    candidate.write_text('{}')
    states=[]
    class InvestigatingJev(FakeJev):
        def review(self,*,state,stage,audit,output):
            states.append(state)
            return GateDecision(approved='additional_astra_investigation' in state,
                repair_stage='brief',feedback='Need evidence',defects=[],model='jev-test-fake',answers={})
    client=FakeSDK()
    result=Pipeline(client,tmp_path)._judge(InvestigatingJev(choice='clarify_definitions'),folder,
        Request(review_mode='gated',prompt='Explain topology'),'brief',[candidate],[],1)
    assert result.approved and len(states)==2
    assert 'additional_astra_investigation' not in states[0]
    assert states[1]['additional_astra_investigation']['feedback']=='repair the named defect'
    assert client.calls==['001-brief-astra-audit.json','001-brief-investigation.json']
    for kind in ('design','action','investigation','final-decision'):
        assert (folder/f'attempts/001-brief-{kind}.json').is_file()


def test_wrong_delivery_profile_fails_without_spending_scene_repairs(tmp_path):
    from astra.rendering import DeliveryError
    def wrong_profile(folder,source,quality,attempt,**options):
        raise DeliveryError('Wrong frame rate')
    client=FakeSDK()
    with pytest.raises(DeliveryError):
        Pipeline(client,tmp_path,wrong_profile,prober=fake_probe).run(Request(prompt='Explain topology',review_mode='off'))
    assert sum('scene-candidate' in c for c in client.calls)==1
