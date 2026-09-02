from __future__ import annotations
from dataclasses import dataclass
from typing import Protocol, Any
from .contracts import RawFrame, VisualObservation

class PerceptionAdapter(Protocol):
    adapter_id: str
    def observe(self, frame: RawFrame) -> VisualObservation: ...

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
