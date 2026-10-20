import importlib.util,json,threading
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
import pytest
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('research_web_host',ROOT/'server.py');web=importlib.util.module_from_spec(spec);spec.loader.exec_module(web)


@pytest.fixture
def app():
    instance=web.ResearchApp()
    yield instance
    instance.close()


def config(**changes):return dict(players=4,dice=[6,6],position='developed',mode='exam',rules_language='en',feedback='category',**changes) if not changes else {**config(),**changes}
def pull(app,record):return app.agent(record['agent_test_token'],{'protocol':web.PROTOCOL,'operation':'pull'})
def submit(task,action,rid='r1'):return dict(protocol=task['protocol'],operation='submit',task_id=task['task_id'],lease_id=task['lease_id'],revision=task['revision'],request_id=rid,action=action)


@pytest.mark.parametrize('count',[2,3,4])
def test_core_fixture_legal_and_validation(app,count):
    r=app.create(config(players=count));assert len(r['state']['pieces'])==count*5
    t=pull(app,r);result=app.agent(r['agent_test_token'],submit(t,r['legalActions'][0]))
    assert result['accepted']
    after=app.research(r['id']);assert after['validations'][0]['valid'] and len(after['audit'])==1


def test_rules_projection_and_exam_error_nonmutation(app):
    r=app.create(config());t=pull(app,r);payload=json.dumps(t)
    for hidden in ('legalActions','legal_actions','action_id','core_state','eventLog','rng_counter','worker_state_id','seed','agent_test_token'):
        assert hidden not in payload
    assert t['rules']['language']=='en' and t['rules']['text']
    before=app.env._request('inspect',state=app.trials[r['id']]['state'])['state_hash']
    message=submit(t,{'kind':'invented'});response=app.agent(r['agent_test_token'],message)
    assert response['accepted'] is False and response['trial_closed']
    assert 'reason' not in response and 'category' not in response
    after=app.research(r['id']);assert len(after['audit'])==1 and after['validations'][0]['category']=='illegal_action'
    assert before==app.env._request('inspect',state=app.trials[r['id']]['state'])['state_hash']
    assert app.agent(r['agent_test_token'],message)==response
    assert len(app.research(r['id'])['audit'])==1


@pytest.mark.parametrize('feedback',['minimal','category'])
def test_learning_attempts_feedback_and_rules_language(app,feedback):
    r=app.create(config(mode='learning',rules_language='ru',feedback=feedback));t=pull(app,r)
    bad=app.agent(r['agent_test_token'],submit(t,{},'bad'))
    assert not bad['trial_closed'] and ('category' in bad)==(feedback=='category')
    good=app.agent(r['agent_test_token'],submit(t,r['legalActions'][0],'good'))
    assert good['accepted'] and len(app.research(r['id'])['audit'])==2
    s=app.research(r['id'])['summary'];assert s==dict(attempts=2,first_success=False,last_success=True,corrections=1)
    assert t['rules']['language']=='ru'


def test_empty_roll_is_finished_by_core(app):
    r=app.create(config(position='opening',dice=[3,3]));assert r['no_decision'] and not r['legalActions']
    inspected=app.env._request('inspect',state=app.trials[r['id']]['state'])
    assert any(e['type']=='extra_roll' for e in inspected['events'])
    assert any(e['type']=='roll_finished' for e in inspected['events'])


def test_revision_foreign_token_and_double_retry(app):
    r=app.create(config());other=app.create(config());task=pull(app,r);msg=submit(task,r['legalActions'][0])
    with pytest.raises(web.ProtocolError):app.agent(other['agent_test_token'],msg)
    with pytest.raises(web.ProtocolError):app.agent(r['agent_test_token'],dict(msg,revision=9))
    first=app.agent(r['agent_test_token'],msg);assert app.agent(r['agent_test_token'],msg)==first
    with pytest.raises(web.ProtocolError):app.agent(r['agent_test_token'],dict(msg,action={}))
    assert len(app.research(r['id'])['audit'])==1


def test_http_boundaries_static_routes_external_client(app):
    server,_=web.create_server(0,app);thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start();base=f'http://127.0.0.1:{server.server_port}'
    def call(path,data=None,headers=None):
        with urlopen(Request(base+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json',**(headers or {})}),timeout=20) as response:
            return response.status,response.read(),response.headers
    try:
        assert json.loads(call('/locales/en.json')[1])['nav']['rules']=='Rules Lab'
        for path in ['/en/rules/','/ru/developers/']:
            assert call(path)[0]==200
        with pytest.raises(HTTPError) as e:call('/api/research/trials',config())
        assert e.value.code==403
        _,_,headers=call('/api/research/login',{'token':app.token})
        cookie=headers['Set-Cookie'].split(';')[0]
        _,body,_=call('/api/research/trials',config(),{'Cookie':cookie});record=json.loads(body)
        bearer={'Authorization':'Bearer '+record['agent_test_token']}
        with pytest.raises(HTTPError) as e:call('/api/research/trials/'+record['id'],headers=bearer)
        assert e.value.code==403
        _,body,_=call('/agent/v1/tasks/pull',{'protocol':web.PROTOCOL,'operation':'pull'},bearer)
        assert 'legalActions' not in json.loads(body)
        with pytest.raises(HTTPError) as e:call('/agent/v1/tasks/pull',{'protocol':web.PROTOCOL,'operation':'pull'},{**bearer,'Origin':'https://untrusted.invalid'})
        assert e.value.code==403
        client_spec=importlib.util.spec_from_file_location('web_agent_client',ROOT/'agent_client.py');client=importlib.util.module_from_spec(client_spec);client_spec.loader.exec_module(client)
        assert client.run(base,record['agent_test_token'],record['legalActions'][0])['accepted']
        for p in (ROOT/'dist').rglob('*'):
            if p.is_file():assert app.token.encode() not in p.read_bytes() and record['agent_test_token'].encode() not in p.read_bytes()
    finally:server.shutdown();server.server_close();thread.join()
