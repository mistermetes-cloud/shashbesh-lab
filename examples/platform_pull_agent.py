"""Independent example client: launch a trusted local bridge, pull, submit.

The platform never imports this client's code. Replace action selection with an
external model on the developer's own machine; no external API is used here.
"""
import json
import subprocess
import sys


def run(players=4):
    with subprocess.Popen([sys.executable, '-m', 'lab.platform_agent', '--players', str(players)],
                          stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True) as bridge:
        def rpc(message):
            bridge.stdin.write(json.dumps(message)+'\n');bridge.stdin.flush()
            return json.loads(bridge.stdout.readline())
        task = rpc({'protocol':'shashbesh-agent/1', 'operation':'pull'})
        response = rpc({'protocol':task['protocol'], 'operation':'submit', 'task_id':task['task_id'],
                        'lease_id':task['lease_id'], 'revision':task['revision'], 'request_id':'example-1',
                        'action':task['legalActions'][0]})
        bridge.stdin.close()
        bridge.wait(timeout=10)
        if bridge.returncode or not response.get('accepted'):
            raise RuntimeError('external agent trial failed')
        return response


if __name__ == '__main__':
    print(json.dumps(run(), ensure_ascii=False))
