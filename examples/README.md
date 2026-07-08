# Examples

Examples are separated from core firmware so learning, experimentation, and integration tests do not obscure production code.

Each runnable example should contain:

- Purpose and subsystem covered.
- Hardware wiring.
- Build and flash instructions.
- Expected serial or telemetry output.
- Validation method.
- Known failure modes.

## Platforms

| Directory | Purpose |
| --- | --- |
| `esp32/` | ESP-IDF examples for ADC DMA, FreeRTOS, MQTT, OTA, deep sleep, I2C, and timers. |
| `stm32/` | STM32 examples and peripheral patterns. |
| `raspberry-pi/` | Raspberry Pi hardware-integration examples. |
| `linux/` | Linux host tools, data capture, and device-service examples. |
| `power-electronics/` | Measurement and control examples for power electronics topics. |

## Legacy Maturity Buckets

The repository may also use maturity-oriented example groupings when helpful:

| Directory | Purpose |
| --- | --- |
| `minimal/` | Smallest buildable example that demonstrates one concept with minimal dependencies. |
| `production/` | Example using diagnostics, retries, safe defaults, telemetry, and watchdog integration. |
| `advanced/` | Multi-feature integration examples, stress scenarios, and extended configurations. |
