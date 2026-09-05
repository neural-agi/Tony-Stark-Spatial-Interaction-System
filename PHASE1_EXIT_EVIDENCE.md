# Phase 1 Exit Evidence Checklist

Current acquisition evidence classification: successful runs establish an observed source-cadence range of approximately 25.5–30 FPS, including controlled default `.high` at 29.661 FPS and explicit 30 FPS at 29.892 FPS, with zero observed sequence gaps and zero acquisition-buffer evictions. Later authorization-denied attempts occurred before capture-session creation and provide no performance evidence. The historical seven-format capability record remains preserved as historical measured evidence. Fresh capability output and repeated native negotiated-state comparisons remain required before freezing acquisition.

Phase 1 is not complete when a demo works. Evidence must be retained and reproducible on the locked M5 platform.

## Functionality

- [ ] Live built-in webcam acquisition and ordered observations
- [ ] Hand observations and explicit application-space mapping
- [ ] Validated arbitrary `.glb`, `.gltf`, and `.obj` content
- [ ] Selection, translation, rotation, scaling
- [ ] Deterministic one-hand/two-hand transitions and scene consistency

## Performance

- [ ] Capture rate, processing throughput, rendering/presentation rate
- [ ] Stage and observation-to-action latency distributions
- [ ] Timing/spatial jitter independent of FPS
- [ ] Missing, skipped, duplicate, late, reordered, and stale observations
- [ ] CPU, GPU, memory, thermal, startup, steady-state, drift, degradation, and recovery evidence
- [ ] Named baseline, percentile distributions, and regression comparisons

## Reliability, quality, and content

- [ ] Landmark/state stability, continuity, confidence, validity, loss/recovery, and hand identity
- [ ] One/two-hand, occlusion, rapid motion, blur, lighting, clutter, and camera-position scenarios
- [ ] Selection reliability, accidental activation, unintended movement, and transition stability
- [ ] Simple/moderate/complex geometry, multiple objects, varied scales, and sustained manipulation

## Observability and documentation

- [ ] Structured logs and frame-to-presentation traceability
- [ ] Versioned run metadata and retained benchmark results
- [ ] Architecture, limitations, bottlenecks, trade-offs, and optimization TDRs

Webcam tracking, MediaPipe landmarks, a 3D model, gesture detection, object manipulation, or high instantaneous FPS are not exit evidence by themselves.

Acquisition evidence now exists: arm64 helper build, authorized one-second smoke (18 real frames), five-second validation (94 frames, zero observed sequence gaps), actual frame metadata, device identity, source timestamp domain, interval statistics, and seven device-reported formats. This does not satisfy the complete Phase 1 exit gate; perception, interaction, sustained system characterization, and robustness evidence remain outstanding.

Fresh acquisition evidence (2026-09-05) now includes two consecutive real-hardware smoke launches, a 5-second run, a 2-second 120 ms consumer-lag run, and a 30-second acquisition-only run. All completed with zero observed native sequence gaps and zero recorded bounded-buffer evictions. The evidence is sufficient to freeze the current RawFrame acquisition boundary for the next milestone, but does not satisfy the overall Phase 1 exit gate: final sustained/thermal characterization, perception, interaction, robustness, and end-to-end latency evidence remain outstanding. Buffer and sequence results do not establish camera-level drop absence.

The targeted 10-second startup/steady-state repeat did not explain the 5-second versus 30-second cadence difference as startup alone: post-start intervals remained near 25 FPS in that run. Acquisition continuity and contracts are validated, but a single frozen camera cadence baseline is not yet established; controlled mode/environment comparison remains open. Perception handoff should wait for that acquisition characterization gap to be resolved.

The 2026-09-05 controlled comparison tested unchanged `.high`/BGRA against an explicit 30 FPS frame-duration request. Both delivered near-30 FPS source cadence (29.661 and 29.892 FPS respectively), with zero observed sequence gaps and zero buffer evictions. This narrows the evidence but does not establish causation for the earlier near-25 FPS runs; acquisition cadence remains characterized across tested configurations but not yet explained or frozen as a single invariant.
