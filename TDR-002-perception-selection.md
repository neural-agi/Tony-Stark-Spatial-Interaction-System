# TDR-002: Perception technology selection governance

- Decision: Keep perception technology open; select a candidate only through controlled comparative evidence.
- Context: Phase 1 requires webcam-only performance on the locked M5 platform while preserving replaceable modality boundaries.
- Alternatives considered: Any compatible tracker, including MediaPipe/OpenCV-based or native alternatives; none is selected now.
- Trade-offs: Open selection delays live implementation but prevents convenience-driven coupling and exposes accuracy, latency, resource, and thermal trade-offs.
- Rationale: Candidates must be compared for latency, throughput, stability, jitter, continuity, loss/recovery, one/two-hand behavior, difficult visual conditions, CPU/GPU/memory cost, sustained behavior, and integration complexity.
- Consequences: Adapters must emit canonical observations only. A candidate decision requires reproducible scenario/configuration metadata and benchmark evidence.
- Status: Proposed, 2026-09-02; remains provisional until candidates are benchmarked.
