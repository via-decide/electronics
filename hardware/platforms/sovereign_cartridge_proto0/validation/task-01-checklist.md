# Task 1 — Topology Freeze Checklist

Software-verifiable acceptance:

- [x] The exact controller is RP2354A A4.
- [x] Boot storage is the 2 MiB in-package W25Q16JVWI.
- [x] Payload storage is a separate W25Q256JVEIQ with 32 MiB capacity.
- [x] Payload storage does not share the XIP bus.
- [x] USB-C is frozen as USB 2.0 UFP/device and sink only.
- [x] SWD, RUN, BOOTSEL, rail, USB and payload-SPI test access is required.
- [x] Raw NAND, FPGA, battery, wireless, USB host/source and PD are excluded.
- [x] Tasks 2-6 own schematic, power, SPI, USB-C and sourcing decisions.
- [x] Real hardware, destructive writes and manufacturing release are disabled.
- [x] Facts, decisions, expected outcomes and unknowns are separated.
- [x] Machine-readable contract, schema, BOM, diagram and decision record exist.
- [x] Negative validator self-tests reject topology drift.

Not accepted by this task:

- schematic correctness;
- PCB layout, ERC or DRC;
- source availability or received-part authenticity;
- voltage, current, timing, signal-integrity, enumeration or storage results;
- any `BENCH_VERIFIED` claim.
