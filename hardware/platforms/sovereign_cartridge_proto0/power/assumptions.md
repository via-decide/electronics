# Task 3 Evidence Status

Retrieval date: 2026-07-27
Physical execution: not performed

## FACT

- The TPS25942A supports programmable undervoltage, overvoltage and current
  limiting, controlled output ramp and reverse-current blocking.
- The TLV62569P operates from 2.5 V to 5.5 V, supplies up to 2 A, supports a
  10 uF to 47 uF ceramic output network and exposes open-drain power-good.
- TLV803E supervisors provide fixed falling thresholds, open-drain active-low
  reset, threshold tolerance and fixed reset-release delays.
- RP2354A `RUN` is a global asynchronous active-low reset input. The RP2354A
  also has a core-supply brownout detector, which does not monitor the external
  3.3 V payload-flash rail.
- W25Q256JV operates from 2.7 V to 3.6 V. The selected WSON-8 package has no
  dedicated hardware reset pin.

## DECISION

- `VBUS_5V` passes through TPS25942ARVCR into a reverse-isolated
  `VBUS_HOLD` node before conversion. `DMODE` is driven by `VBUS_HOLD`, so
  non-ideal-diode mode remains active while stored energy remains.
- `VBUS_HOLD` has 100 uF nominal and at least 80 uF effective capacitance.
- TLV62569PDDCR creates a nominal 3.318 V rail using 2.2 uH, 453 kohm /
  100 kohm feedback and 47 uF nominal output capacitance.
- TLV803EA43DBZR monitors `VBUS_HOLD`; TLV803EA30DBZR monitors `3V3`.
  Their outputs and buck power-good are wired-AND to `RUN`.
- The 3.3 V engineering ceiling is 300 mA. The eFuse current limit is not an
  authorization to exceed the USB current contract. Its 150 kohm programming
  resistor gives 0.593 A nominal in normal mode and 0.297 A nominal in the
  selected non-ideal-diode mode.
- Stored energy is for fail-stop only. It is explicitly not sized to finish
  arbitrary NOR program or erase work.

## EXPECTED

- The eFuse is expected to isolate hold-up energy from a collapsing USB input
  while the 4.38 V supervisor forces `RUN` low.
- At the 300 mA design ceiling, the conservative calculated hold-up interval
  is 176.6 us against a 75 us fail-stop allocation.
- RP2354A reset plus the existing payload chip-select pull-up is expected to
  stop new flash commands before the 3.3 V rail leaves the NOR operating
  range.
- A 200 ms reset-release delay is expected to prevent rapid rail chatter from
  repeatedly releasing the controller.

Expected statements are design predictions, not bench evidence.

## MEASURED

`NONE`.

No voltage, current, energy, waveform, reset, thermal, USB or storage behavior
has been measured.

## UNKNOWN

- Actual pre-configuration, boot, USB, read, program, erase and recovery
  currents across voltage and temperature.
- Margin between controlled startup/current demand and the 0.297 A nominal
  non-ideal-diode current limit.
- Effective hold-up and buck capacitance after tolerance, DC bias, aging and
  temperature.
- Actual buck efficiency and loop response with the selected layout.
- Maximum delay from `RUN` assertion to payload-SPI pins becoming quiescent.
- Power-cut behavior while NOR program or erase is internally busy.
- Task 5 freezes USB-C attach, current, ESD and connector design policy;
  editable capture and every physical result remain open.
- Part lifecycle, authorized supply, alternates and manufacturing constraints
  owned by Task 6.
- Native ERC, PCB parasitics, rail ripple, thermals and every physical result.

## Gate

Task 3 remains open. The calculation and machine contract pass repository
validation, but editable schematic capture, native ERC, simulation, current
measurement and repeated power-cut evidence remain blocking.
