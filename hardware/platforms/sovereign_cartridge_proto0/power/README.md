# Task 3 Power Safety

Status: `POWER_SAFETY_DESIGN_IN_PROGRESS`.

This directory freezes the first reviewable power, reset, brownout and
power-loss contract for Sovereign Cartridge Proto-0. It does not close Task 3.
The circuit still requires editable KiCad capture, native ERC, load-step and
power-cut simulation, and measured bench evidence.

## Safety architecture

```text
VBUS_5V
  -> TPS25942A eFuse
  -> VBUS_HOLD (100 uF nominal, 80 uF minimum effective)
  -> TLV62569P buck
  -> 3V3
  -> RP2354A + W25Q256JVEIQ
```

- The eFuse provides programmable undervoltage, overvoltage, current limiting,
  controlled inrush and reverse-current blocking.
- `VBUS_HOLD` stores only enough calculated energy to force a deterministic
  reset and deselect the payload NOR. It is not sized to finish a page program
  or erase.
- A 4.38 V supervisor watches `VBUS_HOLD`; a 3.08 V supervisor watches `3V3`.
  Their open-drain outputs and the buck power-good output form a wired-AND
  connection to `RUN`.
- The existing 10 kohm pull-up on `PAYLOAD_SPI_CS_N` makes the payload NOR
  inactive when the RP2354A enters reset.
- Recovery firmware must reject incomplete transaction states before exposing
  any object as committed. That rule is implemented in later transaction tasks,
  not by pretending a capacitor can complete arbitrary flash work.

See [`power-safety.svg`](power-safety.svg) for the block and state view.

## Frozen design values

| Function | Design candidate | Value |
| --- | --- | --- |
| Protected power path | TPS25942ARVCR | 4.50 V rising UVLO, 5.70 V rising OVP, 0.297 A nominal limit in reverse-blocking mode |
| Inrush control | TPS25942A `dVdT` | 4.7 nF; 1.951 ms nominal ramp and 0.256 A capacitor-only inrush |
| Hold-up store | `VBUS_HOLD` capacitor | 100 uF nominal; 80 uF minimum effective |
| 3.3 V converter | TLV62569PDDCR | 2.2 uH, 453 kohm / 100 kohm feedback, 3.318 V nominal |
| Converter output | X7R/X5R ceramic | 47 uF nominal, subject to bias derating |
| Hold-up supervisor | TLV803EA43DBZR | 4.38 V nominal, open-drain, 200 ms release delay |
| Rail supervisor | TLV803EA30DBZR | 3.08 V nominal, open-drain, 200 ms release delay |

All MPNs remain `DESIGN_CANDIDATE` until Task 6 checks lifecycle, authorized
sourcing, alternates and assembly constraints.

`DMODE` is driven from `VBUS_HOLD`, so the eFuse stays in non-ideal-diode
mode while hold-up energy remains. The datasheet specifies that this mode
halves the current limit programmed by `R_ILIM`: 150 kohm programs 0.593 A in
normal mode and therefore 0.297 A in the selected operating mode.

## Calculated safety envelope

The 3.3 V rail has a 300 mA engineering allocation. With 80% conversion
efficiency, 80 uF effective hold-up capacitance, a worst-low 4.2924 V
supervisor threshold and a conservative 3.6 V buck-input floor:

```text
E = 0.5 * C * (Vstart^2 - Vend^2) = 218.6 uJ
Pinput = (3.3 V * 0.300 A) / 0.80 = 1.2375 W
thold = E / Pinput = 176.6 us
```

The design allocates 50 us for supervisor assertion and 25 us for `RUN` to
quiescent payload-SPI behavior. The calculated margin is therefore 2.35x.
The 25 us bus-quiescence allocation is not yet a measured or guaranteed
RP2354A value, so it is a blocking validation item. Task 4 carries the same
unverified limit into its
[`../spi/spi-ownership.json`](../spi/spi-ownership.json) recovery contract.

## Artifacts

- [`power-safety.json`](power-safety.json) is the machine-readable contract.
- [`power-budget.csv`](power-budget.csv) records the 3.3 V design allocation.
- [`component-candidates.csv`](component-candidates.csv) records design parts
  without authorizing procurement.
- [`assumptions.md`](assumptions.md) separates facts, decisions, expected
  outcomes, measurements and unknowns.
- [`validation/task-03-checklist.md`](validation/task-03-checklist.md) defines
  the remaining gate.

Validate the contract with:

```sh
python3 tools/validate_sovereign_cartridge_power_safety.py --strict --self-test
```

Do not set `task_03_power_safety_passed` until the circuit is source-captured,
native ERC passes, the full current envelope is justified, and repeated
physical power cuts prove reset and chip-select timing.
