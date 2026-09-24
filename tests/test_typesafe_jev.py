"""Offline contract tests; these fabricated responses are not live review evidence."""
import copy
import pytest
from astra.jev import evaluate_response, load_api_key
from astra.models import Assessment


def audit():
    return Assessment(mathematics=1.0,pedagogy=1.0,visual_design=1.0,
        implementation=1.0,verified=True,defects=[],feedback='Checked',
        evidence=['brief.json'],limitations=[],repair_stage='brief')


def response():
    score={'type':'score','score':3.9,'confidence':.9,
           'probabilities':{'0':0.,'1':0.,'2':0.,'3':.1,'4':.9}}
    return {'model':'jev-1.13.0','answers':{
        'criterion_1':copy.deepcopy(score),'criterion_2':copy.deepcopy(score),
        'evidence_sufficient':{'type':'noul','noul':.98},
        'blocking_defect':{'type':'noul','noul':.01},
        'repair_target':{'type':'choice','choice':'mathematics','confidence':.9,
            'probabilities':{'brief':.02,'mathematics':.94,'storyboard':.02,'scene':.02}}}}


def test_real_schema_accepts_sufficient_evidence():
    assert evaluate_response(response(),stage='brief',audit=audit()).approved


@pytest.mark.parametrize('question,field,value',[
    ('criterion_1','confidence',.4),('evidence_sufficient','noul',.6),
    ('blocking_defect','noul',.4)])
def test_uncertain_or_blocked_evidence_rejected(question,field,value):
    r=response();r['answers'][question][field]=value
    assert not evaluate_response(r,stage='brief',audit=audit()).approved


def test_astra_blocker_cannot_be_overruled_by_jev():
    a=audit();a.defects=['Wrong equation']
    assert not evaluate_response(response(),stage='brief',audit=a).approved


def test_uncertain_routing_stays_at_current_stage():
    r=response();r['answers']['repair_target']['confidence']=.4
    a=audit();a.defects=['Need evidence']
    assert evaluate_response(r,stage='brief',audit=a).repair_stage=='brief'


def test_malformed_answer_fails_closed():
    r=response();del r['answers']['blocking_defect']
    with pytest.raises(ValueError):evaluate_response(r,stage='brief',audit=audit())
    r=response();r['answers']['criterion_1']['score']=float('nan')
    with pytest.raises(ValueError):evaluate_response(r,stage='brief',audit=audit())


def test_file_key_is_not_exported(tmp_path,monkeypatch):
    import os
    monkeypatch.delenv('TYPESAFE_API_KEY',raising=False)
    (tmp_path/'.env.local').write_text('TYPESAFE_API_KEY="fake-local-test"')
    assert load_api_key(tmp_path)=='fake-local-test'
    assert 'TYPESAFE_API_KEY' not in os.environ
    monkeypatch.setenv('TYPESAFE_API_KEY','fake-env-test')
    assert load_api_key(tmp_path)=='fake-env-test'


def test_missing_key_fails_before_model_calls(tmp_path,monkeypatch):
    monkeypatch.delenv('TYPESAFE_API_KEY',raising=False)
    with pytest.raises(RuntimeError,match='Save TYPESAFE_API_KEY'):load_api_key(tmp_path)


def test_rounded_distribution_tolerance_preserves_valid_api_response():
    r=response()
    r['answers']['criterion_1'].update(score=3.55,confidence=.63,
        probabilities={'0':0.,'1':0.,'2':.01,'3':.4,'4':.59})
    # Rounded probabilities imply 3.58; this is valid rounding, not malformed data.
    d=evaluate_response(r,stage='brief',audit=audit())
    assert not d.approved  # Confidence policy still rejects it.


def test_http_receipt_records_transport_without_credentials(tmp_path,monkeypatch):
    import json
    import httpx2
    import typesafe_sdk  # Resolve SDK type annotations before replacing the HTTP factory.
    from astra.jev import JevClient
    original_client=httpx2.Client
    def handler(request):
        assert request.headers['authorization']=='Bearer fake-test-key'
        return httpx2.Response(200,json={'model':'jev-1.13.0',
            'usage':{'input_tokens':1,'output_tokens':1},
            'answers':{'check':{'type':'noul','noul':.99}}},
            headers={'x-request-id':'offline-test-request'})
    monkeypatch.setattr(httpx2,'Client',lambda **kw:original_client(
        transport=httpx2.MockTransport(handler),**kw))
    client=JevClient(api_key='fake-test-key')
    try:
        client.ask(state='Offline fixture',questions={'check':{'type':'noul','instructions':'Fixture?'}},
                   output=tmp_path/'fixture.json')
    finally:client.close()
    receipt=(tmp_path/'fixture.http.json').read_text()
    assert 'fake-test-key' not in receipt
    data=json.loads(receipt)
    assert data[0]['status']==200
    assert data[0]['url']=='https://api.typesafe.ai/v1/systemone'
    assert len(data[0]['request_body_sha256'])==64
    assert data[0]['response_headers']['x-request-id']=='offline-test-request'
