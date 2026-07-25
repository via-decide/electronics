# SPI-Like Shift Register

**Question:** What do clock, data and latch signals physically do to eight visible outputs?

**Build:** Wire SN74HC595N at 3.3 V with eight 1 kohm LED paths, shift a walking bit on MOSI/SHCP and latch it with RCLK.

**Visible or measurable result:** Clock, serial data and latch timing; Q0-Q7 visible state; 3.3 V supply at the IC.

**Why useful:** The shift register comes before flash because its output is visible. RCLK is a storage-register latch, not a generic SPI chip-select.

**Estimated time:** 140 minutes. **Difficulty:** intermediate.

**Required knowledge:** 07-i2c-sensor. Read `BEFORE-YOU-POWER.md`.

**Success:** Captured or manually traced clock/data/latch transitions agree with the displayed output byte.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
