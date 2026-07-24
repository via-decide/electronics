# SPI EEPROM: Pages, Busy State and CRC

**Question:** Why can a memory accept SPI traffic yet refuse or corrupt a write?

**Build:** Wire 25LC256-I/P at 3.3 V, write one bounded record within a 64-byte page, poll WIP, read back and verify CRC32.

**Visible or measurable result:** Supply, CS# idle, SPI signals, status register transitions and readback CRC.

**Why useful:** A storage write is a protocol: address validation, write-enable, page geometry, busy polling, readback and integrity.

**Estimated time:** 180 minutes. **Difficulty:** intermediate.

**Required knowledge:** 08-spi-shift-register. Read `BEFORE-YOU-POWER.md`.

**Success:** Every accepted write is bounds-checked, page-contained, busy-polled and verified.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
