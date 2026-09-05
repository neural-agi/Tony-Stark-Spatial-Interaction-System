"""Deterministic synthetic end-to-end demo driver; no camera or perception."""
import json, subprocess, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parents[1] / "src"))
from spatial_system.contracts import SceneObjectState, TimeRef
from spatial_system.geometry import Quaternion, Transform
from spatial_system.interaction import InteractionState
from spatial_system.scene import Scene

def encode(state):
    objects=[]
    for o in state.objects:
        t=o.transform
        objects.append({"object_id":o.object_id,"selected":o.selected,"visible":o.visible,
                        "translation":[t.translation.x,t.translation.y,t.translation.z],
                        "rotation":[t.rotation.w,t.rotation.x,t.rotation.y,t.rotation.z],"scale":[t.scale.x,t.scale.y,t.scale.z]})
    return json.dumps({"scene_revision":state.scene_revision,"backend_id":state.backend_id,"objects":objects},separators=(",",":"))

def main():
    executable=Path(__file__).parents[1]/"native"/"SyntheticDemo"
    if not executable.is_file(): raise SystemExit(f"native renderer is not built: {executable}")
    process=subprocess.Popen([str(executable)],stdin=subprocess.PIPE,text=True)
    scene=Scene({"demo-cube":SceneObjectState("demo-cube",None,Transform.identity("world"),False,True,"procedural-cube",{"demo":True})})
    interaction=InteractionState(); now=0
    steps=[("select",{}),("translate",{"delta":(0.45,0.15,0)}),("rotate",{"rotation":Quaternion(0.968912,0,0.247404,0)}),("scale",{"factor":1.25}),("reset",{})]
    try:
        while process.poll() is None:
            interaction.update(1,True); now += 1_000_000_000
            action, params=steps[(now//1_000_000_000-1)%len(steps)]
            if action == "reset":
                scene.objects["demo-cube"]=SceneObjectState("demo-cube",None,Transform.identity("world"),False,True,"procedural-cube",{"demo":True}); scene.revision += 1
            else: scene.apply(interaction.event(action,"demo-cube",TimeRef(now,"synthetic-demo","deterministic-step"),params))
            process.stdin.write(encode(scene.presentation("appkit-local-display",frozenset({"local_display","wireframe_3d"}))+"\n")); process.stdin.flush(); time.sleep(1.8)
    except (BrokenPipeError, KeyboardInterrupt): pass
    finally:
        if process.poll() is None: process.terminate()
        process.wait(timeout=3)

if __name__ == "__main__": main()
