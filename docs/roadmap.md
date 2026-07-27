# Repository Roadmap

## Objective

Evolve the repository into a reusable engineering platform that supports learning, implementation, validation, and long-term maintenance.

## Documentation Maturity Stages

| Stage | Definition | Current focus |
| --- | --- | --- |
| 1. Structure | Canonical folders and repository-level README exist. | Complete. |
| 2. Coverage | Every implementation has theory, implementation, debugging, production, benchmark, and reference coverage. | In progress. |
| 3. Examples | Each subsystem has runnable minimal and production examples. | In progress. |
| 4. Validation | Hardware, stress, performance, and integration procedures are executable and repeatable. | In progress. |
| 5. Evidence | Measurements, captures, photos, and benchmark records are linked to documentation. | Planned. |
| 6. Production | Deployment, manufacturing, calibration, OTA, security, and certification procedures are complete. | Planned. |

## Priority Backlog

1. Add ESP32 example projects for ADC DMA, FreeRTOS task isolation, MQTT, OTA, deep sleep, I2C recovery, and timers.
2. Add editable diagrams for boot flow, ADC pipeline, task topology, MQTT state machine, OTA lifecycle, memory layout, interrupt flow, DMA pipeline, power architecture, and signal path.
3. Add hardware-validation templates for oscilloscope, logic analyzer, power analysis, and long-duration testing.
4. Add benchmark records for RAM, flash, CPU, timing, latency, throughput, power consumption, boot time, sampling accuracy, and network performance.
5. Expand platform support for STM32, Raspberry Pi, Linux tooling, and power electronics.

## Sovereign Cartridge post-v1 hardware-validation path

The ordered path begins only after Electronics From Zero v1:

1. **Topology freeze — complete:** RP2354A A4 + W25Q256JVEIQ Proto-0 boundary,
   USB device/service role, debug/test access and no-hardware gates.
2. **Schematic — in progress:** pin/net contract and reference-derived KiCad
   capture added; repository structural ERC passes. Native KiCad ERC,
   TP1-TP14 source capture and electrical review remain blocking.
3. **Power safety — in progress:** protected and reverse-isolated VBUS hold-up,
   3.3 V conversion, wired-AND reset supervision, current allocation and
   fail-stop calculations added; KiCad capture, native ERC, simulation and
   physical power-cut evidence remain blocking.
4. SPI ownership.
5. USB-C service.
6. BOM and sourcing.
7. Identity and schema.
8. Protocol.
9. littlefs block device.
10. Immutable objects.
11. SHA-256 package identity.
12. Dual manifests.
13. Transaction states.
14. Error codes.
15. Desktop backup, restore and verify.
16. Power-cut harness.
17. 10,000 interruption/recovery cycles.
18. Pogo-pad fixture.
19. First custom PCB and enclosure.
20. Raw-NAND and experimental FTL follow-on.

Task 1's contract is
[`hardware/platforms/sovereign_cartridge_proto0/topology.json`](../hardware/platforms/sovereign_cartridge_proto0/topology.json).
Task 2's in-progress contract is
[`hardware/platforms/sovereign_cartridge_proto0/schematics/schematic.json`](../hardware/platforms/sovereign_cartridge_proto0/schematics/schematic.json).
Task 3's in-progress contract is
[`hardware/platforms/sovereign_cartridge_proto0/power/power-safety.json`](../hardware/platforms/sovereign_cartridge_proto0/power/power-safety.json).
Downstream tasks must not be marked complete by documentation-only or simulated
evidence.
