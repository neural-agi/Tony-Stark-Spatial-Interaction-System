"""Short acquisition-only hardware validation; no perception or rendering."""
import argparse, json, platform, subprocess, sys, time, uuid, statistics as py_statistics
try: import resource
except ImportError: resource=None
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from spatial_system.acquisition import CameraConfiguration, MacOSAVFoundationSource, AcquisitionError
from spatial_system.instrumentation import BoundedBuffer, statistics

def main():
    p=argparse.ArgumentParser(); p.add_argument("--duration",type=float,default=5); p.add_argument("--output",default=None); p.add_argument("--consumer-delay",type=float,default=0); p.add_argument("--startup-window",type=float,default=1.0); p.add_argument("--requested-fps",type=float,default=None); a=p.parse_args()
    started=time.monotonic(); config=CameraConfiguration("builtin-webcam","avfoundation",640,480,"BGRA",a.requested_fps,"high-default" if a.requested_fps is None else f"high-explicit-{a.requested_fps:g}fps")
    result={"run_id":str(uuid.uuid4()),"benchmark":"short_acquisition_validation","platform":platform.platform(),"requested":config.__dict__.copy(),"duration_requested_s":a.duration,"consumer_delay_s":a.consumer_delay}
    try: source=MacOSAVFoundationSource(config)
    except AcquisitionError as e: result.update(status="unavailable",error={"code":e.code.value,"message":str(e)}); print(json.dumps(result)); return 2
    buf=BoundedBuffer(2,latest_wins=True); frame_count=0; first=None; last=None; intervals=[]; error=None
    try:
        while time.monotonic()-started < a.duration:
            f=source.read(); frame_count += 1
            if first is None: first=f
            if last is not None: intervals.append((f.time.timestamp_ns-last.time.timestamp_ns)/1e9)
            last=f; buf.put(f, __import__('spatial_system').Clock().now()); buf.pop_latest(); time.sleep(a.consumer_delay)
    except AcquisitionError as e: error={"code":e.code.value,"message":str(e)}
    finally: source.close()
    elapsed=time.monotonic()-started; seq=[first.sequence,last.sequence] if first and last else ([] if not first else [first.sequence]); gaps=0 if not first else (last.sequence-first.sequence-(frame_count-1))
    resources={"status":"unavailable"}
    if resource is not None:
        u=resource.getrusage(resource.RUSAGE_SELF); resources={"status":"measured","cpu_user_s":u.ru_utime,"cpu_system_s":u.ru_stime,"memory_max_rss":u.ru_maxrss,"memory_unit":"bytes on macOS"}
    source_span=(last.time.timestamp_ns-first.time.timestamp_ns)/1e9 if first and last else 0.0
    startup_intervals=[]; steady_intervals=[]
    if first:
        running=0.0
        for interval in intervals:
            running += interval
            (startup_intervals if running <= a.startup_window else steady_intervals).append(interval)
    result.update(status="REAL_HARDWARE" if frame_count else "failed",duration_observed_s=elapsed,frames=frame_count,wall_duration_receipt_rate=frame_count/elapsed if elapsed else None,first_sequence=first.sequence if first else None,last_sequence=last.sequence if last else None,first_source_timestamp_ns=first.time.timestamp_ns if first else None,last_source_timestamp_ns=last.time.timestamp_ns if last else None,source_timestamp_span_s=source_span,source_timestamp_cadence_fps=(frame_count-1)/source_span if source_span>0 else None,mean_reciprocal_interval_fps=(1/py_statistics.mean(intervals)) if intervals and py_statistics.mean(intervals)>0 else None,sequence_gaps=max(0,gaps),interval_seconds=statistics(intervals).__dict__,startup_analysis={"window_seconds":a.startup_window,"startup_intervals":statistics(startup_intervals).__dict__,"steady_state_intervals":statistics(steady_intervals).__dict__},jitter={"definition":"population standard deviation of source inter-frame intervals","stddev_seconds":py_statistics.pstdev(intervals) if len(intervals)>1 else None},queue={"depth":buf.depth,"max_depth":buf.max_depth,"dropped":buf.dropped},resources=resources,thermal={"status":"unavailable"},error=error)
    if first: result["actual"]={"source_id":first.source_id,"frame_id":first.frame_id,"sequence":first.sequence,"width":first.width,"height":first.height,"pixel_format":first.pixel_format,"metadata":dict(first.metadata),"timestamp_domain":first.time.domain,"timestamp_origin":first.time.origin}
    text=json.dumps(result,indent=2); print(text); out=Path(a.output) if a.output else Path("benchmarks/results")/f"{result['run_id']}.json"; out.parent.mkdir(parents=True,exist_ok=True); out.write_text(text+"\n",encoding="utf8"); return 0 if frame_count else 4
if __name__=="__main__": raise SystemExit(main())
