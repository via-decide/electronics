#!/usr/bin/env python3
"""
Append real, differentiated engineering content to the global docs.
Each section is specific to its validation ID — no copy-paste.
"""
import os

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def append(path, content):
    with open(os.path.join(REPO, path), 'a') as f:
        f.write(content)
    print(f"  appended to {path}")

# ─── theory.md ────────────────────────────────────────────
print("theory.md")
append('docs/theory.md', """
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
""")


# ─── debugging.md ─────────────────────────────────────────
print("debugging.md")
append('docs/debugging.md', """
## Subsystem Debugging Playbooks

### `adc_dma_nyquist_v1`
- **Symptoms**: Missed samples, aliased waveforms, inconsistent callback intervals.
- **First checks**: Verify F_s > 2×F_max. Check DMA buffer alignment. Confirm no `analogRead()` in loop.
- **Tools**: Oscilloscope on ADC input, ESP monitor for callback timestamps.

### `freertos_dual_core_v1`
- **Symptoms**: Queue overflow counters increment, stale data in telemetry, watchdog resets.
- **First checks**: Verify task core affinity (`xTaskCreatePinnedToCore`). Check queue depths and consumer priority.
- **Tools**: FreeRTOS trace facility, `uxTaskGetStackHighWaterMark()`, task runtime stats.

### `deep_sleep_rtc_retention_v2`
- **Symptoms**: Counter resets to zero after wake, device does not re-enter sleep.
- **First checks**: Verify variable is in `RTC_DATA_ATTR` section. Check wake reason with `esp_sleep_get_wakeup_cause()`. Confirm sleep call is unconditional (no early return paths).
- **Tools**: Current probe on supply rail, ESP monitor for boot/wake logs.

### `nvs_wear_leveling_v1`
- **Symptoms**: CRC failure on boot, calibration defaults loaded unexpectedly.
- **First checks**: Verify blob struct packing (`__attribute__((packed))`), magic number, schema version. Check if writes are rate-limited.
- **Tools**: `nvs_get_stats()` for page utilization, NVS partition dump.

### `hw_timer_isr_v1`
- **Symptoms**: Non-zero missed deadline counter, jitter in control output.
- **First checks**: Verify ISR is IRAM-safe (no flash access). Check worker task priority. Ensure ISR does no heap allocation or logging.
- **Tools**: GPIO toggle in ISR + oscilloscope, queue overflow counter.

### `bod_panic_suppression_v1`
- **Symptoms**: Boot loops, ESP_RST_BROWNOUT in reset reason, correlation with Wi-Fi activity.
- **First checks**: Measure supply voltage during Wi-Fi TX bursts (oscilloscope on 3.3V rail). Check cable resistance, bulk/bypass capacitors.
- **Tools**: Oscilloscope on VDD, NVS fault counters, `esp_reset_reason()`.

### `mqtt_telemetry` (used by `mtls_x509_auth_v1`, `esp_now_p2p_v2`)
- **Symptoms**: Connection drops, messages not published, TLS handshake failure.
- **First checks**: Verify certificate paths exist on filesystem. Check broker hostname/port. Confirm private key is not hardcoded (grep source for PEM headers).
- **Tools**: `openssl s_client` from host to verify broker cert chain, MQTT broker logs.

### `i2c_recovery` (used by `cap_touch_iir_v1`)
- **Symptoms**: SDA or SCL held low, repeated I2C timeout errors.
- **First checks**: Measure SDA/SCL with logic analyzer. Check pull-up resistor values. Verify sensor power sequencing.
- **Tools**: Logic analyzer on SDA/SCL, GPIO bit-bang recovery (9 SCL pulses + STOP).

### `ota_manager` (used by `esp32_ota_bootstrap_v2`)
- **Symptoms**: Device stuck on old firmware, rollback counter incrementing, image marked invalid.
- **First checks**: Verify health check passes before `esp_ota_mark_app_valid_cancel_rollback()`. Check partition table for two OTA slots. Inspect image header integrity.
- **Tools**: `esp_ota_get_running_partition()`, bootloader log level, partition table dump.

### `jtag_openocd_v1`
- **Symptoms**: Cannot halt, GDB connection refused, register corruption after resume.
- **First checks**: Verify JTAG pinout matches board. Check OpenOCD config file target. Ensure flash breakpoints don't exceed hardware limit.
- **Tools**: OpenOCD log level, `monitor reset halt`, `info threads`.
""")


# ─── benchmarks.md ────────────────────────────────────────
print("benchmarks.md")
append('docs/benchmarks.md', """
## Subsystem Benchmark Specifications

### `adc_dma_nyquist_v1`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Sample rate | 2000 Hz ± 1% | Oscilloscope on ADC input + callback timestamp delta |
| Callback jitter | < 50 µs | Standard deviation of callback intervals over 10,000 samples |
| Nyquist margin | F_max ≤ 800 Hz | Signal generator sweep, verify no aliasing |

### `freertos_dual_core_v1`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Queue overflow count | 0 | Monitor counter during 60s Wi-Fi stress test |
| Acquisition task CPU | < 15% Core 0 | `vTaskGetRunTimeStats()` |
| Watchdog false positives | 0 | Count during network reconnection cycles |

### `deep_sleep_rtc_retention_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Sleep current | ≤ 20 µA | Current probe on supply during sleep phase |
| Active current | ≤ 100 mA | Current probe during sample + transmit |
| Wake-to-sleep cycle | ≤ 15s | Boot timestamp to sleep entry timestamp |
| RTC counter survival | 100% | Verify counter increments across 100 wake cycles |

### `hw_timer_isr_v1`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| ISR latency | < 2.5 µs | GPIO toggle in ISR, measure with oscilloscope |
| Missed deadlines | 0 | Queue overflow counter over 60s at 100 Hz |
| Period accuracy | 10.000 ms ± 0.1% | Oscilloscope period measurement |

### `spi_dma_throughput_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| DMA throughput | ≥ 4 MB/s at 40 MHz | Transfer known buffer, measure wall-clock time |
| CPU utilization during DMA | < 5% | `vTaskGetRunTimeStats()` during transfer |

### `tflm_wakeword_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Model arena RAM | < 100 KB | TFLM arena size report |
| Inference latency | < 200 ms | Timer around `interpreter->Invoke()` |
| Flash footprint | < 300 KB | Partition map / `size` output |

### `ota_bootstrap_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Download + flash time | < 60s on LAN | Timer from OTA start to reboot |
| Rollback trigger time | < 5s | Timer from boot to rollback decision |
| Bad image persistence | 0 (never permanent) | Force health check failure, verify rollback |

### `lvgl_dma_pingpong_v2`
| Metric | Target | Measurement Method |
| --- | --- | --- |
| Frame rate | ≥ 30 FPS | LVGL `lv_tick_get()` delta per frame |
| Tearing | 0 visible | Visual inspection during scroll test |
| DMA CPU overhead | < 10% | `vTaskGetRunTimeStats()` during rendering |
""")


# ─── production.md ────────────────────────────────────────
print("production.md")
append('docs/production.md', """
## Subsystem Production Guidelines

### `nltm_sensor_linearization_v1` — Factory Calibration
- Store calibration coefficients via NVS with CRC32 and schema versioning.
- Rate-limit calibration writes to prevent flash wear during manufacturing test loops.
- Ship safe defaults (gain=1.0, offset=0.0) for uncalibrated units.

### `esp32_ota_bootstrap_v2` — Field Update Safety
- Never allow a bad image to become permanently active.
- Health check must validate core services (Wi-Fi, MQTT, sensor init) before confirming image.
- OTA download must use HTTPS with server certificate pinning.
- Rollback partition must always contain a known-good image.

### `mtls_x509_auth_v1` — Certificate Provisioning
- Private keys loaded from encrypted filesystem partition, never compiled into firmware.
- Factory provisioning writes unique device cert + key pair during manufacturing.
- Certificate rotation requires OTA firmware update with new cert bundle.

### `mcpwm_bldc_foc_v1` — Motor Drive Safety
- Dead-time must be validated with oscilloscope on all three phase outputs before connecting motor.
- Shoot-through detection via current sense feedback and hardware fault pin.
- Emergency stop: disable all PWM outputs and engage brake resistor.

### `deep_sleep_rtc_retention_v2` — Battery-Powered Deployment
- Design supply for peak Wi-Fi TX current (up to 500 mA burst).
- Add bulk capacitors (100 µF+) near ESP32 VDD to absorb current transients.
- Sleep interval tunable via NVS configuration without firmware update.

### `bod_panic_suppression_v1` — Power Supply Design
- Never disable BOD in production firmware.
- Size cable gauge and trace width for peak current without violating BOD threshold.
- Log brownout events for field diagnosis of inadequate power supplies.

### `twai_can_differential_v1` — CAN Bus Deployment
- Require 120Ω termination resistors at each physical bus end.
- Verify differential voltage levels (CAN_H − CAN_L) with oscilloscope.
- Set CAN bus speed to match all nodes; mismatched baud rates corrupt the bus.

### `hw_crypto_aes_v2` — Security Hardening
- Enable flash encryption and secure boot in production builds.
- Validate AES output against NIST test vectors during manufacturing self-test.
- Disable JTAG in production efuses to prevent debug-port key extraction.
""")


# ─── implementation.md ────────────────────────────────────
print("implementation.md")
append('docs/implementation.md', """
## Subsystem Implementation Details

### `adc_dma_continuous` — DMA Ring Buffer Pipeline
- Uses `adc_continuous_new_handle()` with 1024-byte DMA pool.
- Half/full callbacks deliver 512-byte frames to a FreeRTOS queue (depth 8).
- DSP and MQTT work is deferred to consumer tasks — never in the DMA callback.
- GPIO34 (ADC1_CH6), attenuation 11dB, max bitwidth.

### `task_topology` — FreeRTOS Task Isolation
- Acquisition → raw queue (depth 64) → DSP → telemetry queue → MQTT.
- Each task pinned to specific core: acquisition on Core 0, networking on Core 1.
- Watchdog supervisor runs at 1 Hz, detects stale acquisition within 250 ms.
- `TASK_TOPOLOGY_ACQUIRE_PERIOD_MS = 10` (100 Hz acquisition rate).

### `deep_sleep_node` — Low-Power Sensor Cycle
- Uses `esp_deep_sleep_start()` with timer wake at 300s intervals.
- Wi-Fi connection bounded to 8s timeout with 100 ms poll interval.
- RTC_DATA_ATTR variables retain boot count and measurement state.
- Peripheral power-up warmup: 500 ms before sensor read.

### `nvs_calibration` — Versioned Blob Storage
- Packed struct: magic (4B) + schema_version (1B) + gain (4B) + offset (4B) + CRC32 (4B).
- Namespace: `sensor_cal`, key: `cal_v1`.
- CRC seed: `0xFFFFFFFF`. Verification rejects mismatched magic, schema, or CRC.

### `ota_manager` — Rollback-Safe Update Flow
- Downloads to inactive OTA partition while active partition remains bootable.
- Image verification via `esp_https_ota()` with hash check.
- Trial boot with health check timeout before `esp_ota_mark_app_valid_cancel_rollback()`.
- Failed health check triggers `esp_ota_mark_app_invalid_rollback_and_reboot()`.

### `mqtt_telemetry` — Non-Blocking Publish State Machine
- Queue depth 128, payload 256B, topic 96B per message.
- State machine: disconnected → connecting → connected → publishing.
- Exponential backoff on connection failure. Drop oldest on queue full.
- Task priority: `tskIDLE_PRIORITY + 1` (lowest non-idle).

### `hardware_timer_scheduler` — GPTimer ISR-to-Task Handoff
- Resolution: 1 MHz clock. Alarm period: configurable (default 10 ms).
- ISR is IRAM-safe: timestamps and enqueues only. Queue depth 16.
- Worker task priority: `tskIDLE_PRIORITY + 4` (above MQTT, below acquisition).
- Missed deadline counter: incremented on `xQueueSendFromISR` failure.

### `power_diagnostics` — Boot Fault Classification
- Reads `esp_reset_reason()` on every boot.
- Persists per-type counters in NVS namespace `power_diag`.
- Tracks: boot_count, brownouts, wdt_resets, panic_resets, wifi_stress.
- Optionally publishes fault history over MQTT telemetry.

### `i2c_recovery` — Stuck Bus Self-Healing
- Detects stuck SDA/SCL via GPIO read after I2C timeout.
- Recovery: delete I2C driver → reconfigure as open-drain GPIO → pulse SCL 9 times → generate STOP → reinstall driver.
- Retry budget: 3 attempts before reporting hard sensor fault.
- Default config: I2C_NUM_0, SDA=GPIO21, SCL=GPIO22, 100 kHz.
""")


# ─── references.md (already has good content, just add ID mapping) ───
print("references.md")
append('docs/references.md', """
## Validation ID to Reference Mapping

| Validation ID | Primary Reference |
| --- | --- |
| `adc_dma_nyquist_v1` | ESP-IDF ADC continuous driver, DSP sampling theory (Nyquist-Shannon) |
| `freertos_dual_core_v1` | ESP-IDF FreeRTOS SMP docs, task affinity and queue APIs |
| `deep_sleep_rtc_retention_v2` | ESP-IDF sleep modes, RTC memory documentation |
| `nvs_wear_leveling_v1` | ESP-IDF NVS API, flash wear leveling design notes |
| `hw_timer_isr_v1` | ESP-IDF GPTimer driver, ISR context rules |
| `bod_panic_suppression_v1` | ESP32 datasheet brownout detector section, power integrity app notes |
| `esp32_ota_bootstrap_v2` | ESP-IDF OTA API, partition table documentation |
| `mqtt_telemetry` / `mtls_x509_auth_v1` | OASIS MQTT 3.1.1 spec, ESP-IDF MQTT + mbedTLS docs |
| `i2c_recovery` | NXP I2C-bus specification v6.0, stuck bus recovery procedures |
| `mcpwm_bldc_foc_v1` | ESP-IDF MCPWM driver, BLDC motor control application notes |
| `twai_can_differential_v1` | ISO 11898 CAN specification, SN65HVD230 datasheet |
| `tflm_wakeword_v2` | TensorFlow Lite Micro documentation, ESP32 memory map |
| `lvgl_dma_pingpong_v2` | LVGL porting guide, ESP-IDF SPI master DMA docs |
""")

print("Done. All global docs now contain differentiated, real content.")
