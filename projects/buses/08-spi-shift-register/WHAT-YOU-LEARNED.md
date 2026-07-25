# What You Learned

The shift register comes before flash because its output is visible. RCLK is a storage-register latch, not a generic SPI chip-select.

Completion proof: Captured or manually traced clock/data/latch transitions agree with the displayed output byte.
