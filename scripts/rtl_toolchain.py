"""Select and authenticate the pinned OSS CAD Suite execution environment."""
import hashlib
import json
import os
from pathlib import Path, PurePosixPath
import platform
import posixpath
import re
import tarfile

from artifact_paths import validate_artifact_directory

ROOT=Path(__file__).resolve().parents[1]


def sha256(path):
    with Path(path).open('rb') as stream:
        return hashlib.file_digest(stream,'sha256').hexdigest()


def selected_platform():
    if platform.machine().lower() not in {'amd64','x86_64'}:
        raise ValueError('Pinned RTL toolchain supports x64 Windows/Linux only.')
    if os.name=='nt': return 'windows-x64'
    if platform.system()=='Linux': return 'linux-x64'
    raise ValueError('Pinned RTL toolchain supports Windows/Linux only.')


def tool_env(root,runtime):
    root=Path(root);runtime=Path(runtime)
    selected={key:value for key,value in os.environ.items() if not key.upper().startswith(('LD_','DYLD_'))
              and key.upper() not in {'LIBPATH','SHLIB_PATH','IVERILOG_ROOT','VPI_MODULE_PATH',
                                     'IVERILOG_DUMPER','IVERILOG_ICONFIG','GCONV_PATH','BASH_ENV','ENV'}}
    return {**selected,'PATH':os.pathsep.join([str(root/'bin'),str(root/'lib'),os.environ.get('PATH','')]),
            'YOSYSHQ_ROOT':str(root),'TMP':str(runtime),'TEMP':str(runtime),'TMPDIR':str(runtime),
            'PYTHONDONTWRITEBYTECODE':'1'}


def checked_members(archive):
    members=archive.getmembers();seen=set()
    for item in members:
        path=PurePosixPath(item.name)
        if ('\\' in item.name or path.is_absolute() or '..' in path.parts or
            not path.parts or path.parts[0]!='oss-cad-suite' or ':' in item.name or item.name in seen):
            raise ValueError('Unsafe or duplicate toolchain archive member.')
        seen.add(item.name)
        if not (item.isfile() or item.isdir() or item.issym() or item.islnk()):
            raise ValueError('Unsupported toolchain archive member.')
    return members


def authenticate_execution_files(root,archive,expected_archive_sha256):
    """Archive-derived required native helpers, configs, wrappers and libraries.

    Linux modeled-layout tests do not establish actual hosted Linux execution.
    """
    root=Path(root).resolve();archive=Path(archive)
    if sha256(archive)!=expected_archive_sha256:
        raise ValueError('Toolchain archive SHA256 differs from the pinned release.')
    with tarfile.open(archive,'r:gz') as bundle:
        members=checked_members(bundle)
        records={item.name.removeprefix('oss-cad-suite/'):item for item in members if not item.isdir()}
        required={name for name in records if name.startswith(('bin/iverilog','bin/vvp','libexec/','lib/ivl/'))
                  or name.lower().endswith(('.dll','.vpi')) or re.search(r'\.so(?:\.|$)',name.lower())}
        if not required:raise ValueError('Toolchain archive has no execution support inventory.')
        targets={};pending=list(required)
        while pending:
            name=pending.pop();item=records[name]
            if not (item.issym() or item.islnk()):continue
            if item.issym():
                if PurePosixPath(item.linkname).is_absolute():raise ValueError('Unsafe support symlink target.')
                target=posixpath.normpath(posixpath.join(posixpath.dirname(name),item.linkname))
            else:target=item.linkname.removeprefix('oss-cad-suite/')
            if target.startswith('../') or target not in records:
                raise ValueError('Toolchain support link target is absent or unsafe.')
            targets[name]=target
            if target not in required:required.add(target);pending.append(target)
        hashes={}
        # Keep archive order to avoid repeated backward decompression seeks.
        for item in members:
            name=item.name.removeprefix('oss-cad-suite/')
            if name not in required or not item.isfile():continue
            stream=bundle.extractfile(item)
            if stream is None:raise ValueError('Toolchain support archive member has no bytes.')
            expected=hashlib.file_digest(stream,'sha256').hexdigest();hashes[name]=expected
            path=root/name
            if not path.is_file() or path.is_symlink() or not path.resolve().is_relative_to(root) or sha256(path)!=expected:
                raise ValueError('Toolchain support file missing or modified: '+name)
        for name,target in targets.items():
            item=records[name];path=root/name
            if item.issym():
                if not path.is_symlink() or os.readlink(path).replace('\\','/')!=item.linkname:
                    raise ValueError('Toolchain support symlink target differs: '+name)
            elif not path.is_file() or path.is_symlink() or not path.samefile(root/target):
                raise ValueError('Toolchain support hardlink differs: '+name)
            visited={name};final=target
            while final in targets:
                if final in visited:raise ValueError('Toolchain support link cycle.')
                visited.add(final);final=targets[final]
            if (not path.is_file() or not path.resolve().is_relative_to(root) or
                final not in hashes or sha256(path)!=hashes[final]):
                raise ValueError('Toolchain support linked bytes differ: '+name)
    return len(required)


def verify_toolchain(root,provenance=None):
    root=Path(root).resolve()
    validate_artifact_directory(root)
    provenance=Path(provenance) if provenance else (root/'.cirnet-toolchain.json' if (root/'.cirnet-toolchain.json').exists() else root/'.netcircuit-toolchain.json')
    value=json.loads(provenance.read_text())
    lock=json.loads((ROOT/'integration/toolchain-lock.json').read_text())
    key=selected_platform();selected=lock['platforms'][key]
    if (value.get('schemaVersion')!=1 or value.get('platform')!=key or value.get('release')!=lock['tag']
        or value.get('archiveSha256')!=selected['sha256']):
        raise ValueError('Toolchain provenance differs from the pinned platform/archive.')
    archive=Path(value['archivePath'])
    validate_artifact_directory(archive.parent)
    if not archive.is_absolute():raise ValueError('Toolchain archive path must be absolute.')
    authenticated=authenticate_execution_files(root,archive,selected['sha256'])
    tools={}
    for name in ('iverilog','vvp'):
        relative='bin/'+name+('.exe' if key=='windows-x64' else '')
        executable=(root/relative).resolve()
        if not executable.is_relative_to(root): raise ValueError('Toolchain executable escaped its owned root.')
        record=value['tools'][name]
        if record['path']!=relative or sha256(executable)!=record['sha256']:
            raise ValueError('Toolchain executable hash differs from selected provenance: '+name)
        tools[name]=executable
    return tools,{**value,'authenticatedExecutionFiles':authenticated},selected
