"""Selected logical protocol and mandatory actual parser/behavior acceptance."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tarfile

import pytest
from jsonschema import Draft202012Validator, ValidationError

ROOT=Path(__file__).resolve().parents[1]
TOP=ROOT/'rtl/experiment-controller/top.v'
INSTRUMENT=ROOT/'rtl/instrument/top.v'

def contract_resources():
    receipt=os.environ['CIRNET_NATIVE_CONTRACTS_RECEIPT']
    return Path(receipt).parent/'resources/contracts'

def physical_target_fixture():
    path='physical-lab/examples/v1-target-capabilities.json'
    receipt=os.environ['CIRNET_NATIVE_CONTRACTS_RECEIPT']
    manifest=json.loads(Path(receipt).read_text(encoding='utf-8'))
    crate=Path(os.environ['CIRNET_NATIVE_CONTRACTS_CRATE'])
    assert crate.name==manifest['crate']['filename']
    assert hashlib.sha256(crate.read_bytes()).hexdigest()==manifest['crate']['sha256']
    with tarfile.open(crate,'r:gz') as package:
        member=package.extractfile(f"cirnet-contracts-native-{manifest['version']}/contracts/{path}")
        assert member is not None
        return json.load(member)


def test_control_boundary_names_and_transport_neutral_contract():
    text=TOP.read_text()
    for port in ['command_valid','command_code','safe_condition','scan_done','scan_success',
                 'plan_valid','routing_ready','protection_ready','watchdog_armed','watchdog_expired',
                 'fault_in','drive_enable','routing_enable','topology_scan_enable','experiment_clock']:
        assert port in text, f'missing control boundary: {port}'
    schema=json.loads((contract_resources()/'fpga-protocol/control.schema.json').read_text())
    Draft202012Validator.check_schema(schema)
    validator=Draft202012Validator(schema)
    request={'protocol_version':'1.0-scaffold','sequence':1,'operation':'SAFE_STATE'}
    validator.validate(request)
    with pytest.raises(ValidationError): validator.validate({**request,'operation':'AUTO_CORRECT_STUDENT_WIRING'})
    with pytest.raises(ValidationError): validator.validate({**request,'protocol_version':'0.1-dev'})


def test_b12_design_target_is_preserved_and_rejected_as_logical_runtime_protocol():
    resource=contract_resources()
    schema=json.loads((resource/'fpga-protocol/control.schema.json').read_text())
    manifest=json.loads((resource/'manifest.json').read_text())
    record=next(x for x in manifest['contracts'] if x['id']=='FpgaControlScaffold')
    assert record['version']=='1.0-scaffold'
    target=physical_target_fixture()
    assert target['fpga_protocol_version']=='2.0-scaffold' and target['available'] is False
    assert target['firmware_version']=='UNAVAILABLE'
    assert all(x['channels']==0 and x['runtime_reconfiguration_supported'] is False
               for x in target['instrument_capabilities'].values())
    with pytest.raises(ValidationError):
        Draft202012Validator(schema).validate({'protocol_version':target['fpga_protocol_version'],
                                             'sequence':1,'operation':'START'})


def test_future_instrument_interfaces_are_explicitly_unavailable():
    assert INSTRUMENT.is_file(),'future instrument interface missing'
    text=INSTRUMENT.read_text()
    for port in ['acquisition_clk','generator_clk','sdram_clk','logic_analyzer_available',
                 'scope_2ch_available','generator_2ch_available','capture_valid','sdram_request']:
        assert port in text
    docs=(ROOT/'docs/en/architecture/instrument.md').read_text()
    for marker in ['EP4CE10','SDRAM Arbiter','Trigger','Timestamp','CDC','TBD_BY_HARDWARE_DESIGN']:
        assert marker in docs


def test_actual_rtl_compilation_and_original_and_supplemental_behavior():
    result=subprocess.run([sys.executable,'-B',str(ROOT/'scripts/check_rtl.py')],
                          capture_output=True,text=True,timeout=180)
    assert result.returncode==0,result.stdout+result.stderr
    value=json.loads(result.stdout)
    expected_version=(ROOT/'VERSION').read_text().strip()
    assert value['pyslang']=='12.0.0' and value['contracts']['version']==expected_version
    assert value['compileTopExitCode']==0
    assert [(case['compileExitCode'],case['simulationExitCode']) for case in value['results']]==[(0,0),(0,0)]
    assert [x['marker'] for x in value['results']]==['LAB_FIRST_RTL_PASS','PERMIT_MATRIX_RTL_PASS']
