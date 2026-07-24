# Decisions

- Board: Espressif ESP32-DevKitC V4 with ESP32-WROOM-32E; selected once for v1 to avoid duplicate firmware paths.
- Supply: 3.3 V only.
- Project choice: I2C is not a library call. SDA and SCL are shared open-drain lines whose rise time comes from pull-ups and bus capacitance.
- Hardware execution: not performed; evidence remains required.
