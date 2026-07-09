# Authoritative research and traceability policy

This repository prioritizes engineering understanding, validation, and traceability over feature count. Documentation must be written from primary engineering sources, measured evidence, and repository implementation artifacts.

## Source hierarchy

1. Standards bodies and specifications: IEEE, IEC, JEDEC, IPC, NIST, IETF RFCs, USB-IF, Bluetooth SIG, and RISC-V International.
2. Official vendor engineering documentation: Espressif, STMicroelectronics, Microchip, Raspberry Pi, Arm, Texas Instruments, Analog Devices, NXP, Infineon, Renesas, Silicon Labs, Nordic Semiconductor, and semiconductor datasheets or reference manuals.
3. University course material and engineering textbooks from recognized institutions or authors.
4. Repository measurements: validation reports, benchmark logs, oscilloscope captures, logic-analyzer traces, manufacturing records, and regression results.

AI-generated articles, marketing pages, community forums, and videos are not primary evidence. They may only be used as discovery aids and must be replaced by primary references before a claim is accepted.

## Claim classification

Every major claim and decision must state whether it is:

- **Established engineering practice** supported by standards, textbooks, derivations, or repeatable measurements.
- **Vendor recommendation** supported by an official datasheet, reference manual, errata, application note, hardware-design guide, SDK manual, or programming guide.
- **Daxini implementation decision** supported by repository source code, examples, validation, benchmarks, or production constraints.
- **Future proposal** that is not yet production behavior.

## Conflict resolution

When sources disagree, preserve the conflict explicitly. Prefer the device-specific datasheet and errata for electrical limits, the reference manual for peripheral behavior, the SDK manual for driver API constraints, and standards documents for protocol conformance. Do not invent timing, current, voltage, impedance, memory, endurance, or throughput values.

## Minimum documentation links

A production-ready page should link theory, implementation, example, validation, benchmark, report, source code, and references. Missing links are allowed only when marked as gaps in the maturity table.
