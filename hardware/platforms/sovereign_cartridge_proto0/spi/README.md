# Task 4 SPI Ownership

Status: `SPI_OWNERSHIP_DESIGN_IN_PROGRESS`.

This directory freezes the first reviewable controller, command, ownership and
recovery contract for the physically separate W25Q256JVEIQ payload NOR. It
now includes a transport-agnostic C owner and negative host-test suite. It does
not close Task 4: the RP2354A SPI0 adapter, link-boundary enforcement,
logic-analyzer captures and destructive physical fault-injection evidence
remain open.

## Frozen interface

| Function | Proto-0 decision |
| --- | --- |
| Controller | RP2354A `SPI0` |
| CIPO | GPIO16 / `SPI0_RX` |
| CS_N | GPIO17, owner-controlled SIO output with external 10 kohm pull-up |
| SCK | GPIO18 / `SPI0_SCK` |
| COPI | GPIO19 / `SPI0_TX` |
| Format | Mode 0, 8-bit, MSB first |
| Clock | 24 MHz requested ceiling; actual nonzero rate must not exceed it |
| Transfer engine | Polled and blocking for Proto-0 |
| Addressing | Dedicated four-byte opcodes; no persistent four-byte mode |
| Owner | One serialized `PAYLOAD_STORAGE_SERVICE` |

GPIO17 is physically capable of `SPI0_CSn`, but Proto-0 uses it as a
software-controlled GPIO. The owner must hold CS low across one complete
command, address and data frame, then return it high. No other task, core, ISR,
debug path or library may touch SPI0 or these four GPIOs directly.

The in-package boot flash remains on `IN_PACKAGE_BOOT_QSPI`. Payload traffic
never uses the boot XIP bus.

## Command boundary

The allowlist is intentionally small:

- identity and status: `9F`, `05`, `35`, `15`;
- cleanup: `06`, `04`;
- full-range standard-SPI access: `13`, `12`, `21`, `DC`;
- recovery-only reset sequence: `66`, then `99`, only with `BUSY=0` and
  suspend clear.

Chip erase (`C7`/`60`), 24-bit payload access, status-register writes,
persistent four-byte mode, Quad SPI and QPI are prohibited. A 32 MiB device
cannot be covered safely by 24-bit commands without additional global mode
state, so Proto-0 always transmits four address bytes for array access.

Page program requests are limited to 1-256 bytes and may not cross a 256-byte
page. Sector and block erases require 4 KiB and 64 KiB alignment respectively.
All address-plus-length checks occur in a wider integer before conversion.

## Ownership and recovery

```text
typed callers
  -> bounded request queue
  -> PAYLOAD_STORAGE_SERVICE
  -> manual CS + SPI0
  -> W25Q256JVEIQ
```

Only one request can be active. Queued work may be cancelled; an active frame
cannot. After WEL is confirmed, the owner must either issue write-disable or
continue the already-validated mutation. Page program and erase are never
automatically retried after timeout or reset because the physical outcome may
be unknown.

Every mutation requires power-safe state, verified identity, `BUSY=0`,
`WRITE_ENABLE`, confirmed `WEL=1`, valid bounds and valid alignment. Success
requires bounded completion, `WEL=0`, and full read-back verification. This
confirms the device operation only; later transaction tasks decide whether
payload data is committed.

The flash datasheet warns that software reset can corrupt data if program or
erase is active. Therefore `66` + `99` is recovery-only and requires
`BUSY=0`, suspend clear, power-safe state and exclusive ownership.

See [`spi-ownership.svg`](spi-ownership.svg) for the owner and recovery flow.

## Host implementation

[`payload_storage_service.h`](../../../../firmware/storage/include/storage/payload_storage_service.h)
exposes only typed operations, an opaque service allocation and structured
health records. The implementation owns a depth-eight queue, copies page
program input into owner memory, permits cancellation only while queued and
executes one request at a time. Its injected transport is the future hardware
adapter boundary; no RP2354A SDK, register or real-flash access is enabled by
this PR.

The host suite uses a failure-injectable NOR model to cover bounds and overflow,
page crossing, erase alignment, queue saturation, active cancellation,
re-entrancy, all forbidden opcodes, unsafe power/status/reset conditions,
identity mismatch, read timeout, full program/erase read-back, fault locking,
and reset/timeout mutation outcomes. It asserts that a failed mutation opcode
is emitted once and is never replayed by recovery.

## Artifacts

- [`spi-ownership.json`](spi-ownership.json) is the machine contract.
- [`command-policy.csv`](command-policy.csv) is the reviewable opcode allowlist.
- [`assumptions.md`](assumptions.md) separates facts, decisions, expectations,
  measurements and unknowns.
- [`validation/task-04-checklist.md`](validation/task-04-checklist.md) defines
  the open implementation and physical gate.

Validate with:

```sh
python3 tools/validate_sovereign_cartridge_spi_ownership.py --strict --self-test
cmake --preset host
cmake --build --preset host
ctest --preset host --output-on-failure
```

Do not set `task_04_spi_ownership_passed` until the exclusive-owner
hardware binding, timing captures and reset/power-cut evidence all pass.
