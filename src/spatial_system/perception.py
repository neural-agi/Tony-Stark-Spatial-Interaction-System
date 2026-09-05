from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any
from .contracts import RawFrame, VisualObservation, HandLandmarks, TimeRef, TraceRef, Validity
import json, pathlib, struct, subprocess, time

class PerceptionAdapter(Protocol):
    adapter_id: str
    def observe(self, frame: RawFrame) -> VisualObservation: ...

class VisionPerceptionAdapter:
    """macOS Vision hand-pose adapter; emits canonical observations only."""
    adapter_id = "apple-vision-hand-pose"
    def __init__(self, helper_path=None):
        helper=pathlib.Path(helper_path or pathlib.Path(__file__).parents[2]/"native"/"VisionPerception")
        if not helper.is_file(): raise RuntimeError(f"Vision helper not built: {helper}")
        self.process=subprocess.Popen([str(helper)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        self.latency_ns=[]
    def observe(self, frame: RawFrame) -> VisualObservation:
        started=time.monotonic_ns(); header={"frame_id":frame.frame_id,"source_id":frame.source_id,"timestamp_ns":frame.time.timestamp_ns,"timestamp_domain":frame.time.domain,"timestamp_origin":frame.time.origin,"width":frame.width,"height":frame.height,"payload_size":len(frame.payload)}
        self.process.stdin.write((json.dumps(header)+"\n").encode()+struct.pack("<I",len(frame.payload))+frame.payload); self.process.stdin.flush()
        line=self.process.stdout.readline()
        if not line: raise RuntimeError(self.process.stderr.read().decode(errors="replace"))
        data=json.loads(line); hands=[]
        for h in data["hands"]:
            hands.append(HandLandmarks(h["hand_id"],tuple(tuple(p) for p in h["landmarks"]),"image_normalized",frame.time,float(h["confidence"]),Validity.VALID,trace=TraceRef(frame.source_id,frame.frame_id,sequence=frame.sequence)))
        self.latency_ns.append(time.monotonic_ns()-started)
        trace=TraceRef(frame.source_id,frame.frame_id,observation_id=f"observation-{frame.frame_id}",sequence=frame.sequence)
        return VisualObservation(trace.observation_id,frame.source_id,frame.frame_id,frame.time,(frame.width,frame.height),tuple(hands),data["tracking_status"],max((h.confidence for h in hands),default=0.0),Validity.VALID,trace)
    def close(self):
        if self.process.poll() is None: self.process.terminate()
        self.process.wait(timeout=2)

SCENARIOS=("single_hand","two_hands","partial_occlusion","rapid_motion","motion_blur","lighting_variation","background_clutter","enter_frame","leave_frame","temporary_loss","reacquisition")
@dataclass(frozen=True)
class PerceptionMeasurement:
    scenario:str; valid_observations:int; confidence:float|None; positional_jitter:float|None; rotational_jitter:float|None; scale_jitter:float|None
    temporal_continuity:float|None; identity_continuity:float|None; loss_count:int; recovery_ns:int|None; latency_ns:float|None; throughput:float|None
    cpu:float|None; gpu:float|None; memory_bytes:float|None; sustained_drift:float|None
@dataclass(frozen=True)
class PerceptionEvaluation:
    candidate_id:str; configuration:dict[str,Any]; measurements:tuple[PerceptionMeasurement,...]; run_id:str
    def __post_init__(self):
        if any(m.scenario not in SCENARIOS for m in self.measurements): raise ValueError("unknown perception scenario")
