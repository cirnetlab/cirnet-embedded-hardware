"""Observable source-release and fail-closed toolchain boundaries."""
import json
import os
import hashlib
import io
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest

ROOT = Path(__file__).resolve().parents[1]


def run_script(name, *args):
    return subprocess.run([sys.executable, '-B', str(ROOT/'scripts'/name), *map(str,args)],
                          capture_output=True, text=True, timeout=90)


def test_allocator_bridge_reuses_the_owned_session(tmp_path):
    session = Path(os.environ['CIRNET_ARTIFACTS_SESSION']).resolve(strict=True)
    subdirectory = tmp_path.resolve(strict=True).relative_to(session) / 'bridge-output'
    code = (
        'import json, sys; from artifact_paths import artifact_directory; '
        'print(json.dumps([str(artifact_directory()), str(artifact_directory(sys.argv[1]))]))'
    )
    result = subprocess.run(
        [sys.executable, '-B', '-c', code, subdirectory.as_posix()],
        cwd=ROOT / 'scripts', capture_output=True, text=True, timeout=30,
    )
    assert result.returncode == 0, result.stderr
    active, output = map(Path, json.loads(result.stdout))
    assert active.resolve(strict=True) == session
    assert output.resolve(strict=True) == session / subdirectory


def test_allocator_bridge_rejects_an_unselected_module(tmp_path):
    replacement = tmp_path / 'allocator.mjs'
    marker = tmp_path / 'executed'
    replacement.write_text(
        'import {writeFileSync} from "node:fs"; writeFileSync(process.argv[2], "executed");',
        encoding='utf-8',
    )
    env = {**os.environ, 'CIRNET_ARTIFACTS_CLI': str(replacement)}
    code = 'import sys; from artifact_paths import artifact_directory; artifact_directory(sys.argv[1])'
    result = subprocess.run(
        [sys.executable, '-B', '-c', code, str(marker)], cwd=ROOT / 'scripts',
        env=env, capture_output=True, text=True, timeout=30,
    )
    assert result.returncode != 0
    assert 'Contracts DEV allocator SHA256 differs from selection.' in result.stderr
    assert not marker.exists()


def test_rtl_gate_rejects_missing_explicit_toolchain(tmp_path):
    script = ROOT/'scripts/check_rtl.py'
    assert script.is_file(), 'mandatory RTL acceptance runner is missing'
    result = run_script('check_rtl.py','--toolchain',tmp_path/'missing.json')
    assert result.returncode != 0
    assert 'toolchain' in result.stderr.lower()


def test_toolchain_installer_rejects_unverified_archive_before_extraction(tmp_path):
    script = ROOT/'scripts/install_toolchain.py'
    assert script.is_file(), 'digest-verified RTL toolchain installer is missing'
    invalid=tmp_path/'bad.tgz'; invalid.write_bytes(b'not the selected release')
    result=run_script('install_toolchain.py','--archive',invalid)
    assert result.returncode != 0
    assert 'sha256' in result.stderr.lower()


def test_rtl_gate_rejects_wrong_toolchain_archive_identity(tmp_path):
    script = ROOT/'scripts/check_rtl.py'
    assert script.is_file(), 'mandatory RTL acceptance runner is missing'
    path=tmp_path/'wrong.json'
    path.write_text(json.dumps({'schemaVersion':1,'platform':'windows-x64','archiveSha256':'0'*64}))
    result=run_script('check_rtl.py','--toolchain',path)
    assert result.returncode != 0
    assert 'toolchain' in result.stderr.lower()


def test_native_contract_provenance_rejects_wrong_digest_and_shadowed_resource(tmp_path):
    receipt = Path(os.environ['CIRNET_NATIVE_CONTRACTS_RECEIPT'])
    expected_sha = os.environ['CIRNET_NATIVE_CONTRACTS_SHA256']
    crate = Path(os.environ['CIRNET_NATIVE_CONTRACTS_CRATE'])
    manifest = json.loads(receipt.read_bytes())
    crate_bytes = crate.read_bytes()
    assert manifest['crate'] == {
        'filename': crate.name,
        'size': len(crate_bytes),
        'sha256': hashlib.sha256(crate_bytes).hexdigest(),
    }

    def verify(path, digest):
        return subprocess.run(
            ['node', str(ROOT / 'scripts/native-contracts.mjs'), str(path), digest],
            capture_output=True, text=True, timeout=30,
        )

    selected = verify(receipt, expected_sha)
    assert selected.returncode == 0, selected.stderr
    assert json.loads(selected.stdout)['sourceSha256'] == manifest['sourceSha256']
    mismatched = verify(receipt, '0' * 64)
    assert mismatched.returncode != 0
    assert 'receipt SHA-256 mismatch' in mismatched.stderr

    copy = tmp_path / receipt.name
    copy.write_bytes(receipt.read_bytes())
    schema = Path('resources/contracts/fpga-protocol/control.schema.json')
    for resource in (Path('resources/contracts/manifest.json'), schema):
        target = tmp_path / resource
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes((receipt.parent / resource).read_bytes())
    unmodified = verify(copy, expected_sha)
    assert unmodified.returncode == 0, unmodified.stderr
    (tmp_path / schema).write_bytes((tmp_path / schema).read_bytes() + b'\n')
    shadowed = verify(copy, expected_sha)
    assert shadowed.returncode != 0
    assert 'resource differs from the receipt' in shadowed.stderr
    assert schema.as_posix() in shadowed.stderr


@pytest.mark.parametrize('changed,mutation',[
    ('lib/ivl/ivlpp','remove'),('lib/ivl/vvp.conf','tamper'),
    ('lib/required.dll','remove'),('lib/librequired.so.1','tamper'),
    ('libexec/iverilog','remove'),('bin/iverilog','tamper')])
def test_archive_derived_execution_closure_rejects_missing_or_modified_support(tmp_path,changed,mutation):
    """Modeled native layouts; never claims execution of synthetic/Linux tools."""
    archive=tmp_path/'synthetic.tgz';extracted=tmp_path/'oss-cad-suite';extracted.mkdir()
    values={'bin/iverilog':b'wrapper','bin/vvp':b'runtime','libexec/iverilog':b'compiler',
            'lib/ivl/ivlpp':b'preprocessor','lib/ivl/vvp.conf':b'target-config',
            'lib/required.dll':b'native-windows','lib/librequired.so.1':b'native-linux'}
    with tarfile.open(archive,'w:gz') as bundle:
        for name,data in values.items():
            item=tarfile.TarInfo('oss-cad-suite/'+name);item.size=len(data)
            bundle.addfile(item,io.BytesIO(data))
            path=extracted/name;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
    code=('import sys;sys.path.insert(0,sys.argv[1]);'
          'from check_rtl import authenticate_execution_files;'
          'authenticate_execution_files(sys.argv[2],sys.argv[3],sys.argv[4])')
    command=[sys.executable,'-B','-c',code,str(ROOT/'scripts'),str(extracted),str(archive),
             hashlib.sha256(archive.read_bytes()).hexdigest()]
    good=subprocess.run(command,capture_output=True,text=True,timeout=60)
    assert good.returncode==0,good.stderr
    target=extracted/changed
    if mutation=='remove':target.unlink()
    else:target.write_bytes(b'altered support')
    bad=subprocess.run(command,capture_output=True,text=True,timeout=60)
    assert bad.returncode!=0
    assert 'support' in bad.stderr.lower()


def test_canonical_environment_names_override_and_export_legacy_aliases():
    from scripts.environment import getenv, export_environment
    values = {'CIRNET_FPGA_TOOLCHAIN_ROOT': 'canonical', 'NETCIRCUIT_FPGA_TOOLCHAIN_ROOT': 'legacy',
              'NETCIRCUIT_CONTRACTS_ARTIFACT_MANIFEST': 'old-manifest'}
    exported = export_environment(values)
    assert getenv('NETCIRCUIT_FPGA_TOOLCHAIN_ROOT', environ=values) == 'canonical'
    assert exported['CIRNET_FPGA_TOOLCHAIN_ROOT'] == exported['NETCIRCUIT_FPGA_TOOLCHAIN_ROOT'] == 'canonical'
    assert exported['CIRNET_CONTRACTS_ARTIFACT_MANIFEST'] == exported['NETCIRCUIT_CONTRACTS_ARTIFACT_MANIFEST'] == 'old-manifest'
