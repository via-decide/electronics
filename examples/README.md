# Examples

Examples are separated from core firmware so learning, experimentation, and integration tests do not obscure production code.

## Directory Responsibilities

| Directory | Purpose |
| --- | --- |
| `minimal/` | Smallest buildable example that demonstrates one concept with minimal dependencies. |
| `production/` | Example using production patterns: diagnostics, retries, safe defaults, telemetry, and watchdog integration. |
| `advanced/` | Multi-feature integration examples, stress scenarios, and extended configurations. |

Each example should include its own build instructions, expected hardware wiring, configuration, and validation steps.
