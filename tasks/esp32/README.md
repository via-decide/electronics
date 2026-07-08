# ESP32 Master Validation Tasks

This directory contains one task file per validation ID in `validation_matrix.yaml`. Each task defines the engineering risk, source mapping, required hardware, test method, pass metric, and evidence links for one subsystem in the ESP32 production validation stack.

## Master Validation

Run:

```sh
tasks/esp32/run_master_validation.sh \
  --repo=via-decide/electronics \
  --board=esp32 \
  --framework=arduino,esp-idf \
  --domains=core,peripherals,rtos,power,dma,networking,security,industrial,edge \
  --validation_matrix=tasks/esp32/validation_matrix.yaml \
  --report=reports/esp32_master_validation.md
```

The script verifies matrix/task/source consistency and generates the master report.
