"""Capture or replay owned RawFrames for isolated Vision validation."""
import argparse, base64, json, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1]/"src"))
from spatial_system.acquisition import CameraConfiguration, MacOSAVFoundationSource
from spatial_system.contracts import RawFrame, TimeRef
from spatial_system.perception import VisionPerceptionAdapter

def save_frame(path, frame):
    record={"frame_id":frame.frame_id,"source_id":frame.source_id,"timestamp_ns":frame.time.timestamp_ns,"timestamp_domain":frame.time.domain,"timestamp_origin":frame.time.origin,"sequence":frame.sequence,"width":frame.width,"height":frame.height,"pixel_format":frame.pixel_format,"orientation":frame.orientation,"mirrored":frame.mirrored,"metadata":dict(frame.metadata),"payload_b64":base64.b64encode(frame.payload).decode("ascii")}
    with path.open("a",encoding="utf8") as f: f.write(json.dumps(record,separators=(",",":"))+"\n")

def load_frames(path):
    for line in path.read_text(encoding="utf8").splitlines():
        r=json.loads(line); payload=base64.b64decode(r.pop("payload_b64")); yield RawFrame(r.pop("frame_id"),r.pop("source_id"),TimeRef(r.pop("timestamp_ns"),r.pop("timestamp_domain"),r.pop("timestamp_origin")),r.pop("sequence"),r.pop("width"),r.pop("height"),r.pop("pixel_format"),r.pop("orientation"),r.pop("mirrored"),payload=payload,metadata=r.pop("metadata"))

def process(frames, label):
    adapter=VisionPerceptionAdapter(); count=hands=landmarks=0; lat=[]; ids=[]; error=None; started=time.monotonic()
    try:
        for frame in frames:
            observation=adapter.observe(frame); count+=1; hands+=len(observation.hands); landmarks+=sum(len(h.landmarks) for h in observation.hands); ids.append((observation.source_id,observation.frame_id,frame.sequence)); lat.extend(adapter.latency_ns[-1:])
    except Exception as exc: error=str(exc)
    finally: adapter.close()
    print(json.dumps({"status":label,"frames_processed":count,"hands_detected":hands,"landmarks_produced":landmarks,"source_frame_sequence":ids,"latency_ns":lat,"throughput_fps":count/(time.monotonic()-started) if count else 0,"error":error}))
    return 0 if count and error is None else 1

def main():
    p=argparse.ArgumentParser(); p.add_argument("--capture",type=Path); p.add_argument("--replay",type=Path); p.add_argument("--duration",type=float,default=1); a=p.parse_args()
    if bool(a.capture)==bool(a.replay): p.error("choose exactly one of --capture or --replay")
    if a.replay: return process(load_frames(a.replay),"REPLAY")
    source=MacOSAVFoundationSource(CameraConfiguration("builtin-webcam","avfoundation",640,480,"BGRA",None,"high-default")); a.capture.unlink(missing_ok=True); end=time.monotonic()+a.duration; frames=[]
    try:
        while time.monotonic()<end: frame=source.read(); save_frame(a.capture,frame); frames.append(frame)
    finally: source.close()
    return process(frames,"REAL_HARDWARE_CAPTURE_THEN_VISION")
if __name__=="__main__": raise SystemExit(main())
