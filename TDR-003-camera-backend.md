# TDR-003: Phase 1 camera backend

- Decision: Define a narrow `FrameSource` contract and implement the macOS AVFoundation adapter as a small native Swift helper with a length-delimited stdout protocol; do not select or install a CV dependency.
- Context: Phase 1 is locked to the built-in webcam on macOS Apple Silicon. Acquisition must end at owned canonical `RawFrame` bytes and remain independent of perception.
- Alternatives considered: OpenCV, ffmpeg/device subprocesses, browser capture, and native AVFoundation integration. OpenCV would introduce an unnecessary perception-adjacent dependency; subprocess/browser paths complicate ownership, timestamping, and permission semantics; native AVFoundation is the platform-aligned candidate.
- Trade-offs: Native capture now has an actual implementation, but requires compiling the Swift helper on macOS and cannot be validated in this environment. A subprocess boundary adds copy/protocol overhead but isolates native types and makes ownership explicit. Synthetic acquisition remains fully testable.
- Rationale: Keep the camera API replaceable and avoid installing CV libraries before evidence justifies them.
- Consequences: The adapter does not fabricate frames and preserves canonical metadata, ownership, timing, and error semantics. Native delivery, negotiated modes, permissions, and performance still require macOS/M5 validation.
- Status: Proposed, 2026-09-03.
- Timing note: CMSampleBuffer presentation timestamps are preserved as a separate AVFoundation media-time domain. Python monotonic receipt time is not substituted or mixed with that source clock; cross-clock latency requires future explicit correlation.
