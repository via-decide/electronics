# External EEPROM

## 1. Physical problem this lesson solves

This lesson solves how to **respect page and busy-state rules during nonvolatile writes**.

## 2. What you need to know first

lesson 11.

## 3. Components required

25LC256-I/P. Power policy: 3.3 V only; power off before rewiring.

## 4. What you will build

The physical circuit in [Project 09](../../projects/storage/09-spi-eeprom/PROJECT.md).

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

[Project 09](../../projects/storage/09-spi-eeprom/PROJECT.md)

## 11. Success condition

perform WREN, bounded write, WIP poll and readback. Save evidence using the linked project template.

## 12. Next lesson

[SPI NOR Flash](13-spi-nor-flash.md)

## 13. Primary references

- Espressif, [ESP32-DevKitC V4 User Guide](https://docs.espressif.com/projects/esp-dev-kits/en/latest/esp32/esp32-devkitc/user_guide.html) (retrieved 2026-07-25).
- Espressif, [ESP32 Series Datasheet](https://documentation.espressif.com/esp32_datasheet_en.pdf) (retrieved 2026-07-25).
- Espressif, [ESP-IDF SPI Master Driver](https://docs.espressif.com/projects/esp-idf/en/stable/esp32/api-reference/peripherals/spi_master.html) (retrieved 2026-07-25).
- Microchip, [25AA256/25LC256 Datasheet](https://ww1.microchip.com/downloads/aemDocuments/documents/MPD/ProductDocuments/DataSheets/25AA256-25LC256-256K-SPI-Bus-Serial-EEPROM-20001822J.pdf) (retrieved 2026-07-25).

## 14. Facts, expected results and required measurements

- **FACT:** only values linked to a primary source.
- **EXPECTED:** calculate for the exact circuit and state assumptions.
- **MEASURED:** enter only instrument output from real hardware.
- **UNKNOWN:** leave unknown until evidence exists.
