# What You Learned

UART moves bits. A frame adds meaning: magic, sequence, length, payload and CRC.

Completion proof: The receiver validates magic, length and CRC before printing the payload.
