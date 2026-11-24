"""Verify selected Contracts, slang elaboration and actual RTL simulation."""
import argparse
from importlib.metadata import distribution
import json
try:
    from scripts.environment import getenv
except ModuleNotFoundError:
    from environment import getenv
from pathlib import Path
import subprocess
import uuid

from artifact_paths import artifact_directory
from rtl_toolchain import ROOT, sha256, tool_env, verify_toolchain


def compile_slang():
    if distribution('pyslang').version!='12.0.0':
        raise ValueError('RTL acceptance requires pyslang==12.0.0; no optional skip.')
    from pyslang.syntax import SyntaxTree
    from pyslang.ast import Compilation
    compilation=Compilation()
    sources=[ROOT/'rtl/experiment-controller/top.v',ROOT/'rtl/instrument/top.v',
             ROOT/'verification/rtl/tb_lab_first_control.v',ROOT/'verification/rtl/tb_permit_matrix.v']
    for path in sources: compilation.addSyntaxTree(SyntaxTree.fromFile(str(path)))
    errors=[str(d.code) for d in compilation.getAllDiagnostics() if d.isError()]
    if errors: raise RuntimeError('Slang parsing/elaboration failed: '+repr(errors))
    return sources


def main(argv=None):
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--toolchain-root',type=Path)
    parser.add_argument('--toolchain',type=Path,help='Explicit provenance JSON, primarily for diagnostics.')
    parser.add_argument('--contracts-receipt',type=Path,default=getenv('CIRNET_NATIVE_CONTRACTS_RECEIPT'))
    parser.add_argument('--contracts-sha256',default=getenv('CIRNET_NATIVE_CONTRACTS_SHA256'))
    args=parser.parse_args(argv)
    selected=args.toolchain_root or getenv('CIRNET_FPGA_TOOLCHAIN_ROOT')
    if not selected and args.toolchain: selected=args.toolchain.parent
    if not selected: parser.error('An explicit pinned toolchain root is required; no PATH fallback.')
    tools,provenance,pin=verify_toolchain(selected,args.toolchain)
    if not args.contracts_receipt or not args.contracts_sha256:
        parser.error('Supply both --contracts-receipt and --contracts-sha256.')
    result=subprocess.run(['node',str(ROOT/'scripts/native-contracts.mjs'),str(args.contracts_receipt),
                           args.contracts_sha256],capture_output=True,text=True,check=True,timeout=20)
    contracts=json.loads(result.stdout)
    sources=compile_slang()
    runtime=artifact_directory('embedded-rtl-'+uuid.uuid4().hex[:8]);env=tool_env(selected,runtime)
    report={'contracts':contracts,'pyslang':'12.0.0','toolchain':provenance,'results':[],
            'outputDirectory':str(runtime),'sourceHashes':{p.relative_to(ROOT).as_posix():sha256(p) for p in sources}}
    for name,executable in tools.items():
        result=subprocess.run([str(executable),'-V'],env=env,cwd=runtime,capture_output=True,text=True,timeout=60)
        output=result.stdout+result.stderr
        if result.returncode or pin['version'] not in output:
            raise ValueError('Toolchain execution version differs from the pinned release: '+name)
    command=[str(tools['iverilog']),'-g2012','-tnull',str(sources[0]),str(sources[1])]
    result=subprocess.run(command,env=env,cwd=runtime,capture_output=True,text=True,timeout=60)
    report['compileTopExitCode']=result.returncode
    if result.returncode: raise RuntimeError(f'Both-top syntax failure (exit {result.returncode}): '+result.stdout+result.stderr)
    for bench,marker in [('tb_lab_first_control','LAB_FIRST_RTL_PASS'),('tb_permit_matrix','PERMIT_MATRIX_RTL_PASS')]:
        image=runtime/(bench+'.vvp')
        command=[str(tools['iverilog']),'-g2012','-s',bench,'-o',str(image),*[str(p) for p in sources[:2]],
                 str(ROOT/'verification/rtl'/(bench+'.v'))]
        built=subprocess.run(command,env=env,cwd=runtime,capture_output=True,text=True,timeout=60)
        (runtime/(bench+'-compile.log')).write_text(built.stdout+built.stderr)
        if built.returncode: raise RuntimeError(f'RTL compilation failed (exit {built.returncode}): '+built.stdout+built.stderr)
        run=subprocess.run([str(tools['vvp']),str(image)],env=env,cwd=runtime,capture_output=True,text=True,timeout=60)
        (runtime/(bench+'-behavior.log')).write_text(run.stdout+run.stderr)
        if run.returncode or marker not in run.stdout:
            raise RuntimeError(f'RTL behavioral simulation failed (exit {run.returncode}): '+run.stdout+run.stderr)
        report['results'].append({'testbench':bench,'compileExitCode':built.returncode,
                                  'simulationExitCode':run.returncode,'marker':marker,'status':'PASS'})
    (runtime/'result.json').write_text(json.dumps(report,indent=2)+'\n')
    print(json.dumps(report,indent=2))
    return report


if __name__=='__main__': main()
