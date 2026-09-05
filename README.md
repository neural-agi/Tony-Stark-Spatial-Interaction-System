# Tony Stark Spatial Interaction System

> **Real-time spatial hand interaction inspired by sci-fi, built on engineering rigor. Webcam only. Measurable. Reproducible.**

[![Tests Passing](https://img.shields.io/badge/tests-31%20passing-brightgreen)](tests/)
[![Platform](https://img.shields.io/badge/platform-macOS%20M5-blue)](docs/PHASE1_AUDIT.md)
[![Stage](https://img.shields.io/badge/stage-Phase%201%20%7C%20Acquisition%20Ready-orange)](docs/)
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
5. **Deterministic tests** — 31+ tests pass without touching hardware; hardware-specific tests are separate
6. **Honest limitations** — unresolved problems are documented, not hidden

**Current state:** Phase 1 acquisition foundation is complete and tested. Ready for M5 hardware validation.

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
| Native macOS AVFoundation | ✅ Complete (untested on M5) |
| Acquisition protocol & tests | ✅ 31/31 passing |
| Hand perception | ⏳ Pending perception selection |
| State estimation | ⏳ Pending perception |
| Live interaction | ⏳ Pending perception |
| Phase 1 exit evidence | ⏳ Pending M5 validation |

### What's NOT Built (Yet)

- Live hand perception (intentionally deferred until M5 baseline exists)
- Performance benchmarks on target hardware
- Gesture recognition
- Wearable sensor integration (Phase 2)

**No Phase 1 completion claim is made until M5 validation exists.**

---

## Why NOT MediaPipe (Or Why The Architecture Matters)

A faster path would be:

```
Webcam → MediaPipe → Gesture Detection → 3D Renderer → Demo
```

That produces something impressive in a day. **This project doesn't do that.**

Instead, the perception backend will be selected empirically using measured evidence across:
- latency / throughput
- landmark stability
- jitter under different conditions
- resource usage (CPU/GPU/memory)
- sustained behavior (what happens after 2 hours?)
- integration complexity

The key architectural insight: **the rest of the system doesn't care which perception backend you choose.** Swap out MediaPipe for MediaPipe 2.0, or Ultralytics, or future tech—the interaction semantics remain identical.

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
- Hand perception (pending)
- Gesture/intent (pending)
- Single & two-hand interaction (pending)

Live two-hand mapping: a two-hand gesture locks on the first significant motion
(radial distance change >= 0.03 selects SCALE; midpoint-X change >= 0.03 selects
ROTATE, with SCALE winning ties). ROTATE uses horizontal midpoint displacement
at 1.0 radian per normalized screen-width and a 0.005 deadzone; vertical motion
does not rotate. The lock lasts until two-hand tracking ends.
- Arbitrary 3D content support ✅ (contract-level)
- Target: Measured baseline on MacBook Air M5

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
git clone https://github.com/your-username/tony-stark-spatial-interaction-system.git
cd tony-stark-spatial-interaction-system

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install the local package (no runtime dependencies)
python3 -m pip install -e .

# Run tests (no camera required)
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
# Requires a matching macOS/Xcode Swift toolchain and M5 hardware.
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
├── native/                      # Native platform code
│   └── CameraCapture.swift      # macOS AVFoundation impl
├── tests/                       # 31+ deterministic tests
│   ├── test_acquisition.py
│   ├── test_interaction.py
│   ├── test_geometry.py
│   ├── test_scene.py
│   ├── test_contracts.py
│   └── ...
├── tools/                       # Development utilities
│   └── acquisition_smoke.py
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
  → Interaction: object rotated 15° around Y
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
| M5 camera validation | ⏳ Pending | Not yet tested on target |
| Camera capability characterization | ⏳ Pending | Depends on M5 access |
| Acquisition benchmarking | ⏳ Pending | Depends on M5 hardware |
| Sustained thermal behavior | ⏳ Pending | Requires real hardware |
| Phase 1 exit gate | ⏳ Pending | Requires M5 baseline |

**Immediate next milestone:** Get this running on MacBook Air M5, measure camera baseline, establish reproducible performance envelope.

---

## Performance Contract

This project makes an explicit performance contract:

**Phase 1 Target (M5):**
- Camera capture → perception → state → gesture: **< 35ms end-to-end**
- Hand landmark jitter (RMS): **< 2 pixels**
- Gesture recognition latency: **< 50ms**
- Interaction update → render: **< 16ms** (60 FPS)
- Sustained operation: **> 2 hours** without performance degradation

**Currently:** Deterministic tests pass. Hardware validation pending.

---

## Known Limitations

**Intentionally unresolved:**
- M5 hardware validation (primary blocker)
- Perception backend selection (deferred until M5 baseline exists)
- Live hand tracking (requires perception)
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
| **Perception** | Use MediaPipe, assume it works | Select empirically after M5 baseline |
| **Performance metric** | FPS | End-to-end latency by stage |
| **Architecture** | Monolithic demo | Modular, replaceable components |
| **Buffering** | Unbounded queue (hidden latency) | Bounded, tracked, measurable |
| **Coordinate spaces** | Implicit, mixed | Explicit, typed, validated |
| **Limitations** | Hidden or undocumented | Explicit & itemized |
| **Testing** | Run on hardware | Deterministic tests + hardware validation |

---

## Gallery & Examples

*Screenshots and demos coming with M5 hardware validation.*

Expected artifacts:
- Single-hand object manipulation
- Two-hand rotation & scaling
- Gesture recognition (pinch, swipe, rotate)
- Arbitrary 3D model support
- Performance benchmarks by stage

---

## FAQ

**Q: Why not just use MediaPipe?**
A: We will—after measuring whether it's actually the right choice. Early commitment without data is how you end up optimizing the wrong thing.

**Q: Why only macOS M5?**
A: Phase 1 focuses on *one* well-characterized platform. Porting to other hardware (Windows, Linux, other ARM chips) comes after we understand the M5 baseline.

**Q: When will it be ready?**
A: Phase 1 exits when we have: (1) M5 hardware baseline, (2) live hand perception, (3) reproducible performance measurements, (4) honest performance contract. That's weeks/months away, not days.

**Q: Can I contribute?**
A: Yes. See [CONTRIBUTING.md](CONTRIBUTING.md). We need performance measurement, hardware testing, perception evaluation, and documentation help.

**Q: Is this a game engine?**
A: No. It's a spatial interaction system. You can render to any output (3D viewer, game engine, UI framework, etc.) via the display abstraction.

---

## Citation & Academic Use

If you're building on this work for research:

```bibtex
@software{tony-stark-2024,
  title={Tony Stark Spatial Interaction System},
  author={Your Name},
  year={2024},
  url={https://github.com/your-username/tony-stark-spatial-interaction-system}
}
```

---

## License

[License TBD]

---

## Roadmap

### Q4 2024 (Phase 1)
- [ ] M5 hardware validation
- [ ] Camera baseline characterization
- [ ] Perception backend evaluation
- [ ] Live hand perception implementation
- [ ] Phase 1 exit evidence

### Q1 2025 (Phase 2)
- [ ] Wearable sensor firmware
- [ ] Temporal alignment
- [ ] Sensor fusion

### Q2+ 2025 (Phase 3)
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

Current acquisition status: the native helper builds on the target arm64 MacBook Air M5, but the first hardware smoke run was blocked by macOS camera authorization (`camera authorization denied`). No frame-delivery or performance result is claimed.

Latest acquisition status: camera authorization is granted and short real-frame validation has succeeded. Evidence is recorded in `ACQUISITION.md` and `benchmarks/results/`; this is not sustained performance validation and does not open the perception gate.

*"The goal is not to make the fastest demo. The goal is to build a spatial interaction system whose performance, limitations, and architectural decisions can be measured and defended."*
