# Sovereign Cartridge Proto-0

This directory contains the Task 1 topology freeze and the in-progress Task 2
schematic, Task 3 power-safety, Task 4 SPI-ownership and Task 5 USB-C service
contracts for the post-v1 hardware-validation roadmap.

## Frozen product boundary

Proto-0 is one USB-powered service board containing:

- an **RP2354A, A4 stepping** controller with 2 MiB flash-in-package for boot
  firmware;
- a physically separate **W25Q256JVEIQ** 256 Mbit NOR device for cartridge
  payloads;
- USB 2.0 device/service access through a USB-C receptacle;
- SWD, RUN, BOOTSEL, rail, USB and payload-SPI test access;
- a 5 V VBUS input domain, a regulated 3.3 V I/O/storage domain and the
  RP2354A reference 1.1 V core-regulator domain.

The boot flash and payload flash are different physical devices. Proto-0 does
not contain raw NAND, an FPGA, wireless networking, a battery, USB host/source
functionality or USB Power Delivery.

## Evidence boundary

Status is `TOPOLOGY_FROZEN`; evidence status is `DESIGN_ONLY`.

Repository structural schematic ERC is available, but native KiCad ERC, PCB
DRC, assembly, voltage, current, timing, USB compliance, flash read/write,
reset and brownout results are not claimed. Real-hardware and destructive
operations remain disabled.

## Artifacts

- [`topology.json`](topology.json) is the machine-readable contract.
- [`topology.schema.json`](topology.schema.json) defines its interchange shape.
- [`architecture.svg`](architecture.svg) shows the frozen blocks and domains.
- [`bom/bom.csv`](bom/bom.csv) freezes only Task 1 parts and blocks premature
  purchase of parts owned by Tasks 2-6.
- [`assumptions.md`](assumptions.md) separates facts, decisions, expected
  outcomes and unknowns.
- [`decisions/0001-topology-freeze.md`](decisions/0001-topology-freeze.md)
  records alternatives and consequences.
- [`schematics/README.md`](schematics/README.md) tracks the Task 2 capture,
  editable KiCad source, pin/test-access contracts, review rendering and ERC
  status.
- [`power/README.md`](power/README.md) tracks the Task 3 protected input,
  regulator, reset, brownout, hold-up and fail-stop design.
- [`spi/README.md`](spi/README.md) tracks the Task 4 controller instance,
  exclusive owner, command allowlist, framing and recovery design.
- [`usb/README.md`](usb/README.md) tracks the Task 5 USB-C sink, protection,
  descriptor, service-owner, storage handoff and physical-recovery design.
- [`validation/task-01-checklist.md`](validation/task-01-checklist.md) defines
  the software-verifiable acceptance gate.

Validate with:

```sh
python3 tools/validate_sovereign_cartridge_topology.py --strict --self-test
python3 tools/validate_sovereign_cartridge_schematic.py --strict --self-test
python3 tools/validate_sovereign_cartridge_power_safety.py --strict --self-test
python3 tools/validate_sovereign_cartridge_spi_ownership.py --strict --self-test
python3 tools/validate_sovereign_cartridge_usb_service.py --strict --self-test
```
