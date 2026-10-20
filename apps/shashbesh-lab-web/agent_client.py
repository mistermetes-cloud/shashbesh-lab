"""Local Agent Pull V1 client. Token is read with getpass, never from a URL/CLI flag."""
import argparse,getpass,json
from pathlib import Path
from urllib.parse import urlsplit
from urllib.request import Request,urlopen


def run(base,token,action):
    parsed=urlsplit(base)
    if parsed.scheme!='http' or parsed.hostname!='127.0.0.1' or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError('only local 127.0.0.1 HTTP is supported')
    def post(path,data):
        request=Request(base.rstrip('/')+path,data=json.dumps(data).encode(),headers={'Content-Type':'application/json','Authorization':'Bearer '+token})
        with urlopen(request,timeout=20) as response:return json.load(response)
    task=post('/agent/v1/tasks/pull',{'protocol':'shashbesh-agent/1','operation':'pull'})
    return post('/agent/v1/tasks/'+task['task_id']+'/submit',{'protocol':task['protocol'],'operation':'submit','task_id':task['task_id'],
        'lease_id':task['lease_id'],'revision':task['revision'],'request_id':__import__('uuid').uuid4().hex,'action':action})


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--base',default='http://127.0.0.1:8787');p.add_argument('--action',required=True);args=p.parse_args()
    print(json.dumps(run(args.base,getpass.getpass('Ephemeral agent test token: '),json.loads(Path(args.action).read_text())),ensure_ascii=False))
