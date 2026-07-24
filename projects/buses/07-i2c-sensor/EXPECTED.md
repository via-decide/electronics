# Expected

## FACT

Electrical limits and protocol behaviour come from the exact sources in `project.yaml` and `bom.csv`.

## EXPECTED

Default 7-bit address is expected at 0x48 and device ID register reset value is 0x0117. Temperature is MEASURED, not predicted.

- **Serial/output pattern:** an address scan ACK at the wired address, TMP117 ID `0x0117`, and an explicit NACK path.
- **Voltage and logic range:** the project rail is 3.3 V nominal. Signal nodes are expected between
  project GND and the measured rail; low is near GND and high is near the rail. Exact thresholds and
  supply limits remain the authoritative device-datasheet constraints.
- **Current:** No numeric current range is asserted without a complete load model and physical measurement.
- **State transition:** Firmware shows at least one raw register transaction without a sensor abstraction library.
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
