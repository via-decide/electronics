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

- [ ] LED polarity is identified and a measured resistor is in series
- [ ] Meter lead remains in the voltage/resistance jack unless a powered-down series-current setup is reviewed

Any unchecked item blocks power-up.
