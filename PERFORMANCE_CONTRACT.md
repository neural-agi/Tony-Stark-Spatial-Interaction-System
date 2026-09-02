# Phase 1 Performance Contract

Status: normative definitions for future runtime work. This document claims no measurements.

## Timing and latency

The locked platform is the specified fanless MacBook Air M5. Every source uses a monotonic timestamp domain with documented origin and resolution. Traces preserve source/frame, sequence, observation, state, gesture/event, scene revision, and presentation-frame identifiers.

The measured path is `capture -> acquisition -> perception -> state estimation -> gesture/intent -> interaction/scene -> rendering -> presentation`. Capture time is source delivery time; stage latency is stage end minus stage start; observation-to-action latency is presentation time minus the trace-linked capture time. Physical scan-out latency is reported only if the platform exposes it; otherwise the boundary limitation is recorded.

Required metrics: capture/processing/render rates and burstiness; stage and end-to-end latency; timing and spatial jitter; missing/skipped/duplicate/late/reordered frames; stale observations; CPU/GPU utilization; memory current/peak/growth; thermal indicators and performance drift. Reports retain counts, raw or losslessly derived samples, and p50/p90/p95/p99 plus min/max where meaningful. Jitter definitions are documented per run: timing interval deviation and stationary-hand positional/rotational/scale variation are independent of FPS.

## Queues and freshness

Every boundary has bounded capacity, explicit ownership, immutable timestamps/sequences, queue-age metrics, and an overflow/backpressure policy. The default interaction path is latest-observation-wins for superseded visual observations; every discard increments an explicit counter. No queue grows without bound, and no unmeasured smoothing/waiting queue is allowed. Consumers reject or explicitly degrade on stale, invalid, or out-of-order data. Arrival order never substitutes for timestamp association.

## Resources, thermal behavior, and run protocol

CPU/GPU measurements record tool/source, sampling interval, application/system scope, and observation window. Memory records process identity, resident/unified current and peak use, and growth. Thermal runs record available temperature/power/performance indicators, tool/source, sampling interval, ambient/setup, and throughput/latency drift.

Each run records machine/chip/core/GPU/memory, OS/runtime, application version/commit, dependencies, configuration, camera settings, perception configuration, content manifest, environment, workload, duration, timestamp definitions, tools, and run ID. Transient runs cover startup and short load; sustained runs include warm-up, steady state, long-session load, and recovery after load reduction. Degradation is a documented change in throughput, latency, jitter, drops, or resources relative to steady state. Runs are comparable only when definitions and configuration match or differences are documented.

The benchmark matrix separates camera acquisition, controlled-input perception, rendering-only content workloads, and complete interaction runs, distinguishing camera, perception, application, rendering, and presentation limits. Synthetic replay cannot be reported as camera performance.

## Optimization governance

Every material change records the measured bottleneck, hypothesis, expected metric, possible regressions, before/after baseline, transient/sustained classification, resource/thermal effects, tracking-quality effects, and interaction-latency effects. Material architectural trade-offs require a TDR; improvements with regressions are reported as trade-offs.

