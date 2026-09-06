"""Pure frame-associated measurement primitives for Phase 1 evidence."""
from dataclasses import dataclass
from math import sqrt
from typing import Iterable
from collections import OrderedDict

def distribution(values: Iterable[float]):
    xs=sorted(float(x) for x in values); n=len(xs)
    def q(p): return xs[min(n-1, int((p/100)*(n-1)+.5))]
    return {"sample_count":n,"min":xs[0] if n else None,"median":q(50) if n else None,"p95":q(95) if n else None,"p99":q(99) if n else None,"max":xs[-1] if n else None}

def interval_statistics(values: Iterable[float]):
    xs=[float(x) for x in values]; d=distribution(xs); mean=sum(xs)/len(xs) if xs else None
    d.update({"mean":mean,"population_stddev":sqrt(sum((x-mean)**2 for x in xs)/len(xs)) if xs else None}); return d

@dataclass
class FrameTiming:
    frame_id: str|None; source_identity: str|None; sequence: int|None; source_timestamp_ns: int|None; timestamp_domain: str|None
    capture_receipt_ns: int|None=None; vision_submit_ns: int|None=None; vision_complete_ns: int|None=None; ipc_send_ns: int|None=None
    python_receive_ns: int|None=None; interaction_update_ns: int|None=None; presentation_ns: int|None=None; render_ns: int|None=None
    identity_status: str="authoritative"
    def latency_samples(self):
        pairs={"capture_to_receipt":("source_timestamp_ns","capture_receipt_ns"),"vision_duration":("vision_submit_ns","vision_complete_ns"),"vision_to_ipc":("vision_complete_ns","ipc_send_ns"),"ipc_to_python":("ipc_send_ns","python_receive_ns"),"python_to_interaction":("python_receive_ns","interaction_update_ns"),"interaction_to_presentation":("interaction_update_ns","presentation_ns"),"capture_to_presentation":("source_timestamp_ns","presentation_ns"),"capture_to_render":("source_timestamp_ns","render_ns")}
        out={}
        for name,(a,b) in pairs.items():
            x,y=getattr(self,a),getattr(self,b); out[name]=None if x is None or y is None or y<x else (y-x)/1e6
        return out

def rss_summary(samples):
    xs=[int(x["rss_bytes"] if isinstance(x,dict) else x) for x in samples]
    if not xs: return {"sample_count":0,"initial":None,"minimum":None,"maximum":None,"final":None,"growth_bytes":None,"classification":"inconclusive"}
    growth=xs[-1]-xs[0]
    return {"sample_count":len(xs),"initial":xs[0],"minimum":min(xs),"maximum":max(xs),"final":xs[-1],"growth_bytes":growth,"growth_rate_bytes_per_sample":growth/(len(xs)-1) if len(xs)>1 else None,"classification":"stable_or_bounded" if growth<=max(4096,xs[0]*.01) else "growing"}

class FrameTimingRegistry:
    """Bounded authoritative frame registry; eviction is deterministic FIFO."""
    def __init__(self, capacity=256):
        if capacity <= 0: raise ValueError("capacity must be positive")
        self.capacity=capacity; self._items=OrderedDict(); self.evictions=0
    def put(self, timing: FrameTiming):
        if timing.frame_id is None: raise ValueError("authoritative frame_id required")
        if timing.frame_id not in self._items and len(self._items)>=self.capacity: self._items.popitem(last=False); self.evictions+=1
        self._items[timing.frame_id]=timing; return timing
    def get(self, frame_id): return self._items.get(frame_id)
    def bind_render(self, frame_id, timestamp_ns):
        item=self._items.get(frame_id)
        if item is None or frame_id is None: return False
        item.render_ns=timestamp_ns; return True
    def values(self): return tuple(self._items.values())
    def __len__(self): return len(self._items)

def summarize_timings(records):
    """Derive latency summaries only from retained FrameTiming records."""
    names={"capture_to_receipt":"capture_to_receipt","vision_processing":"vision_duration","vision_to_ipc":"vision_to_ipc","ipc_to_python":"ipc_to_python","python_to_interaction":"python_to_interaction","interaction_to_presentation":"interaction_to_presentation","capture_to_presentation":"capture_to_presentation","capture_to_render":"capture_to_render"}
    out={}
    for label,key in names.items():
        values=[v for r in records for v in [r.latency_samples().get(key)] if v is not None]
        out[label]=distribution(values) if values else {"status":"NOT_EXECUTED"}
    return out

def interval_summary(records, field):
    values=[]; previous=None
    for r in records:
        value=getattr(r,field,None)
        if value is not None and previous is not None and value>=previous: values.append((value-previous)/1e6)
        if value is not None: previous=value
    return interval_statistics(values) if values else {"status":"NOT_EXECUTED"}
