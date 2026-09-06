"""Python-authoritative live Vision bridge: native host observations -> Scene -> presentation."""
import argparse, json, subprocess, sys, time, math, threading
from dataclasses import asdict
from pathlib import Path
sys.path.insert(0,str(Path(__file__).parents[1]/"src"))
from spatial_system.contracts import SceneObjectState, TimeRef, Validity
from spatial_system.geometry import Quaternion, Transform, Vec3
from spatial_system.interaction import InteractionState
from spatial_system.scene import Scene
from spatial_system.measurement import FrameTiming, FrameTimingRegistry, summarize_timings, interval_summary

def signed_angle_delta(current, previous):
    return (current - previous + math.pi) % (2 * math.pi) - math.pi

class PinchRotationController:
    """One-hand pinch state with hysteresis and horizontal-drag Z rotation."""
    ROTATION_SENSITIVITY = 2.0  # radians per normalized screen-width of horizontal drag
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
        t=o.transform; objects.append({"object_id":o.object_id,"selected":o.selected,"visible":o.visible,"asset_id":o.metadata.get("asset_id","procedural-cube"),"translation":[t.translation.x,t.translation.y,t.translation.z],"rotation":[t.rotation.w,t.rotation.x,t.rotation.y,t.rotation.z],"scale":[t.scale.x,t.scale.y,t.scale.z],"metadata":dict(o.metadata)})
    return {"type":"presentation","scene_revision":scene.revision,"backend_id":"appkit-live-display","objects":objects,"hands":hands}

def main():
    parser=argparse.ArgumentParser(); parser.add_argument("--duration",type=float,default=None); parser.add_argument("--record",type=Path); parser.add_argument("--timing-output",type=Path); args=parser.parse_args()
    host=Path(__file__).parents[1]/"native/SpatialInteraction.app/Contents/MacOS/SpatialInteraction"
    if not host.is_file(): raise SystemExit(f"build host first: {host}")
    launch_time=time.monotonic(); launch_env={k:v for k,v in __import__('os').environ.items() if k in {"PATH","HOME","TMPDIR","XPC_SERVICE_NAME","__CF_USER_TEXT_ENCODING"}}
    print(json.dumps({"driver_pid":__import__('os').getpid(),"native_executable":str(host.resolve()),"cwd":str(Path.cwd()),"env":launch_env},separators=(",",":")),flush=True)
    mode=__import__('os').environ.get("SPATIAL_BENCHMARK_MODE", "full")
    child_env=dict(__import__('os').environ); child_env["SPATIAL_BENCHMARK_MODE"]=mode
    p=subprocess.Popen([str(host)],stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True,bufsize=1,env=child_env)
    print(json.dumps({"native_pid":p.pid,"poll_0ms":p.poll()},separators=(",",":")),flush=True)
    native_diagnostics=[]; native_cpu_accounting=None
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
    asset_ids=["assets/phase1-cube.obj","assets/phase1-triangle.gltf","assets/phase1-triangle.glb"]
    scene=Scene({f"object-{i}":SceneObjectState(f"object-{i}",None,Transform("world","world",Vec3((i-1)*1.5,0,0)),i==1,True,"model",{"asset_id":asset_ids[i]}) for i in range(3)}); interaction=InteractionState(); timing_registry=FrameTimingRegistry(); previous=None; pinch=PinchRotationController(); two_hand=TwoHandScaleController(); frame_times=[]; observations=0; updates=0; presentations=0; selected="object-1"; last_rates={}
    record_file=args.record.open("w") if args.record else None
    last_event=None
    def apply_event(event):
        nonlocal last_event
        last_event=event
        scene.apply(event)
    try:
        for line in p.stdout:
            msg=json.loads(line)
            if msg.get("type")=="render":
                timing=timing_registry.get(msg.get("frame_id"))
                if msg.get("identity_status")=="authoritative": timing_registry.bind_render(msg.get("frame_id"),msg.get("render_timestamp_ns"))
                continue
            if msg.get("type")=="cpu_accounting": native_cpu_accounting=msg; continue
            if msg.get("type")=="control":
                now=TimeRef(int(time.monotonic_ns()),"python-monotonic","live_demo control receipt")
                key=msg.get("key","")
                if key in "123":
                    selected=f"object-{int(key)-1}"; apply_event(interaction.event("select",selected,now,{},1.0)); scene.set_visibility(selected,True)
                elif key=="r": scene.reset_object(selected)
                elif key=="h": scene.set_visibility(selected,False)
                elif key=="a":
                    for object_id in scene.objects: scene.set_visibility(object_id,True)
                continue
            if msg.get("type")!="observation": continue
            observations+=1; updates+=1
            hands=msg.get("hands",[]); count=len(hands); interaction_start=time.monotonic_ns(); interaction.update(count,True)
            frame_times.append(time.monotonic()); frame_times=frame_times[-30:]
            active="NONE"
            now=TimeRef(msg["timestamp_ns"],msg["timestamp_domain"],msg["timestamp_origin"])
            if count:
                hand=hands[0]; lm=hand["landmarks"]; wrist=lm[0]; x,y=wrist[0],wrist[1]
                # Deterministic projected-target selection: nearest visible object in image X/Y.
                candidates=[o for o in scene.objects.values() if o.visible]; target=min(candidates,key=lambda o:(x-(0.5+o.transform.translation.x/3))**2+(y-(0.5+o.transform.translation.y/3))**2) if candidates else scene.objects[selected]
                if target.object_id != selected: selected=target.object_id; apply_event(interaction.event("select",selected,now,{},hand.get("confidence",0)))
                if not scene.objects[selected].selected: apply_event(interaction.event("select",selected,now,{},hand.get("confidence",0)))
                pinch_result=pinch.update(hands)
                if previous is not None and not pinch_result["pinching"] and count==1: apply_event(interaction.event("translate",selected,now,{"delta":((x-previous[0])*2,(y-previous[1])*2,0)},hand.get("confidence",0))); active="TRANSLATE"
                previous=(x,y)
                if pinch_result["pinching"]:
                    d=pinch_result["delta"] * pinch.ROTATION_SENSITIVITY; apply_event(interaction.event("rotate",selected,now,{"rotation":Quaternion(math.cos(d/2),0,0,math.sin(d/2))},hand.get("confidence",0))); active="ROTATE"
                    selected_object=next((o for o in scene.objects.values() if o.selected),None)
                    if selected_object is not None:
                        q=selected_object.transform.rotation
                        print(json.dumps({"stage":"pinch_rotation","controller_id":pinch_result["controller_id"],"pinch_distance":pinch_result["distance"],"controller_x":x,"x_delta":d,"selected_object":selected_object.object_id,"rotation_quaternion":[q.w,q.x,q.y,q.z]},separators=(",",":")),file=sys.stderr,flush=True)
                elif count == 2:
                    factor=two_hand.update(hands); confidence=min(hand.get("confidence",0),hands[1].get("confidence",0))
                    if factor is not None: apply_event(interaction.event("scale",selected,now,{"factor":max(0.8,min(1.25,factor))},confidence)); active="SCALE"
                else: two_hand.update([])
            else:
                pinch.reset(); two_hand.update([])
            presentation_ns=time.monotonic_ns(); payload=encode(scene,[[list(point) for point in h["landmarks"]] for h in hands]); interaction_rate=(len(frame_times)-1)/(frame_times[-1]-frame_times[0]) if len(frame_times)>1 and frame_times[-1]>frame_times[0] else 0.0; last_rates={"camera_fps":msg.get("camera_fps",0.0),"vision_fps":msg.get("vision_fps",0.0),"interaction_fps":interaction_rate,"render_fps":msg.get("render_fps")}; payload.update({"hands_count":count,"selected_object":selected,"active_interaction":active,"interaction_fps":interaction_rate,"camera_fps":msg.get("camera_fps",0.0),"vision_fps":msg.get("vision_fps",0.0),"render_fps":msg.get("render_fps"),"frame_id":msg.get("frame_id"),"source_id":msg.get("source_id"),"sequence":msg.get("sequence"),"source_timestamp_ns":msg.get("timestamp_ns"),"timestamp_domain":msg.get("timestamp_domain")}); timing_registry.put(FrameTiming(msg.get("frame_id"),msg.get("source_id"),msg.get("sequence"),msg.get("timestamp_ns"),msg.get("timestamp_domain"),msg.get("capture_receipt_timestamp_ns"),msg.get("vision_submit_timestamp_ns"),msg.get("vision_complete_timestamp_ns"),msg.get("ipc_send_timestamp_ns"),time.monotonic_ns(),presentation_ns,None))
            if record_file:
                event=None if last_event is None else {"action":last_event.action,"target_id":last_event.target_id,"parameters":last_event.parameters,"timestamp_ns":last_event.time.timestamp_ns,"timestamp_domain":last_event.time.domain,"timestamp_origin":last_event.time.origin,"confidence":last_event.confidence,"authorized":last_event.authorized}
                record_file.write(json.dumps({"version":"1.0","timestamp":msg["timestamp_ns"],"hands":hands,"active_interaction":active,"selected_object":selected,"event":event,"scene_revision":scene.revision,"resulting_objects":payload["objects"]},default=lambda x:[x.w,x.x,x.y,x.z] if isinstance(x,Quaternion) else str(x),separators=(",",":"))+"\n"); record_file.flush()
            last_event=None
            if active == "SCALE+ROTATE":
                selected_object=next((o for o in scene.objects.values() if o.selected),None)
                if selected_object is None: continue
                t=selected_object.transform
                payload["rotation_trace"]={"quaternion":[t.rotation.w,t.rotation.x,t.rotation.y,t.rotation.z],"z_angle_rad":2*math.atan2(t.rotation.z,t.rotation.w)}
            if mode != "interaction":
                p.stdin.write(json.dumps(payload,separators=(",",":"))+"\n"); p.stdin.flush(); presentations+=1
    except KeyboardInterrupt: pass
    finally:
        if record_file: record_file.close()
        if args.timing_output:
            args.timing_output.parent.mkdir(parents=True,exist_ok=True)
            with args.timing_output.open("w",encoding="utf8") as timing_file:
                for timing in timing_registry.values():
                    row=asdict(timing); row["schema"]="phase1-frame-timing-1.0"; row["latency_ms"]=timing.latency_samples(); timing_file.write(json.dumps(row,separators=(",",":"))+"\n")
                timing_file.write(json.dumps({"schema":"phase1-frame-timing-summary-1.0","latency_summaries":summarize_timings(timing_registry.values()),"interval_summaries":{k:interval_summary(timing_registry.values(),k) for k in ("capture_receipt_ns","vision_complete_ns","ipc_send_ns","interaction_update_ns","presentation_ns","render_ns")},"registry_evictions":timing_registry.evictions},separators=(",",":"))+"\n")
                timing_file.write(json.dumps({"schema":"phase1-process-accounting-1.0","native":native_cpu_accounting,"python":{"pid":__import__('os').getpid(),"process_identity":"python-benchmark","accounting_status":"runtime-wrapper-accounting-not-substituted"}},separators=(",",":"))+"\n")
        if p.poll() is None: p.terminate()
        p.wait(timeout=3)
        stderr_thread.join(timeout=2)
        print(json.dumps({"driver_pid":__import__("os").getpid(),"native_pid":p.pid,"lifetime_s":time.monotonic()-launch_time,"native_exit":p.returncode,"observations_received":observations,"interaction_updates":updates,"presentation_writes":presentations,"native_diagnostics":len(native_diagnostics),"rates":last_rates,"native_all":native_diagnostics},separators=(",",":")),flush=True)
if __name__=="__main__": main()
