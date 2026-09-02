# Phase 1 Implementation Gates

- Gate A: contracts, validity/confidence, coordinate conventions, transforms, scene, and display boundaries pass deterministic tests.
- Gate B: timestamp domain, sequences, freshness/staleness, stage boundaries, and latency definitions are documented and tested.
- Gate C: synthetic/replay observations prove downstream interaction, loss/recovery, one/two-hand transitions, and scene revisions without camera dependencies.
- Gate D: a future perception adapter emits canonical observations without exposing model/library objects downstream.
- Gate E: frame-to-presentation tracing, stage spans, queue age, drops, resource metrics, and run metadata are recordable.
- Gate F: only after A-E may live webcam/perception implementation begin; a material CV choice requires benchmark evidence and a TDR.

These gates do not authorize wearable sensing, fusion, AR, or Phase 3 functionality.
