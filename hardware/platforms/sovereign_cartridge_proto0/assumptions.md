# Proto-0 Assumption Ledger

Retrieval date: 2026-07-25
Physical execution: not performed

## FACT

| ID | Statement | Source |
| --- | --- | --- |
| F-001 | RP2354A is a QFN-60 RP2350-family device with 2 MiB flash-in-package and 30 GPIO. | Raspberry Pi RP2350 datasheet |
| F-002 | The RP2354A flash die is a W25Q16JVWI connected to the dedicated QSPI pads; the pads remain externally available. | Raspberry Pi RP2350 datasheet |
| F-003 | A4 fixes most A2 errata, including the documented GPIO high-impedance defect; Proto-0 therefore excludes A2. | Raspberry Pi A4 announcement |
| F-004 | W25Q256JVEIQ is a 256 Mbit, 2.7-3.6 V, WSON-8 8x6 mm production-listed NOR device. | Winbond 2025 code-storage selection guide |
| F-005 | Raspberry Pi recommends ABM8-272-T3 and AOTA-B201610S3R3-101-T in its RP2350-family reference design. | Hardware design with RP2350 |

## DECISION

| ID | Statement | Consequence |
| --- | --- | --- |
| D-001 | RP2354A A4 is the sole Proto-0 controller. | Firmware boots from the in-package 2 MiB NOR; A2 stock is prohibited. |
| D-002 | W25Q256JVEIQ is payload storage, not boot storage. | Payload corruption or erase work cannot directly overwrite the RP2354A boot device. |
| D-003 | Payload NOR uses a dedicated user-SPI path, not the RP2354A XIP bus. | Full 32 MiB addressing and bus ownership are defined explicitly in Tasks 2 and 4. |
| D-004 | USB-C is a sink-only USB 2.0 device/service boundary. | USB host, source and Power Delivery modes are outside Proto-0. |
| D-005 | Proto-0 is one PCB with no removable flash socket. | “Cartridge” describes the product unit; flash is not user-removable. |

## EXPECTED — requires later validation

| ID | Statement | Validation owner |
| --- | --- | --- |
| E-001 | A correctly implemented RP2354A reference power and clock circuit should boot repeatably from internal flash. | Tasks 2, 3 and bench bring-up |
| E-002 | The external NOR should be independently discoverable and writable without changing boot-flash contents. | Tasks 4, 8 and bench storage tests |
| E-003 | USB service should enumerate as a device without enabling host, source or PD behavior. | Task 5 and USB validation |

## UNKNOWN / blocking

| ID | Unknown | Resolution |
| --- | --- | --- |
| U-001 | Total and transient 3.3 V current demand. | Task 3 power budget and measurement |
| U-002 | Final regulator, supervisor, protection parts and safe-shutdown energy. | Task 3 |
| U-003 | RP2354A and payload-SPI pin assignment, passive values and net names. | Task 2 |
| U-004 | SPI peripheral, ownership state machine and recovery timing. | Task 4 |
| U-005 | USB-C receptacle, CC, ESD and shield implementation. | Task 5 |
| U-006 | Received-part identity, A4 marking, flash JEDEC identity and counterfeit risk. | Task 6 and incoming inspection |
| U-007 | All voltages, currents, waveforms, timing margins and thermal behavior. | Physical validation only |

Unknown, expected or simulated results must never be promoted to `MEASURED` or
`BENCH_VERIFIED`.
