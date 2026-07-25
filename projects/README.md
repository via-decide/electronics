# Projects

Projects combine firmware, hardware, documentation, validation, diagrams, and assets into complete end-to-end systems.

Beginner physical sequence:

1. [`breadboard/`](breadboard/README.md) — continuity, current, GPIO, switching and ADC.
2. [`buses/`](buses/README.md) — framed UART, register-level I²C and visible SPI.
3. [`storage/`](storage/README.md) — SPI EEPROM and crash-safe SPI NOR.
4. [`ssd_lab/`](ssd_lab/README.md) — raw NAND, FTL, ECC, mapping and controller validation.

A project should include:

- System purpose and requirements.
- Hardware bill of materials and wiring.
- Firmware configuration and build instructions.
- Validation procedures and benchmark results.
- Production notes and field diagnostics.
- Links to related feature documents and examples.
