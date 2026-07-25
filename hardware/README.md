# Hardware

Hardware documentation captures board interfaces, power architecture, sensor wiring, protection circuits, mechanical constraints, and production hardware considerations.

Expected content:

- Board revisions and pin maps.
- Power tree and regulator limits.
- Sensor and connector wiring.
- Protection, filtering, and EMC/EMI notes.
- Calibration fixtures and manufacturing test interfaces.
- Links to diagrams, oscilloscope captures, photos, and datasheets.

## Frozen platforms

- [`platforms/sovereign_cartridge_proto0/`](platforms/sovereign_cartridge_proto0/README.md)
  is the post-v1 Sovereign Cartridge Task 1 topology contract. It freezes the
  RP2354A A4 controller, separate W25Q256JVEIQ payload NOR, USB device boundary
  and evidence gates while leaving schematic, power, SPI, USB and sourcing work
  to Tasks 2-6.
- [`platforms/w25n01jw_lab/`](platforms/w25n01jw_lab/README.md) is the gated
  1.8 V raw-NAND lab fixture for the later experimental FTL path.
