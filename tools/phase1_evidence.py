"""Versioned Phase 1 evidence infrastructure and operator scenario records.

This module creates evidence hooks/manifests; it never upgrades unexecuted
hardware scenarios to PASS.
"""
import argparse, json, platform, time, uuid
from pathlib import Path
from statistics import mean, pstdev

SCHEMA="phase1-evidence-suite-1.0"
SCENARIO_GROUPS={
 "tracking":["stationary","slow_movement","rapid_movement","hand_entry","hand_exit","reacquisition","one_to_two","two_to_one","identity_continuity"],
 "gesture":["translation_lifecycle","pinch_rotation_lifecycle","scale_lifecycle","selection","repetition","neutral_motion","confusable_motion","false_activation"],
 "environment":["normal_lighting","reduced_lighting","contrast","clutter","motion_blur","camera_position"],
 "occlusion":["partial_hand","self_occlusion","object_occlusion","camera_blockage"],
 "degradation":["no_hand","low_confidence","invalid_observation","stale_observation","frame_loss","interruption","hand_loss_reacquisition"],
 "multi_hand":["one_hand_baseline","two_hand","count_transition","identity_continuity","ambiguity","scale_isolation","pinch_isolation","translation_isolation"],
}
def manifest(run_id=None, mode="unexecuted", duration_s=0, **extra):
    return {"schema":SCHEMA,"run_id":run_id or str(uuid.uuid4()),"created_ns":time.time_ns(),"mode":mode,"duration_s":duration_s,"hardware":platform.platform(),"os":platform.platform(),"status":"IMPLEMENTED_INFRASTRUCTURE","telemetry":{"gpu":{"status":"NOT_MEASURABLE","reason":"no reliable project telemetry"},"thermal":{"status":"NOT_MEASURABLE","reason":"no reliable project telemetry"}},**extra}
def scenario_record(run_id, group, scenario_id, operator_required=True, **extra):
    return {"schema":SCHEMA,"run_id":run_id,"group":group,"scenario_id":scenario_id,"result":"OPERATOR_REQUIRED" if operator_required else "NOT_EXECUTED","evidence_status":"OPERATOR_REQUIRED" if operator_required else "AUTOMATED_REPLAY","duration_s":None,"observations":0,"detections":0,"confidence":[],"validity":[],"transitions":[],"diagnostics":[],**extra}
def spatial_jitter(points):
    """Return per-axis and RMS jitter for repeated normalized landmark samples."""
    if not points: return {"status":"NOT_MEASURABLE","sample_count":0}
    n=len(points); dims=len(points[0]); axes=[]
    for i in range(dims): axes.append(pstdev(float(p[i]) for p in points))
    displacements=[sum((float(points[i][j])-float(points[i-1][j]))**2 for j in range(dims))**.5 for i in range(1,n)]
    def percentile(xs,p): return sorted(xs)[min(len(xs)-1,int((p/100)*(len(xs)-1)+.5))] if xs else None
    return {"status":"MEASURED","sample_count":n,"axis_stddev":axes,"rms":(mean(x*x for x in axes))**.5,"mean_displacement":mean(displacements) if displacements else None,"p95_displacement":percentile(displacements,95),"p99_displacement":percentile(displacements,99),"coordinate_space":"normalized_image"}
def sustained_summary(snapshots):
    if not snapshots: return {"status":"NOT_MEASURABLE"}
    return {"status":"MEASURED","phases":{"startup":snapshots[0],"early_steady":snapshots[min(1,len(snapshots)-1)],"mid_run":snapshots[len(snapshots)//2],"late_run":snapshots[-1]},"sample_count":len(snapshots)}
def classify_ceiling(runs, stable_key="stable"):
    valid=[r for r in runs if r.get(stable_key) is True]
    return {"status":"ESTABLISHED","ceiling":max((r.get("rate") for r in valid),default=None)} if valid else {"status":"NOT_MEASURABLE","reason":"no defensible stable operating point"}
def benchmark_plan(run_id, modes=("acquisition","vision","ipc","interaction","render","full"), durations=(5,30)):
    return {"schema":SCHEMA,"run_id":run_id,"kind":"benchmark_plan","stability_criterion":{"minimum_repetitions":3,"no_sequence_gaps":True,"bounded_p95_jitter":True,"stable_memory_classification":True},"runs":[{"mode":m,"duration_s":d,"status":"NOT_EXECUTED"} for m in modes for d in durations]}
def operator_checklist(run_id):
    ids=["select_1","select_2","select_3","translation","pinch_rotation","two_hand_scale","reset","hide","show_all","object_independence","hand_loss_reacquisition","asset_rendering"]
    return {"schema":SCHEMA,"run_id":run_id,"kind":"operator_acceptance","items":[{"scenario_id":x,"result":"OPERATOR_REQUIRED","setup":None,"expected":None,"observed":None,"artifact":None} for x in ids]}
def coordinate_record(run_id, samples, orientation="native", mirrored=False):
    return {"schema":SCHEMA,"run_id":run_id,"kind":"coordinate_validation","orientation":orientation,"mirrored":mirrored,"normalization":"Vision normalized coordinates","samples":len(samples),"mapped_jitter":spatial_jitter(samples) if samples else {"status":"NOT_MEASURABLE"}}
def generate_suite(path, run_id=None):
    run_id=run_id or str(uuid.uuid4()); rows=[manifest(run_id,mode="scenario-suite")]
    for group,ids in SCENARIO_GROUPS.items():
        for sid in ids: rows.append(scenario_record(run_id,group,sid,True))
    path.parent.mkdir(parents=True,exist_ok=True); path.write_text("\n".join(json.dumps(x,separators=(",",":")) for x in rows)+"\n"); return run_id
def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); rid=generate_suite(a.output); print(json.dumps({"schema":SCHEMA,"run_id":rid,"artifact":str(a.output)}))
if __name__=="__main__": main()
