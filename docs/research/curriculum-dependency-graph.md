# Curriculum Dependency Graph

```mermaid
flowchart TD
  A[Electricity] --> B[Breadboard]
  B --> C[Measurement]
  C --> D[GPIO and switching]
  D --> E[Analog measurement]
  E --> F[UART]
  F --> G[I2C]
  G --> H[SPI]
  H --> I[EEPROM]
  I --> J[NOR flash]
  J --> K[Integrity]
  K --> L[Crash safety]
  L --> M[Raw NAND]
  M --> N[ECC and mapping]
  N --> O[Storage controller]
```

No NAND, PCIe or controller RTL entry path bypasses power, measurement, synchronous buses,
integrity and recovery. The first ten projects stop at crash-safe NOR; the existing SSD lab
continues through NAND, ECC, FTL and controller behaviour.
