# MOSFET Low-Side Load Switch

**Question:** How can a GPIO control a load without supplying the load current?

**Build:** Use AO3400A as a 3.3 V low-side switch for a red LED and 1 kohm series resistor. Add 100 ohm gate series and 100 kohm gate pull-down.

**Visible or measurable result:** Gate-to-source voltage, drain voltage and load resistor voltage in ON and OFF states.

**Why useful:** A GPIO is a logic source, not a general-purpose power supply. The MOSFET separates control current from load current.

**Estimated time:** 100 minutes. **Difficulty:** beginner.

**Required knowledge:** 03-button-input. Read `BEFORE-YOU-POWER.md`.

**Success:** The load follows the logged gate command and the learner identifies gate, drain and source from the datasheet and adapter labels.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
