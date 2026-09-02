from __future__ import annotations

from dataclasses import dataclass, field
from types import MappingProxyType
from enum import Enum
from typing import Any, Mapping
import math

SCHEMA_VERSION = "1.0"

class Validity(str, Enum):
    VALID = "valid"; INVALID = "invalid"; STALE = "stale"; DEGRADED = "degraded"
class TemporalStatus(str, Enum):
    OBSERVED = "observed"; PREDICTED = "predicted"; INTERPOLATED = "interpolated"

@dataclass(frozen=True)
class TimeRef:
    timestamp_ns: int
    domain: str
    origin: str
    def __post_init__(self):
        if self.timestamp_ns < 0 or not self.domain or not self.origin: raise ValueError("invalid time reference")

@dataclass(frozen=True)
class TraceRef:
    source_id: str
    frame_id: str | None = None
    observation_id: str | None = None
    state_id: str | None = None
    gesture_id: str | None = None
    event_id: str | None = None
    scene_revision: int | None = None
    presentation_frame_id: str | None = None
    sequence: int | None = None

@dataclass(frozen=True)
class RawFrame:
    frame_id: str; source_id: str; time: TimeRef; sequence: int; width: int; height: int
    pixel_format: str; orientation: str; mirrored: bool; validity: Validity = Validity.VALID
    schema_version: str = SCHEMA_VERSION; payload: bytes = b""; metadata: Mapping[str, Any] = field(default_factory=dict)
    def __post_init__(self):
        if self.sequence < 0 or self.width <= 0 or self.height <= 0: raise ValueError("invalid frame metadata")
        if not isinstance(self.payload, bytes): raise TypeError("RawFrame payload must be owned bytes")
        object.__setattr__(self, "metadata", MappingProxyType(dict(self.metadata)))

@dataclass(frozen=True)
class HandLandmarks:
    hand_id: str; landmarks: tuple[tuple[float, float, float], ...]; coordinate_space: str
    time: TimeRef; confidence: float; validity: Validity; visibility: tuple[float, ...] = ()
    trace: TraceRef | None = None; schema_version: str = SCHEMA_VERSION
    def __post_init__(self):
        if not self.coordinate_space or not self.hand_id or not 0 <= self.confidence <= 1: raise ValueError("invalid landmarks")
        if self.visibility and len(self.visibility) != len(self.landmarks): raise ValueError("visibility mismatch")

@dataclass(frozen=True)
class VisualObservation:
    observation_id: str; source_id: str; frame_id: str; time: TimeRef
    image_size: tuple[int, int]; hands: tuple[HandLandmarks, ...]; tracking_status: str
    confidence: float; validity: Validity; trace: TraceRef | None = None; schema_version: str = SCHEMA_VERSION

@dataclass(frozen=True)
class HandState:
    state_id: str; hand_id: str; position: tuple[float, float, float]; orientation: tuple[float, float, float, float]
    coordinate_space: str; time: TimeRef; confidence: float; validity: Validity; freshness_ns: int
    temporal_status: TemporalStatus; continuity: str; source_observation_id: str | None = None
    trace: TraceRef | None = None; units: str = "meters"; schema_version: str = SCHEMA_VERSION
    def __post_init__(self):
        if not self.coordinate_space or not self.units or self.freshness_ns < 0 or not 0 <= self.confidence <= 1: raise ValueError("invalid hand state")

@dataclass(frozen=True)
class GestureHypothesis:
    gesture_id: str; name: str; phase: str; confidence: float; time: TimeRef
    onset: bool; continuation: bool; termination: bool; supporting_interval_ns: tuple[int, int]
    source_state_id: str | None = None; schema_version: str = SCHEMA_VERSION
    def __post_init__(self):
        if not self.name or not 0 <= self.confidence <= 1 or self.supporting_interval_ns[1] < self.supporting_interval_ns[0]: raise ValueError("invalid gesture hypothesis")

@dataclass(frozen=True)
class InteractionEvent:
    event_id: str; action: str; target_id: str | None; parameters: Mapping[str, Any]
    time: TimeRef; source_state_id: str | None; confidence: float; authorized: bool
    trace: TraceRef | None = None; schema_version: str = SCHEMA_VERSION

@dataclass(frozen=True)
class SceneObjectState:
    object_id: str; parent_id: str | None; transform: Any; selected: bool; visible: bool
    content_type: str; metadata: Mapping[str, Any] = field(default_factory=dict)

@dataclass(frozen=True)
class PresentationState:
    scene_revision: int; objects: tuple[SceneObjectState, ...]; backend_id: str
    capabilities: frozenset[str] = frozenset(); presentation_frame_id: str | None = None

@dataclass(frozen=True)
class MetricSample:
    metric: str; value: float; unit: str; time: TimeRef; stage: str; trace: TraceRef | None = None
    tags: Mapping[str, str] = field(default_factory=dict)

@dataclass(frozen=True)
class TraceSpan:
    span_id: str; stage: str; start: TimeRef; end: TimeRef | None; trace: TraceRef
    status: str = "ok"
