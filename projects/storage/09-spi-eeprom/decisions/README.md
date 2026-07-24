# Decisions

- Board: Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E; selected once for v1 to avoid duplicate firmware paths.
- Supply: 3.3 V only.
- Project choice: A storage write is a protocol: address validation, write-enable, page geometry, busy polling, readback and integrity.
- Hardware execution: not performed; evidence remains required.
