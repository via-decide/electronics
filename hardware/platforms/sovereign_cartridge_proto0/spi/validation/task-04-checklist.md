# Task 4 SPI Ownership Checklist

Status: `OPEN`.

## Repository contract

- [x] SPI0 instance and GPIO16-GPIO19 mapping are explicit.
- [x] Boot XIP and payload storage remain physically separate.
- [x] One exclusive owner and one-inflight-request rule are explicit.
- [x] Manual chip-select framing and reset-safe idle state are explicit.
- [x] Full-range four-byte opcodes are allowlisted.
- [x] Chip erase, 24-bit array access, persistent address mode and Quad/QPI
  modes are prohibited.
- [x] Program/erase bounds, alignment, WEL, timeout and read-back rules are
  explicit.
- [x] Reset during mutation produces an unknown outcome and no automatic
  mutation retry.
- [x] Facts, decisions, expectations, measurements and unknowns are separated.

## Firmware proof

- [ ] Implement a single `PAYLOAD_STORAGE_SERVICE` owner.
- [ ] Prevent direct SPI0 SDK/register use outside the owner at review and
  link boundaries.
- [ ] Add typed queue requests with depth and one-inflight enforcement.
- [ ] Add unit tests for bounds, overflow, page crossing and erase alignment.
- [ ] Add negative tests for every forbidden opcode.
- [ ] Add state-transition, cancellation, timeout and recovery tests.
- [ ] Prove reset recovery never replays a mutation automatically.
- [ ] Prove full read-back verification for program and erase.
- [ ] Preserve structured request/error counters without logging payload data.

## Physical evidence

- [ ] Verify JEDEC identity `EF 40 19` on the assembled board.
- [ ] Capture TP11-TP14 traces for probe, read, program and both erase sizes.
- [ ] Measure actual clock and Mode 0 setup/hold behavior.
- [ ] Confirm CS is high during boot, reset and power-fault entry.
- [ ] Prove the maximum 25 us `RUN`-to-bus-quiescent allocation.
- [ ] Inject reset during read, page program, sector erase and block erase.
- [ ] Show timeouts enter recovery or fault-lock without automatic mutation
  retry.
- [ ] Repeat power cuts and show incomplete work is not exposed as committed.

## Gate rule

`task_04_spi_ownership_passed` remains false until every firmware-proof and
physical-evidence item above passes. Documentation, simulation or host-only
tests cannot close the gate.
