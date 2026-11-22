# Controller and instrument scaffold

English · [Tiếng Việt](../vi/scaffold.md)

[Documentation index](index.md)

The [FPGA Architecture](https://github.com/cirnetlab/cirnet-remote-next/blob/master/docs/cirnetlab-FPGA-architecture-en.md) defines the board design target within the [Lab-First safety rules](https://github.com/cirnetlab/cirnet-remote-next/blob/master/docs/cirnet-architecture-lab-first-en.md).

| Owner | Boundary |
| --- | --- |
| FPGA | Verilog/SystemVerilog controller and instrument RTL, timing, trigger and capture design, SDRAM/CDC interfaces, and board-specific evidence. This source provides a controller scaffold and RTL testbenches. |
| Hardware | Local station driver, private FPGA transport and station-level protection. |
| Contracts and Remote | Contracts owns the logical `1.0-scaffold` schema and reserved register-map version. Remote owns the Web API, scheduler, authorization and Lab release selection. |

The EP4CE6E22C8N prototype target has no external SDRAM. In simulation, the controller moves through SAFE → SCANNING → SCANNED → PREPARED → ROUTED → POWERED → ARMED → RUNNING. A successful scan indicates readiness of the observation step. Electrical safety and topology correctness remain separate checks.

Reset enters SAFE with drive, routing and experiment clock disabled. The simulated controller requires a safe plan, route readiness, protection and an armed watchdog before enabling drive. These permits remain live. A fault or watchdog assertion immediately inhibits outputs and latches FAULT. Reset after clearance invalidates the old scan and plan. The experiment clock uses abstract control ticks. See the [controller specification](architecture/controller.md).

The EP4CE10E22C8N target with external SDRAM reserves interfaces for Logic Analyzer, Scope 2CH, Generator 2CH, SDRAM Arbiter, Trigger, Timestamp and CDC. Availability, capture validity, generator enable and SDRAM request remain false. The domain clock ports do not establish any board frequency. See the [instrument interface](architecture/instrument.md).

Physical firmware and transport remain `UNAVAILABLE`. Source packaging and RTL simulation cover the scaffold, while bitstream, timing, protection and HIL require board-specific evidence. Before enabling a physical target, obtain the board schematic, pin assignments, electrical limits, selected ADC/DAC and SDRAM, timing constraints, clock and reset plan, and measured protection and acquisition results. These inputs remain `TBD_BY_HARDWARE_DESIGN`. The Hardware Service owns the private transport boundary. Serial and USB-SPI adapters depend on real hardware selection.
