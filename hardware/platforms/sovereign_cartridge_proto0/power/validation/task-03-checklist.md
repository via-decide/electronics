# Task 3 Power-Safety Checklist

Status: `OPEN`.

## Repository contract

- [x] Power entry, regulator, hold-up and reset responsibilities are explicit.
- [x] Current allocations total 300 mA on `3V3`.
- [x] UVLO, OVP, current-limit, ramp and feedback equations are reproducible.
- [x] Hold-up energy is calculated with effective capacitance and efficiency
  derating.
- [x] Fail-stop energy is not misrepresented as flash-operation completion.
- [x] `FACT`, `DECISION`, `EXPECTED`, `MEASURED` and `UNKNOWN` claims are
  separated.
- [x] Procurement and real-hardware authorization remain blocked.

## Electrical source and review

- [ ] Replace the Task 3 DNP placeholder in editable KiCad source.
- [ ] Capture U4 eFuse, U2 buck, U5/U6 supervisors, support passives and the
  wired-AND `POWER_SAFE_N` to `RUN` path.
- [ ] Capture `VBUS_HOLD`, `POWER_SAFE_N` and eFuse-fault test points.
- [ ] Run native KiCad ERC with zero unwaived errors.
- [ ] Review eFuse divider tolerances, DMODE current limit, startup SOA and
  thermals.
- [ ] Simulate buck stability, load steps, startup and abrupt input removal.
- [ ] Review capacitor voltage/temperature derating against the 80 uF minimum.

## Physical evidence

- [ ] Current-limited first power-up is authorized by all Tasks 2-6.
- [ ] Measure pre-configuration input current below the Task 5 limit.
- [ ] Measure every current-budget mode and prove the 300 mA ceiling.
- [ ] Measure UVLO, OVP, inrush and short-circuit behavior.
- [ ] Measure `VBUS_HOLD`, `3V3`, `POWER_SAFE_N`, `RUN` and
  `PAYLOAD_SPI_CS_N` during abrupt input removal.
- [ ] Prove the maximum 25 us `RUN`-to-bus-quiescent allocation or increase
  hold-up energy.
- [ ] Repeat power cuts during payload read, page program, sector erase and
  metadata commit.
- [ ] Show that incomplete transactions are never exposed as committed.
- [ ] Record waveforms, instrument settings, board identity and environment.

## Gate rule

`task_03_power_safety_passed` remains false until every electrical-source and
physical-evidence item above passes. Calculation, simulation or documentation
alone cannot close the gate.
