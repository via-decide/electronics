# Power-Loss-Safe Write

## 1. Physical problem this lesson solves

This lesson solves how to **preserve last-known-good state across interruption**.

## 2. What you need to know first

lesson 14.

## 3. Components required

dual metadata sectors and commit states. Power policy: 3.3 V only; power off before rewiring.

## 4. What you will build

The physical circuit in [Project 10](../../projects/storage/10-spi-nor-mini-storage/PROJECT.md).

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

[Project 10](../../projects/storage/10-spi-nor-mini-storage/PROJECT.md)

## 11. Success condition

ignore a valid-CRC but uncommitted higher generation. Save evidence using the linked project template.

## 12. Next lesson

[Logic Analyzer](16-logic-analyzer.md)

## 13. Primary references

- Espressif, [ESP32-DevKitC V4 User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) (retrieved 2026-07-25).
- Espressif, [ESP32 Series Datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf) (retrieved 2026-07-25).
- Espressif, [ESP-IDF SPI Master Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/spi_master.html) (retrieved 2026-07-25).
- Macronix, [MX25L3233F Datasheet](https://www.macronix.com/Lists/Datasheet/Attachments/8933/MX25L3233F%2C%203V%2C%2032Mb%2C%20v1.7.pdf) (retrieved 2026-07-25).

## 14. Facts, expected results and required measurements

- **FACT:** only values linked to a primary source.
- **EXPECTED:** calculate for the exact circuit and state assumptions.
- **MEASURED:** enter only instrument output from real hardware.
- **UNKNOWN:** leave unknown until evidence exists.
