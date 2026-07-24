# UART Framed Conversation

**Question:** How do two devices agree where a message begins and whether it arrived intact?

**Build:** Jumper UART1 TX GPIO17 to UART2 RX GPIO16 on the selected WROOM-32E board and loop back a binary frame between independently configured peripherals.

**Visible or measurable result:** TX/RX idle voltage, accepted frame count, CRC rejection count and optional logic timing.

**Why useful:** UART moves bits. A frame adds meaning: magic, sequence, length, payload and CRC.

**Estimated time:** 120 minutes. **Difficulty:** intermediate.

**Required knowledge:** 05-analog-voltage. Read `BEFORE-YOU-POWER.md`.

**Success:** The receiver validates magic, length and CRC before printing the payload.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
