# TDR-001: Python standard-library contract foundation

- Decision: Implement the Phase 1 contract-first foundation in Python 3.11+ using the standard library only.
- Context: The repository had no implementation stack, and this stage requires typed contracts, deterministic transforms/state semantics, testability, and minimal dependencies. Live capture and perception are explicitly deferred.
- Alternatives considered: A native Apple/Swift stack; a browser/TypeScript stack; a Python stack with a third-party rendering or perception framework. These remain candidates for later stages where target-hardware benchmarks and capability requirements justify them.
- Trade-offs: Standard-library Python minimizes dependency and installation risk and supports rapid deterministic unit testing, but does not yet provide production webcam, GPU rendering, or complete glTF/OBJ decoding. The asset and display boundaries therefore remain replaceable adapters. Python performance is not evidence for live-runtime suitability.
- Rationale: This choice is reversible at the boundary level and is sufficient for the requested foundation without simulating deferred functionality.
- Consequences: Contracts, scene semantics, transforms, state machine, validation boundary, and renderer protocol can be tested now. A future runtime/perception/rendering decision must be benchmarked on the locked target and may supersede this record.
- Status: Proposed, 2026-09-02. Requires empirical review before live runtime adoption.

