# Decisions

- Board: Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E; selected once for v1 to avoid duplicate firmware paths.
- Supply: 3.3 V only.
- Project choice: A GPIO is a logic source, not a general-purpose power supply. The MOSFET separates control current from load current.
- Hardware execution: not performed; evidence remains required.
