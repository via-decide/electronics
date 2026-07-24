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

- [ ] Device marking is 25LC256-I/P, not the I2C 24LC256
- [ ] CS# has a 10 kohm pull-up; WP# and HOLD# are tied high
- [ ] Only dedicated test addresses 0x0100 through 0x0183 will be written

Any unchecked item blocks power-up.
