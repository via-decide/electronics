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

- [ ] Adapter pin map and exact MX25L3233FM2I-08G marking are inspected
- [ ] CS# has a 10 kohm pull-up; WP# and HOLD# are tied high
- [ ] Write gate remains zero until JEDEC ID C2-20-16 and a dedicated blank lab part are confirmed

Any unchecked item blocks power-up.
