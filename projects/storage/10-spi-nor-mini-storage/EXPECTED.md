# Expected

## FACT

Electrical limits and protocol behaviour come from the exact sources in `project.yaml` and `bom.csv`.

## EXPECTED

A prepared but uncommitted higher generation is ignored; the newest fully committed CRC-valid copy wins.

- **Serial/output pattern:** JEDEC ID `c2-20-16`, explicit write-gate state, both slot-valid flags and recovered generation.
- **Voltage and logic range:** the project rail is 3.3 V nominal. Signal nodes are expected between
  project GND and the measured rail; low is near GND and high is near the rail. Exact thresholds and
  supply limits remain the authoritative device-datasheet constraints.
- **Current:** No numeric current range is asserted without a complete load model and physical measurement.
- **State transition:** Power-on scan returns a committed record or an explicit empty/corrupt state; it never silently accepts an invalid record.
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
