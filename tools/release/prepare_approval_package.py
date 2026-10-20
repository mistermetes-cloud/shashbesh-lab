"""Prepare an exact PRIVATE license-approval candidate. Never activates rights or publishes."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from audit_repository import scan


def prepare(output):
    output=pathlib.Path(output).resolve()
    if output.exists() or not output.is_relative_to(pathlib.Path(tempfile.gettempdir()).resolve()):raise ValueError('new /tmp directory required')
    plan=json.loads((ROOT/'docs/release/PUBLIC_PACKAGE_ALLOWLIST_V0_1.json').read_text())
    sources=[]
    for name in plan['source_files']:
        rel=pathlib.PurePosixPath(name);source=ROOT/name
        if rel.is_absolute() or '..' in rel.parts or any(p in {'.git','artifacts','dist','dist-public','node_modules','__pycache__','secrets','.aws','.codex'} for p in rel.parts):raise ValueError('forbidden path')
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(ROOT):raise ValueError('unsafe source')
        allowed=source.suffix in {'.py','.js','.mjs','.cjs','.md','.json','.jsonc','.css','.html'} or name in {'.gitignore','apps/shashbesh-lab-web/.gitignore','COPYING'} or (name.startswith('LICENSES/') and source.suffix=='.txt')
        if not allowed or name.startswith(('docs/engineering-review/','docs/research/','docs/L2_')):raise ValueError('non-release source')
        data=source.read_bytes()
        if len(data)>1024*1024 or data.startswith(b'SQLite format 3') or scan(data):raise ValueError('sensitive/oversized file')
        sources.append((name,data))
    if len({n for n,d in sources})!=len(sources):raise ValueError('duplicate entry')
    output.mkdir(parents=True)
    records=[]
    baseline=json.loads((ROOT/'docs/release/FILE_PROVENANCE_61.json').read_text())
    original={r['path']:r for r in baseline['files']}
    third={'COPYING','LICENSES/MIT-esbuild.txt','LICENSES/MIT-noble-hashes.txt','LICENSES/Apache-2.0.txt'}
    generated={'docs/release/FILE_PROVENANCE_61.json','docs/release/THIRD_PARTY_COMPONENTS.json','docs/release/PUBLIC_PACKAGE_ALLOWLIST_V0_1.json'}
    for name,data in sources:
        target=output/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
        category=original[name]['classification'] if name in original else 'THIRD_PARTY' if name in third else 'GENERATED' if name in generated else 'UNKNOWN_ORIGIN'
        records.append({'path':name,'sha256':hashlib.sha256(data).hexdigest(),'bytes':len(data),'classification':category,
                        'original_61_sha256':original[name]['sha256'] if name in original else None})
    hashes={r['path']:r['sha256'] for r in records}
    content_hash=hashlib.sha256(json.dumps(hashes,sort_keys=True,separators=(',',':')).encode()).hexdigest()
    result={'release':'v0.1.0 private license-approval candidate','proposed_owner_license':'GPL-3.0-only',
            'owner_approval_received':False,'publication_approved':False,'source_files':len(records),
            'source_tree_sha256':content_hash,'scope':'source only; no .git, generated builds, dependencies, Core/CSV or private data',
            'classification_counts':{k:sum(r['classification']==k for r in records) for k in ['OWNER_AUTHORED','THIRD_PARTY','GENERATED','UNKNOWN_ORIGIN']},'files':records}
    manifest=output.parent/(output.name+'-manifest.json');manifest.write_text(json.dumps(result,indent=2)+'\n')
    return result,manifest


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);args=parser.parse_args()
    result,manifest=prepare(args.output);print(json.dumps({k:v for k,v in result.items() if k!='files'}));print('EXTERNAL_MANIFEST',manifest)
