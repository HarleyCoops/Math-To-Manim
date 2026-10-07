"""A cloud candidate must match a completed source-bound Astra run."""
import json
import pytest

from astra.models import STAGES
from astra.pipeline import digest, save
from scripts.export_paper_candidate import export_candidate


@pytest.fixture
def authored_run(tmp_path):
    paper = tmp_path / 'papers/quasi-riemann'
    run = tmp_path / 'runs/astra/20261007-000000-abcdef'
    paper.mkdir(parents=True)
    (run / 'attempts').mkdir(parents=True)
    save(run / 'request.json', {'prompt': 'An authored film'})
    stages = {}
    for stage in STAGES:
        content = ('from manim import *\nclass AstraFilm(ThreeDScene):\n'
                   '    def construct(self):\n        self.wait(30)\n') if stage == 'scene' else stage
        save(run / f'{stage}.json', {'summary': stage, 'content': content,
                                    'checks': [], 'sources': []})
        stages[stage] = {'hashes': {'request.json': digest(run / 'request.json'),
                                   f'{stage}.json': digest(run / f'{stage}.json')}}
        candidate = run / f'attempts/001-{stage}-candidate.json'
        candidate.write_bytes((run / f'{stage}.json').read_bytes())
        audit = run / f'attempts/001-{stage}-astra-audit.json'
        save(audit, {'evidence': [candidate.relative_to(run).as_posix()]})
        save(audit.with_suffix('.record.json'), {
            'model': 'gpt-6-astra', 'role': 'astra-evidence-auditor',
            'input_hashes': {candidate.relative_to(run).as_posix(): digest(candidate)},
        })
    save(run / 'manifest.json', {'status': 'completed', 'model': 'gpt-6-astra',
         'stages': stages, 'review_mode': 'off', 'review_status': 'astra_only'})
    return tmp_path, paper, run


def test_export_preserves_exact_scene_without_claiming_a_film(authored_run):
    root, paper, run = authored_run
    result = export_candidate(paper, run, root=root)
    assert (paper / 'candidate.json').read_bytes() == (run / 'scene.json').read_bytes()
    assert result['candidate_sha256'] == digest(run / 'scene.json')
    record = json.loads((paper / 'production.json').read_text(encoding='utf-8'))
    assert record['film_status'] == 'pending_cloud_render'
    assert record['review_status'] == 'astra_only'
    assert 'video' not in record


def test_export_rejects_tampered_source_before_writing(authored_run):
    root, paper, run = authored_run
    (run / 'scene.json').write_text('{}', encoding='utf-8')
    with pytest.raises(ValueError, match='source binding'):
        export_candidate(paper, run, root=root)
    assert not (paper / 'candidate.json').exists()


def test_export_rejects_running_authoring(authored_run):
    root, paper, run = authored_run
    state = json.loads((run / 'manifest.json').read_text(encoding='utf-8'))
    state['status'] = 'running'
    save(run / 'manifest.json', state)
    with pytest.raises(ValueError, match='completed Astra'):
        export_candidate(paper, run, root=root)


def test_export_rejects_an_unbound_scene_audit(authored_run):
    root, paper, run = authored_run
    (run / 'attempts/001-scene-candidate.json').write_text('{}', encoding='utf-8')
    with pytest.raises(ValueError, match='audit evidence'):
        export_candidate(paper, run, root=root)
    assert not (paper / 'candidate.json').exists()
