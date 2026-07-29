# Task 2 Schematic Capture

Status: `SCHEMATIC_CAPTURE_IN_PROGRESS`.

This directory turns the frozen topology into a reviewable electrical contract.
It does not close Task 2: the repository structural ERC passes, while native
KiCad ERC, test-point source capture and electrical review remain open.

## Captured decisions

- RP2354A A4 power, ground, core-regulator, clock, USB, QSPI, SWD and RUN
  connections follow the cited Raspberry Pi reference design.
- RP2354A in-package 2 MiB NOR remains the only boot device.
- The physically separate W25Q256JVEIQ payload NOR is assigned to:
  GPIO16/CIPO, GPIO17/CS_N, GPIO18/SCK and GPIO19/COPI.
- The payload NOR is not connected to the QSPI/XIP bus. Its chip-select has a
  10 kohm pull-up and WP#/IO2 and HOLD#/IO3 are defined high for single-SPI
  operation.
- BOOTSEL uses QSPI_SS; RUN, SWDIO and SWCLK remain accessible.
- TP1-TP14 have a net and footprint contract in `test-access.csv`, but their
  KiCad symbols are still explicitly pending.
- The input-power implementation remains a DNP placeholder in this editable
  sheet. Task 3 now defines its design in
  [`../power/power-safety.json`](../power/power-safety.json), but source
  capture and native ERC remain open. Task 5 now selects the USB-C receptacle,
  CC and ESD design candidates, but their editable source implementation
  remains a DNP placeholder.

Task 4 defines the SPI0 instance, manual chip-select framing, exclusive owner,
opcode allowlist and recovery policy in
[`../spi/spi-ownership.json`](../spi/spi-ownership.json). Firmware
implementation and physical timing evidence remain open.

## Artifacts

- [`schematic.json`](schematic.json) is the machine-readable Task 2 contract.
- [`pinmap.csv`](pinmap.csv) enumerates every RP2354A QFN pin and exposed pad.
- [`test-access.csv`](test-access.csv) assigns TP1-TP14 nets and footprints.
- [`kicad/sovereign_cartridge_proto0.kicad_sch`](kicad/sovereign_cartridge_proto0.kicad_sch)
  is the editable, reference-derived electrical source.
- [`kicad/SOURCE.md`](kicad/SOURCE.md) records source provenance and
  transformations.
- [`rendered-schematic.svg`](rendered-schematic.svg) is the current review
  overview, not a native KiCad export.
- [`assumptions.md`](assumptions.md) separates facts, decisions, expected
  behavior, measured evidence and unknowns.
- [`erc-report.json`](erc-report.json) records repository structural ERC and
  its limitations.

## Validation

Run the repository structural ERC:

```sh
python3 tools/validate_sovereign_cartridge_schematic.py --strict --self-test
```

On a workstation with KiCad 9, run the blocking native checks:

```sh
kicad-cli sch erc \
  --format json \
  --severity-all \
  --exit-code-violations \
  --output hardware/platforms/sovereign_cartridge_proto0/schematics/native-kicad-erc.json \
  hardware/platforms/sovereign_cartridge_proto0/schematics/kicad/sovereign_cartridge_proto0.kicad_sch

kicad-cli sch export svg \
  --black-and-white \
  --output hardware/platforms/sovereign_cartridge_proto0/schematics/native-render/ \
  hardware/platforms/sovereign_cartridge_proto0/schematics/kicad/sovereign_cartridge_proto0.kicad_sch
```

Do not set `task_02_schematic_passed` until the test-point symbols are captured,
native ERC output is committed and the editable sheet/native render are
reviewed. No physical behavior is measured or claimed here.
