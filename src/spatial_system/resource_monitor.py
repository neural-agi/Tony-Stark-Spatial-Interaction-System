"""Low-impact process resource sampling and deterministic aggregation."""
from dataclasses import dataclass
import os, subprocess, threading, time
from .measurement import rss_summary

def process_rss_bytes(pid):
    try:
        out=subprocess.check_output(["ps","-o","rss=","-p",str(pid)],text=True,stderr=subprocess.DEVNULL).strip()
        return int(out)*1024
    except (OSError,ValueError,subprocess.SubprocessError): return None

@dataclass
class ResourceSampler:
    pid:int; identity:str; interval_s:float=.25
    def __post_init__(self): self.samples=[]; self._stop=threading.Event(); self._thread=None; self.started_ns=None
    def start(self):
        self.started_ns=time.monotonic_ns(); self._thread=threading.Thread(target=self._run,name="rss-sampler"); self._thread.start(); return self
    def _run(self):
        while not self._stop.is_set():
            now=time.monotonic_ns(); rss=process_rss_bytes(self.pid)
            if rss is not None: self.samples.append({"pid":self.pid,"process_identity":self.identity,"timestamp_ns":now,"elapsed_s":(now-self.started_ns)/1e9,"rss_bytes":rss})
            self._stop.wait(self.interval_s)
    def stop(self):
        self._stop.set()
        if self._thread: self._thread.join(timeout=max(1.0,self.interval_s*4))
        return self.samples

def cpu_record(pid, identity, wall_duration_s):
    try:
        row=subprocess.check_output(["ps","-o","utime=,stime=","-p",str(pid)],text=True,stderr=subprocess.DEVNULL).strip().split()
        if len(row)!=2: raise ValueError
        def seconds(v):
            p=v.split(":"); return sum(float(x)*60**i for i,x in enumerate(reversed(p)))
        user,system=seconds(row[0]),seconds(row[1]); return {"pid":pid,"process_identity":identity,"user_cpu_time_s":user,"system_cpu_time_s":system,"wall_duration_s":wall_duration_s,"cpu_time_wall_ratio":(user+system)/wall_duration_s if wall_duration_s>0 else None,"status":"complete"}
    except (OSError,ValueError,subprocess.SubprocessError): return {"pid":pid,"process_identity":identity,"status":"incomplete"}
