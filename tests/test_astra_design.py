import pytest
from astra.design import mapping,questions,interpret
from astra.actions import STAGE_ACTIONS


def response(stage,confidence=.9):
    return {'model':'jev-1.13.0','answers':{k:{'type':'score','score':2.,
        'confidence':confidence,'probabilities':{'0':0.,'1':0.,'2':1.,'3':0.,'4':0.}}
        for k in questions(stage)}}


def test_detailed_mapping_is_stage_scoped_and_actionable():
    assert len(mapping())==16
    for stage in STAGE_ACTIONS:
        assert all(r['action'] in STAGE_ACTIONS[stage] for r in mapping(stage))
        assert all(r['evidence'] and r['repair'] and r['verify'] for r in mapping(stage))


def test_high_confidence_weakness_is_advice_not_approval():
    r=interpret(response('storyboard'),'storyboard')
    assert r['advisory_only'] and r['priority']
    assert all(f['status']=='improve' for f in r['findings'])
    assert 'approved' not in r


def test_uncertainty_requests_evidence_not_speculative_repair():
    r=interpret(response('render',.3),'render')
    assert not r['priority']
    assert all(f['status']=='investigate' for f in r['findings'])


def test_incomplete_design_response_fails_closed():
    r=response('brief');r['answers'].pop(next(iter(r['answers'])))
    with pytest.raises(ValueError):interpret(r,'brief')
