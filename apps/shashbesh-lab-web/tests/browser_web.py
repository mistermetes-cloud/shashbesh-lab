"""Real Firefox E2E for the isolated website; temporary profile, no SQLite."""
import base64,importlib.util,json,os,shutil,subprocess,tempfile,threading,time,sys
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.error import HTTPError
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('research_web_host',ROOT/'server.py');web=importlib.util.module_from_spec(spec);spec.loader.exec_module(web)


def main():
    artifacts=Path(tempfile.mkdtemp(prefix='shashbesh-web-firefox-'))
    public='--public-preview' in sys.argv
    if public:
        from http.server import SimpleHTTPRequestHandler,HTTPServer
        class Static(SimpleHTTPRequestHandler):
            posts=0
            def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT/'dist-public'),**kwargs)
            def log_message(self,*args):pass
            def do_POST(self):
                type(self).posts+=1;self.send_response(503);self.end_headers()
        server=HTTPServer(('127.0.0.1',0),Static);app=None
    else:server,app=web.create_server()
    thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
    base=f'http://127.0.0.1:{server.server_port}';port=os.environ.get('SHASHBESH_TEST_WEBDRIVER_PORT','4458')
    log=(artifacts/'geckodriver.log').open('w')
    driver=subprocess.Popen([shutil.which('geckodriver'),'--host','127.0.0.1','--port',port,'--allow-system-access'],stdout=log,stderr=subprocess.STDOUT)
    webdriver='http://127.0.0.1:'+port;prefix=None
    def wd(path,data=None,method=None):
        try:
            with urlopen(Request(webdriver+path,data=json.dumps(data).encode() if data is not None else None,headers={'Content-Type':'application/json'},method=method),timeout=60) as r:return json.load(r)['value']
        except HTTPError as e:raise AssertionError(e.read().decode()) from e
    def wait(fn,timeout=35):
        end=time.monotonic()+timeout
        while time.monotonic()<end:
            result=fn()
            if result:return result
            time.sleep(.08)
        raise AssertionError('Firefox condition timed out')
    def ready():
        try:return wd('/status')['ready']
        except Exception:return False
    errors=[]
    try:
        wait(ready)
        session=wd('/session',{'capabilities':{'alwaysMatch':{'browserName':'firefox','moz:firefoxOptions':{'args':['-headless'],'prefs':{
            'intl.accept_languages':'ru-RU,ru','network.proxy.type':1,'network.proxy.http':'127.0.0.1','network.proxy.http_port':9,
            'network.proxy.ssl':'127.0.0.1','network.proxy.ssl_port':9,'network.proxy.no_proxies_on':'localhost,127.0.0.1',
            'app.update.enabled':False,'browser.newtabpage.enabled':False,'browser.startup.homepage':'about:blank'}}}}})
        prefix='/session/'+session['sessionId']
        def js(script):return wd(prefix+'/execute/sync',{'script':script,'args':[]})
        def click(selector):return js('document.querySelector('+json.dumps(selector)+').click();return true')
        def value(selector,v,event='change'):return js('const e=document.querySelector('+json.dumps(selector)+');e.value='+json.dumps(v)+';e.dispatchEvent(new Event('+json.dumps(event)+'));return true')
        def page(path):
            wd(prefix+'/url',{'url':base+path});wait(lambda:js('return document.documentElement.dataset.ready')=='true')
            js('window.pageErrors=[];addEventListener("error",e=>pageErrors.push(e.message));addEventListener("unhandledrejection",e=>pageErrors.push(String(e.reason)));return true')
        wd(prefix+'/window/rect',{'width':1280,'height':960})
        page('/');assert js('return location.pathname')=='/ru/home/'
        for lang in ['en','ru']:
            for name in ['home','arena','rules','strategy','learning','developers','benchmarks','rankings','documentation']:
                page(f'/{lang}/{name}/');assert js('return document.documentElement.lang')==lang
                assert js('return document.querySelectorAll("#navigation a").length')==9
                errors.extend(js('return pageErrors'))
        if public:
            for language in ['en','ru']:
                page('/'+language+'/rules/')
                assert js('return Boolean(document.querySelector("#public-rules-disabled"))')
                assert not js('return Boolean(document.querySelector("#login-form,#load-trial,#validate-action,#agent-token"))')
            assert Static.posts==0
            print(json.dumps({'public_preview':'PASS','routes':18,'interactive_backend':'DISABLED','api_posts':0,'artifacts':str(artifacts)}),flush=True)
            return
        page('/en/rules/')
        value('#research-code',app.token,'input');js('document.querySelector("#login-form").requestSubmit();return true')
        wait(lambda:js('return document.querySelector("#login-form").hidden'))
        click('#load-trial');wait(lambda:js('return document.querySelectorAll("#board .token").length')==20)
        wait(lambda:js('return document.body.dataset.busy')=='false')
        initial=js('return document.querySelector("#board").innerHTML')
        click('#view-agent');assert not js('return Boolean(document.querySelector("#legal-actions"))')
        task=json.loads(js('return document.querySelector(".agent-task").textContent'))
        for hidden in ['legalActions','legal_actions','action_id','core_state','eventLog','worker_state_id','rng_counter','seed']:
            assert hidden not in json.dumps(task)
        click('#validate-action');wait(lambda:js('return document.body.dataset.busy')=='false')
        assert js('return document.querySelector("#validate-action").disabled')
        assert initial==js('return document.querySelector("#board").innerHTML')
        click('#view-researcher');assert len(app.trials[next(iter(app.trials))]['trial'].audit)==1
        value('#mode','learning');value('#rules-language','ru');click('#load-trial')
        wait(lambda:len(app.trials)==2 and js('return document.body.dataset.busy')=='false')
        click('#validate-action');wait(lambda:js('return document.body.dataset.busy')=='false')
        assert not js('return document.querySelector("#validate-action").disabled')
        click('#legal-actions summary');click('.action-row button');click('#validate-action')
        wait(lambda:js('return document.body.dataset.busy')=='false')
        latest=list(app.trials.values())[-1]['trial'];assert [a['response']['accepted'] for a in latest.audit]==[False,True]
        value('#language','ru');wait(lambda:js('return document.documentElement.lang')=='ru')
        assert latest.task['rules']['language']=='ru'
        value('#language','en');wait(lambda:js('return document.documentElement.lang')=='en')
        assert latest.task['rules']['language']=='ru'
        click('#theme');assert js('return document.documentElement.dataset.theme')=='light'
        # Explicit localStorage preference survives a root navigation.
        page('/');assert js('return location.pathname')=='/en/home/'
        page('/en/rules/');value('#research-code',app.token,'input');js('document.querySelector("#login-form").requestSubmit();return true')
        wait(lambda:js('return document.querySelector("#login-form").hidden'));click('#load-trial')
        wait(lambda:js('return document.querySelectorAll("#board .token").length')==20)
        def viewport(width):
            wd(prefix+'/window/rect',{'width':max(500,width),'height':960})
            wd(prefix+'/moz/context',{'context':'chrome'})
            js('const b=window.gBrowser.selectedBrowser;b.style.setProperty("max-width",'+json.dumps(str(width)+'px')+',"important");b.style.setProperty("min-width","0","important");b.style.setProperty("width",'+json.dumps(str(width)+'px')+',"important");return true')
            wd(prefix+'/moz/context',{'context':'content'})
            wait(lambda:js('return innerWidth')==width)
        layouts=[]
        for width in [320,360,390,768,1280]:
            viewport(width);time.sleep(.12)
            rect=js('const b=document.getElementById("board").getBoundingClientRect();return {viewport:innerWidth,page:document.documentElement.scrollWidth,x:b.x,y:b.y,w:b.width,h:b.height}')
            assert rect['page']<=rect['viewport']+1,rect
            assert abs(rect['w']-rect['h'])<=1,rect
            layouts.append(rect)
        viewport(1280);time.sleep(.15)
        (artifacts/'rules-desktop.png').write_bytes(base64.b64decode(wd(prefix+'/screenshot')))
        viewport(390);time.sleep(.15)
        (artifacts/'rules-mobile.png').write_bytes(base64.b64decode(wd(prefix+'/screenshot')))
        errors.extend(js('return pageErrors'));assert not errors,errors
        # Network error keeps the authoritative state and pending proposal intact.
        before=js('return document.querySelector("#board").innerHTML')
        js('window.nativeFetch=fetch;window.fetch=()=>Promise.reject(new Error("simulated offline"));return true')
        click('#validate-action');wait(lambda:js('return document.body.dataset.busy')=='false')
        assert before==js('return document.querySelector("#board").innerHTML')
        js('window.fetch=nativeFetch;return true')
        print(json.dumps({'firefox':'PASS','routes':18,'exam':'PASS','learning':'PASS','agent_serialization':'PASS','network_error':'PASS','layouts':layouts,'script_errors':errors,'artifacts':str(artifacts)}),flush=True)
    finally:
        if prefix:
            try:wd(prefix,method='DELETE')
            except Exception:pass
        driver.terminate()
        try:driver.wait(timeout=10)
        except subprocess.TimeoutExpired:driver.kill();driver.wait()
        log.close();server.shutdown();server.server_close();
        if app:app.close()
        thread.join()


if __name__=='__main__':main()
