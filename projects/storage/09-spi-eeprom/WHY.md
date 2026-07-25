# Why

A storage write is a protocol: address validation, write-enable, page geometry, busy polling, readback and integrity.


## Write protection boundary

`WREN` controls the write-enable latch. `WP#` protects status-register writes only when the status
register's WPEN bit enables that behavior; tying WP# high does not replace bounds checks, page checks,
busy polling or readback. The v1 demo does not enable block-protection bits.
