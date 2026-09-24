import json
from astra.evidence import text_evidence


def test_identical_source_is_referenced_without_loss(tmp_path):
    source='from manim import *\n'
    candidate=tmp_path/'scene.json';candidate.write_text(json.dumps({'content':source,'summary':'Scene'}))
    code=tmp_path/'scene.py';code.write_text(source)
    evidence=text_evidence(tmp_path,[candidate,code])
    assert evidence['scene.py']==source
    assert evidence['scene.json']['content']=={'exact_source_supplied_under':'scene.py'}
    assert evidence['scene.json']['summary']=='Scene'


def test_distinct_source_is_not_deduplicated(tmp_path):
    candidate=tmp_path/'scene.json';candidate.write_text(json.dumps({'content':'old source'}))
    code=tmp_path/'scene.py';code.write_text('new source')
    assert text_evidence(tmp_path,[candidate,code])['scene.json']['content']=='old source'
