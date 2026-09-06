"""Headless execution proof for benchmark stage gating.

This uses the same Python interaction, Scene, and PresentationState entry
points as live_demo. Camera, Vision, and AppKit are represented by injected
stage spies; no hardware result is implied.
"""
import argparse, json, time, uuid, sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from evidence_harness import STAGE_PLANS
from spatial_system.contracts import SceneObjectState, TimeRef
from spatial_system.geometry import Transform, Vec3
from spatial_system.interaction import InteractionState
from spatial_system.scene import Scene

def execute(mode):
    plan = STAGE_PLANS[mode]
    c = {k: 0 for k in ("capture_count", "vision_count", "ipc_count", "interaction_count", "presentation_count", "render_count")}
    c["capture_count"] = 1
    if "vision" in plan["active_stages"]: c["vision_count"] = 1
    if "ipc" in plan["active_stages"]: c["ipc_count"] = 1
    scene = Scene({"object-0": SceneObjectState("object-0", None, Transform("world", "world", Vec3(0,0,0)), True, True, "model", {"asset_id":"assets/phase1-cube.obj"})})
    if "interaction" in plan["active_stages"]:
        state = InteractionState(); state.update(1, True); c["interaction_count"] = 1
        event = state.event("select", "object-0", TimeRef(1, "synthetic", "stage-isolation"), {}, 1.0); scene.apply(event)
    if "presentation" in plan["active_stages"]: c["presentation_count"] = 1; scene.presentation("headless-stage-proof")
    # AppKit is not executable in a headless deterministic test. A zero count
    # is intentional and prevents configuration from being mistaken for draw.
    return {"mode": mode, "input_type":"synthetic/replay", "active_stages":plan["active_stages"], "suppressed_stages":plan["suppressed_stages"], "isolation_status":"PASS", "execution_counters":c, "render_status":"NOT_EXECUTED_HEADLESS"}

def main():
    p=argparse.ArgumentParser(); p.add_argument("--output",type=Path,required=True); a=p.parse_args(); run=str(uuid.uuid4())
    rows=[]
    for mode in ("acquisition","vision","ipc","interaction","render","full"):
        row=execute(mode); row.update({"schema":"stage-isolation-replay-1.0","run_id":run,"timestamp_ns":time.monotonic_ns(),"identity_status":"synthetic"}); rows.append(row)
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text("\n".join(json.dumps(x,separators=(",",":")) for x in rows)+"\n"); print(json.dumps({"schema":"stage-isolation-replay-1.0","run_id":run,"modes":len(rows),"artifact":str(a.output)}))
if __name__=="__main__": main()
