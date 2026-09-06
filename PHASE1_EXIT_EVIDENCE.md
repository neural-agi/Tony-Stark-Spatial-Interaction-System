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

## Canonical Revision 1.0 cross-check (2026-09-05)

Status is deliberately conservative: PASS means verified by implementation and retained evidence; PARTIAL means a working slice exists but the specification's complete evidence obligation is not met; NOT MEASURABLE means the current implementation/platform run does not expose a trustworthy measurement; FAIL means a required result is absent or contradicted. No acceptance threshold has been invented.

| Requirement | Status | Evidence / gap |
|---|---|---|
| P1-F01 live webcam ordered stream | PASS | Signed AVFoundation path, real M5 frames, native timestamps/sequences, bounded acquisition. |
| P1-F02 hand observations | PARTIAL | Native Vision produces observations/21-point hands in successful runs; scenario corpus and repeatability evidence are incomplete. |
| P1-F03 application-space mapping | PARTIAL | Explicit normalized image-to-display mapping exists; calibration repeatability and camera-geometry validation are incomplete. |
| P1-F04 select/manipulate supported assets | PARTIAL | OBJ runtime loading is exercised; glTF/GLB loader paths are not hardware/runtime fixture validated; interaction/content matrix is absent. |
| P1-F05 renderer-independent interaction | PASS | Python InteractionState, InteractionEvent, Scene, PresentationState boundaries and deterministic tests pass. |
| P1-F06 one/two-hand deterministic transitions | PARTIAL | Translation, pinch rotation, and two-hand scale paths are implemented/tested; full loss, transition, confusable-motion, and false-activation evidence is incomplete. |
| P1-F07 correlated instrumentation | PARTIAL | Frame/observation/event/scene/presentation identifiers are present in parts of the path; complete end-to-end trace artifacts are not established for all runs. |
| P1-P01 separable latency | PARTIAL | Capture/processing/update/render boundaries exist; complete capture-to-action and presentation distributions are not retained in benchmark artifacts. |
| P1-P02 throughput/resources | PARTIAL | Camera, Vision, interaction, and render rates plus CPU time/peak memory are available; utilization, GPU, and thermal evidence are unavailable. |
| P1-P03 sustained load | PARTIAL | A 30-second acquisition-only run exists; representative full-pipeline sustained and degradation/recovery evidence is absent. |
| P1-P04 practical performance ceiling | FAIL | Candidate configuration campaign and defined ceiling/stability criterion have not been completed. |
| P1-P05 reproducible baseline | PARTIAL | Acquisition artifacts contain run metadata and distributions; complete perception/content/environment manifests are not consistently retained. |
| P1-P06 independent jitter | PARTIAL | Timestamp interval jitter is measured; stationary-hand spatial jitter and full interaction jitter corpus are absent. |
| TIME-01..TIME-06 timing contract | PARTIAL | Source media time and application clocks remain distinct; complete cross-stage temporal association evidence is incomplete. |
| REL-01..REL-05 reliability/degradation | PARTIAL | Invalid/stale/buffer behavior is tested deterministically; hardware interruption, recovery, occlusion, and reacquisition scenarios remain incomplete. |
| OBS-01..OBS-04 observability | PARTIAL | Structured native/Python diagnostics and four rolling rates exist; durable end-to-end trace correlation is incomplete. |

### Formal exit-gate decision

**PHASE 1 COMPLETE: NO.** The formal exit gate is **FAIL/PARTIAL**, not PASS, because the specification requires all functional requirements plus representative tracking/gesture/environment/occlusion testing, sustained characterization, practical-ceiling evidence, latency distributions, and documented limitations. The current evidence proves a working acquisition-to-Vision-to-interaction vertical slice, not the complete Phase 1 exit obligation.

Required before completion: a versioned full-pipeline benchmark corpus and protocol; stage/end-to-end latency distributions; CPU utilization and memory-growth methodology; GPU/thermal measurements or explicit platform-unavailable records; stationary/slow/rapid/loss/reacquisition/identity scenarios; gesture onset/continuation/termination and false-activation scenarios; lighting/background/clutter/camera-position/occlusion tests; reproducible asset-format fixtures; practical ceiling experiments; and durable frame-to-presentation trace artifacts.

### Latest full-pipeline sample (2026-09-06)

Artifact: `benchmarks/results/phase1_live_30s_20260906.jsonl` with stderr diagnostics in the adjacent `.stderr` file. The 30-second run received 577 observations, produced 577 interaction updates and 577 presentation writes, collected 3,250 native diagnostics, and exited with status 0. Rolling terminal rates were camera 16.60 FPS, Vision 16.61 FPS, interaction 16.62 FPS, and AppKit render 16.56 FPS. This is one full-pipeline sample, not a practical ceiling or thermal conclusion. It does not provide GPU/thermal utilization, stage latency distributions, spatial jitter, or environmental/occlusion scenario coverage, so it does not change the formal exit decision above.

The final evidence audit also found that the current shell reports zero valid code-signing identities and strict verification of the current app returns `CSSMERR_TP_NOT_TRUSTED`. No new signed hardware claim is made from this state; the retained signed-run artifact remains historical evidence.

## Reliability/robustness matrix (2026-09-06)

Artifact: `benchmarks/results/phase1-scenarios-20260906.jsonl`, schema `phase1-scenarios-1.0`. Eight deterministic replay scenarios executed: stationary, slow, rapid, loss/reacquisition, one/two/one hand transition, pinch lifecycle, scale lifecycle, and neutral non-pinch movement. All produced `PASS` under the fixture conditions. Thirteen physical rows (lighting, clutter, camera position, occlusion, low confidence, stale data, and frame interruption) are recorded as `OPERATOR_REQUIRED`/`NOT_EXECUTED`; they are not hardware evidence. No production reliability defect was observed in the automated rows.

## 16.6 FPS controlled comparison (2026-09-06)

Artifacts: `benchmarks/results/root-cause/acquisition-5s.jsonl` and `benchmarks/results/root-cause/full-5s.jsonl`, schema `phase1-evidence-1.0`. The fresh acquisition-only run delivered 129 frames over 5.087 s: source timestamp cadence 29.976 FPS, wall receipt rate 25.360 FPS, zero observed sequence gaps, zero buffer drops, and source interval jitter 2.163 ms. The fresh full pipeline delivered native rolling camera/Vision/interaction/render rates of 30.019/30.027/30.127/29.974 FPS. Thus the historical 16.6 FPS convergence was not reproduced under this controlled comparison and is not established as a camera ceiling. The current evidence is insufficient to attribute the historical run to a specific stage; likely startup/runtime-condition differences remain an unresolved hypothesis, not a conclusion.

## Final evidence campaign status (2026-09-06)

Fresh signed hardware execution is blocked before measurement: `security find-identity -v -p codesigning` reports zero valid identities and `codesign --verify --deep --strict native/SpatialInteraction.app` returns `CSSMERR_TP_NOT_TRUSTED`. Existing successful artifacts remain historical and are not reused as fresh campaign evidence. The available implementation does not expose trustworthy GPU utilization or direct thermal telemetry; these metrics are **NOT MEASURABLE** with the current tooling. Physical tracking, gesture, environmental, occlusion, and operator acceptance scenarios require an operator and are **NOT MEASURABLE** by unattended execution.

### Operator acceptance procedure

After signing is restored, record one JSONL result per scenario with the app build ID, camera/perception configuration, environment, duration, observations, scene revisions, and native diagnostics. Verify: (1) keys `1/2/3` select/show each object, (2) `R` resets the selected object, (3) `A` shows all and `H` hides the selected object, (4) OBJ content is visible, (5) one open hand translates only the selected object, (6) pinch plus horizontal drag rotates only it, (7) two non-pinching hands scale only it, and (8) temporary hand disappearance terminates active manipulation and reacquisition resumes observation. Each item must be marked PASS/FAIL by the operator; unattended code execution is not physical evidence.
\n+### Unified evidence harness
\n+Run `PYTHONPATH=src python3 tools/evidence_harness.py --mode full --duration 30 --output benchmarks/results/phase1-evidence-<run-id>.jsonl`. Supported modes are `acquisition`, `vision`, `interaction`, `render`, and `full`. The versioned schema is `phase1-evidence-1.0`; each artifact begins with a manifest and includes stage/rate records, CPU/peak-RSS records, and explicit unavailable telemetry statuses.
## Content and trace evidence (2026-09-06)

The live recording input is `benchmarks/results/phase1-live-trace-input-20260906.jsonl`; the derived durable trace is `benchmarks/results/phase1-trace-20260906.jsonl` with 36 correlated entries using schema `phase1-trace-1.0`. Entries retain frame/sequence/timestamp, observation, hand count, interaction event, scene revision/object state, presentation state, and render-event fields. This is IPC/state correlation evidence, not manual gesture evidence.

Content fixtures include OBJ, glTF, and a `.glb` path fixture. OBJ was previously runtime-loaded. glTF/GLB runtime rendering was not conclusively verified in this run and remain PARTIAL pending valid Model I/O fixture execution.

## Final certification audit (2026-09-06)

This section is the certification audit of the repository as it exists locally. It does not replace historical artifacts or convert implementation into validation. `PASS` means the requirement has direct retained evidence; `PARTIAL` means only a subset of the required evidence exists; `FAIL` means the available evidence contradicts or does not establish the required result; `NOT MEASURABLE` is used only where the current platform/tooling cannot expose a trustworthy metric.

### Requirement-to-evidence matrix

| Criterion | Status | Evidence artifact(s) | Condition / duration / samples | Measurement definition and finding |
|---|---|---|---|---|
| P1-F01 webcam ordered stream | PASS | `acquisition_30s_final.json`, `m5-thirty-second-final.json` | M5 built-in camera; 30 s; 888 frames in retained successful run | Source presentation timestamps and monotonic sequence; zero observed sequence gaps and zero acquisition-buffer evictions. |
| P1-F02 hand observations | PARTIAL | `phase1_live_30s_20260906.jsonl`, prior native diagnostics | Real webcam; 30.07 s; 577 observations; prior successful runs include 21-point hands | Vision observations are real and timestamped, but stability/recovery/environment coverage is incomplete. |
| P1-F03 application-space mapping | PARTIAL | coordinate/unit tests; native Vision conversion code | Deterministic fixtures; test samples; no complete physical repeatability run | Explicit normalized Vision-to-application conversion exists; camera geometry/mirroring repeatability is not fully evidenced. |
| P1-F04 generalized assets | PARTIAL | `assets/phase1-cube.obj`, `assets/phase1-triangle.gltf`, `assets/phase1-triangle.glb`; native ModelIO loader | OBJ previously loaded in live app; glTF/GLB no retained runtime render run | OBJ has runtime evidence. glTF fixture has not been runtime-verified. The `.glb` file is not a valid binary GLB fixture, so GLB support is unproven. |
| P1-F05 renderer-independent interaction | PASS | Python scene/interaction/replay tests | 46 deterministic tests; synthetic/replay conditions | InteractionEvent and Scene.apply() own state transitions; renderer consumes PresentationState. |
| P1-F06 one/two-hand transitions | PARTIAL | `phase1-scenarios-20260906.jsonl`; interaction tests | 8 automated fixture scenarios; physical scenarios not executed | Translation, pinch rotation, scale, and fixture transitions pass; physical loss/reacquisition, identity, confusable motion, and false activation remain unverified. |
| P1-F07 correlated instrumentation | PARTIAL | `phase1-trace-20260906.jsonl`; live 30 s artifact | 36 trace entries; 30.07 s full run / 577 observations | Durable state trace exists, but the trace adapter supplies fallback record-based frame/sequence IDs for some source fields and is not a complete native frame-to-render correlation. |
| P1-P01 separable latency | PARTIAL | `PERFORMANCE_CONTRACT.md`; harness artifacts | 5 s acquisition/full artifacts; sample counts vary by stage | Boundary definitions exist, but retained artifacts do not contain complete frame-associated min/median/p95/p99/max distributions for all stages and end-to-end. |
| P1-P02 throughput/resources | PARTIAL | `phase1_live_30s_20260906.jsonl`; root-cause artifacts | 30.07 s full; 5.09 s acquisition; 577/129 samples | Four rates and limited CPU/RSS are present. Reliable GPU and direct thermal telemetry are not exposed; utilization methodology is incomplete. |
| P1-P03 sustained behavior | PARTIAL | `phase1_live_30s_20260906.jsonl` | Full pipeline; 30.07 s; 577 observations | One stable aggregate run exists, but no periodic late-session latency/memory/thermal series establishes sustained drift or fanless-platform behavior. |
| P1-P04 practical ceiling | FAIL | `root-cause/acquisition-5s.jsonl`, `root-cause/full-5s.jsonl` | 5.09 s and 5 s controlled samples | The historical 16.6 FPS result was not reproduced, but the named modes are not truly isolated: all non-acquisition modes invoke `live_demo.py`. No ceiling/stability criterion was experimentally established. |
| P1-P05 reproducible baseline | PARTIAL | `phase1_live_30s_20260906.jsonl`; `phase1-evidence-1.0` artifacts | Named runs; 5–30 s | Some metadata and definitions are retained, but build identity, environment, and complete stage distributions are not consistently recorded across every artifact. |
| P1-P06 independent jitter | PARTIAL | acquisition artifacts; interaction tests | 5.09 s acquisition interval sample; deterministic fixtures | Acquisition interval jitter is available (2.163 ms stddev in `acquisition-5s.jsonl`; historical 1.783 ms). Independent Vision/interaction/render timing and stationary spatial/transform jitter are not retained. |
| TIME requirements | PARTIAL | `PERFORMANCE_CONTRACT.md`; native timestamps; acquisition artifacts | Real runs 5–30 s plus deterministic tests | Media-time, monotonic, sequence, and origin fields exist; complete cross-stage timestamp association and bounded late/stale behavior evidence are incomplete. |
| Reliability/degradation | PARTIAL | `phase1-scenarios-20260906.jsonl`; replay tests | 8 automated fixture scenarios; 13 operator rows unexecuted | Automated loss/transition fixtures pass. Lighting, occlusion, stale/low-confidence, interruption, and physical recovery evidence is absent. |
| Observability | PARTIAL | native stderr, live summaries, `phase1-trace-20260906.jsonl` | 36 trace entries; 577-observation run | Structured counters and four rates exist; durable correlation is partial and render events are not independently captured for every presentation update. |

### 16.6 FPS finding

The historical `phase1_live_30s_20260906.jsonl` run recorded 577 observations over 30.07 s with all four rolling rates near 16.6 FPS. The controlled artifacts `root-cause/acquisition-5s.jsonl` (129 frames, 5.087 s, source cadence 29.976 FPS) and `root-cause/full-5s.jsonl` (camera/Vision/interaction/render 30.019/30.027/30.127/29.974 FPS) did not reproduce it. Therefore 16.6 FPS is not established as a hardware ceiling and no causal bottleneck has been proven. The harness implementation shows why: its `vision`, `interaction`, `render`, and `full` modes all launch the same full `live_demo.py`; they are labels, not independent controlled stages. The correct classification is **unresolved measurement/runtime-condition difference**, not camera, Vision, renderer, or hardware causation.

The harness now emits explicit `active_stages`, `suppressed_stages`, and `isolation_status` in every manifest. Acquisition and full are declared implemented. Vision-only, interaction-only, and render-only remain explicitly marked unavailable because their current production launch path still includes downstream work; those modes are not used as causal evidence.

Measurement integration update: `FrameTiming` and the bounded `FrameTimingRegistry` are now attached to live Python observation handling, while native observations carry capture-receipt, Vision-submit/completion, and IPC-send timestamps. Python receive and presentation timestamps are recorded in the same timing record. Native and Python process-monotonic values are retained with their clock-domain label; cross-process latency is not calculated unless domains are proven comparable. This is hardware-ready instrumentation, not fresh hardware evidence.

Current measurement implementation status: LIVE TIMING implemented; RSS SAMPLING implemented as a reusable process sampler but not yet wired into a hardware benchmark; CPU ACCOUNTING implemented as a reusable process record but not yet wired into a hardware benchmark; RENDER TIMING implemented as a native draw counter, with frame association still unavailable when presentation identity is absent; HARDWARE VALIDATION blocked by signing identity unavailable; CROSS-PROCESS LATENCY NOT_MEASURABLE because native and Python clock comparability has not been proven.

The live driver now accepts `--timing-output <path>` and writes `phase1-frame-timing-1.0` JSONL records from the bounded registry. The evidence harness passes this output path for interaction/render/full runs and retains the frame records in the benchmark artifact. Cross-process latency fields remain unavailable unless clock comparability is established.

Frame timing:               LIVE INTEGRATED
RSS sampling:               LIVE INTEGRATED
CPU accounting:             LIVE INTEGRATED
Render timing:              AUTHORITATIVE ASSOCIATION INTEGRATED
Cross-process latency:      NOT_MEASURABLE
Hardware evidence:          BLOCKED BY SIGNING
Phase 1 status:             INCOMPLETE

## Measurement closure status (2026-09-06)

Deterministic measurement analysis now includes retained-record latency extraction, per-stage interval/jitter statistics, normalized-image spatial landmark displacement statistics, sustained-run phase aggregation, and conservative ceiling classification. No new hardware evidence was produced. The historical approximately 16.6 FPS run remains historical and was not causally reproduced in this pass. Cross-process latency remains `NOT_MEASURABLE`; GPU and thermal telemetry remain `NOT_MEASURABLE`; fresh hardware measurements remain `BLOCKED_EXTERNAL_SIGNING`.

### Performance envelope actually evidenced

The retained successful envelope is approximately 25.5–30 FPS source cadence: 5–10 s historical runs were about 25.5 FPS, controlled `.high` was 29.661 FPS, explicit 30 FPS was 29.892 FPS, and a 30 s acquisition run was 29.960 FPS. A separate full-pipeline run was 16.56–16.62 FPS for its rolling window. No practical ceiling is established. The only retained latency-like acquisition statistic is source interval jitter; complete stage latency distributions are unavailable. The 30 s run had 888-frame acquisition evidence in the acquisition artifact and 577 full-pipeline observations in the separate full-pipeline artifact; these are different runs and must not be combined.

GPU utilization and direct thermal state are **NOT MEASURABLE** with the current project tooling. The harness explicitly records those statuses as unavailable. Memory growth is also not measured: the harness records no periodic child RSS series, only limited peak/wrapper observations. CPU values in the harness are wrapper/process measurements and are not sufficient to claim whole-system utilization.

### Reliability, robustness, and operator evidence

`phase1-scenarios-20260906.jsonl` contains 21 versioned rows. Eight deterministic fixture scenarios pass (stationary, slow, rapid, loss/reacquisition, one-two-one transition, pinch lifecycle, scale lifecycle, and neutral non-pinch); 13 rows are `OPERATOR_REQUIRED`/`NOT_EXECUTED` for lighting, clutter, camera position, occlusion, low confidence, stale data, and frame interruption. This is a procedure matrix, not physical evidence. No unattended agent run can claim manual selection, translation, rotation, scale, recovery, environmental, or occlusion acceptance.

### Asset and trace findings

OBJ runtime loading has historical live evidence through `assets/phase1-cube.obj`. `assets/phase1-triangle.gltf` is a contract fixture but has no retained native runtime-render artifact. `assets/phase1-triangle.glb` is JSON text with a `.glb` extension rather than a valid GLB binary, so GLB runtime support is not evidenced. `phase1-trace-20260906.jsonl` is durable and contains 36 entries spanning observation, hand count, event, scene revision, object state, presentation, and render fields; however, source linkage is partly fallback-derived and therefore only partial trace certification.

### Formal exit-gate matrix

| Exit criterion | Status | Evidence / blocker |
|---|---|---|
| All functional requirements verified | PARTIAL | Live vertical slice is evidenced, but glTF/GLB runtime and physical interaction/robustness scenarios are incomplete. |
| Instrumentation operational | PARTIAL | Four rates/counters are operational; complete latency, spatial jitter, memory-growth, and durable frame-to-render correlation are incomplete. |
| Practical performance ceiling characterized | FAIL | No valid isolated stage campaign or stability-defined ceiling exists. |
| Major latency/drop/jitter/instability sources identified | PARTIAL | Sequence/drop evidence is good; 16.6 FPS cause, stage latency, spatial jitter, and instability sources remain unresolved. |
| Issues accepted/reduced/documented | PARTIAL | Unavailable GPU/thermal are documented; remaining measurement and robustness gaps are not closed. |
| Single-hand behavior validated | PARTIAL | Implemented and deterministic/reported in historical live runs; no current operator acceptance artifact. |
| Two-hand behavior validated | PARTIAL | Deterministic scale/transition evidence exists; physical transition/identity/isolation evidence is missing. |
| Defined environmental conditions covered | FAIL | Operator matrix exists, but no executed environmental/occlusion evidence. |
| Phase 2 boundaries preserved | PASS | No Phase 2 interfaces or responsibilities were introduced in the audited changes. |
| Documentation complete | PARTIAL | Requirements and limitations are documented; missing measurements cannot be documented as completed evidence. |
| Reproducible baseline | PARTIAL | Named artifacts exist, but metadata and stage isolation are incomplete. |
| Limitations/open questions documented | PASS | Current audit records the unresolved cadence cause, unavailable telemetry, missing physical evidence, and invalid GLB fixture. |

## Final certification decision

**PHASE 1 NOT COMPLETE.** The implementation has a working real-camera vertical slice and strong deterministic contract coverage, but the formal gate is not satisfied. Exact remaining blockers are: (1) restore a currently valid Apple Development signing state before a fresh signed campaign; (2) replace the non-isolated benchmark mode labels with genuinely controlled stage comparisons and explain the 16.6 FPS divergence; (3) retain complete frame-associated latency distributions, independent temporal/spatial jitter, and sustained memory/resource series; (4) establish a practical ceiling under a defined sustained criterion; (5) obtain operator-executed tracking, gesture, environmental, occlusion, degradation/recovery, and multi-hand evidence; (6) produce valid glTF and GLB runtime fixtures and retained render evidence; and (7) improve trace linkage so native frame identity is preserved end-to-end without fallback IDs.
