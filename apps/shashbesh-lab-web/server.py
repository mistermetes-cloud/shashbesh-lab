"""Local Research website host. Run from this directory: python3 server.py.
No database writes, remote calls or public bind; credentials are ephemeral test capabilities.
"""
from __future__ import annotations
import copy, hashlib, json, mimetypes, secrets, sys, threading, time
from pathlib import Path
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlsplit

ROOT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT.parents[1]))
from lab.platform_agent import AgentTrial, ProtocolError, decode, canonical, PROTOCOL
from lab.shashbesh_environment import ShashBeshEnvironment


class WebEnvironment(ShashBeshEnvironment):
    def __init__(self):
        super().__init__(worker_timeout_seconds=15,node_heap_mb=192)
        self._worker_path=ROOT/'core_bridge.cjs'


class ResearchApp:
    def __init__(self):
        self.env=WebEnvironment();self.token=secrets.token_urlsafe(32)
        self.sessions=set();self.trials={};self.agents={};self.lock=threading.RLock()
    def close(self):self.env.close()
    def prune(self):
        for key,row in list(self.trials.items()):
            if time.monotonic()-row['created']>1200:
                self.env._request('release',id=key)
                self.agents.pop(row['token'],None);self.trials.pop(key)
    def create(self,data):
        self.prune()
        if len(self.trials)>=32:raise ProtocolError('capacity')
        if set(data)!={'players','dice','position','mode','rules_language','feedback'}:raise ProtocolError('invalid_configuration')
        if type(data['players']) is not int or data['players'] not in (2,3,4):raise ProtocolError('invalid_configuration')
        if not isinstance(data['dice'],list) or len(data['dice'])!=2 or any(type(x) is not int or not 1<=x<=6 for x in data['dice']):raise ProtocolError('invalid_configuration')
        if data['position'] not in ('opening','developed') or data['mode'] not in ('exam','learning') or data['rules_language'] not in ('ru','en') or data['feedback'] not in ('minimal','category'):raise ProtocolError('invalid_configuration')
        key=secrets.token_hex(16);state=self.env._request('fixture',id=key,players=data['players'],dice=data['dice'],position=data['position'])['state']
        token=secrets.token_urlsafe(32)
        legal=self.env.legal_actions(state)
        trial=AgentTrial(self.env,state,benchmark='rules',mode=data['mode'],lease_seconds=300,max_attempts=10) if legal else None
        if trial:
            catalog=json.loads((ROOT/'locales'/f"{data['rules_language']}.json").read_text())
            text=catalog['rulesText']
            trial.task['rules']={'language':data['rules_language'],'version':'web-preview/1','text':text,'sha256':hashlib.sha256(text.encode()).hexdigest()}
        self.trials[key]={'state':state,'trial':trial,'configuration':copy.deepcopy(data),'token':token,'created':time.monotonic(),'validations':[]}
        self.agents[token]=key
        return self.research(key)
    def research(self,key):
        row=self.trials[key];trial=row['trial'];state=trial.state if trial else row['state']
        audit=trial.audit if trial else []
        return {'id':key,'state':self.env.serialize(state),'geometry':self.env.geometry(),
                'legalActions':self.env.legal_actions(state),'configuration':row['configuration'],'agent_test_token':row['token'],
                'audit':copy.deepcopy(audit),'validations':copy.deepcopy(row['validations']),
                'closed':trial.closed if trial else True,'no_decision':trial is None,
                'summary':{'attempts':len(audit),'first_success':audit[0]['response']['accepted'] if audit else None,
                           'last_success':audit[-1]['response']['accepted'] if audit else None,
                           'corrections':sum(not a['response']['accepted'] for a in audit)}}
    def agent(self,token,message):
        self.prune()
        key=self.agents.get(token)
        if not key:raise PermissionError('unauthorized')
        row=self.trials[key];trial=row['trial']
        if trial is None:raise ProtocolError('no_decision')
        # Independently invoke Core on every new valid-envelope action proposal.
        # Validation is non-mutating and its reasons remain Researcher-only.
        if message.get('operation')=='submit' and message.get('request_id') not in trial.receipts:
            expected={'protocol','operation','task_id','lease_id','revision','request_id','action'}
            if (set(message)==expected and message['protocol']==PROTOCOL and message['task_id']==trial.task_id and
                message['lease_id']==trial.lease_id and type(message['revision']) is int and message['revision']==trial.revision and
                isinstance(message['request_id'],str) and 1<=len(message['request_id'])<=128 and
                not trial.closed and trial.clock()<trial.deadline):
                validation=self.env._request('validate',state=trial.state,action=message['action'])
            else:validation=None
        else:validation=None
        response=trial.handle(message)
        if validation is not None:row['validations'].append(validation)
        if row['configuration']['mode']=='learning' and row['configuration']['feedback']=='category' and response.get('accepted') is False:
            response['category']='illegal_action'
            for attempt in trial.audit:
                if attempt['response']['request_id']==response['request_id']:attempt['response']['category']='illegal_action'
        # Only AgentTrial's dedicated response projection crosses this boundary.
        return response


def create_server(port=0,app=None):
    app=app or ResearchApp()
    class Handler(BaseHTTPRequestHandler):
        def setup(self):
            super().setup();self.connection.settimeout(20)
        def log_message(self,*args):pass
        def send(self,status,value,kind='application/json; charset=utf-8',cookie=None):
            body=value if isinstance(value,bytes) else canonical(value).encode()
            self.send_response(status);self.send_header('Content-Type',kind);self.send_header('Content-Length',str(len(body)))
            self.send_header('Cache-Control','no-store');self.send_header('X-Content-Type-Options','nosniff')
            self.send_header('Content-Security-Policy',"default-src 'self'; script-src 'self'; style-src 'self'; img-src 'self' data:; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
            self.send_header('Referrer-Policy','no-referrer')
            if cookie:self.send_header('Set-Cookie',cookie)
            self.end_headers();self.wfile.write(body)
        def check_host(self):
            if self.headers.get('Host')!=f'127.0.0.1:{self.server.server_port}':raise PermissionError('host')
        def researcher(self):
            cookies=SimpleCookie();cookies.load(self.headers.get('Cookie',''))
            if 'research_session' not in cookies or cookies['research_session'].value not in app.sessions:raise PermissionError('unauthorized')
        def do_GET(self):
            try:
                self.check_host();path=urlsplit(self.path).path
                if path.startswith('/api/research/trials/'):
                    self.researcher()
                    with app.lock:app.prune();self.send(200,app.research(path.rsplit('/',1)[1]))
                elif path=='/api/health':self.send(200,{'local':True,'protocol':PROTOCOL})
                elif path.startswith('/api/') or path.startswith('/agent/'):self.send(404,{'error':'not_found'})
                else:
                    target=(ROOT/'dist'/path.lstrip('/')).resolve()
                    if not target.is_relative_to((ROOT/'dist').resolve()):raise PermissionError('path')
                    if target.is_dir():target=target/'index.html'
                    if not target.exists():self.send(404,(ROOT/'dist/404.html').read_bytes(),'text/html; charset=utf-8');return
                    self.send(200,target.read_bytes(),(mimetypes.guess_type(target)[0] or 'application/octet-stream')+'; charset=utf-8')
            except PermissionError:self.send(403,{'error':'unauthorized'})
            except KeyError:self.send(404,{'error':'not_found'})
        def do_POST(self):
            try:
                self.check_host();origin=self.headers.get('Origin')
                if origin and origin!=f'http://127.0.0.1:{self.server.server_port}':raise PermissionError('origin')
                if self.headers.get('Content-Type','').split(';')[0]!='application/json':raise ProtocolError('invalid_request')
                size=int(self.headers.get('Content-Length','0'))
                if not 0<size<=65536:raise ProtocolError('invalid_request')
                data=decode(self.rfile.read(size).decode());path=urlsplit(self.path).path
                with app.lock:
                    if path=='/api/research/login':
                        if set(data)!={'token'} or not isinstance(data['token'],str) or not secrets.compare_digest(data['token'],app.token):raise PermissionError('unauthorized')
                        if len(app.sessions)>=16:raise ProtocolError('capacity')
                        session=secrets.token_urlsafe(32);app.sessions.add(session)
                        self.send(200,{'ok':True},cookie=f'research_session={session}; HttpOnly; SameSite=Strict; Path=/api/research');return
                    if path=='/api/research/trials':self.researcher();self.send(200,app.create(data));return
                    if path=='/agent/v1/tasks/pull' or path=='/agent/v1/tasks/'+str(data.get('task_id',''))+'/submit':
                        authorization=self.headers.get('Authorization','')
                        if not authorization.startswith('Bearer '):raise PermissionError('unauthorized')
                        operation='pull' if path.endswith('/pull') else 'submit'
                        if data.get('operation')!=operation:raise ProtocolError('invalid_request')
                        self.send(200,app.agent(authorization[7:],data));return
                    self.send(404,{'error':'not_found'})
            except PermissionError:self.send(403,{'error':'unauthorized'})
            except (ProtocolError,ValueError,TypeError,UnicodeError,KeyError,RecursionError):self.send(409,{'error':'invalid_request'})
            except (RuntimeError,TimeoutError,OSError):self.send(503,{'error':'core_unavailable'})
    server=HTTPServer(('127.0.0.1',port),Handler);server.timeout=15
    return server,app


if __name__=='__main__':
    import argparse
    parser=argparse.ArgumentParser();parser.add_argument('--port',type=int,default=8787);args=parser.parse_args()
    server,app=create_server(args.port)
    print(f'Local Research Lab: http://127.0.0.1:{server.server_port}/',flush=True)
    print(f'Ephemeral researcher test code (local console only): {app.token}',flush=True)
    try:server.serve_forever()
    except KeyboardInterrupt:pass
    finally:server.server_close();app.close()
