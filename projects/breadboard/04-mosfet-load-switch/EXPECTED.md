# Expected

## FACT

Electrical limits and protocol behaviour come from the exact sources in `project.yaml` and `bom.csv`.

## EXPECTED

GPIO low keeps the load off; GPIO high drives the gate near 3.3 V and lights the bounded low-current load.

- **Serial/output pattern:** `gate_command=ON|OFF` with `measure=required`; the log is not accepted as a voltage measurement.
- **Voltage and logic range:** the project rail is 3.3 V nominal. Signal nodes are expected between
  project GND and the measured rail; low is near GND and high is near the rail. Exact thresholds and
  supply limits remain the authoritative device-datasheet constraints.
- **Current:** Calculate bounded load current from the measured 1 kohm resistor voltage. The design intent is approximately 10 mA or less, not a measured claim.
- **State transition:** The load follows the logged gate command and the learner identifies gate, drain and source from the datasheet and adapter labels.
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
