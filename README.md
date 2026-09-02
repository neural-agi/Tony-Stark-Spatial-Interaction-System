# Tony Stark-Inspired Spatial Interaction System

This repository currently implements the contract-first Phase 1 foundation only. The canonical specification remains authoritative.

## Ownership and status

`src/spatial_system` owns reusable contracts and Phase 1 foundation semantics. `tests` owns fast deterministic foundation tests. `docs` is reserved for project documentation, `tools` for benchmark/maintenance tooling, and `phase2`/`phase3` for separately authorized future work; those directories are intentionally absent until needed. The canonical PDF remains at repository root and is never modified by implementation work.

The foundation is implemented and audited, but Phase 1 itself is not complete. Live acquisition/perception and all performance validation remain deferred.

The performance definitions are frozen in [PERFORMANCE_CONTRACT.md](PERFORMANCE_CONTRACT.md). Exit evidence is tracked in [PHASE1_EXIT_EVIDENCE.md](PHASE1_EXIT_EVIDENCE.md), and pre-live implementation gates are defined in [PHASE1_IMPLEMENTATION_GATES.md](PHASE1_IMPLEMENTATION_GATES.md). Success cannot be reduced to webcam tracking, a renderer demo, or instantaneous FPS.

Implemented: versioned typed contracts, explicit coordinate spaces and deterministic transform primitives, object-independent interaction state/events, generalized scene/object state, `.glb`/`.gltf`/`.obj` asset validation boundary, display/presentation protocol, and traceability fields for future observability.

Runtime instrumentation now provides monotonic timestamps, trace contexts, stage spans, latency/age calculations, sequence/drop tracking, bounded buffers, metrics, retained-sample statistics, and benchmark metadata. Tests are separated by responsibility under `tests/` (`contracts`, `geometry`, `interaction`, `scene`, `assets`, `display`, `observability`, and `perception`). The perception boundary is defined by `PerceptionAdapter` and `PERCEPTION_EVALUATION.md`; technology selection remains open under TDR-002.

Deferred by design: live webcam capture, computer vision/hand tracking, MediaPipe, gesture ML, live runtime optimization, wearable sensing/BLE, sensor fusion, intelligent intent recognition, AR and other future display backends.

## Development

Requires Python 3.11+; runtime dependencies are intentionally empty. Run tests with:

```text
python -m unittest discover -s tests -v
```

`pyproject.toml` records the package manifest and pytest discovery convention for environments that provide pytest. No benchmark is implemented at this stage; future benchmarks must record the hardware/configuration/run metadata required by the specification.

The provisional Python choice and its limitations are recorded in [TDR-001-python-stdlib-foundation.md](TDR-001-python-stdlib-foundation.md). It must be revisited before selecting live perception, rendering, or capture technology.

Instrumented acquisition infrastructure is documented in [ACQUISITION.md](ACQUISITION.md). The target backend remains provisional under TDR-003; the current environment has no validated macOS camera integration. The hardware smoke entry point is `python tools/acquisition_smoke.py` and is not part of deterministic CI.
