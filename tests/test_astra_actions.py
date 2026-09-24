from pathlib import Path
import pytest
from astra.actions import parse_action, execute_action, ActionDecision
from astra.models import Request


def raw(confidence=.9):
    return {'model':'jev-1.13.0','answers':{'next_action':{'type':'choice',
        'choice':'clarify_definitions','confidence':confidence,
        'probabilities':{'clarify_definitions':.95,'no_action':.05}}}}


def test_confident_selection_dispatches_known_action():
    d=parse_action(raw(),'brief')
    assert d.execute and d.action=='clarify_definitions'


def test_uncertain_selection_does_not_execute():
    assert not parse_action(raw(.2),'brief').execute


def test_unknown_action_rejected():
    r=raw();r['answers']['next_action']['choice']='run_arbitrary_shell'
    with pytest.raises(ValueError):parse_action(r,'brief')


def test_no_action_does_not_call_astra(tmp_path):
    class NoCalls:
        def call(self,*a,**kw):pytest.fail('Unexpected tool execution')
    d=ActionDecision(action='no_action',confidence=.9,execute=False,
        model='jev-1.13.0',probabilities={'no_action':1.})
    assert execute_action(NoCalls(),d,stage='brief',request=Request(prompt='Explain topology'),
        folder=tmp_path,paths=[],images=[],output=tmp_path/'report.json') is None


def test_frame_inspection_requires_real_images(tmp_path):
    d=ActionDecision(action='inspect_frames',confidence=.9,execute=True,
        model='jev-1.13.0',probabilities={'inspect_frames':1.})
    with pytest.raises(ValueError,match='actual images'):
        execute_action(None,d,stage='render',request=Request(prompt='Explain topology'),
            folder=tmp_path,paths=[],images=[],output=tmp_path/'report.json')
