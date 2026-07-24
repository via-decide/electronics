# Before You Power

- [ ] Supply voltage measured or source confirmed before connection
- [ ] GND continuity confirmed
- [ ] No VCC-to-GND short
- [ ] MCU and peripheral share ground
- [ ] Logic voltage compatible
- [ ] Polarized parts oriented correctly
- [ ] Current limit or resistor configured
- [ ] Correct chip orientation
- [ ] 100 nF decoupling installed at each external IC
- [ ] Test points identified
- [ ] Only the documented 3.3 V rail is used
- [ ] No mains, battery or external high-current source is connected

## Project-specific blocking checks

- [ ] AO3400A adapter pin labels agree with the datasheet and continuity test
- [ ] Load is the bounded 3.3 V resistor/LED path; no motor, relay or external supply is connected
- [ ] 100 kohm gate pull-down is present before firmware starts

Any unchecked item blocks power-up.
