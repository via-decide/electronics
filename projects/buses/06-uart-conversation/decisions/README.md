# Decisions

- Board: Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E; selected once for v1 to avoid duplicate firmware paths.
- Supply: 3.3 V only.
- Project choice: UART moves bits. A frame adds meaning: magic, sequence, length, payload and CRC.
- Hardware execution: not performed; evidence remains required.
