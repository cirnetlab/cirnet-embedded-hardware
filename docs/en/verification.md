# Verify and package the RTL

[Tiếng Việt](../vi/verification.md) · [Documentation](index.md)

Use Node 26 and Python 3.14. Select the Contracts producer's external native receipt, crate and allocator module. Provide their reviewed SHA-256 digests and allocate an external session. Install the verification dependencies in an external virtual environment using `python -m pip install --require-hashes -r requirements-verification.lock`.

```powershell
$env:CIRNET_NATIVE_CONTRACTS_RECEIPT = $contractsReceipt
$env:CIRNET_NATIVE_CONTRACTS_SHA256 = $contractsSha256
$env:CIRNET_NATIVE_CONTRACTS_CRATE = $contractsCrate
$env:CIRNET_ARTIFACTS_CLI = $allocator
$env:CIRNET_ARTIFACTS_CLI_SHA256 = $allocatorSha256
$env:CIRNET_ARTIFACTS_CONTEXT = node $allocator --context-info
$env:CIRNET_ARTIFACTS_SESSION = node $allocator
python -B scripts/install_toolchain.py
```

Set `CIRNET_FPGA_TOOLCHAIN_ROOT` to the installed root printed by the toolchain script, or select an existing matching pinned toolchain. The toolchain gate authenticates the archive and execution dependencies before slang elaboration and Icarus simulation.

```powershell
python -B -m pytest --basetemp (Join-Path $env:CIRNET_ARTIFACTS_SESSION 'pytest')
node --test tests/build-source.test.mjs
$filename = "cirnet-embedded-hardware-$(Get-Content VERSION)-native-source.tar.gz"
node scripts/build-source.mjs --output (Join-Path $env:CIRNET_ARTIFACTS_SESSION $filename) --contracts-receipt $contractsReceipt --contracts-sha256 $contractsSha256
```

Both `LAB_FIRST_RTL_PASS` and `PERMIT_MATRIX_RTL_PASS` must come from actual simulation. The package contains RTL, testbenches and an inventory in `fpga-artifact.json`; source packaging records the selected Contracts receipt and logical schema digests. Bitstream, timing, electrical protection and hardware-in-the-loop qualification require board-specific evidence.

The permit matrix checks that STATUS preserves failed scan evidence, Stop discards late scan completions, and reset leaves a persistent interlock fault effective. The tooling tests verify that the Python adapter reuses the owned Contracts allocator session and rejects a module with different bytes before invoking it.
