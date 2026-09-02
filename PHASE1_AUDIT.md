# Phase 1 Audit and Implementation Plan

Status: planning only  
Authority: `Tony_Stark_Inspired_Spatial_Interaction_System_Technical_Specification.pdf`, Revision 1.0  
Scope: Phase 1 - Visual Interaction System only

## 1. Current repository assessment

The repository contains only the canonical technical specification PDF. There are no source files, project manifests, tests, benchmark tools, datasets, configuration schemas, TDRs, or CI scripts. Git has no commits; the PDF is currently untracked. The implementation baseline is therefore empty, not partially implemented.

The environment used for this audit does not provide the required `rtk` wrapper or Poppler utilities. Python 3.13 and `pypdf` 6.14.2 are available and were used to extract all 13 specification pages. No claim about target-device performance can be made from this environment: the locked MacBook Air M5 is not available here.

## 2. Phase 1 requirement-to-component mapping

| Requirement | Planned owning component(s) | Evidence required |
|---|---|---|
| P1-F01 live webcam, ordered observations | Sensor/Input + Acquisition | timestamp/sequence tests; capture benchmark |
| P1-F02 hand observations | Perception adapter | landmark/hand-state contract tests; tracking scenarios |
| P1-F03 application-space mapping | Coordinate/Calibration service | transform unit tests; calibration repeatability |
| P1-F04 selection/manipulation of `.glb`, `.gltf`, `.obj` | Asset importer + Scene + Interaction | fixture matrix; asset validation report |
| P1-F05 renderer-independent interaction state | Interaction contracts + Scene model | backend-independent integration tests |
| P1-F06 one/two-hand deterministic transitions | State estimator + Gesture/Intent + Interaction | transition-table tests; multi-hand scenarios |
| P1-F07 correlated instrumentation | Observability subsystem | trace correlation and benchmark artifacts |
| P1-P01 separable latency | Instrumentation across all stages | stage percentile distributions |
| P1-P02 throughput/resources/thermal | Benchmark runner + platform adapters | reproducible report on target hardware |
| P1-P03 sustained behavior | Soak benchmark | long-duration memory/thermal/resource report |
| P1-P04 practical ceiling | benchmark matrix + optimization log | baseline/comparison evidence |
| P1-P05 reproducible baseline | versioned benchmark config/results | named baseline artifact |
| P1-P06 independent jitter | metrics pipeline | spatial and timing jitter statistics |

Cross-cutting contracts: DC-01..DC-07, TIME-01..TIME-06, REL-01..REL-05, MOD-01..MOD-05, DISP-01..DISP-04, SEC-01, OBS-01..OBS-04, and CHG-01..CHG-04.

## 3. Proposed Phase 1 architecture

Use a modular application with explicit typed contracts and dependency inversion:

`WebcamSource -> AcquisitionBuffer -> VisualPerception -> TemporalStateEstimator -> GestureIntent -> InteractionEngine -> SceneModel -> Renderer/Display`

An independent observability path receives immutable events/measurements from every stage. The renderer reads scene/presentation state and never becomes interaction truth. Asset import and validation terminate at the content boundary and produce generalized scene/object abstractions. A future modality adapter can feed the same normalized observation boundary without changing interaction semantics; Phase 2/3 behavior will not be implemented now.

The initial runtime topology should remain experimentally adjustable (single process and bounded queues are candidates, not decisions). Queue policy, perception implementation, renderer, and asset libraries require benchmarking before being locked.

## 4. Data flow

1. The built-in webcam emits frames plus source timing metadata.
2. Acquisition assigns/validates sequence identity, timestamps, dimensions, orientation, mirroring, and health status.
3. Perception converts frames into normalized hand landmarks/observations with explicit image space, confidence, visibility, and validity.
4. State estimation associates observations by timestamp, maintains hand identity/continuity, and emits current/stale/degraded/invalid state explicitly.
5. Gesture/intent interprets trajectories into confidence-bearing semantic hypotheses with onset/continuation/termination.
6. Interaction maps those hypotheses to object-independent selection, translation, rotation, and scale commands.
7. Scene applies commands to generalized object state and selection/hierarchy state.
8. Rendering consumes scene state and records render/presentation timing and frame association.
9. Observability correlates source frame, observation, state, event, scene revision, render frame, and presentation where the platform permits.

## 5. Initial interface/contracts plan

Every time-varying type includes a schema/version, source identity, timestamp domain/time origin, sequence/reference, coordinate space, units, validity, confidence where applicable, and freshness/continuity metadata.

Initial conceptual contracts:

- `RawFrame`: camera identity, frame reference, capture timestamp, sequence, image geometry, orientation/mirror metadata, health.
- `VisualObservation`: frame reference, hand collection, tracking status, confidence, image-space geometry.
- `HandLandmarks`: stable hand identity, ordered landmarks, coordinate space, per-quantity confidence/visibility, timestamp.
- `HandState`: hand pose/continuity, finger quantities if available, temporal status, freshness, validity, confidence.
- `GestureHypothesis`: identifier, phase, confidence, temporal interval, onset/continuation/termination.
- `InteractionEvent`: semantic action, target abstraction, parameters, timestamp, source-state reference, authorization/confidence.
- `SceneObjectState`: object identity, hierarchy, transform, selection, visibility, content metadata.
- `PresentationState`: display-neutral scene snapshot plus backend capability information.
- `MetricSample`/`TraceSpan`: stage, frame/observation IDs, start/end timestamps, status, configuration and run IDs.

Coordinate spaces are explicit: camera, image, hand/local, application/world, and object. Transform mappings are versioned and independently testable.

## 6. Performance instrumentation plan

Instrument capture, acquisition queueing, perception, state estimation, gesture/intent, interaction, scene update, rendering, and presentation as separate spans. Record capture time, processing time, presentation time, and the defined observation-to-action/end-to-end measurement; do not infer latency from FPS.

Each run records hardware state, OS/runtime/build, configuration, camera settings, content workload, environment, duration, benchmark protocol, and run ID. Reports retain distributions and percentiles, not only means/medians, including:

- input/processing/render rates and burstiness;
- missing, skipped, duplicated, late, reordered, and stale frames;
- stage and end-to-end latency distributions;
- timing jitter and landmark/hand-state spatial jitter independently;
- CPU, GPU, memory peak/growth, and thermal/performance drift;
- tracking quality, confidence, validity, and degraded-mode counts.

The first target-hardware benchmark establishes a named baseline. Optimizations must report improvements and regressions against that same definition. Short transient and sustained runs are separate experiments.

## 7. Testing and benchmark plan

Build tests alongside components:

- contract, timestamp, coordinate/unit, validity/confidence, and transform tests;
- deterministic state-transition tests for selection, translation, rotation, scale, one-hand, two-hand, loss, and recovery;
- asset fixture tests for valid/invalid `.glb`, `.gltf`, and `.obj` files and scene consistency;
- integration tests across acquisition, perception adapter, state, interaction, scene, and renderer;
- recorded-observation replay tests so interaction semantics can be tested without a live camera;
- tracking scenarios: stationary, slow, rapid, blur, self-occlusion, partial loss, and recovery;
- environmental matrix: lighting, background, clutter, camera positioning, and hand/object occlusion;
- performance baseline, regression, and sustained soak tests with controlled run metadata.

Acceptance thresholds should be proposed only after target-device measurements establish meaningful optimization targets. Correctness, data integrity, and explicit degraded behavior remain hard requirements; they must not be weakened to improve a metric.

## 8. Initial TDR candidates

These are candidates, not decisions:

1. Perception/tracking implementation and runtime strategy, selected after accuracy/latency/CPU/GPU benchmarking.
2. Rendering backend and asset-import stack, selected against supported-format coverage, portability, frame stability, and future display abstraction.
3. Capture/queue/backpressure policy, selected against latency, drops, freshness, and sustained behavior.
4. Coordinate mapping and calibration contract, selected by repeatability/jitter experiments.
5. State-estimation and smoothing policy, selected by responsiveness/stability trade-off measurements.
6. Observability storage/retention policy, including privacy-preserving recording choices.

No material TDR is accepted yet because the repository has no empirical evidence. Each decision should use the specification's Decision, Context, Alternatives, Trade-offs, Rationale, Consequences, and Status fields.

## 9. Implementation risks

- The locked M5 target hardware is unavailable in this environment, preventing valid performance or thermal claims.
- Webcam capture rate, exposure, blur, and OS camera behavior are unresolved.
- Two-hand identity continuity and self-occlusion may be the limiting correctness/stability factors.
- Coordinate calibration can introduce hidden mirroring, handedness, scale, or latency errors.
- Asset import differences, malformed files, and object hierarchies can undermine content agnosticism.
- Presentation timing may be inaccessible or platform-dependent; the measurement definition must document its boundary.
- Unbounded queues or excessive recording can create latency, memory, and privacy regressions.
- Premature selection of a perception or rendering dependency could violate replaceability and future-phase boundaries.

## 10. Open questions requiring empirical validation

The specification's Phase 1 questions remain open: maximum stable webcam rate and blur envelope; sustained fanless thermal behavior; perception quality under fast motion, clutter, and two hands; the coordinate/calibration representation; and benchmark corpus/protocol sufficient to distinguish improvement from noise. Additional implementation questions include platform capture/presentation timestamp access, supported asset-feature subset, and measurable definitions for selection authorization and degraded interaction behavior.

## 11. Proposed implementation sequence

1. Add repository structure, project manifest, coding/test conventions, and traceability matrix without selecting heavyweight dependencies.
2. Define/version the typed contracts, coordinate conventions, timestamps, validity, confidence, and error semantics.
3. Implement pure coordinate transforms, scene/object model, interaction commands, and deterministic state machine with tests.
4. Implement asset validation/import boundary and renderer/display abstraction with representative fixtures.
5. Implement acquisition and a replaceable perception adapter, initially supporting recorded replay and live webcam input.
6. Implement state estimation and gesture/intent semantics; validate one-hand and two-hand transitions using replayed observations.
7. Implement end-to-end instrumentation and benchmark runner before optimization.
8. Establish the target-hardware baseline, then benchmark material alternatives and create/accept TDRs.
9. Iterate against functional, environmental, tracking, performance, and sustained benchmarks; document limitations and regressions.
10. Prepare Phase 1 exit evidence only when every gate item is measured and traceable. Do not begin Phase 2/3 implementation before Phase 1 acceptance.

## Audit conclusion

The project is specification-only and ready for contract-first implementation planning. There is no current implementation/specification conflict. The principal blocker to performance-complete validation is access to the locked MacBook Air M5 and its built-in webcam/display; this is an external validation dependency, not a reason to weaken the architecture or claim completion.

## Foundation implementation status

The contract-first foundation described by this audit is now implemented under `src/spatial_system` with deterministic tests under `tests`. Live acquisition, perception, and performance benchmarking remain intentionally deferred. Transform semantics are TRS-based: pure non-uniform scale is supported; non-uniform scale combined with rotation is explicitly rejected until a matrix representation is justified and recorded by a future TDR.
