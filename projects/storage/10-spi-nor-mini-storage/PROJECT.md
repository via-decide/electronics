# SPI NOR Mini-Storage

**Question:** How do pages and erase sectors become a recoverable committed record?

**Build:** Wire MX25L3233FM2I-08G at 3.3 V, read JEDEC ID, erase only reserved sectors, page-program a CRC-protected record, commit it and select last-known-good metadata.

**Visible or measurable result:** Supply, JEDEC ID, status transitions, program/erase busy time, record CRC and selected generation.

**Why useful:** Storage is not saving bytes. A usable record needs geometry, integrity, commit ordering, redundant metadata and recovery.

**Estimated time:** 240 minutes. **Difficulty:** advanced-beginner.

**Required knowledge:** 09-spi-eeprom. Read `BEFORE-YOU-POWER.md`.

**Success:** Power-on scan returns a committed record or an explicit empty/corrupt state; it never silently accepts an invalid record.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
