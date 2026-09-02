# Phase 1 Exit Evidence Checklist

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

