"""Python-authoritative live Vision bridge: native host observations -> Scene -> presentation."""
import argparse, json, subprocess, sys, time, math, threading
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from spatial_system.contracts import SceneObjectState, TimeRef, Validity
from spatial_system.geometry import Quaternion, Transform
from spatial_system.interaction import InteractionState
from spatial_system.scene import Scene

def signed_angle_delta(current, previous):
    return (current - previous + math.pi) % (2 * math.pi) - math.pi

class PinchRotationController:
    """One-hand pinch state with hysteresis and horizontal-drag Z rotation."""
    ROTATION_SENSITIVITY = 1.0  # radians per normalized screen-width of horizontal drag
    DEADZONE = 0.005
    PINCH_ENTER = 0.06
    PINCH_EXIT = 0.075
    def __init__(self): self.reset()
    def reset(self): self.pinching=False; self.controller_id=None; self.previous_x=None; self.last_delta=0.0
    def update(self, hands):
        candidate=None
        for hand in hands:
            lm=hand.get("landmarks",[])
            if len(lm) > 8:
                distance=math.dist(lm[4][:2],lm[8][:2])
                limit=self.PINCH_EXIT if self.pinching and self.controller_id == hand.get("hand_id") else self.PINCH_ENTER
                if distance <= limit: candidate=(hand,distance); break
        if candidate is None:
            self.reset(); return {"pinching":False,"distance":None,"delta":0.0,"controller_id":None}
        hand,distance=candidate; ident=hand.get("hand_id")
        if not self.pinching or self.controller_id != ident: self.pinching=True; self.controller_id=ident; self.previous_x=hand["landmarks"][0][0]; self.last_delta=0.0
        else:
            x=hand["landmarks"][0][0]; self.last_delta=x-self.previous_x; self.previous_x=x
        delta=self.last_delta if abs(self.last_delta) >= self.DEADZONE else 0.0
        return {"pinching":True,"distance":distance,"delta":delta,"controller_id":ident}

class TwoHandScaleController:
    def __init__(self): self.previous_distance=None
    def update(self,hands):
        if len(hands)!=2: self.previous_distance=None; return None
        a,b=hands[0]["landmarks"][0],hands[1]["landmarks"][0]; distance=math.dist(a[:2],b[:2])
        factor=distance/self.previous_distance if self.previous_distance and self.previous_distance>1e-6 else 1.0; self.previous_distance=distance
        return factor

def encode(scene, hands):
    objects=[]
    for o in scene.objects.values():
        t=o.transform; objects.append({"object_id":o.object_id,"selected":o.selected,"visible":o.visible,"translation":[t.translation.x,t.translation.y,t.translation.z],"rotation":[t.rotation.w,t.rotation.x,t.rotation.y,t.rotation.z],"scale":[t.scale.x,t.scale.y,t.scale.z]})
    return {"type":"presentation","scene_revision":scene.revision,"backend_id":"appkit-live-display","objects":objects,"hands":hands}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--duration",type=float,default=None); args=parser.parse_args()
    host=Path(__file__).parents[1]/"native/SpatialInteraction.app/Contents/MacOS/SpatialInteraction"
    if not host.is_file(): raise SystemExit(f"build host first: {host}")
    launch_time=time.monotonic(); launch_env={k:v for k,v in __import__('os').environ.items() if k in {"PATH","HOME","TMPDIR","XPC_SERVICE_NAME","__CF_USER_TEXT_ENCODING"}}
    print(json.dumps({"driver_pid":__import__('os').getpid(),"native_executable":str(host.resolve()),"cwd":str(Path.cwd()),"env":launch_env},separators=(",",":")),flush=True)
    p=subprocess.Popen([str(host)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1)
    print(json.dumps({"native_pid":p.pid,"poll_0ms":p.poll()},separators=(",",":")),flush=True)
    native_diagnostics=[]
    def drain_stderr():
        for line in p.stderr:
            native_diagnostics.append(line.rstrip())
    stderr_thread=threading.Thread(target=drain_stderr); stderr_thread.start()
    for delay in (0.1,0.5,1.0,2.0,5.0):
        def snapshot(d=delay):
            time.sleep(d); print(json.dumps({"native_pid":p.pid,"poll_after_s":d,"poll":p.poll()},separators=(",",":")),flush=True)
        threading.Thread(target=snapshot,daemon=True).start()
    if args.duration is not None:
        def stop_child():
            time.sleep(args.duration)
            if p.poll() is None: p.terminate()
        threading.Thread(target=stop_child,daemon=True).start()
    scene=Scene({"live-cube":SceneObjectState("live-cube",None,Transform.identity("world"),False,True,"procedural-cube")}); interaction=InteractionState(); previous=None; pinch=PinchRotationController(); two_hand=TwoHandScaleController(); frame_times=[]; observations=0; updates=0; presentations=0
    try:
        for line in p.stdout:
            msg=json.loads(line)
            if msg.get("type")!="observation": continue
            observations+=1; updates+=1
            hands=msg.get("hands",[]); count=len(hands); interaction.update(count,True)
            frame_times.append(time.monotonic()); frame_times=frame_times[-30:]
            active="NONE"
            now=TimeRef(msg["timestamp_ns"],msg["timestamp_domain"],msg["timestamp_origin"])
            if count:
                hand=hands[0]; lm=hand["landmarks"]; wrist=lm[0]; x,y=wrist[0],wrist[1]
                if not scene.objects["live-cube"].selected: scene.apply(interaction.event("select","live-cube",now,{},hand.get("confidence",0)))
                pinch_result=pinch.update(hands)
                if previous is not None and not pinch_result["pinching"]: scene.apply(interaction.event("translate","live-cube",now,{"delta":((x-previous[0])*2,(y-previous[1])*2,0)},hand.get("confidence",0))); active="TRANSLATE"
                previous=(x,y)
                if pinch_result["pinching"]:
                    d=pinch_result["delta"]; scene.apply(interaction.event("rotate","live-cube",now,{"rotation":Quaternion(math.cos(d/2),0,0,math.sin(d/2))},hand.get("confidence",0))); active="ROTATE"
                    print(json.dumps({"stage":"pinch_rotation","controller_id":pinch_result["controller_id"],"pinch_distance":pinch_result["distance"],"controller_x":x,"x_delta":d,"rotation_quaternion":[scene.objects["live-cube"].transform.rotation.w,scene.objects["live-cube"].transform.rotation.x,scene.objects["live-cube"].transform.rotation.y,scene.objects["live-cube"].transform.rotation.z]},separators=(",",":")),file=sys.stderr,flush=True)
                elif count == 2:
                    factor=two_hand.update(hands); confidence=min(hand.get("confidence",0),hands[1].get("confidence",0))
                    if factor is not None: scene.apply(interaction.event("scale","live-cube",now,{"factor":max(0.8,min(1.25,factor))},confidence)); active="SCALE"
                else: two_hand.update([])
            else:
                pinch.reset(); two_hand.update([])
            payload=encode(scene,[[list(point) for point in h["landmarks"]] for h in hands]); interaction_rate=(len(frame_times)-1)/(frame_times[-1]-frame_times[0]) if len(frame_times)>1 and frame_times[-1]>frame_times[0] else 0.0; payload.update({"hands_count":count,"active_interaction":active,"interaction_fps":interaction_rate,"camera_fps":msg.get("camera_fps",0.0),"vision_fps":msg.get("vision_fps",0.0)});
            if active == "SCALE+ROTATE":
                t=scene.objects["live-cube"].transform
                payload["rotation_trace"]={"quaternion":[t.rotation.w,t.rotation.x,t.rotation.y,t.rotation.z],"z_angle_rad":2*math.atan2(t.rotation.z,t.rotation.w)}
            p.stdin.write(json.dumps(payload,separators=(",",":"))+"\n"); p.stdin.flush(); presentations+=1
    except KeyboardInterrupt: pass
    finally:
        if p.poll() is None: p.terminate()
        p.wait(timeout=3)
        stderr_thread.join(timeout=2)
        print(json.dumps({"driver_pid":__import__("os").getpid(),"native_pid":p.pid,"lifetime_s":time.monotonic()-launch_time,"native_exit":p.returncode,"observations_received":observations,"interaction_updates":updates,"presentation_writes":presentations,"native_diagnostics":len(native_diagnostics),"native_all":native_diagnostics},separators=(",",":")),flush=True)
if __name__=="__main__": main()
