from __future__ import annotations
from dataclasses import dataclass, field, replace
from enum import Enum
import platform, json, struct, subprocess, pathlib
try:
    import resource
except ImportError:
    resource = None
from typing import Iterable, Protocol
from .contracts import RawFrame, TimeRef, Validity
from .instrumentation import Clock, TraceContext, Sink, StageTimer, BoundedBuffer, SequenceTracker, metric, statistics

class AcquisitionErrorCode(str,Enum):
    UNAVAILABLE="camera_unavailable"; PERMISSION="permission_denied"; UNSUPPORTED="unsupported_configuration"; INITIALIZATION="initialization_failure"; READ="frame_read_failure"; TERMINATED="stream_terminated"
class AcquisitionError(Exception):
    def __init__(self, code, message, recoverable=False): super().__init__(message); self.code=code; self.recoverable=recoverable

@dataclass(frozen=True)
class CameraConfiguration:
    source_id:str; backend_id:str; width:int; height:int; pixel_format:str; requested_fps:float|None; configuration_id:str
    def __post_init__(self):
        if self.width<=0 or self.height<=0 or not self.source_id or not self.backend_id: raise ValueError("invalid camera configuration")
@dataclass(frozen=True)
class CameraCapabilities:
    resolutions:tuple[tuple[int,int],...]=(); pixel_formats:tuple[str,...]=(); frame_rates:tuple[float,...]=(); discovery_supported:bool=False
class FrameSource(Protocol):
    configuration:CameraConfiguration
    def capabilities(self)->CameraCapabilities: ...
    def read(self)->RawFrame: ...
    def close(self)->None: ...

class SyntheticFrameSource:
    def __init__(self, frames:Iterable[RawFrame], configuration=None):
        self.frames=iter(frames); self.configuration=configuration or CameraConfiguration("synthetic","synthetic",1,1,"bytes",None,"synthetic")
    def capabilities(self): return CameraCapabilities(((self.configuration.width,self.configuration.height),),(self.configuration.pixel_format,),(),False)
    def read(self):
        try: return next(self.frames)
        except StopIteration: raise AcquisitionError(AcquisitionErrorCode.TERMINATED,"synthetic source exhausted")
    def close(self): pass

class MacOSAVFoundationSource:
    """Native AVFoundation subprocess adapter; emits only canonical RawFrames."""
    def __init__(self, configuration, helper_path=None):
        if platform.system()!="Darwin": raise AcquisitionError(AcquisitionErrorCode.UNAVAILABLE,"AVFoundation backend requires macOS")
        self.configuration=configuration
        helper=pathlib.Path(helper_path or pathlib.Path(__file__).parents[2]/"native"/"CameraCapture")
        if not helper.is_file(): raise AcquisitionError(AcquisitionErrorCode.INITIALIZATION,f"native AVFoundation helper not built: {helper}")
        try:
            self.process=subprocess.Popen([str(helper),json.dumps(configuration.__dict__)],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        except PermissionError as e: raise AcquisitionError(AcquisitionErrorCode.PERMISSION,"camera helper permission denied",False) from e
        except OSError as e: raise AcquisitionError(AcquisitionErrorCode.INITIALIZATION,str(e),False) from e
    def capabilities(self): return CameraCapabilities(discovery_supported=False)
    def read(self):
        if self.process.stdout is None: raise AcquisitionError(AcquisitionErrorCode.READ,"camera helper has no output")
        line=self.process.stdout.readline()
        if not line:
            code=AcquisitionErrorCode.READ if self.process.poll() not in (None,0) else AcquisitionErrorCode.TERMINATED
            detail="native camera helper failed" if code is AcquisitionErrorCode.READ else "native camera stream terminated"
            raise AcquisitionError(code,detail)
        try:
            header=json.loads(line); required={"frame_id","source_id","sequence","timestamp_ns","timestamp_domain","timestamp_origin","width","height","pixel_format","orientation","mirrored","payload_size","bytes_per_row"}
            if not isinstance(header,dict) or not required.issubset(header): raise ValueError("missing frame metadata")
            size=struct.unpack("<I",self._read_exact(4))[0]
            if size != header["payload_size"] or size == 0 or size < header["bytes_per_row"]*header["height"]: raise ValueError("invalid payload size")
            payload=self._read_exact(size)
        except (ValueError,struct.error,TypeError,UnicodeDecodeError) as e: raise AcquisitionError(AcquisitionErrorCode.READ,"invalid native frame protocol") from e
        if len(payload)!=size: raise AcquisitionError(AcquisitionErrorCode.READ,"truncated native frame payload")
        if header["bytes_per_row"] < header["width"]*4: raise AcquisitionError(AcquisitionErrorCode.READ,"invalid BGRA stride")
        return RawFrame(header["frame_id"],header["source_id"],TimeRef(header["timestamp_ns"],header["timestamp_domain"],header["timestamp_origin"]),header["sequence"],header["width"],header["height"],header["pixel_format"],header["orientation"],header["mirrored"],payload=payload,metadata={"capture_timestamp_source":"avfoundation","bytes_per_row":header["bytes_per_row"],"payload_size":size})
    def _read_exact(self, size):
        chunks=[]; remaining=size
        while remaining:
            chunk=self.process.stdout.read(remaining)
            if not chunk: break
            chunks.append(chunk); remaining-=len(chunk)
        return b"".join(chunks)
    def close(self):
        if getattr(self,"process",None) and self.process.poll() is None:
            self.process.terminate()
            try: self.process.wait(timeout=2)
            except subprocess.TimeoutExpired: self.process.kill(); self.process.wait(timeout=2)

@dataclass
class AcquisitionReport:
    accepted:int=0; invalid:int=0; sequence:SequenceTracker=field(default_factory=SequenceTracker); interval_ns:list[int]=field(default_factory=list); stage_ns:list[int]=field(default_factory=list)
    actual_configuration:CameraConfiguration|None=None
    def summary(self): return {"accepted":self.accepted,"invalid":self.invalid,"missing":self.sequence.missing,"duplicates":self.sequence.duplicates,"reordered":self.sequence.reordered,"intervals":statistics(self.interval_ns),"stage_latency":statistics(self.stage_ns),"actual_configuration":self.actual_configuration}

class AcquisitionService:
    def __init__(self, source:FrameSource, buffer:BoundedBuffer[RawFrame], clock=None, sink=None):
        self.source,self.buffer=source,buffer; self.clock=clock or Clock(); self.sink=sink or Sink(); self.report=AcquisitionReport(); self._last_capture=None; self._capture_domain=None
    def acquire_once(self):
        start=self.clock.now(); trace=TraceContext(self.source.configuration.source_id); trace.acquisition_id=f"acq-{start.timestamp_ns}"
        try:
            with StageTimer("acquisition",self.clock,self.sink,trace): frame=self.source.read()
        except AcquisitionError: raise
        end=self.clock.now(); self.report.stage_ns.append(end.timestamp_ns-start.timestamp_ns)
        if frame.validity is not Validity.VALID: self.report.invalid+=1; return False
        trace.frame_id=frame.frame_id; trace.sequence=frame.sequence
        self.report.actual_configuration=CameraConfiguration(self.source.configuration.source_id,self.source.configuration.backend_id,frame.width,frame.height,frame.pixel_format,self.source.configuration.requested_fps,self.source.configuration.configuration_id)
        if self.sink.spans: self.sink.spans[-1]=replace(self.sink.spans[-1],trace=trace.ref())
        result=self.report.sequence.observe(frame.sequence)
        if result in ("duplicate","reordered"): self.sink.record_metric(metric("sequence_"+result,1,"count",end,"acquisition",trace.ref()))
        if self._capture_domain is None: self._capture_domain=frame.time.domain
        if self._last_capture is not None:
            if frame.time.domain != self._capture_domain:
                self.sink.record_metric(metric("inter_frame_interval_invalid_domain",1,"count",end,"acquisition",trace.ref()))
            else:
                age=frame.time.timestamp_ns-self._last_capture
                if age>=0: self.report.interval_ns.append(age); self.sink.record_metric(metric("inter_frame_interval",age,"ns",end,"acquisition",trace.ref()))
                else: self.sink.record_metric(metric("inter_frame_interval_invalid_order",1,"count",end,"acquisition",trace.ref()))
        self._last_capture=frame.time.timestamp_ns
        accepted=self.buffer.put(frame,end); self.report.accepted += int(accepted); self.sink.record_metric(metric("queue_depth",self.buffer.depth,"frames",end,"acquisition",trace.ref())); return accepted
    def resource_sample(self):
        if resource is None: return {"cpu_user_s":None,"cpu_system_s":None,"memory_max_rss":None,"status":"unavailable","platform":platform.platform()}
        usage=resource.getrusage(resource.RUSAGE_SELF); return {"cpu_user_s":usage.ru_utime,"cpu_system_s":usage.ru_stime,"memory_max_rss":usage.ru_maxrss,"status":"measured","platform":platform.platform()}
