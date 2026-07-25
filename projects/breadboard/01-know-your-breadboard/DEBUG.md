# Debug

Use this order and stop when a stage is wrong:

Power → ground → orientation → continuity → idle voltage → clock → data → protocol → firmware → output

| Symptom | Check first | Evidence |
| --- | --- | --- |
| no output | 3.3 V and common GND | TP supply measurement |
| unstable output | floating pin, split rail, loose jumper | continuity and idle voltage |
| wrong device/data | mirrored IC, wrong address/CS, pin mismatch | pin 1 photo requirement and capture |
| firmware log but no physical action | load path and GPIO voltage | GPIO/load measurements |
| intermittent bus | decoupling, ground lead, pull-up/clock timing | supply and logic capture |
