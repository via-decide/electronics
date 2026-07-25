# Capacitor and Time

## 1. Physical problem this lesson solves

This lesson solves how to **observe stored charge and RC settling**.

## 2. What you need to know first

lesson 06.

## 3. Components required

10 kohm resistor, 10 uF capacitor and DMM. Power policy: 3.3 V only; power off before rewiring.

## 4. What you will build

The physical circuit in [Project 05 extension](../../projects/breadboard/05-analog-voltage/PROJECT.md).

## 5. What you will measure

Use the project measurement plan. Identify supply, ground, orientation, decoupling and test
points before power. Measure the named physical quantity before accepting firmware output.

## 6. Minimum theory

Voltage is a difference between nodes; current needs a closed path; logic thresholds are ranges,
not perfect numbers. Protocols add timing and state rules to those electrical facts. Storage adds
geometry, integrity and recovery rules to protocols.

## 7. Physical explanation

Trace the path with a finger while power is off: source → controlled element → return. Then trace
the information path separately. If the two paths are not clear, do not power the circuit.

## 8. Common misconceptions

- Wire colour proves nothing.
- A successful build does not validate an absolute rating.
- A package name does not prove a pinout.
- A firmware log does not prove supply integrity.

## 9. Common wiring mistakes

- Mirrored IC orientation, split rails and missing common ground are checked first.

## 10. Linked project

[Project 05 extension](../../projects/breadboard/05-analog-voltage/PROJECT.md)

## 11. Success condition

record charge/discharge time without claiming an oscilloscope trace. Save evidence using the linked project template.

## 12. Next lesson

[Power Supply and Decoupling](08-power-supply-and-decoupling.md)

## 13. Primary references

- Espressif, [ESP32-DevKitC V4 User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) (retrieved 2026-07-25).
- Espressif, [ESP32 Series Datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf) (retrieved 2026-07-25).

## 14. Facts, expected results and required measurements

- **FACT:** only values linked to a primary source.
- **EXPECTED:** calculate for the exact circuit and state assumptions.
- **MEASURED:** enter only instrument output from real hardware.
- **UNKNOWN:** leave unknown until evidence exists.
