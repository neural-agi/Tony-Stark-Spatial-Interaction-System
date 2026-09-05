# Tony Stark Spatial Interaction System

> **Real-time spatial hand interaction inspired by sci-fi, built on engineering rigor. Webcam only. Measurable. Reproducible.**

[![Tests Passing](https://img.shields.io/badge/tests-37%20passing-brightgreen)](tests/)
[![Platform](https://img.shields.io/badge/platform-macOS%20M5-blue)](docs/PHASE1_AUDIT.md)
[![Stage](https://img.shields.io/badge/stage-Phase%201%20%7C%20Live%20Interaction-orange)](docs/)
[![License](https://img.shields.io/badge/license-TBD-lightgrey)]()

---

## The Problem

You've seen Tony Stark pinch, rotate, and manipulate 3D objects in mid-air. It looks like magic. But real-time spatial interaction on consumer hardware with **low latency, high responsiveness, and measurable performance** is genuinely hard.

Most hand-tracking demos:
- ✗ Start with a prebuilt library (MediaPipe, etc.) and hope it works
- ✗ Measure only FPS, not actual latency or jitter
- ✗ Break when conditions change
- ✗ Can't tell you *where* the slowness actually is
- ✗ Treat perception as a black box

**This project does none of that.**

---

## What This Actually Is

A **low-latency, hand-driven spatial interaction system** built from first principles:

1. **Strict architectural boundaries** — sensing, perception, state, gesture, interaction, scene, rendering are all independently replaceable
2. **Measured performance** — latency broken down stage-by-stage, not just "FPS go brrr"
3. **Explicit semantics** — coordinate spaces, timestamps, transforms, validity, confidence are all explicit, never implicit
4. **Reproducible baselines** — bounded buffering, sequence tracking, drop accounting mean results actually repeat
5. **Deterministic tests** — 37+ tests pass without touching hardware; hardware-specific validation is separate
6. **Honest limitations** — unresolved problems are documented, not hidden

**Current state:** Phase 1 acquisition, Vision perception, and live spatial interaction foundations are implemented and validated on the target MacBook Air M5. Phase 1 exit evidence is still in progress.

---

## The Architecture

```
Input → Acquisition → Perception → State → Intent → Interaction → Scene → Render

                    ┌────────────────────┐
                    │   Observability    │
                    │ (traces/metrics)   │
                    └────────────────────┘
                               │
                               ↓
          Every stage is traceable, every frame is accounted for
```

**Why this matters:** If you need to know why interaction feels sluggish, you can actually find out instead of guessing.

### What's Built

| Component | Status |
|-----------|--------|
| Contracts & types | ✅ Complete |
| Geometry & transforms | ✅ Complete |
| Scene/content abstraction | ✅ Complete |
| Bounded acquisition | ✅ Complete |
| Synthetic acquisition (testing) | ✅ Complete |
| Native macOS AVFoundation | ✅ Complete and hardware-validated |
| Acquisition protocol & tests | ✅ 37/37 deterministic tests passing |
| Hand perception | ✅ Apple Vision hand-pose backend implemented and hardware-validated |
| State estimation | 🟡 Foundation implemented; Phase 3 filtering/state estimation pending |
| Live interaction | ✅ Selection, translation, two-hand scaling, and pinch-based rotation implemented |
| Phase 1 exit evidence | 🟡 In progress; sustained performance and robustness evidence remain |

### What's NOT Built (Yet)

- Sustained live perception characterization and robustness validation
- Complete sustained performance characterization on target hardware
- Higher-level temporal gesture recognition and intent semantics (Phase 3)
- Wearable sensor integration (Phase 2)

**M5 hardware validation has begun and live interaction is operational; no Phase 1 completion claim is made until the full exit evidence is satisfied.**

---

## Why NOT MediaPipe (Or Why The Architecture Matters)

A faster path would be:

```
Webcam → MediaPipe → Gesture Detection → 3D Renderer → Demo
```

That produces something impressive in a day. **This project doesn't do that.**

Instead, the perception backend is provisionally implemented using Apple Vision and will be evaluated empirically using measured evidence across:
- latency / throughput
- landmark stability
- jitter under different conditions
- resource usage (CPU/GPU/memory)
- sustained behavior (what happens after 2 hours?)
- integration complexity

The key architectural insight: **the rest of the system doesn't care which perception backend is selected.** Apple Vision is currently the provisional Phase 1 backend, and the perception adapter preserves the ability to replace it without changing interaction semantics.

---

## Performance Matters (For Real)

This isn't a "let's optimize later" project.

**Performance model distinguishes:**
- Capture time (when the sensor grabbed the frame)
- Acquisition time (when the system received it)
- Perception time (hand landmark extraction)
- State estimation time (filtering/smoothing)
- Gesture interpretation time
- Interaction update time (what changed in the scene)
- Rendering time (GPU work)
- Presentation time (when it hit the display)
- **Observation-to-action latency** (the one you actually feel)

Plus: queue age, frame drops, jitter, CPU/GPU/memory usage, thermal behavior.

**Why?** Because 60 FPS at 200ms latency feels worse than 30 FPS at 30ms latency. FPS is a terrible proxy for responsiveness.

---

## Phase Roadmap

### Phase 1 — Visual Interaction (Current)
- Webcam acquisition ✅
- Hand perception ✅
- Gesture/interaction ✅
- Single & two-hand interaction ✅

Live interaction mapping: one open hand translates; one hand with a thumb/index pinch rotates through horizontal hand displacement at 1.0 radian per normalized screen-width with a 0.005 horizontal deadzone; two non-pinching hands scale from wrist distance. Pinch uses a 0.06 enter threshold and 0.075 exit threshold with hysteresis. Vertical movement does not rotate, and pinching suppresses translation for that frame.

- Arbitrary 3D content support ✅ (contract-level)
- Target: Characterize the practical performance ceiling and complete Phase 1 exit evidence on MacBook Air M5

### Phase 2 — Sensorized Wearable Input
- Physical wearable device for complementary sensing
- Temporal alignment & sensor fusion
- Cross-modal consistency validation

### Phase 3 — Intelligent Interaction
- Multimodal intent understanding
- Temporal gesture learning
- Context-aware interaction
- Higher-level command inference

---

## Quick Start

### Prerequisites
- **macOS** (Sonoma or later)
- **Python 3.11+**
- **MacBook Air M5** (for actual hand tracking; works on other hardware for development/testing)

### Installation

```bash
git clone https://github.com/neural-agi/Tony-Stark-Spatial-Interaction-System.git
cd tony-stark-spatial-interaction-system

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the local package (no runtime dependencies)
python3 -m pip install -e .

# Run deterministic tests (no camera required)
PYTHONPATH=src python3 -m unittest discover -s tests -v
```

### Run Deterministic Tests

```bash
# All tests (no hardware needed)
PYTHONPATH=src python3 -m unittest discover -s tests -v

# Specific test category
PYTHONPATH=src python3 -m unittest tests.test_acquisition -v
PYTHONPATH=src python3 -m unittest tests.test_interaction -v
PYTHONPATH=src python3 -m unittest tests.test_geometry -v
```

### Build & Run (M5 Hardware)

```bash
# Requires a matching macOS/Xcode Swift toolchain and the target MacBook Air M5.
# Build the helper from the repository root:
mkdir -p native/CameraCapture.app/Contents/MacOS
swiftc -O -module-cache-path .build/module-cache -o native/CameraCapture.app/Contents/MacOS/CameraCapture native/CameraCapture.swift -framework AVFoundation -framework Foundation -framework AppKit
codesign --force --deep --options runtime --entitlements native/CameraCapture.entitlements --sign "Apple Development: 919748180001 (ZYPYRD6L9U)" native/CameraCapture.app
PYTHONPATH=src python3 tools/acquisition_smoke.py --duration 5
```

---

## Project Structure

```
tony-stark-spatial-interaction-system/
├── src/spatial_system/          # Core system
│   ├── contracts.py             # Type definitions & versioning
│   ├── acquisition.py           # Camera → RawFrame pipeline
│   ├── perception.py            # Perception adapter contracts
│   ├── geometry.py              # Transforms, quaternions, coordinate spaces
│   ├── interaction.py           # Gesture → scene updates
│   ├── scene.py                 # 3D object state
│   ├── assets.py                # .glb/.gltf/.obj support
│   ├── display.py               # Rendering abstraction
│   └── instrumentation.py       # Observability & tracing
├── native/                      # Native macOS platform code
│   ├── CameraCapture.swift      # macOS AVFoundation acquisition
│   ├── VisionPerception.swift   # Apple Vision hand perception
│   ├── SpatialInteraction.swift # Live camera/Vision/interaction host
│   └── SyntheticDemo.swift      # Native synthetic renderer
├── tests/                       # 37+ deterministic tests
│   ├── test_acquisition.py
│   ├── test_interaction.py
│   ├── test_geometry.py
│   ├── test_scene.py
│   ├── test_contracts.py
│   └── ...
├── tools/                       # Development utilities
│   ├── acquisition_smoke.py
│   ├── acquisition_baseline.py
│   ├── perception_smoke.py
│   ├── vision_replay.py
│   ├── live_demo.py
│   └── synthetic_demo.py
├── docs/                        # Technical documentation
│   ├── PHASE1_AUDIT.md
│   ├── PERFORMANCE_CONTRACT.md
│   ├── ACQUISITION.md
│   └── TDR-*.md                 # Technical Decision Records
└── pyproject.toml
```

---

## Technical Highlights

### Coordinate Spaces (Explicit)
Every spatial value knows its coordinate space. No silent transforms:
```python
# ✅ Correct: explicit coordinate spaces
image_coords = ImageCoordinates(x=100, y=200)
camera_coords = to_camera_space(image_coords)
world_coords = to_world_space(camera_coords)

# ❌ Not allowed: mixing spaces silently
world_coords = image_coords + some_magic_number
```

### Contracts (Versioned, Typed)
Every inter-system message is a versioned contract:
```python
class VisualObservation(VersionedContract):
    version: Literal["1.0"]
    source_timestamp: int           # ns since epoch (source clock)
    receipt_timestamp: int          # ns since epoch (app clock)
    sequence_number: int            # monotonic, detects reordering
    hand_landmarks: List[Landmark]  # never None; validity is separate
    validity: Validity              # explicitly indicates if data is usable
    confidence: float               # not the same as validity
```

### Bounded Buffering (Responsiveness)
Interactive systems need responsiveness, not batch processing:
```
Queue Policy: Latest observation wins
Max queue depth: 2 frames
Tracking: drops, stale frames, reorders, duplicates
Result: Measurable latency, no hidden queues
```

### Tests Without Hardware
All acquisition tests run deterministically using synthetic frame sources:
```bash
pytest tests/test_acquisition.py -v
# Validates protocol, buffering, sequencing WITHOUT camera
```

---

## Coordinate Systems (Explained)

The system distinguishes:
- **Image coordinates** — pixel space (camera output)
- **Camera coordinates** — 3D space relative to camera
- **Hand/local coordinates** — relative to hand/object
- **World/app coordinates** — application coordinate frame
- **Object/local coordinates** — relative to specific object

Transforms are deterministic, composable, and explicit. The system rejects mathematically invalid operations rather than returning garbage.

---

## Observability

Every frame is traceable end-to-end:

```
Camera Frame ID: frame-000512
  → Acquisition: queued at 12ms, processed at 15ms
  → Perception: hand landmarks extracted at 8ms
  → State: filtered & smoothed at 3ms
  → Gesture: "pinch" detected with confidence 0.94
  → Interaction: object rotated 15° around Z
  → Scene: object state committed, revision 512
  → Render: GPU processed in 4ms
  → Display: frame presented at 48.3ms (end-to-end)
```

Queries like *"where did the latency come from?"* have real answers.

---

## Asset Support

Supports arbitrary 3D content:
- ✅ `.glb` (GLTF binary)
- ✅ `.gltf` (GLTF text)
- ✅ `.obj` (Wavefront OBJ)

Asset validation happens at a strict boundary—keeps asset-specific concerns out of interaction logic.

---

## Contributing

This is a research-grade project. We welcome:
- 🔬 Performance improvements backed by measurement
- 🏗️ Architectural refinements with evidence
- 🧪 Perception backend evaluations
- 📊 Benchmarking & reproducibility work
- 📝 Documentation improvements

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

**Contributing requires:**
- Deterministic tests for new features
- Performance impact analysis
- Architecture boundary preservation
- Clear technical justification

---

## Hardware Validation Status

| Aspect | Status | Evidence |
|--------|--------|----------|
| Native macOS build | ✅ Complete | Swift code compiles |
| M5 camera validation | ✅ Complete | Real MacBook Air Camera observations validated |
| Camera capability characterization | 🟡 Partial | Real hardware cadence characterized; capability enumeration discrepancies remain |
| Acquisition benchmarking | 🟡 Partial | 5s, 10s, 30s, lag, and configuration baseline artifacts exist; sustained Phase 1 characterization remains |
| Sustained thermal behavior | ⏳ Pending | GPU/thermal measurements remain unavailable in current instrumentation |
| Phase 1 exit gate | ⏳ Pending | Performance, robustness, and final evidence remain |

**Immediate next milestone:** Complete sustained live performance characterization, render-rate export, latency/jitter/drop evidence, resource measurements, robustness validation, and the Phase 1 exit evidence package.

---

## Performance Contract

This project makes an explicit performance contract:

**Phase 1 Target (M5):**
- Camera capture → perception → state → gesture: **< 35ms end-to-end**
- Hand landmark jitter (RMS): **< 2 pixels**
- Gesture recognition latency: **< 50ms**
- Interaction update → render: **< 16ms** (60 FPS)
- Sustained operation: **> 2 hours** without performance degradation

**Currently:** 37 deterministic tests pass, real M5 camera/Vision/live interaction validation is operational, and performance characterization is in progress.

---

## Known Limitations

**Intentionally unresolved:**
- Complete Phase 1 sustained performance and robustness validation
- Perception backend remains provisionally selected as Apple Vision pending broader comparative evaluation
- Sustained live hand-tracking characterization and robustness validation
- Some affine transform cases (require matrix representation)

**Not limitations, just deferred:**
- Phase 2 wearable sensor integration
- Phase 3 intelligent intent interpretation

---

## Technical Decision Records

Philosophy: Major decisions are documented with context, evidence, and revision status.

- **TDR-001:** Python stdlib foundation (vs. frameworks)
- **TDR-002:** Perception backend selection strategy
- **TDR-003:** Native macOS camera backend choice

See [docs/](docs/) for full TDRs.

---

## Observability & Benchmarking

Built-in instrumentation:
- Frame tracing with source timestamps
- Stage-by-stage latency breakdown
- Queue depth tracking & drop accounting
- Statistical summaries (min/max/mean/p95)
- Metadata for reproducibility

**Example:**
```python
from spatial_system.instrumentation import PerformanceTrace

trace = PerformanceTrace()
# ... run interaction ...
report = trace.generate_report()
print(f"Observation-to-action latency (p95): {report.e2e_latency_p95_ms}ms")
print(f"Dropped frames: {report.dropped_frame_count}")
print(f"Queue age (max): {report.max_queue_age_ms}ms")
```

---

## Research & Context

Spatial interaction is an active research area. This system is designed to be:
- **Reproducible** — bounded buffering, explicit sequencing, deterministic tests
- **Measurable** — latency broken down stage-by-stage, not aggregate FPS
- **Improvable** — replaceable perception backend, extensible architecture
- **Honest** — explicit about limitations, not hiding complexity

The goal is not to prove that spatial interaction *can* be done (it obviously can). The goal is to characterize *how well* it can be done on consumer hardware with clear engineering constraints.

---

## What Makes This Different

| Aspect | Typical Approach | This Project |
|--------|-----------------|--------------|
| **Perception** | Use MediaPipe, assume it works | Apple Vision (provisional), evaluated by measurement |
| **Performance metric** | FPS | End-to-end latency by stage |
| **Architecture** | Monolithic demo | Modular, replaceable components |
| **Buffering** | Unbounded queue (hidden latency) | Bounded, tracked, measurable |
| **Coordinate spaces** | Implicit, mixed | Explicit, typed, validated |
| **Limitations** | Hidden or undocumented | Explicit & itemized |
| **Testing** | Run on hardware | Deterministic tests + hardware validation |

---

## Gallery & Examples

*Live screenshots and recordings are now available from the validated M5 hardware pipeline; sustained benchmark artifacts are still being expanded.*

Expected artifacts:
- Single-hand object manipulation
- Two-hand scaling and pinch-based one-hand rotation
- Pinch-based rotation and deterministic spatial interaction
- Arbitrary 3D model support
- Performance benchmarks by stage

---

## FAQ

**Q: Why not just use MediaPipe?**
A: Apple Vision is currently the provisional Phase 1 backend. The perception adapter keeps the backend replaceable, while further evaluation is driven by measured performance, stability, and robustness evidence.

**Q: Why only macOS M5?**
A: Phase 1 focuses on *one* well-characterized platform: the MacBook Air M5. Porting to other hardware comes after the M5 baseline and Phase 1 evidence are complete.

**Q: When will it be ready?**
A: Phase 1 exits when functionality, instrumentation, sustained performance characterization, reliability, validation, and documentation evidence satisfy the defined exit gate.

**Q: Can I contribute?**
A: Yes. See [CONTRIBUTING.md](CONTRIBUTING.md). We need performance measurement, hardware testing, perception evaluation, and documentation help.

**Q: Is this a game engine?**
A: No. It's a spatial interaction system. You can render to any output (3D viewer, game engine, UI framework, etc.) via the display abstraction.

---

## Citation & Academic Use

If you're building on this work for research:

```bibtex
@software{tony-stark-spatial-interaction-system,
  title={Tony Stark-Inspired Spatial Interaction System},
  author={Paranjay Das},
  year={2026},
  url={https://github.com/neural-agi/Tony-Stark-Spatial-Interaction-System}
}
```

---

## License

[License TBD]

---

## Roadmap

### Phase 1 (Current)
- [x] M5 hardware validation
- [x] Camera baseline characterization
- [x] Initial Apple Vision backend selection and hardware validation
- [x] Live hand perception implementation
- [ ] Phase 1 exit evidence

### Phase 2 (After Phase 1 Exit)
- [ ] Wearable sensor firmware
- [ ] Temporal alignment
- [ ] Sensor fusion

### Phase 3 (After Phase 2)
- [ ] Intelligent intent interpretation
- [ ] Temporal gesture learning
- [ ] Multimodal interaction

---

## Stay Updated

- 📧 Watch releases for Phase 1 exit evidence
- 🔔 Enable discussions for technical questions
- 📖 Check [docs/](docs/) for decision records and technical deep-dives

---

## Questions?

- 🔬 Technical: Open an issue with label `question`
- 🏗️ Architecture: See [docs/](docs/)
- 🧪 Contributing: See [CONTRIBUTING.md](CONTRIBUTING.md)
- 📊 Performance: See [PERFORMANCE_CONTRACT.md](docs/PERFORMANCE_CONTRACT.md)

---

**Built by engineers who think latency matters and handwaving about "it's fast" isn't a performance metric.**

Current acquisition status: the native helper is signed for arm64 and real MacBook Air Camera frame delivery has been validated. Acquisition baselines include approximately 30 FPS source cadence under representative runs, with cadence variability and sustained performance still being characterized.

Latest live status: Apple Vision hand perception and the native live interaction pipeline are operational on real hardware. Two-hand scaling and pinch-based rotation are implemented, while sustained performance, robustness, and final Phase 1 exit evidence remain incomplete.

*"The goal is not to make the fastest demo. The goal is to build a spatial interaction system whose performance, limitations, and architectural decisions can be measured and defended."*
