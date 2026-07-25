# Why

Storage is not saving bytes. A usable record needs geometry, integrity, commit ordering, redundant metadata and recovery.


## Immutable v1 object

The packed on-media header is little-endian for this ESP32-only v1 demonstration:

| Field | Width | Rule |
| --- | ---: | --- |
| magic | 32 bits | `0x455A4631` identifies this teaching record |
| schema version | 16 bits | exactly `1` |
| generation | 32 bits | monotonically selects the newest valid copy |
| payload length | 16 bits | at most 128 bytes in v1 |
| payload CRC32 | 32 bits | CRC-32 over exactly `payload length` bytes |
| header CRC32 | 32 bits | CRC-32 over fields from magic through payload CRC |
| commit state | 8 bits | `0x7F` prepared, then one-way programmed to `0x3F` committed |

Header and payload are verified before the commit byte changes. After commit, that record is immutable:
the next update erases and writes the other 4 KiB sector. Recovery accepts only committed copies whose
header and payload CRCs pass, then chooses the greater generation. A prepared higher generation is ignored.
This is a record demonstration, not a filesystem or a portable interchange format.
