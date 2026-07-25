# Expected

## FACT

Electrical limits and protocol behaviour come from the exact sources in `project.yaml` and `bom.csv`.

## EXPECTED

WREN sets WEL, WRITE begins a self-timed cycle, WIP eventually clears, and readback matches. Timing is MEASURED if captured.

- **Serial/output pattern:** WEL/WIP status, no-WREN rejection, page-cross rejection, premature-read observation and matching CRCs.
- **Voltage and logic range:** the project rail is 3.3 V nominal. Signal nodes are expected between
  project GND and the measured rail; low is near GND and high is near the rail. Exact thresholds and
  supply limits remain the authoritative device-datasheet constraints.
- **Current:** No numeric current range is asserted without a complete load model and physical measurement.
- **State transition:** Every accepted write is bounds-checked, page-contained, busy-polled and verified.
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
