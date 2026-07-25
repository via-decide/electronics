# KiCad Source Provenance

The editable source in this directory is derived from Raspberry Pi's official
**RP2350A Minimal KiCad reference design**, document RP-008295-DS-1:

<https://pip-assets.raspberrypi.com/categories/1214-rp2350/documents/RP-008295-DS-1-Minimal-KiCAD%20rp2350.zip>

Retrieved: 2026-07-25.

Imported source:

- the minimal `.kicad_sch` and `.kicad_pro` files;
- the RP2350 symbol library and symbol table;
- the project footprint library and footprint table.

Task 2 transformations:

- renamed the project and added Proto-0 title/revision metadata;
- identified U1 as the pin-compatible RP2354A A4 package;
- removed the external boot-flash role and assigned U3 as the physically
  separate W25Q256JVEIQ payload NOR;
- routed payload SPI to GPIO16-GPIO19 and fixed the flash in single-SPI mode;
- renamed USB, SWD, RUN and BOOTSEL nets to the repository contract;
- retained the reference core-regulator, clock, USB series-resistor and
  decoupling circuits;
- marked the input regulator and USB connector as DNP placeholders owned by
  Tasks 3 and 5;
- removed the obsolete USB Micro-B footprint from the imported local
  footprint library.

The embedded symbol definitions retain upstream library identifiers such as
`RP2350`, `W25Q128JVS`, `USB_B_Micro` and `NCP1117`. Top-level instances carry
the Proto-0 visible values and DNP status. This is deliberate for a
pin-compatible, reference-derived work-in-progress, not a claim that those
upstream parts are selected.

The rendered overview is a repository review aid. The `.kicad_sch` file is the
editable electrical source and must pass native KiCad ERC before Task 2 closes.
