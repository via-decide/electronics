# Tests

Tests are separated by validation type so firmware behavior can be reviewed at the correct abstraction level.

| Directory | Responsibility |
| --- | --- |
| `unit/` | Host-testable logic such as CRC, state machines, queue policies, and math helpers. |
| `integration/` | ESP-IDF component integration and feature interactions. |
| `stress/` | Long-duration, high-load, reconnect, queue pressure, and watchdog scenarios. |
| `hardware_validation/` | Tests requiring real boards, sensors, instruments, or fixtures. |

Each test should document hardware, firmware revision, commands, expected output, and acceptance criteria.
