# Button Input: Floating, Pulled and Debounced

**Question:** Why does an unconnected digital input change when nobody pressed anything?

**Build:** Wire a normally-open button from GPIO27 to GND, use the internal pull-up, and compare raw state with a 30 ms debounced state.

**Visible or measurable result:** Idle and pressed voltage at GPIO27, raw transition count and debounced transition count.

**Why useful:** The button is not unstable. The unconnected input is electrically undefined; mechanical contacts also bounce.

**Estimated time:** 90 minutes. **Difficulty:** beginner.

**Required knowledge:** 02-led-current. Read `BEFORE-YOU-POWER.md`.

**Success:** Serial output distinguishes raw and stable state and one deliberate press produces one stable transition.

Hardware status: **HARDWARE_VALIDATION_REQUIRED**. Documentation and firmware are not physical proof.
