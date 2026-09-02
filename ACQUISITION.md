# Instrumented webcam acquisition

Acquisition is isolated behind `FrameSource` and terminates at an owned immutable `RawFrame` payload. `AcquisitionService` adds monotonic receipt timing, bounded buffering, sequence/drop accounting, queue depth, stage spans, and inter-frame interval metrics. It does not know about hands, landmarks, gestures, scenes, or rendering.

`SyntheticFrameSource` is the deterministic test source. `MacOSAVFoundationSource` launches the native `native/CameraCapture.swift` AVFoundation helper and converts its length-delimited BGRA protocol into `RawFrame`; it never fabricates frames. The helper must be built on macOS. The hardware smoke entry point is `tools/acquisition_smoke.py`, intentionally excluded from normal tests.

The acquisition buffer is bounded and can use latest-observation-wins. Every eviction is counted. Raw frame bytes are owned immutable `bytes` at the contract boundary; no native buffer lifetime is exposed downstream. Native capture timestamps are CMSampleBuffer media-time values (`avfoundation-media-time`, nanoseconds derived from CMTime), while application receipt/queue timestamps use the Python monotonic clock and are never subtracted from source timestamps. Source and receipt times therefore remain separate; cross-clock capture latency is unavailable until an explicit correlation is established. Native BGRA stride and payload size are validated and retained in metadata, so padded rows are not interpreted as tightly packed data. Requested camera rate is configuration metadata only; actual delivery is derived from source frame timestamps.

This milestone does not claim webcam availability, M5 measurements, delivered FPS, low latency, or real-time performance.
