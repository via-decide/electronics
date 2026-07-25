# Expected

## FACT

Electrical limits and protocol behaviour come from the exact sources in `project.yaml` and `bom.csv`.

## EXPECTED

For an illustrative 1.8 V LED drop, calculated current is about 6.8 mA, 1.5 mA and 0.15 mA. These are EXPECTED examples, not measured values.

- **Serial/output pattern:** Not applicable: this project intentionally has no firmware.
- **Voltage and logic range:** the project rail is 3.3 V nominal. Signal nodes are expected between
  project GND and the measured rail; low is near GND and high is near the rail. Exact thresholds and
  supply limits remain the authoritative device-datasheet constraints.
- **Current:** Calculate `I = V_resistor / R_measured` for each resistor. No numeric current is accepted until LED and resistor voltages are measured.
- **State transition:** Measured V_LED plus V_R is consistent with the measured rail within instrument and contact uncertainty.
- **Calculation assumptions:** exact MPNs and wiring in `bom.csv`/`pinmap.yaml`, 3.3 V nominal rail,
  measured resistor values, correct package orientation and no unlisted external load.
- **Tolerance:** resistor tolerance, supply variation, device thresholds, temperature, breadboard
  resistance and instrument accuracy widen predictions. Record instrument uncertainty; do not turn
  a nominal value into a measured result.

## MEASURED

UNKNOWN until a learner records real instrument results under `evidence/`.

## Failure output

The controlled failure in `BREAK-IT.md` must produce an explicit changed or rejected state, never a
fabricated screenshot.
