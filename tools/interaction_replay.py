"""Versioned interaction recording/replay through the canonical Scene path."""
import argparse, json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from spatial_system.contracts import SceneObjectState, TimeRef, InteractionEvent
from spatial_system.geometry import Quaternion, Transform, Vec3
from spatial_system.scene import Scene

def run(path):
    scene=Scene({f"object-{i}":SceneObjectState(f"object-{i}",None,Transform("world","world",Vec3((i-1)*1.5,0,0)),i==1,True,"model",{"asset_id":"assets/phase1-cube.obj"}) for i in range(3)})
    count=0
    for raw in Path(path).read_text().splitlines():
        rec=json.loads(raw); count+=1
        event=rec.get("event")
        if event:
            tm=TimeRef(event["timestamp_ns"],event["timestamp_domain"],event["timestamp_origin"])
            params=dict(event.get("parameters",{}))
            if isinstance(params.get("rotation"),list): params["rotation"]=Quaternion(*params["rotation"])
            action=event["action"]
            if action == "reset": scene.reset_object(event["target_id"])
            elif action == "visibility": scene.set_visibility(event["target_id"],params["visible"])
            else: scene.apply(InteractionEvent(f"replay-{count}",action,event.get("target_id"),params,tm,None,event.get("confidence",1),event.get("authorized",True)))
    print(json.dumps({"status":"REPLAY","records":count,"scene_revision":scene.revision,"objects":len(scene.objects),"final_objects":[{"object_id":o.object_id,"translation":[o.transform.translation.x,o.transform.translation.y,o.transform.translation.z],"rotation":[o.transform.rotation.w,o.transform.rotation.x,o.transform.rotation.y,o.transform.rotation.z],"scale":[o.transform.scale.x,o.transform.scale.y,o.transform.scale.z]} for o in scene.objects.values()]},separators=(",",":")))

if __name__ == "__main__":
    p=argparse.ArgumentParser(); p.add_argument("--replay",type=Path,required=True); run(p.parse_args().replay)
