# I2C TMP117 Register Transaction

**Question:** How can two open-drain wires address a device and read a specific register?

**Build:** Wire Adafruit TMP117 breakout 4821 at 3.3 V, scan addresses, read device-ID register 0x0F, then temperature register 0x00.

**Visible or measurable result:** SDA/SCL idle voltage, detected address, device ID, ACK/NACK result and decoded temperature.

**Why useful:** I2C is not a library call. SDA and SCL are shared open-drain lines whose rise time comes from pull-ups and bus capacitance.

**Estimated time:** 130 minutes. **Difficulty:** intermediate.

**Required knowledge:** 06-uart-conversation. Read `BEFORE-YOU-POWER.md`.

**Success:** Firmware shows at least one raw register transaction without a sensor abstraction library.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
