# Perception Evaluation Contract

This is an evaluation boundary, not a perception implementation. Future adapters emit only `VisualObservation` and must not expose model, framework, or library objects downstream. Candidates are compared using identical scenario/configuration/run metadata.

Required scenarios are single hand, two hands, partial occlusion, rapid motion, motion blur, lighting variation, background clutter, entering/leaving frame, temporary loss, and reacquisition. Each result records validity separately from confidence and records positional, rotational, and scale stability; temporal and identity continuity; loss count/recovery time; jitter; latency; throughput; CPU/GPU/memory; and sustained drift.

No pass/fail thresholds are defined until evidence establishes them. Interaction usability is evaluated downstream and must not be inferred from detector confidence.
