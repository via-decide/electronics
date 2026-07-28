# Task 4 Evidence Status

Retrieval date: 2026-07-28
Physical execution: not performed

## FACT

- RP-series microcontrollers expose two PrimeCell SSP SPI instances.
- RP2350 GPIO16, GPIO17, GPIO18 and GPIO19 support `SPI0_RX`, `SPI0_CSn`,
  `SPI0_SCK` and `SPI0_TX`.
- W25Q256JV-IQ reports JEDEC identity `EF 40 19`, contains 32 MiB, uses
  256-byte pages, 4 KiB sectors and 64 KiB blocks, and supports Mode 0 and
  Mode 3 standard SPI.
- Dedicated four-byte opcodes `13`, `12`, `21` and `DC` address the full
  device without depending on persistent four-byte-address mode.
- Maximum cited operation times are 3 ms for page program, 400 ms for
  4 KiB sector erase and 2,000 ms for 64 KiB block erase.
- The flash requires at least 20 us after valid power before the first read and
  5 ms before program, erase or status-register mutation.
- The software reset sequence can terminate an internal operation; the
  manufacturer warns of corruption if reset is accepted while program or
  erase is active.

## DECISION

- Payload storage uses `SPI0` only. The in-package boot QSPI bus is not shared.
- GPIO17 is controlled as SIO by the exclusive owner so CS remains asserted
  across an entire command frame and returns high after each command.
- Proto-0 uses Mode 0, 8-bit, MSB-first, polled blocking transfers with a
  requested 24 MHz ceiling.
- `PAYLOAD_STORAGE_SERVICE` is the only SPI0 owner. Other clients submit typed
  requests through a depth-eight queue; only one request can be active.
- Runtime array access uses dedicated four-byte opcodes. Persistent address
  mode, 24-bit payload access, Quad SPI, QPI, status writes and chip erase are
  prohibited.
- Mutations require WEL confirmation, bounded BUSY polling and complete
  read-back verification.
- Mutations are never replayed automatically after timeout, reset or an
  unknown physical outcome.

## EXPECTED

- A single blocking owner is expected to eliminate CS framing races and
  cross-core SPI reconfiguration.
- At the 24 MHz requested ceiling, the raw serial rate is 3,000,000 bytes/s
  and a 32 MiB scan would require at least 11.19 seconds before protocol and
  software overhead.
- Manual CS plus the external pull-up is expected to leave the payload NOR
  inactive during RP2354A reset.
- Bounded command-specific timeouts are expected to distinguish a slow valid
  operation from a locked or electrically failed bus.

Expected statements are design predictions, not firmware or bench evidence.

## MEASURED

`NONE`.

No clock, waveform, latency, concurrency, reset, power-cut, identity,
read-back, timeout or recovery behavior has been measured.

## UNKNOWN

- Actual SPI0 clock selected from the production peripheral clock.
- Rise/fall time, ringing, setup/hold margin and maximum reliable frequency on
  the eventual PCB.
- Whether the 24 MHz ceiling must be reduced after layout and waveform review.
- Maximum delay from `RUN` assertion to SCK/COPI/CS becoming quiescent.
- Real page-program and erase distributions across lot, voltage and
  temperature.
- Queue latency, starvation behavior and owner scheduling implementation.
- Payload state after reset or input loss during an internal mutation.
- Higher-level commit, journal and recovery semantics owned by later tasks.
- Every physical result.

## Gate

Task 4 remains open. The interface and ownership contract passes repository
validation, but no owner implementation, host proof, logic trace or physical
fault evidence exists.
