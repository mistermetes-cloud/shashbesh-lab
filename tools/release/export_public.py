"""Prepare a NEW allowlisted source tree under /tmp. Does not create Git/cloud resources."""
from __future__ import annotations
import argparse,hashlib,json,pathlib,shutil,sys,tempfile
ROOT=pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0,str(pathlib.Path(__file__).resolve().parent))
from audit_repository import scan
DENIED_PARTS={'.git','artifacts','node_modules','__pycache__','.pytest_cache','dist','dist-public','logs','results','experiments','secrets','.aws','.codex','.agents'}
DENIED_SUFFIX={'.sqlite','.sqlite3','.db','.log','.tgz','.zip','.pem','.key','.pyc'}


def export(destination):
    destination=pathlib.Path(destination).resolve()
    if not destination.is_relative_to(pathlib.Path(tempfile.gettempdir()).resolve()) or destination.exists():
        raise ValueError('output must be a NEW directory under /tmp; existing files are never overwritten')
    manifest=json.loads((ROOT/'docs/release/RELEASE_ALLOWLIST.json').read_text())
    checked=[]
    for name in manifest['source_files']:
        relative=pathlib.PurePosixPath(name)
        if relative.name.startswith('.env') or (relative.name!='.gitignore' and relative.suffix not in {'.py','.md','.json','.jsonc','.js','.mjs','.cjs','.css','.html'}):raise ValueError('non-source or credential file')
        if relative.is_absolute() or '..' in relative.parts or any(p in DENIED_PARTS for p in relative.parts) or relative.suffix in DENIED_SUFFIX:
            raise ValueError('forbidden allowlist entry')
        if name.startswith(('docs/engineering-review/','docs/research/','docs/L2_')):raise ValueError('private historical document')
        source=ROOT/name
        if source.is_symlink() or not source.is_file() or not source.resolve().is_relative_to(ROOT):raise ValueError('unsafe source')
        data=source.read_bytes()
        if data.startswith(b'SQLite format 3') or scan(data):raise ValueError('sensitive source finding')
        if len(data)>1024*1024:raise ValueError('oversized source')
        checked.append((name,data))
    if len({n for n,d in checked})!=len(checked):raise ValueError('duplicate allowlist')
    destination.mkdir(parents=True)
    hashes={}
    for name,data in checked:
        target=destination/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data);hashes[name]=hashlib.sha256(data).hexdigest()
    result={'source_files':len(hashes),'sha256':hashes,'publication_approved':False,'history_included':False,'core_artifact_included':False}
    # The export evidence stays outside the proposed public tree.
    (destination.parent/(destination.name+'-manifest.json')).write_text(json.dumps(result,indent=2)+'\n')
    return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--output',required=True);args=parser.parse_args()
    result=export(args.output);print(json.dumps({k:v for k,v in result.items() if k!='sha256'}))
