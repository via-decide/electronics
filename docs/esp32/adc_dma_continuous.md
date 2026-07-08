# Continuous ADC Sampling using DMA on ESP32

## Overview

Continuous analog-to-digital conversion is the practice of sampling an analog signal at a controlled rate and moving the resulting digital samples into memory without requiring the main application loop to perform each read. On ESP32-class systems, this is usually implemented with an ADC peripheral, a hardware timing source, interrupt signaling, and DMA-backed buffering.

Engineers use continuous ADC sampling when the timestamp of each sample matters. Examples include vibration sensing, audio-rate acquisition, power monitoring, electrochemical sensing, motor-current measurement, and spectral analysis. In these systems, a sample is not merely a number; it is a number associated with a time index. If the time index is unstable, downstream filtering, frequency-domain analysis, threshold detection, and control decisions are degraded.

This technology exists because mixed-workload embedded systems cannot rely on foreground software timing. ESP32 firmware often runs Wi-Fi, Bluetooth, MQTT, logging, flash storage, OTA, filesystem work, and FreeRTOS scheduling at the same time as sensor acquisition. A peripheral-owned acquisition path separates sample timing from application latency.

A typical continuous ADC architecture is:

```text
Analog signal
    ↓
ADC peripheral
    ↓ hardware-paced conversion
DMA engine / digital controller
    ↓
DMA-capable memory buffer
    ↓ interrupt or callback notification
DSP / acquisition task
    ↓
Telemetry, storage, control, or analysis
```

The key engineering idea is ownership: the ADC peripheral owns conversion cadence, DMA owns sample transport, and firmware tasks own processing after samples have already been captured.

## Engineering Problem

Software-loop ADC sampling cannot guarantee deterministic sampling intervals on an ESP32 running real firmware workloads. A loop such as:

```text
read ADC
process sample
publish MQTT
write log
wait a little
repeat
```

appears simple, but every operation in the loop can perturb sample timing. Wi-Fi interrupts, radio coexistence, flash-cache stalls, filesystem operations, Bluetooth activity, logging, RTOS task preemption, and memory allocation can all introduce variable latency.

The engineering problem is not only that samples may be late. The deeper problem is that the sample interval becomes a variable of the software workload rather than a property of the acquisition system. Signal processing algorithms assume a known sampling period. If the interval varies, the acquired sequence no longer represents uniformly sampled data.

For a target sample rate of 2 kHz, the nominal period is:

\[
T_s = \frac{1}{F_s} = \frac{1}{2000} = 500\ \mu s
\]

A Wi-Fi transmit burst, flash write, or MQTT reconnect can consume far more than 500 microseconds. If the firmware loop is responsible for sampling, those events directly corrupt the time base.

## Why Naive Approaches Fail

### `analogRead()` in the Main Loop

A direct `analogRead()` call is convenient, but it is a synchronous software request. The call occurs only when the CPU reaches that line of code. If the CPU is executing another task, servicing an interrupt, waiting for a mutex, or handling networking work, the read occurs late.

```text
loop:
    sample = analogRead(pin)
    process(sample)
    publish(sample)
    delayMicroseconds(period)
```

This is not a sampling system. It is a best-effort polling loop.

### `delay()` and `delayMicroseconds()`

Delay functions do not make a system deterministic. They only postpone execution relative to the moment the delay begins. If the previous iteration ran late, the next delay starts late. This creates drift and jitter.

The loop period becomes:

\[
T_{loop} = T_{adc} + T_{process} + T_{network} + T_{logging} + T_{delay} + T_{preemption}
\]

Only one term is intentionally controlled. The other terms vary.

### Polling Loops

Polling loops waste CPU time and still fail under preemption. A high-priority interrupt or system task can interrupt the polling loop. If the polling loop is assigned high priority to reduce jitter, it may starve networking, storage, or watchdog tasks.

### Blocking APIs

Blocking MQTT publishes, TLS handshakes, DNS lookups, file writes, NVS commits, and serial logging can all delay the next sample. A single blocking operation can produce a long sample gap.

### Signal Consequences

Nonuniform sampling introduces:

- phase error,
- spectral leakage,
- apparent frequency modulation,
- incorrect filter response,
- aliasing-like artifacts,
- lost transient information,
- unstable control-loop behavior.

For frequency-domain analysis, time error becomes phase error:

\[
\phi_e = 2\pi f J_t
\]

where \(f\) is signal frequency and \(J_t\) is sampling-time jitter. Higher-frequency signals are more sensitive to the same absolute jitter.

## Engineering Principles

### Peripheral Ownership

A robust acquisition design assigns the sampling cadence to hardware. The ADC or digital controller should trigger conversions at a configured rate. Firmware should not decide when each sample occurs.

### DMA Ownership

DMA allows sample movement from peripheral to memory without CPU intervention for every sample. This reduces CPU load and prevents application latency from creating gaps in the sample stream.

### Interrupt Minimalism

Interrupts should signal that data is ready, not process the data. Heavy computation, logging, allocation, and networking do not belong in ISR context.

A good ISR or callback does only lightweight work:

```text
capture event metadata
notify task or queue
return quickly
```

### RTOS Separation

FreeRTOS tasks allow acquisition, DSP, storage, and telemetry to run at different priorities. Acquisition-adjacent work can run at higher priority, while MQTT and filesystem work can run at lower priority.

### Buffering

Buffers absorb short processing delays. A half/full buffer callback pattern lets one buffer region be processed while another region is being filled.

### Timing Discipline

A discrete-time system requires a stable sample period. The acquisition clock should be defined in hardware, and all downstream algorithms should treat samples as a sequence indexed by that hardware clock.

## Mathematical Foundation

### Sampling Requirement

For a highest expected analog frequency \(F_{max}\), the minimum sample rate is governed by Nyquist:

\[
F_s > 2F_{max}
\]

In production systems, engineers usually add margin:

\[
F_s \ge 2.5F_{max}\ \text{to}\ 10F_{max}
\]

The exact margin depends on filter rolloff, anti-aliasing design, and measurement accuracy requirements.

### Sample Period

\[
T_s = \frac{1}{F_s}
\]

For \(F_s = 2000\ Hz\):

\[
T_s = 500\ \mu s
\]

### Jitter-Induced Phase Error

Sampling jitter \(J_t\) creates phase error:

\[
\phi_e = 2\pi f J_t
\]

At \(f = 500\ Hz\) and \(J_t = 50\ \mu s\):

\[
\phi_e = 2\pi(500)(50\times10^{-6}) \approx 0.157\ rad \approx 9^\circ
\]

That is already significant for phase-sensitive measurements.

### DMA Buffer Duration

If each ADC result consumes \(B_s\) bytes and the DMA frame contains \(B_f\) bytes, the number of samples per frame is:

\[
N_f = \frac{B_f}{B_s}
\]

The frame duration is:

\[
T_f = \frac{N_f}{F_s}
\]

For a 512-byte frame and 4-byte ADC result:

\[
N_f = \frac{512}{4} = 128\ samples
\]

At 2 kHz:

\[
T_f = \frac{128}{2000} = 64\ ms
\]

This means a half/full callback should occur approximately every 64 ms for each 512-byte frame.

### Required Processing Throughput

The processing task must consume samples at least as fast as they arrive:

\[
R_{process} \ge R_{sample}
\]

In bytes per second:

\[
R_{dma} = F_s \cdot B_s
\]

At 2 kHz and 4 bytes/sample:

\[
R_{dma} = 8000\ bytes/s
\]

This is small for the ESP32, but the architectural requirement remains important because network and storage latency can create bursts.

### Queue Depth

If a producer creates frames every \(T_f\) and the consumer may be delayed for \(T_d\), the minimum queue depth is approximately:

\[
Q_{min} = \left\lceil\frac{T_d}{T_f}\right\rceil + 1
\]

This queue does not fix sustained overload. It only absorbs temporary delay.

## Hardware Architecture

The ESP32 acquisition path uses several hardware blocks:

```text
Analog input pin
    ↓
ADC1 / ADC2 analog frontend
    ↓
SAR ADC conversion engine
    ↓
Digital controller / DMA-capable path
    ↓
DMA-accessible internal memory
    ↓
Interrupt controller
    ↓
FreeRTOS task notification or queue
```

### ADC Peripheral

The ADC converts analog voltage into digital codes. On ESP32, ADC behavior depends on attenuation, bit width, reference variation, input impedance, and calibration. ADC1 is generally preferred when Wi-Fi is active because ADC2 can be constrained by Wi-Fi use on classic ESP32 variants.

### Timer or Digital Controller

The conversion cadence should be hardware-owned. In ESP-IDF continuous ADC mode, the driver configures a digital controller path that schedules conversions according to the requested sample frequency.

### DMA Path

DMA reduces per-sample CPU involvement. Rather than interrupting the CPU for every sample, the hardware fills memory frames and signals when a frame is ready.

### Interrupt Controller

An interrupt or driver callback indicates that a conversion frame has completed. The callback should not perform DSP, MQTT, filesystem writes, or logging-heavy work.

### Memory

DMA buffers must be in memory accessible by the DMA engine. On ESP32, internal RAM is generally safer for DMA than PSRAM. Alignment and buffer size should match driver requirements.

## Firmware Architecture

A robust firmware pipeline separates acquisition from processing:

```text
ADC peripheral
    ↓ hardware-paced samples
DMA frame buffer
    ↓ frame-ready callback
ISR-safe event queue
    ↓
DSP/acquisition task
    ↓
filtering, scaling, feature extraction
    ↓
storage queue / telemetry queue
    ↓
filesystem / MQTT / cloud
```

A control-oriented view is:

```text
Hardware time domain
    ADC conversion cadence
    DMA frame completion

RTOS time domain
    callback event handling
    DSP task execution
    storage task execution
    MQTT task execution
```

The engineering boundary is important. Hardware time defines when samples are taken. RTOS time defines when samples are processed.

## State Machine

A continuous ADC acquisition module can be represented as:

```text
INIT
  ↓
CONFIGURE_ADC
  ↓
CONFIGURE_DMA
  ↓
REGISTER_CALLBACK
  ↓
START
  ↓
RUNNING
  ├── FRAME_READY_HALF
  │       ↓
  │    QUEUE_EVENT
  │       ↓
  │    PROCESS_FRAME
  │
  ├── FRAME_READY_FULL
  │       ↓
  │    QUEUE_EVENT
  │       ↓
  │    PROCESS_FRAME
  │
  ├── OVERFLOW
  │       ↓
  │    COUNT_DROP / RECOVER
  │
  └── STOP_REQUEST
          ↓
       STOP_ADC
          ↓
       FREE_RESOURCES
```

Important state transitions include:

| State | Purpose | Failure Risk |
|---|---|---|
| `CONFIGURE_ADC` | Select channel, attenuation, bit width, sample rate | invalid channel or unsupported sample rate |
| `CONFIGURE_DMA` | Allocate and size frame buffers | insufficient DMA-capable memory |
| `REGISTER_CALLBACK` | Connect frame completion to firmware | ISR misuse or missing notification |
| `RUNNING` | Hardware samples continuously | downstream backlog |
| `PROCESS_FRAME` | DSP task consumes data | CPU overload or queue overflow |
| `OVERFLOW` | Detect missed processing | data loss if ignored |
| `STOP_ADC` | Controlled shutdown | resource leak if incomplete |

## Data Flow

Complete data movement for an acquisition system is:

```text
Physical quantity
    ↓
Sensor analog output
    ↓
Anti-alias filter / signal conditioning
    ↓
ESP32 ADC input
    ↓
SAR ADC conversion result
    ↓
DMA frame
    ↓
Frame event queue
    ↓
DSP task
    ↓
calibration and filtering
    ↓
feature or sample packet
    ↓
telemetry queue / storage queue
    ↓
MQTT, flash, SD card, or control task
```

A common mistake is placing MQTT or filesystem work too close to the acquisition path. The correct design uses queues so network or storage latency cannot change the sample timestamps.

## ESP-IDF Components

| Component | Role in the Design |
|---|---|
| `esp_adc` / ADC continuous driver | Configures continuous ADC conversion and frame delivery. |
| `freertos` | Provides tasks, queues, priorities, and synchronization. |
| `esp_timer` | Useful for diagnostics and timestamping, but not a substitute for ADC hardware timing. |
| `esp_event` | Useful for system events such as Wi-Fi state changes that may affect downstream telemetry. |
| `nvs_flash` | Stores calibration, configuration, and persistent counters. |
| `esp_wifi` | Represents a major source of interrupt and scheduling load. |
| `mqtt_client` | Sends processed telemetry after acquisition and DSP. |
| `esp_log` | Provides diagnostics, but excessive logging can perturb processing tasks. |

The ADC driver should own sampling. FreeRTOS should own processing orchestration. Networking components should be isolated behind bounded queues.

## Memory Model

### Stack

Each FreeRTOS task requires stack. DSP tasks need enough stack for frame parsing and filter state, but large sample buffers should generally not be placed on small stacks unless their size is carefully controlled.

### Heap

Driver handles, queues, and task creation consume heap. Heap fragmentation can become a production problem if modules repeatedly allocate and free buffers.

### DMA Memory

DMA buffers must be accessible by the DMA engine. Internal RAM is preferred. PSRAM may not be suitable for all DMA paths or may require specific allocation capabilities.

### Alignment

DMA and peripheral drivers often require alignment constraints. Buffer sizes should be multiples of the ADC result size. Frame sizes should avoid partial samples.

### Fragmentation

Long-running firmware should avoid dynamic allocation in high-frequency paths. Allocate acquisition buffers during initialization and reuse them.

### Buffer Ownership

A buffer should have a clear owner at every point:

```text
DMA owns filling buffer
    ↓
callback signals frame ready
    ↓
DSP task owns reading frame
    ↓
buffer returned to driver or reused
```

Ambiguous ownership creates race conditions and corrupted data.

## RTOS Interaction

### Tasks

A typical task split is:

| Task | Priority | Purpose |
|---|---:|---|
| ADC/DSP task | high | Drain ADC frames and perform lightweight processing. |
| Storage task | medium | Persist samples or features. |
| MQTT task | low/medium | Publish telemetry without blocking acquisition. |
| Logging task | low | Emit diagnostics asynchronously. |
| Watchdog task | medium/high | Detect stalled tasks and queue buildup. |

### Queues

Queues decouple producer and consumer timing. The ADC callback should enqueue only small event metadata. The DSP task should perform the heavier read/parse/process operation.

### Semaphores and Notifications

Direct-to-task notifications can be lower overhead than queues when only a signal is required. Queues are useful when metadata such as frame size, sequence number, or buffer index must be transferred.

### Interrupts

Interrupt callbacks must be bounded. They should not allocate memory, print large logs, publish MQTT, write files, or perform floating-point-heavy DSP.

### Priority

The DSP task must run often enough to avoid buffer overflow. However, assigning it the highest possible priority can starve Wi-Fi and system tasks. Priority design is a system-level trade-off.

### Watchdog

If a high-priority task spins or blocks incorrectly, the watchdog should detect it. Watchdog supervision should distinguish between network latency and acquisition failure.

## Performance Analysis

### Latency

Frame latency is approximately:

\[
T_{latency} = T_f + T_{queue} + T_{task\_schedule} + T_{process}
\]

The sample timestamp is still hardware-defined, but application visibility is delayed by buffering and scheduling.

### CPU Load

DMA reduces CPU load because the CPU handles frames rather than individual samples. CPU work scales with frame rate rather than sample rate.

Frame interrupt rate is:

\[
R_f = \frac{F_s}{N_f}
\]

For 2 kHz and 128 samples/frame:

\[
R_f = \frac{2000}{128} \approx 15.625\ callbacks/s
\]

This is much easier to manage than 2000 callbacks/s.

### RAM Use

RAM use includes:

\[
M_{total} = M_{dma} + M_{queue} + M_{task\_stack} + M_{filter\_state}
\]

A larger DMA buffer reduces interrupt rate but increases latency and memory consumption.

### DMA Bandwidth

DMA bandwidth is usually modest for low-kHz ADC acquisition, but the design must still avoid memory contention and ensure buffers are in accessible memory.

### Jitter

Hardware-timed ADC sampling minimizes sampling jitter. Processing jitter may still exist, but processing jitter is not sampling jitter if samples have already been captured at deterministic intervals.

### Worst-Case Timing

Worst-case analysis should include:

- longest Wi-Fi interrupt burst,
- flash erase/write stalls,
- maximum DSP processing time per frame,
- queue depth under telemetry outage,
- watchdog timeout margin,
- DMA overflow behavior.

## Design Trade-offs

| Approach | Advantages | Disadvantages | Best Use |
|---|---|---|---|
| Polling loop | Simple, easy to prototype | high jitter, CPU waste, poor under Wi-Fi load | demos, noncritical measurements |
| Timer interrupt per sample | better timing than loop | ISR rate can be high, ISR abuse risk | low-rate control events |
| ADC continuous + DMA | stable cadence, low CPU load, scalable | more complex driver setup, buffer management | signal acquisition and production sensing |
| External ADC with data-ready pin | better analog performance possible | extra BOM, board complexity | precision measurement |
| I2S-style ADC streaming | stream-oriented acquisition | platform-specific constraints | audio-like sampling paths |

The best design depends on sample rate, accuracy, analog frontend quality, power budget, memory budget, and firmware complexity tolerance.

## Failure Modes

### Buffer Overflow

If the DSP task cannot drain frames fast enough, DMA or driver buffers can overflow. This must be counted and reported.

### Queue Overflow

If frame-ready events accumulate faster than they are processed, the event queue overflows. Queue overflow is a system health signal.

### ISR Abuse

Doing too much in the callback increases interrupt latency and can destabilize the system.

### Timing Drift

Timing drift occurs when sampling is tied to software delays instead of hardware cadence.

### ADC Calibration Error

ESP32 ADC readings vary across chips and attenuation settings. Calibration is required for voltage accuracy.

### Aliasing

Without analog anti-alias filtering, signals above Nyquist can fold into the measured band.

### Power and Brownout

Wi-Fi current bursts or weak supplies can reset the ESP32, interrupt acquisition, and corrupt logs or storage operations.

### Watchdog Reset

A blocked high-priority task or unbounded processing loop can trigger watchdog resets.

### Race Conditions

Incorrect buffer ownership between callback and worker task can produce corrupted samples.

## Debugging Strategy

### Serial Logs

Use logs for initialization, configuration, overflow counts, and state transitions. Avoid high-rate logging in acquisition paths.

### Logic Analyzer

A logic analyzer can observe debug GPIO toggles from callbacks or worker tasks. This helps measure callback periodicity and processing latency.

### Oscilloscope

An oscilloscope can verify analog signal integrity, input settling, anti-alias filtering, and supply stability during Wi-Fi bursts.

### ESP Monitor

ESP-IDF monitor helps inspect logs, reset reasons, backtraces, and panic output.

### FreeRTOS Tracing

Task runtime and scheduling traces show whether DSP tasks are being starved or whether lower-priority work is accumulating.

### Heap Tracing

Heap tracing detects allocation leaks and fragmentation caused by dynamic allocation in long-running systems.

### Performance Counters

Useful counters include:

- frames received,
- frames processed,
- queue high-water mark,
- queue overflow count,
- DMA overflow count,
- maximum processing time,
- watchdog near-miss count.

## Testing Methodology

### Unit Testing

Unit tests can validate frame parsers, calibration math, queue accounting, and DSP filters without hardware.

### Driver Integration Testing

On target hardware, verify ADC configuration, sample format, frame size, and callback rate.

### Timing Testing

Toggle a GPIO in the callback and another in the DSP task. Measure callback interval and processing latency with a logic analyzer.

### Stress Testing

Run acquisition while enabling:

- Wi-Fi scans,
- MQTT reconnect loops,
- flash writes,
- serial logging,
- filesystem activity,
- OTA download simulation.

The sample stream should continue without timing ownership returning to the application loop.

### Fault Injection

Inject queue overflow by slowing the DSP task. Disconnect Wi-Fi. Force MQTT failures. Reduce buffer sizes. Verify counters and recovery behavior.

### Signal Validation

Feed a known sine wave and compare:

- measured frequency,
- amplitude stability,
- phase stability,
- spectral leakage,
- noise floor.

### Power Cycling

Repeatedly power-cycle the board during acquisition and verify clean initialization, no resource leaks, and correct reset diagnostics.

### Thermal Testing

ADC characteristics and timing margins can vary with temperature. Long-duration testing should include expected temperature range.

## Production Considerations

### OTA

OTA updates must preserve acquisition safety. New firmware should not be marked valid until acquisition, buffering, telemetry, and watchdog health checks pass.

### Diagnostics

Expose counters for:

- sample frames,
- dropped frames,
- queue overflows,
- DMA errors,
- watchdog resets,
- brownouts,
- telemetry backlog.

### Metrics

Metrics should be low overhead and bounded. They should not require high-rate logging.

### Logging

Production logging must be rate-limited. Excessive logging can create the very timing problems the architecture is meant to avoid.

### Versioning

Frame formats, calibration schema, and telemetry payloads should be versioned so firmware and cloud systems can evolve safely.

### Telemetry

Telemetry must be downstream of acquisition. Network failure should not alter sampling cadence.

### Security

If samples influence control or safety decisions, OTA, telemetry, and configuration channels must be authenticated and protected from tampering.

### Manufacturing

Manufacturing tests should verify ADC channel mapping, input range, calibration storage, sample-rate accuracy, and noise performance.

### Calibration

Board-specific calibration is often required due to ADC reference variation, divider tolerance, amplifier gain error, and sensor batch variation.

## Related Topics

- SAR ADC architecture
- DMA and bus arbitration
- Interrupt latency
- FreeRTOS queues and task priorities
- Sampling theory
- Anti-alias filtering
- Digital signal processing
- ESP-IDF ADC continuous driver
- MQTT telemetry architecture
- Watchdog supervision
- Brownout diagnostics
- NVS calibration storage
- OTA validation and rollback

## Implementation Task

TASK:
Implement a continuous ADC sampling pipeline on ESP32 using hardware-timed sampling and DMA-backed buffering instead of loop-based `analogRead()` acquisition.

CAUSATION:
ESP32 firmware running Wi-Fi, Bluetooth, MQTT, or filesystem tasks cannot guarantee fixed sampling intervals from a software loop. FreeRTOS scheduling, interrupt load, and radio-stack activity introduce jitter. For signal acquisition, jitter corrupts discrete-time assumptions and causes phase distortion, spectral leakage, and aliasing artifacts.

CONVERGENCE PROOF:
Variables:
  $F_{max}$ = highest expected analog signal frequency.
  $F_s$ = ADC sampling rate.
  $J_t$ = sampling-time jitter.
  $Equation$: $F_s > 2 \cdot F_{max}$ and $J_t \rightarrow minimum$.
  $Logic$: ADC peripheral → hardware timer trigger → DMA buffer → half/full buffer callback → DSP task → MQTT/storage task.

Why naive fails:
  - Approach A: `analogRead()` inside `loop()` with `delayMicroseconds()`. Fails because sampling cadence is not hardware-owned and can be interrupted by Wi-Fi, logging, or scheduler activity.

STATE TOPOLOGY:
{
  "validation_id": "esp32_adc_dma_continuous_v1",
  "sampling_model": {
    "hardware_timed": true,
    "dma_buffered": true,
    "loop_polling_removed": true,
    "jitter_budget_declared": true
  },
  "status": "ADC_SAMPLING_LOCKED"
}

CODE:
firmware/esp32/adc_dma_continuous.c --sample_rate=2000 --adc_channel=GPIO34 --dma_buffer=1024 --callback=half_full

PASS CRITERIA:
✓ Sampling continues while Wi-Fi and MQTT are active.
✓ Buffer callbacks fire at predictable intervals.
✓ No ADC samples are collected inside `loop()`.
✓ Captured sine wave shows no visible timing distortion at target frequency.

## Key Takeaways

- Sampling is a timing problem before it is a data problem.
- A software loop cannot guarantee fixed sample intervals on a mixed-workload ESP32.
- Hardware-timed ADC conversion protects the sample time base from Wi-Fi, logging, storage, and scheduler latency.
- DMA reduces CPU load by moving frames rather than individual samples.
- ISR callbacks should notify tasks, not perform DSP, logging, networking, or storage.
- Buffer sizes determine latency, interrupt rate, and processing slack.
- Queue overflow and DMA overflow are production diagnostics, not rare edge cases to ignore.
- Calibration, anti-alias filtering, and power integrity are part of the acquisition system.
- Telemetry and storage must be downstream of acquisition and must not control sample timing.
- Production firmware should validate timing with instruments, not only by inspecting code.
