# Task 2 Evidence Status

## FACT

- The RP2354A uses the same QFN-60 pinout represented by the official
  Raspberry Pi RP2350A minimal KiCad design and contains a 2 MiB boot NOR
  device in-package.
- The RP2354A reference core supply uses the on-chip switching regulator,
  including the 3.3 uH inductor, 4.7 uF capacitors and 33 ohm feedback path
  captured in the imported reference design.
- GPIO16 through GPIO19 expose the SPI0 RX, CSn, SCK and TX alternate
  functions respectively.
- The W25Q256JVEIQ payload NOR is a distinct 256 Mbit device. Its single-SPI
  pins are CS# 1, DO/IO1 2, GND 4, DI/IO0 5, CLK 6 and VCC 8; WP#/IO2 and
  HOLD#/IO3 are held high in this capture.
- USB_DM and USB_DP are RP2354A pins 51 and 52. The Raspberry Pi reference
  circuit places 27 ohm series resistors in both paths.
- `schematic.json` and `pinmap.csv` are the canonical Task 2 contract. The
  editable KiCad source is derived from the official Raspberry Pi minimal
  reference design.

## DECISION

- GPIO16 = `PAYLOAD_SPI_CIPO`, GPIO17 = `PAYLOAD_SPI_CS_N`, GPIO18 =
  `PAYLOAD_SPI_SCK`, and GPIO19 = `PAYLOAD_SPI_COPI`.
- The payload NOR does not share the QSPI/XIP bus used by the boot flash.
- A 10 kohm pull-up defines payload chip-select inactive during reset.
- The selected pins are SPI0-compatible, but Task 2 does not allocate runtime
  ownership. Controller-instance and exclusive-owner policy remain Task 4.
- TP1 through TP14 use a plated 1.0 mm test-point footprint contract. Their
  symbols are intentionally not claimed as captured in the imported KiCad
  sheet yet; `test-access.csv` marks this remaining source-capture work.

## EXPECTED

- The schematic is expected to become an ERC-clean electrical handoff after
  the test-point symbols are captured, the Task 3 and Task 5 placeholders are
  replaced, and native KiCad ERC is run.
- The separated payload bus is expected to make boot-flash and payload-flash
  ownership independently reviewable.

Expected statements are design predictions, not bench evidence.

## MEASURED

`NONE`.

No PCB, assembly, voltage, current, timing, USB, flash, reset, thermal or
brownout behavior has been measured.

## UNKNOWN

- Native KiCad ERC results: `kicad-cli` is unavailable in the current
  workspace.
- The final 5 V protection, 3.3 V regulator, rail budget, supervisor,
  brownout and safe-shutdown implementation: Task 3.
- Payload-SPI ownership, isolation and recovery policy: Task 4.
- USB-C receptacle, CC terminations and ESD candidates: selected by Task 5;
  editable capture, layout and compliance evidence remain open.
- Test-point physical placement, fixture clearance, controlled-impedance
  layout, decoupling placement and all PCB parasitics.
- Physical behavior until current-limited bring-up produces measured evidence.

## Gate

Task 2 remains open. Repository structural ERC passes; native KiCad ERC,
source capture of TP1-TP14, review of the KiCad sheet, and completion of the
downstream-owned placeholder circuits are required before
`task_02_schematic_passed` can become true.
