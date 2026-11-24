from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]



def test_fpga_workspace_has_expected_boundaries():
    required=[
        'rtl/experiment-controller/top.v','rtl/instrument/top.v',
        'verification/rtl/tb_lab_first_control.v','verification/rtl/tb_permit_matrix.v',
        'docs/en/architecture/controller.md','docs/en/architecture/instrument.md',
    ]
    missing=[p for p in required if not (ROOT/p).is_file()]
    assert not missing, missing


def test_experiment_controller_docs_name_both_targets_and_no_sdram_prototype():
    text=(ROOT/'docs/en/architecture/controller.md').read_text()
    for marker in ['EP4CE6E22C8N','EP4CE10E22C8N','no external SDRAM']:
        assert marker in text


def test_top_is_explicit_placeholder_not_feature_claim():
    text=(ROOT/'rtl/experiment-controller/top.v').read_text().lower()
    assert 'placeholder' in text
    assert 'module cirnet_experiment_top' in text
    assert 'module netcircuit_experiment_top' not in text
    assert 'sdram controller implemented' not in text


def test_instrument_top_has_only_the_current_module_name():
    text = (ROOT / 'rtl/instrument/top.v').read_text()
    assert 'module cirnet_instrument_scaffold' in text
    assert 'module netcircuit_instrument_scaffold' not in text
