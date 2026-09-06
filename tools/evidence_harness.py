"""Unified Phase 1 evidence artifact producer.

This is a measurement wrapper: production acquisition, Vision, interaction, and
rendering semantics are unchanged.  Each run emits a versioned JSONL stream and
one manifest/result record.
"""
import argparse, json, os, platform, subprocess, sys, time, uuid, resource, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from spatial_system.resource_monitor import ResourceSampler, rss_summary, cpu_record

SCHEMA="phase1-evidence-1.0"
STAGE_PLANS={
 "acquisition":{"active_stages":["camera","acquisition"],"suppressed_stages":["vision","ipc","interaction","render"],"isolation":"implemented"},
 "vision":{"active_stages":["camera","acquisition","vision"],"suppressed_stages":["ipc","interaction","presentation","render"],"isolation":"PASS"},
 "ipc":{"active_stages":["camera","acquisition","vision","ipc"],"suppressed_stages":["interaction","presentation","render"],"isolation":"PASS"},
 "interaction":{"active_stages":["camera","acquisition","vision","ipc","interaction"],"suppressed_stages":["presentation","render"],"isolation":"PASS"},
 "render":{"active_stages":["camera","acquisition","vision","ipc","interaction","presentation","render"],"suppressed_stages":[],"isolation":"PASS"},
 "full":{"active_stages":["camera","acquisition","vision","ipc","interaction","presentation","render"],"suppressed_stages":[],"isolation":"implemented"},
}
def stats(xs):
    xs=sorted(float(x) for x in xs); n=len(xs)
    if not n: return {"count":0,"min":None,"median":None,"p95":None,"p99":None,"max":None,"mean":None}
    def q(p): return xs[min(n-1, int((p/100)*(n-1)+.5))]
    return {"count":n,"min":xs[0],"median":q(50),"p95":q(95),"p99":q(99),"max":xs[-1],"mean":sum(xs)/n}
def record(run, stage, metric, value=None, sample_count=0, **extra):
    return {"schema":SCHEMA,"run_id":run,"timestamp_ns":time.monotonic_ns(),"stage":stage,"metric":metric,"value":value,"sample_count":sample_count,**extra}
def run_child(cmd, root, env, duration):
    started=time.monotonic(); proc=subprocess.Popen(cmd,cwd=root,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,env=env,bufsize=1)
    sampler=ResourceSampler(proc.pid,"native" if cmd and "SpatialInteraction" in cmd[0] else "python",.25).start()
    python_sampler=ResourceSampler(os.getpid(),"python-benchmark",.25).start()
    try: stdout,stderr=proc.communicate(timeout=duration+30)
    except subprocess.TimeoutExpired:
        proc.terminate(); stdout,stderr=proc.communicate()
    samples=sampler.stop(); python_samples=python_sampler.stop(); wall=time.monotonic()-started
    cpu=cpu_record(proc.pid,sampler.identity,wall)
    return proc,stdout,stderr,{"native":samples,"python":python_samples},cpu
def main():
    p=argparse.ArgumentParser(); p.add_argument("--mode",choices=("acquisition","vision","ipc","interaction","render","full"),required=True); p.add_argument("--duration",type=float,default=5); p.add_argument("--output",type=Path,required=True); p.add_argument("--environment",default="unspecified"); a=p.parse_args()
    run=str(uuid.uuid4()); started=time.monotonic(); root=Path(__file__).parents[1]; artifact=a.output; artifact.parent.mkdir(parents=True,exist_ok=True)
    plan=STAGE_PLANS[a.mode]
    manifest={"schema":SCHEMA,"run_id":run,"benchmark_type":a.mode,"active_stages":plan["active_stages"],"suppressed_stages":plan["suppressed_stages"],"isolation_status":plan["isolation"],"started_monotonic_ns":time.monotonic_ns(),"duration_requested_s":a.duration,"hardware":platform.platform(),"python":platform.python_version(),"os":platform.platform(),"application_build":"native/SpatialInteraction.app (existing build)","camera_configuration":"existing production configuration","perception_configuration":"Apple Vision VNDetectHumanHandPoseRequest, existing configuration","content_workload":"three canonical scene objects / existing live presentation","environment":a.environment,"metric_definitions":{"camera_fps":"native rolling sample-buffer receipt rate","vision_fps":"native rolling completed Vision request rate","interaction_fps":"Python observation/update rate","render_fps":"AppKit draw calls over native rolling window","jitter":"population standard deviation of recorded interval samples","latency":"reported only when start/end clocks share an explicit domain"},"telemetry":{"gpu":{"status":"NOT_MEASURABLE","reason":"not exposed by current project instrumentation"},"thermal":{"status":"NOT_MEASURABLE","reason":"not exposed by current project instrumentation"}}}
    lines=[manifest]; rss=[]; cpu0=resource.getrusage(resource.RUSAGE_SELF); t0=time.monotonic()
    child_env=dict(os.environ); child_env["SPATIAL_BENCHMARK_MODE"]=a.mode
    timing_path=Path(tempfile.mkstemp(prefix="phase1-timing-",suffix=".jsonl")[1])
    if a.mode=="acquisition": cmd=[sys.executable,str(root/"tools/acquisition_baseline.py"),"--duration",str(a.duration)]
    elif a.mode in ("interaction","render","full"): cmd=[sys.executable,str(root/"tools/live_demo.py"),"--duration",str(a.duration),"--timing-output",str(timing_path)]
    else: cmd=[str(root/"native/SpatialInteraction.app/Contents/MacOS/SpatialInteraction")]
    exit_code=0
    try:
        proc,stdout,stderr,rss_samples,child_cpu=run_child(cmd,root,child_env,a.duration)
        exit_code=proc.returncode; payload=None
        try: payload=json.loads(stdout) if a.mode=="acquisition" else json.loads(stdout.splitlines()[-1])
        except (json.JSONDecodeError, IndexError): pass
        if payload:
            for key in ("frames","observations_received","interaction_updates","presentation_writes"): 
                if key in payload: lines.append(record(run,a.mode,key,payload[key],payload[key],exit_code=proc.returncode))
            rates=payload.get("rates",{})
            for key,value in rates.items(): lines.append(record(run,"runtime",key,value,1,source="native/Python live result"))
            lines.append(record(run,"runtime","process_result",None,payload.get("observations_received",0),exit_code=proc.returncode,summary=payload))
        if timing_path.exists():
            timing_records=[json.loads(x) for x in timing_path.read_text().splitlines() if x.strip()]
            for timing in timing_records: lines.append(record(run,"timing","frame",timing,1,frame_id=timing.get("frame_id"),sequence=timing.get("sequence")))
        else: lines.append(record(run,a.mode,"process_result",None,0,exit_code=proc.returncode,stdout_tail=stdout[-2000:],stderr_tail=stderr[-4000:]))
        for identity,samples in rss_samples.items():
            lines.append(record(run,"resources","rss_samples",samples,len(samples),process_identity=identity))
            lines.append(record(run,"resources","rss_summary",rss_summary(samples),len(samples),process_identity=identity))
        lines.append(record(run,"resources","cpu_process",child_cpu,1,process_identity=child_cpu.get("process_identity"),pid=child_cpu.get("pid")))
    except Exception as e:
        lines.append(record(run,a.mode,"error",None,0,error=repr(e)))
    cpu1=resource.getrusage(resource.RUSAGE_SELF); elapsed=time.monotonic()-t0
    lines.append(record(run,"resources","cpu_time_s",(cpu1.ru_utime-cpu0.ru_utime)+(cpu1.ru_stime-cpu0.ru_stime),1,method="wrapper process CPU time",unit="s"))
    lines.append(record(run,"resources","peak_rss",cpu1.ru_maxrss,1,unit="bytes on macOS"))
    lines.append(record(run,"resources","python_wrapper_cpu_time_s",(cpu1.ru_utime-cpu0.ru_utime)+(cpu1.ru_stime-cpu0.ru_stime),1,method="wrapper diagnostic only; not child CPU"))
    manifest["duration_observed_s"]=elapsed; manifest["record_count"]=len(lines); lines[0]=manifest
    artifact.write_text("\n".join(json.dumps(x,separators=(",",":")) for x in lines)+"\n",encoding="utf8")
    print(json.dumps({"status":"written","schema":SCHEMA,"run_id":run,"artifact":str(artifact),"records":len(lines)},separators=(",",":")))
    return 0 if exit_code == 0 else 2
if __name__=="__main__": raise SystemExit(main())
