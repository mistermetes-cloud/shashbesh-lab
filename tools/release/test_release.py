import importlib.util,json,pathlib,subprocess,tempfile
import pytest
ROOT=pathlib.Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('release_export',ROOT/'tools/release/export_public.py');module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)


def test_public_build_is_separate_and_disabled():
    local=json.loads((ROOT/'apps/shashbesh-lab-web/dist/build-config.json').read_text())
    public=json.loads((ROOT/'apps/shashbesh-lab-web/dist-public/build-config.json').read_text())
    assert local=={'mode':'local','interactive':True}
    assert public=={'mode':'public-preview','interactive':False}
    assert 'dist-public' in (ROOT/'apps/shashbesh-lab-web/wrangler.jsonc').read_text()
    for p in (ROOT/'apps/shashbesh-lab-web/dist-public').rglob('*'):
        if p.is_file():assert p.suffix not in {'.sqlite3','.tgz','.key'} and p.name not in {'server.py','core_bridge.cjs'}


def test_allowlisted_export_has_no_history_artifacts_and_builds():
    parent=pathlib.Path(tempfile.mkdtemp(prefix='shashbesh-export-test-'));out=parent/'source'
    result=module.export(out)
    assert not result['publication_approved'] and not (out/'.git').exists() and not (out/'artifacts').exists()
    actual={p.relative_to(out).as_posix() for p in out.rglob('*') if p.is_file()}
    assert actual==set(result['sha256'])
    subprocess.run(['node',str(out/'apps/shashbesh-lab-web/build.mjs'),'--public-preview'],check=True,stdout=subprocess.PIPE)
    assert json.loads((out/'apps/shashbesh-lab-web/dist-public/build-config.json').read_text())['interactive'] is False
    with pytest.raises(ValueError):module.export(out)


def test_url_status_does_not_mark_lab_published():
    data=json.loads((ROOT/'docs/release/URL_STATUS.json').read_text())
    assert data['lab_publication_confirmed'] is False
    assert all(r['planned'] for r in data['results'] if r['resource'].startswith('lab'))
