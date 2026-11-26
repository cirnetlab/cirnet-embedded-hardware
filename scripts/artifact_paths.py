"""Use the selected Contracts DEV allocator for verification outputs."""
import hashlib
import json
import os
from pathlib import Path
import subprocess

from environment import export_environment, getenv

ROOT = Path(__file__).resolve().parents[1]


def _call(arguments):
    path = Path(getenv('CIRNET_ARTIFACTS_CLI', ''))
    expected = getenv('CIRNET_ARTIFACTS_CLI_SHA256')
    if not path.is_absolute() or not path.is_file() or path.is_symlink():
        raise ValueError('Select an absolute regular Contracts DEV allocator.')
    if hashlib.sha256(path.read_bytes()).hexdigest() != expected:
        raise ValueError('Contracts DEV allocator SHA256 differs from selection.')
    env = export_environment()
    env.setdefault('CIRNET_ARTIFACTS_CONTEXT', json.dumps({'owner': 'git:' + str(ROOT), 'roots': [str(ROOT)]}))
    env['NETCIRCUIT_ARTIFACTS_CONTEXT'] = env['CIRNET_ARTIFACTS_CONTEXT']
    result = subprocess.run(['node', str(path), *arguments], cwd=ROOT, env=env,
                            capture_output=True, text=True, timeout=30)
    if result.returncode != 0:
        raise ValueError(result.stderr.strip() or 'Contracts DEV allocator failed.')
    return Path(result.stdout.strip())


def artifact_directory(subdirectory=''):
    if 'CIRNET_LOCAL_STORAGE_ROOT' in os.environ:
        # Older selected DEV modules must not silently allocate into OS temp.
        _call(['--parent-info'])
    if not getenv('CIRNET_ARTIFACTS_SESSION'):
        os.environ['CIRNET_ARTIFACTS_SESSION'] = str(_call([]))
    return _call([subdirectory] if subdirectory else [])


def validate_artifact_directory(directory):
    return _call(['--validate', str(directory)])
