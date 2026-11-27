# CIRNET Embedded Hardware version 0 changelog

[Changelog index](README.md)

## Unreleased

### Changed

- Standardize English major-version changelog navigation.

## v0.3.0-dev.1 — Development

Git tags and GitHub Releases provide no publication date for this development version.

### Added

- Verify allocator session reuse and digest rejection, late scanner replies, and reset with an active interlock fault.

### Changed

- Give the installer and RTL verification commands a common module for pinned toolchain checks. Document the RTL, testbench and tool responsibilities.
- Migrate the controller and instrument RTL and both behavioral testbenches. Bind source candidates to the native Contracts receipt.
- Link the verified RTL scaffold to the FPGA and CIRNET Lab-First targets.
- Document offline RTL verification with the selected native Contracts receipt, hash-pinned wheels and OSS CAD Suite archive.

**Source**

- [Native implementation baseline](https://github.com/cirnetlab/cirnet-embedded-hardware/commit/0373bf6e4f0407d0595a9c9f2a1c8e16b341d75e)
