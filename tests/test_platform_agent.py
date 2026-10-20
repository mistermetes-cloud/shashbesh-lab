"""Core-backed Agent protocol, disclosure policy and attempt semantics."""
import copy
import json
import subprocess
import sys
from pathlib import Path
import pytest
from lab.platform_agent import AgentTrial, ProtocolError, PROTOCOL, decode, canonical
from lab.shashbesh_environment import ShashBeshEnvironment


@pytest.fixture
def env():
    with ShashBeshEnvironment() as environment:
        yield environment


def submit(task, action, request='r1'):
    return dict(protocol=PROTOCOL, operation='submit', task_id=task['task_id'],
                lease_id=task['lease_id'], revision=task['revision'], request_id=request, action=action)


def pull(trial):
    return trial.handle(dict(protocol=PROTOCOL, operation='pull'))


@pytest.mark.parametrize('players', [2, 3, 4])
def test_strategy_external_choice_core_and_duplicate(env, players):
    state = env.reset(112, players=list(range(1,players+1)))
    trial = AgentTrial(env,state)
    task = pull(trial)
    assert len(task['observation']['pieces']) == players*5
    assert task['legalActions'] == env.legal_actions(state)
    assert task == pull(trial)
    task['legalActions'].clear()
    task = pull(trial)
    message = submit(task,task['legalActions'][0])
    result = trial.handle(message)
    assert result['accepted'] and result['trial_closed'] and result['revision']==1
    assert trial.handle(message)==result and len(trial.audit)==1
    assert trial.state['pieces'] != state['pieces']
    with pytest.raises(ProtocolError,match='idempotency_conflict'):
        trial.handle(dict(message, action={}))
    saved = env.serialize_replay(trial.state)
    assert env.verify_replay(saved)['valid']


def test_rules_exam_records_first_wrong_without_answer(env):
    state = env.reset(112)
    trial = AgentTrial(env,state,benchmark='rules',mode='exam')
    task = pull(trial)
    for hidden in ('legalActions','legal_actions','core_state','worker_state_id','seed','rng_counter','eventLog'):
        assert hidden not in canonical(task)
    before = env.serialize_replay(state)
    wrong = submit(task, {'kind':'invented'})
    result = trial.handle(wrong)
    assert not result['accepted'] and result['trial_closed']
    assert set(result)=={'protocol','task_id','request_id','accepted','feedback','trial_closed','revision'}
    assert len(trial.audit)==1 and trial.audit[0]['action']==wrong['action']
    assert env.serialize_replay(state)==before
    assert trial.handle(wrong)==result
    with pytest.raises(ProtocolError,match='trial_closed'):
        trial.handle(submit(task,env.legal_actions(state)[0],'r2'))


def test_rules_learning_feedback_retry_and_budget(env):
    state=env.reset(112);trial=AgentTrial(env,state,benchmark='rules',mode='learning')
    task=pull(trial)
    result=trial.handle(submit(task,{},'wrong'))
    assert not result['accepted'] and not result['trial_closed']
    assert trial.handle(submit(task,env.legal_actions(state)[0],'correct'))['accepted']
    assert [a['response']['accepted'] for a in trial.audit]==[False,True]
    state=env.reset(113);limited=AgentTrial(env,state,benchmark='rules',mode='learning',max_attempts=2)
    t=pull(limited)
    assert not limited.handle(submit(t,{},'one'))['trial_closed']
    assert limited.handle(submit(t,{},'two'))['trial_closed']


def test_version_lease_revision_and_timeout_rejected(env):
    now=[1];trial=AgentTrial(env,env.reset(112),clock=lambda:now[0],lease_seconds=2)
    task=pull(trial);message=submit(task,task['legalActions'][0])
    for replacement in ({'revision':1},{'revision':True},{'lease_id':'other'},{'task_id':'other'}):
        with pytest.raises(ProtocolError):trial.handle(dict(message,**replacement))
    for replacement in ({'protocol':'shashbesh-agent/2'},{'extra':'x'}):
        with pytest.raises(ProtocolError,match='invalid_envelope'):trial.handle(dict(message,**replacement))
    assert not trial.audit
    now[0]=3
    with pytest.raises(ProtocolError):trial.handle(message)


@pytest.mark.parametrize('text',['[]','{"a":1,"a":2}','{"x":NaN}','{"x":Infinity}','{broken}', ' ' * 65537])
def test_strict_protocol_json(text):
    with pytest.raises(ProtocolError):decode(text)


def test_observation_allowlist_prevents_nested_leaks(env):
    state=env.reset(112);poison=copy.deepcopy(state)
    poison['legal_actions']=['secret'];poison['current_roll']['legalActions']=['secret']
    trial=AgentTrial(env,poison,benchmark='rules')
    assert 'secret' not in canonical(pull(trial))


def test_independent_client_process():
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run([sys.executable,'examples/platform_pull_agent.py'],cwd=root,
                          capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    assert json.loads(result.stdout)['accepted']


def test_core_edge_dependency_preflight():
    root=Path(__file__).resolve().parents[1]
    result=subprocess.run(['node','tests/core_edge_probe.cjs'],cwd=root,capture_output=True,text=True,timeout=30)
    assert result.returncode==0,result.stderr
    report=json.loads(result.stdout)
    assert report['status']=='PREFLIGHT_PASS' and len(report['results'])==3
    assert not report['cloudflare_runtime_verified']
