from __future__ import annotations
from dataclasses import dataclass, field
from time import monotonic_ns
from typing import Any, Generic, Iterable, TypeVar
from .contracts import TimeRef, TraceRef, MetricSample, TraceSpan

@dataclass(frozen=True)
class Clock:
    domain: str = "monotonic"; origin: str = "process-monotonic"; resolution_ns: int = 1
    def now(self) -> TimeRef: return TimeRef(monotonic_ns(), self.domain, self.origin)

@dataclass
class TraceContext:
    source_id: str; frame_id: str|None=None; sequence: int|None=None; acquisition_id: str|None=None
    observation_id: str|None=None; state_id: str|None=None; gesture_id: str|None=None; event_id: str|None=None
    scene_revision: int|None=None; presentation_frame_id: str|None=None
    def ref(self) -> TraceRef: return TraceRef(self.source_id,self.frame_id,self.observation_id,self.state_id,self.gesture_id,self.event_id,self.scene_revision,self.presentation_frame_id,self.sequence)

class Sink:
    def __init__(self): self.spans=[]; self.metrics=[]
    def record_span(self, span): self.spans.append(span)
    def record_metric(self, sample): self.metrics.append(sample)

class StageTimer:
    def __init__(self, stage, clock, sink, trace): self.stage,self.clock,self.sink,self.trace=stage,clock,sink,trace; self.start=None
    def __enter__(self): self.start=self.clock.now(); return self
    def __exit__(self, typ, value, tb):
        end=self.clock.now(); status="error" if typ else "ok"; self.sink.record_span(TraceSpan(f"span-{self.stage}-{self.start.timestamp_ns}",self.stage,self.start,end,self.trace.ref(),status)); return False

def duration_ns(start: TimeRef, end: TimeRef):
    if start.domain != end.domain or end.timestamp_ns < start.timestamp_ns: return None
    return end.timestamp_ns-start.timestamp_ns
def observation_age(now, observed): return duration_ns(observed,now)
def queue_age(now, enqueued): return duration_ns(enqueued,now)
def observation_to_action(capture, presentation): return duration_ns(capture,presentation)

T=TypeVar("T")
@dataclass
class BoundedBuffer(Generic[T]):
    capacity: int; latest_wins: bool=False; _items: list[tuple[T,TimeRef]]=field(default_factory=list); dropped: int=0; stale_discarded: int=0; max_depth: int=0
    def __post_init__(self):
        if self.capacity <= 0: raise ValueError("capacity must be positive")
    def put(self, item:T, time:TimeRef):
        if len(self._items)>=self.capacity:
            if not self.latest_wins: self.dropped+=1; return False
            self._items.pop(0); self.dropped+=1
        self._items.append((item,time)); self.max_depth=max(self.max_depth,len(self._items)); return True
    def discard_stale(self, now:TimeRef, max_age_ns:int):
        kept=[]
        for item,t in self._items:
            age=queue_age(now,t)
            if age is not None and age>max_age_ns: self.stale_discarded+=1
            else: kept.append((item,t))
        self._items=kept
    def pop_latest(self): return self._items.pop() if self._items else None
    @property
    def depth(self): return len(self._items)
    def oldest_age(self, now): return queue_age(now,self._items[0][1]) if self._items else None

@dataclass
class SequenceTracker:
    last: int|None=None; missing: int=0; duplicates: int=0; reordered: int=0
    def observe(self, sequence:int):
        if self.last is None: self.last=sequence; return "first"
        if sequence==self.last: self.duplicates+=1; return "duplicate"
        if sequence<self.last: self.reordered+=1; return "reordered"
        gap=sequence-self.last-1; self.missing += gap; self.last=sequence; return "missing" if gap else "ok"

@dataclass(frozen=True)
class BenchmarkMetadata:
    run_id:str; time:TimeRef; application_version:str; commit_id:str|None; hardware_id:str; os_runtime:str; configuration:dict[str,Any]
    camera_configuration:dict[str,Any]|None; perception_configuration:dict[str,Any]|None; content_id:str; environment_id:str; duration_ns:int; benchmark_type:str

def metric(metric, value, unit, time, stage, trace=None, tags=None): return MetricSample(metric,float(value),unit,time,stage,trace,tags or {})

@dataclass(frozen=True)
class Statistics:
    count:int; minimum:float|None; maximum:float|None; mean:float|None; median:float|None; p95:float|None; p99:float|None; samples:tuple[float,...]
def statistics(values:Iterable[float]):
    xs=tuple(sorted(float(x) for x in values)); n=len(xs)
    if not n: return Statistics(0,None,None,None,None,None,None,())
    def percentile(p): return xs[min(n-1,max(0,int((p/100)*(n-1)+0.5)))]
    return Statistics(n,xs[0],xs[-1],sum(xs)/n,percentile(50),percentile(95),percentile(99),xs)
