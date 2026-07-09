# Engineering Theory Knowledge Base

## Purpose

This document defines the theory layer for the electronics repository. It preserves the engineering reasoning behind firmware, hardware, validation, and production decisions so the repository functions as both a production codebase and an Embedded Systems Engineering Handbook.

## Repository Knowledge Model

Validation marker: `engineering_learning_repository_structure_v1`

Status: `ENGINEERING_KNOWLEDGE_BASE_STANDARDIZED`

```text
Engineering task
    ↓
Theory and first principles
    ↓
Implementation architecture
    ↓
Examples and validation
    ↓
Debugging and benchmarks
    ↓
Production guidance
    ↓
References and long-term knowledge preservation
```

The knowledge base separates concepts by responsibility instead of mixing all information into a single README. This reduces onboarding time, improves review quality, and makes each engineering decision traceable.

## Engineering Principles

Every feature document should explain the physical, mathematical, and architectural principles that make the implementation necessary:

| Principle | Required explanation |
| --- | --- |
| Physics | Sensor behavior, analog limits, noise, thermal drift, signal integrity, power integrity, EMC/EMI coupling. |
| Mathematics | Sampling, latency, queue depth, bandwidth, error budgets, timing bounds, reliability estimates. |
| Hardware | Peripheral ownership, electrical interfaces, ADC/I2C/SPI/UART behavior, memory and DMA constraints. |
| Firmware | Driver contracts, ISR rules, RTOS scheduling, watchdog policy, persistence, telemetry boundaries. |
| Production | Calibration, diagnostics, field update safety, manufacturing variation, observability, traceability. |

## Mathematical Reasoning Standard

Engineering claims should be tied to equations where possible. Examples include:

```text
Nyquist condition:       F_s > 2 · F_max
Sample period:          T_s = 1 / F_s
Queue residence time:   T_queue = Q_depth / event_rate
Throughput margin:      margin = consumer_rate - producer_rate
Average current:        I_avg = ((I_active · T_active) + (I_sleep · T_sleep)) / (T_active + T_sleep)
Timing validity:        deadline_met = C_exec + Jitter < T_period
```

Equations are not decorative; they define acceptance criteria and explain why a design fails or succeeds under load.

## Task-to-Documentation Rule

Every new engineering task must add or update the following documentation areas:

1. `docs/theory.md` for principles and design motivation.
2. `docs/implementation.md` for firmware and hardware architecture.
3. `docs/debugging.md` for failure diagnosis.
4. `docs/production.md` for deployment and field constraints.
5. `docs/benchmarks.md` for measurement methodology and reproducible results.
6. `docs/references.md` for primary sources.
7. `examples/` for runnable usage patterns when implementation code exists.
8. `tests/` for separated validation categories.
9. `diagrams/` for architecture, state, data-flow, timing, and PCB context.
10. `assets/` for supporting captures, measurements, images, and datasheets.

## Naive Documentation Failure Modes

| Naive approach | Failure mechanism |
| --- | --- |
| Put everything in `README.md` | Theory, debugging, production, examples, and validation become intermixed and hard to maintain. |
| Document only APIs | Contributors learn how to call code but not why the design is safe or how to validate it. |
| Keep measurements in issues | Benchmark context disappears from the repository history and cannot be reproduced. |
| Store diagrams ad hoc | Architecture knowledge becomes inconsistent and difficult to review. |
| Omit references | Designs cannot be audited against official datasheets, standards, or vendor guidance. |

## Required Feature Learning Document Shape

Feature-specific learning documents, such as ESP32 ADC/DMA material, should follow a complete teaching order:

```text
Title → Overview → Engineering Problem → Why Naive Approaches Fail
→ Engineering Principles → Mathematical Foundation → Hardware Architecture
→ Firmware Architecture → State Machine → Data Flow → ESP-IDF Components
→ Memory Model → RTOS Interaction → Performance Analysis → Design Trade-offs
→ Failure Modes → Debugging Strategy → Testing Methodology
→ Production Considerations → Related Topics → Implementation Task → Key Takeaways
```

This order teaches first principles before implementation details and preserves the original task as an engineering exercise.


## Subsystem Theory by Validation ID

### `esp32_core_installation_v1` — Toolchain and Environment

The toolchain smoke test validates that the ESP-IDF build system, partition table, and flash procedure produce a bootable image from a clean repository checkout. No domain-specific theory applies; the pass criterion is reproducibility of the build-flash-monitor cycle.

---

### `esp32_hall_diagnostic_v1` — Silicon Diagnostics and Reset Classification

ESP32 reset sources are enumerable via `esp_reset_reason()`. The firmware must distinguish brownout (`ESP_RST_BROWNOUT`), watchdog (`ESP_RST_TASK_WDT`, `ESP_RST_INT_WDT`), panic, and software resets. The Hall sensor peripheral reads an internal magnetic field proportional to chip package stress; it is used here as a silicon-availability probe, not a measurement instrument.

---

### `nltm_sensor_linearization_v1` — Nonlinear Transfer Mapping

Real sensors exhibit nonlinear transfer functions. Calibration stores gain/offset coefficients in NVS with a versioned schema (magic `0x314C4143`, CRC32):

```
V_eng = gain × V_raw + offset
```

CRC verification on boot rejects corrupted blobs and falls back to safe defaults (`gain=1.0`, `offset=0.0`).

---

### `logic_level_shift_v2` — Voltage Domain Interfacing

ESP32 GPIOs have an absolute maximum of 3.6V. Interfacing with 5V sensors requires bidirectional level shifters (TXS0108E). Signal integrity degrades if the shifter output impedance creates RC time constants that violate setup/hold timing.

```
V_GPIO_max = 3.3V + margin < V_abs_max = 3.6V
```

---

### `ledc_pwm_matrix_v1` — Hardware PWM Generation

LEDC generates PWM via hardware timer and duty comparator — no `delay()` loops. For 5 kHz:

```
T_period = 200 µs,  Resolution = log2(APB_CLK / F_target) bits
```

---

### `cap_touch_iir_v1` — Capacitive Touch with IIR Filtering

Touch pad raw counts pass through an IIR low-pass filter:

```
y[n] = α × x[n] + (1 − α) × y[n−1]
```

Small α rejects noise but increases response latency. Threshold must separate baseline from valid touch deflections.

---

### `freertos_dual_core_v1` — Dual-Core Task Isolation

Acquisition tasks pin to Core 0, networking to Core 1. Bounded queue absorbs burst timing:

```
Q_residence = Q_depth / event_rate
```

Queue overflow = consumer cannot keep up. Watchdog must distinguish lockup from network reconnection delay.

---

### `deep_sleep_rtc_retention_v2` — Low-Power Sensor Node Lifecycle

Cycle: wake → sample → bounded telemetry → deep sleep unconditionally. Battery life dominated by sleep current:

```
I_avg = (I_active × T_active + I_sleep × T_sleep) / (T_active + T_sleep)
```

With I_active ≈ 80 mA, I_sleep ≈ 15 µA, T_sleep = 300s. RTC memory retains counters; main SRAM does not survive deep sleep.

---

### `nvs_wear_leveling_v1` — Flash Wear and Schema Integrity

NVS uses page-based wear leveling. Write frequency must be bounded:

```
max_writes = page_count × entries_per_page × erase_cycles_per_sector
```

Corrupted blobs (bad magic, CRC mismatch) are rejected; safe defaults loaded.

---

### `hw_timer_isr_v1` — Hardware Timer ISR Discipline

GPTimer ISR must only timestamp and enqueue — no heap alloc, no logging, no FP. Worker task does control logic:

```
deadline_met = C_isr + C_queue_send < T_period
missed_deadlines = queue_overflow_count
```

---

### `bod_panic_suppression_v1` — Brownout Detection

BOD resets on VDD drop. Firmware classifies reset reasons, persists fault counters:

```
V_supply − I_peak × (R_cable + R_trace) > V_BOD_threshold
```

Disabling BOD is unsafe. Design the supply to handle Wi-Fi transmit bursts.

---

### `ulp_fsm_assembly_v1` — ULP Coprocessor Threshold Polling

ULP FSM runs from RTC memory during deep sleep, polling ADC. Wakes main cores only on threshold. No C runtime, no heap, no FreeRTOS — assembly-level instruction set at 8 MHz RTC_FAST_CLK.

---

### `i2s_dma_audio_v1` — Audio DMA Ping-Pong Buffering

Ping-pong buffers: DMA fills one while app processes the other. At 44.1 kHz stereo 16-bit: 176,400 B/s. Underrun = app fails to provide next buffer before DMA exhausts current one.

---

### `adc_dma_nyquist_v1` — Continuous ADC and Nyquist Compliance

`adc_continuous` driver owns cadence — no `analogRead()`. At F_s = 2 kHz, F_max = 1 kHz by Nyquist, recommended ≤ 800 Hz. DMA callbacks deliver 512-byte frames. DSP/MQTT deferred to separate task via queue.

---

### `spi_dma_throughput_v2` — SPI DMA Throughput

SPI DMA decouples CPU from byte clocking. At 40 MHz SPI clock: theoretical 5 MB/s. CPU utilization during DMA should be near zero; polling-based transfer is a bug.

---

### `esp32_ota_bootstrap_v2` — Rollback-Safe OTA

Writes to inactive partition. After reboot, app must confirm validity via `esp_ota_mark_app_valid_cancel_rollback()` or bootloader reverts. Bad image must never become permanently active.

---

### `esp_now_p2p_v2` — Peer-to-Peer Without Infrastructure

ESP-NOW transmits directly between peers without Wi-Fi router. Latency bounded by 802.11 channel access time. Protocol is unreliable — packet loss under collision must be measured.

---

### `async_web_littlefs_v1` — Concurrent Serving and Acquisition

Async HTTP serves compressed LittleFS assets on a separate core. Flash I/O must not block acquisition queue. LittleFS ops are not ISR-safe.

---

### `hw_crypto_aes_v2` — Hardware AES Validation

ESP32 hardware AES accelerator output must match NIST test vectors. CPU load during HW AES vs SW AES confirms accelerator is actually used.

---

### `mtls_x509_auth_v1` — Mutual TLS Authentication

Client cert + private key loaded from filesystem, never hardcoded. Private key must never appear in version control.

---

### `jtag_openocd_v1` — JTAG Debug Validation

Proves halt, inspect, resume without corrupting running state. Non-invasive debugging must not alter program behavior except at breakpoints.

---

### `tflm_wakeword_v2` — TinyML Inference Budget

Quantized 8-bit TFLM model. Must fit RAM and latency budgets:

```
RAM < available_SRAM,  latency = cycles / CPU_freq < deadline
```

---

### `mcpwm_bldc_foc_v1` — BLDC Dead-Time Enforcement

MCPWM generates complementary PWM. Dead-time prevents shoot-through:

```
t_dead > t_off_max(high) − t_on_min(low)
```

Validate before connecting motor.

---

### `twai_can_differential_v1` — CAN Bus Signaling

TWAI + external transceiver (SN65HVD230). Monitor TEC/REC error counters under load. Requires 120Ω termination at each bus end.

---

### `lvgl_dma_pingpong_v2` — Display DMA Double Buffering

LVGL renders into buffer A while DMA sends buffer B to display. Tearing = overlap. Display priority must be lower than acquisition and safety tasks.
