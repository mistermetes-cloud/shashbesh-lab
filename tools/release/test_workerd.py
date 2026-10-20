"""Real workerd audit with no sockets or outbound network. Artifacts stay in /tmp."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,platform,subprocess,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from lab.shashbesh_environment import ShashBeshEnvironment,CORE_SHA256,CORE_VERSION


def main():
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--tool-root',required=True,type=pathlib.Path);args=p.parse_args()
    tool=args.tool_root.resolve();runtime=tool/'node_modules/workerd/bin/workerd'
    for name,version in [('workerd','1.20261019.1'),('esbuild','0.28.2')]:
        assert json.loads((tool/'node_modules'/name/'package.json').read_text())['version']==version
    with ShashBeshEnvironment():pass # Includes exact archive + extracted-file verification, no game worker.
    output=pathlib.Path(tempfile.mkdtemp(prefix='shashbesh-workerd-audit-'))
    subprocess.run(['node',str(ROOT/'tools/release/build-runtime.mjs'),str(tool),str(output)],check=True)
    config='''using Workerd = import "/workerd/workerd.capnp";
const config :Workerd.Config = (
 services = [(name = "core", worker = (
  modules = [(name = "main.mjs", esModule = embed "core-bundle.mjs")],
  compatibilityDate = "2026-10-19", compatibilityFlags = [], globalOutbound = "internet"
 )),(name = "internet", network = (allow = []))], sockets = []
);
'''
    (output/'core.capnp').write_text(config)
    (output/'empty.mjs').write_text('export default {async test(){}};')
    (output/'baseline.capnp').write_text(config.replace('core-bundle.mjs','empty.mjs'))
    results=[];native=[]
    for case,count,repeats in [('baseline',None,0),('players2',2,1),('players3',3,1),('players4',4,1),('stress4',4,25)]:
        metrics=output/(case+'-resource.json')
        cmd=['/usr/bin/time','-f','{"cpu_user_seconds":%U,"cpu_system_seconds":%S,"peak_rss_kib":%M,"wall_seconds":%e}',
             '-o',str(metrics),str(runtime),'test',str(output/('baseline.capnp' if count is None else 'core.capnp'))]
        if count is not None:cmd.append('core:'+case)
        run=subprocess.run(cmd,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,timeout=60)
        (output/(case+'.log')).write_text(run.stdout)
        assert run.returncode==0,run.stdout
        summary={'case':case,**json.loads(metrics.read_text())}
        if count is not None:
            data=json.loads(next(line.split('CORE_RESULT ',1)[1] for line in run.stdout.splitlines() if 'CORE_RESULT ' in line))
            script='import {runCase} from '+json.dumps((output/'core-bundle.mjs').as_uri())+';console.log(JSON.stringify(runCase('+str(count)+','+str(repeats)+')));'
            comparison=subprocess.run(['node','--input-type=module','-e',script],check=True,stdout=subprocess.PIPE,text=True,timeout=60)
            native_result=json.loads(comparison.stdout);assert native_result==data,(native_result,data)
            summary.update(result=data,native_hash_match=True)
        results.append(summary)
    packages={name:json.loads((tool/'node_modules'/name/'package.json').read_text())['version'] for name in ('workerd','esbuild')}
    bundle=(output/'core-bundle.mjs').read_bytes()
    report={'status':'PASS','runtime':subprocess.check_output([str(runtime),'--version'],text=True).strip(),
            'packages':packages,'host':platform.system()+' '+platform.machine()+'; '+ ' '.join(platform.libc_ver()),'compatibility_date':'2026-10-19','compatibility_flags':[],
            'network':'deny all outbound; no sockets','core_version':CORE_VERSION,'core_archive_sha256':CORE_SHA256,
            'bundle_bytes':len(bundle),'bundle_sha256':hashlib.sha256(bundle).hexdigest(),'results':results,
            'measurement_scope':'OS CPU/wall/peak RSS for whole workerd process including startup; not isolate heap or cloud quota verification',
            'production_api_tested':False,'artifacts':str(output)}
    (output/'report.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
