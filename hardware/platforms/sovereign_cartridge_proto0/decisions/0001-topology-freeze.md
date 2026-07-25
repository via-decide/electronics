# Decision 0001 — Freeze Proto-0 Topology

Status: accepted for Task 1
Date: 2026-07-25

## Context

The Electronics From Zero v1 path ends with crash-safe NOR records and links
forward into cartridge and controller engineering. The next phase needs a
physical target that is specific enough for schematic, power, bus, USB and BOM
review without pretending those downstream contracts are already complete.

## Decision

Use RP2354A A4 as the controller and its in-package 2 MiB flash only for boot
firmware. Add one W25Q256JVEIQ as a physically separate 32 MiB payload store on
a dedicated user-SPI path. Make Proto-0 a single USB-C-powered USB 2.0 device
board with SWD/RUN/BOOTSEL and required rail/bus test access.

Keep hardware execution and destructive writes disabled.

## Alternatives rejected for Proto-0

- **RP2350A plus external boot flash:** adds a second externally assembled boot
  dependency and weakens physical separation between boot and payload roles.
- **Use W25Q256JV on XIP CS1:** couples payload traffic to the boot XIP fabric
  and its address/mode constraints. Proto-0 uses a user-SPI peripheral instead.
- **Raw NAND:** requires ECC, bad-block and translation-layer work that belongs
  to the later Task 20 follow-on.
- **A2 silicon:** carries errata that A4 was selected to avoid.
- **USB host/source or USB-PD:** expands power and compliance scope without
  serving the Proto-0 service/backup objective.
- **Removable socketed flash:** increases connector, hot-plug and integrity
  scope before the first soldered reference platform is validated.

## Consequences

Tasks 2-6 now receive an unambiguous block boundary. They must fill in the
schematic, power safety, SPI ownership, USB-C implementation and sourceable BOM
without changing the frozen controller, payload flash or device-only USB role.
A topology change requires a new decision record and validator update.
