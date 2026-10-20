"""Local, single-trial Agent Pull v1 prototype. No network listener or database writes.

Transport is JSON-lines over stdin/stdout; an independently launched client pulls
one leased observation and submits an action. This is not a production sandbox.
"""
from __future__ import annotations
import copy
import hashlib
import json
import secrets
import time

PROTOCOL = 'shashbesh-agent/1'
MAX_BYTES = 65536


class ProtocolError(ValueError):
    pass


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(',', ':'), allow_nan=False)


def decode(line):
    if len(line.encode('utf-8')) > MAX_BYTES:
        raise ProtocolError('message_too_large')
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ProtocolError('duplicate_key')
            result[key] = value
        return result
    try:
        value = json.loads(line, object_pairs_hook=pairs, parse_constant=lambda _: (_ for _ in ()).throw(ProtocolError('non_finite')))
    except (ValueError, RecursionError) as exc:
        raise ProtocolError('invalid_json') from exc
    if not isinstance(value, dict):
        raise ProtocolError('object_required')
    return value


class AgentTrial:
    """One choice for one bound agent; engine legality never comes from Python rules.

    Caller owns the environment exclusively. Retain this object only for the
    trial lifetime; receipts and audit are intentionally memory-only here.
    """
    def __init__(self, environment, state, *, benchmark='strategy', mode='exam', agent_id='local.external',
                 max_attempts=3, lease_seconds=60, clock=time.monotonic):
        if benchmark not in {'strategy', 'rules'} or mode not in {'exam', 'learning'}:
            raise ProtocolError('unsupported_mode')
        if type(max_attempts) is not int or not 1 <= max_attempts <= 10 or not 0 < lease_seconds <= 300:
            raise ProtocolError('invalid_limits')
        self.env, self.state = environment, state
        self.benchmark, self.mode, self.agent_id = benchmark, mode, agent_id
        self.clock, self.deadline = clock, clock() + lease_seconds
        self.max_attempts = 1 if mode == 'exam' else max_attempts
        self.task_id, self.lease_id = secrets.token_hex(16), secrets.token_hex(16)
        self.revision, self.closed = 0, False
        self.receipts, self.audit = {}, []
        # Private oracle: never attached to Rules observations or error responses.
        self.legal = environment.legal_actions(state)
        if not self.legal:
            raise ProtocolError('no_decision')
        # Explicit allowlist: no RNG seed/counter, Core journal, worker id, or history.
        roll = state.get('current_roll') or {}
        observation = {'active_seat': environment.current_player(state), 'phase': state['phase'],
                       'pieces': copy.deepcopy(state['pieces']),
                       'dice': copy.deepcopy(roll.get('dice', [])),
                       'remaining_actions': copy.deepcopy(roll.get('remainingActions', [])),
                       'forced_piece_id': roll.get('forcedPieceId'),
                       'extra_roll': bool(roll.get('extraRoll', False)),
                       'players': sorted({piece['owner'] for piece in state['pieces']})}
        self.task = {'protocol': PROTOCOL, 'task_id': self.task_id, 'lease_id': self.lease_id,
                     'revision': self.revision, 'agent_id': agent_id, 'benchmark': benchmark, 'mode': mode,
                     'core_version': state['core_version'], 'core_sha256': state['core_artifact_sha256'],
                     'action_schema': 'core-action/0.1.0-g0.65e1ec3', 'observation': observation,
                     'geometry': environment.geometry(), 'lease_seconds': lease_seconds}
        if benchmark == 'strategy':
            self.task['legalActions'] = copy.deepcopy(self.legal)

    def handle(self, message):
        fingerprint = canonical(message)
        if len(fingerprint.encode()) > MAX_BYTES:
            raise ProtocolError('message_too_large')
        operation = message.get('operation')
        fields = {'protocol', 'operation'} if operation == 'pull' else {
            'protocol', 'operation', 'task_id', 'lease_id', 'revision', 'request_id', 'action'}
        if message.get('protocol') != PROTOCOL or set(message) != fields or operation not in {'pull', 'submit'}:
            raise ProtocolError('invalid_envelope')
        if operation == 'pull':
            if self.closed or self.clock() >= self.deadline:
                raise ProtocolError('trial_closed')
            return copy.deepcopy(self.task)
        request_id = message['request_id']
        if not isinstance(request_id, str) or not 1 <= len(request_id) <= 128:
            raise ProtocolError('invalid_request_id')
        if request_id in self.receipts:
            old, response = self.receipts[request_id]
            if old != fingerprint:
                raise ProtocolError('idempotency_conflict')
            return copy.deepcopy(response)
        if self.closed or self.clock() >= self.deadline:
            raise ProtocolError('trial_closed')
        if (message['task_id'] != self.task_id or message['lease_id'] != self.lease_id or
            type(message['revision']) is not int or message['revision'] != self.revision):
            raise ProtocolError('stale_or_foreign_task')
        # Exact canonical equality avoids bool==int acceptance and delegates the
        # entire action language/legality to the original Core legalActions.
        action = message['action']
        correct = isinstance(action, dict) and canonical(action) in {canonical(a) for a in self.legal}
        if correct:
            # Core applies the action and settles the roll using the existing adapter.
            self.state = self.env.step(self.state, action)
            self.revision += 1
        self.closed = correct or len(self.audit) + 1 >= self.max_attempts
        response = {'protocol': PROTOCOL, 'task_id': self.task_id, 'request_id': request_id,
                    'accepted': correct, 'feedback': 'accepted' if correct else 'invalid_action',
                    'trial_closed': self.closed, 'revision': self.revision}
        self.audit.append({'attempt': len(self.audit)+1, 'agent_id': self.agent_id,
                           'action': copy.deepcopy(action), 'response': copy.deepcopy(response),
                           'request_sha256': hashlib.sha256(fingerprint.encode()).hexdigest()})
        self.receipts[request_id] = (fingerprint, copy.deepcopy(response))
        return response


def main():
    import argparse
    import sys
    from .shashbesh_environment import ShashBeshEnvironment
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--benchmark', choices=['strategy', 'rules'], default='strategy')
    parser.add_argument('--mode', choices=['exam', 'learning'], default='exam')
    parser.add_argument('--players', type=int, choices=[2, 3, 4], default=2)
    parser.add_argument('--seed', type=int, default=112)
    args = parser.parse_args()
    with ShashBeshEnvironment() as env:
        state = env.reset(args.seed, players=list(range(1, args.players+1)))
        trial = AgentTrial(env, state, benchmark=args.benchmark, mode=args.mode)
        while True:
            line = sys.stdin.buffer.readline(MAX_BYTES+1)
            if not line:
                break
            if len(line) > MAX_BYTES:
                print(canonical({'error': 'message_too_large'}), flush=True)
                break
            try:
                reply = trial.handle(decode(line.decode('utf-8')))
            except (ProtocolError, UnicodeError, ValueError, TypeError, RecursionError):
                # Do not reflect Core exceptions, payloads or alternatives to agents.
                reply = {'protocol': PROTOCOL, 'error': 'invalid_request'}
            print(canonical(reply), flush=True)


if __name__ == '__main__':
    main()
