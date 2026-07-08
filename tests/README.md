# Tests

Tests are separated by validation type so firmware behavior can be reviewed at the correct abstraction level.

Each test procedure should document:

- Objective.
- Required equipment.
- Firmware and hardware revision.
- Procedure.
- Pass criteria.
- Failure criteria.
- Evidence location.

| Directory | Responsibility |
| --- | --- |
| `unit/` | Host-testable logic such as CRC, state machines, queue policies, and math helpers. |
| `integration/` | ESP-IDF component integration and feature interactions. |
| `hardware/` | Board, sensor, peripheral, and instrumented hardware validation. |
| `hardware-validation/` | Compatibility path for hardware validation procedures using hyphenated naming. |
| `performance/` | RAM, flash, CPU, latency, throughput, power, boot, and network measurements. |
| `stress/` | Long-duration, high-load, reconnect, queue pressure, fault injection, and watchdog scenarios. |
