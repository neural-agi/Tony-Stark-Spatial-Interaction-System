"""Convert a live JSONL recording into a durable correlation trace."""
import argparse,json,uuid,time
from pathlib import Path
def main():
 p=argparse.ArgumentParser(); p.add_argument("--input",required=True,type=Path); p.add_argument("--output",required=True,type=Path); a=p.parse_args(); run=str(uuid.uuid4()); out=[]
 for n,line in enumerate(a.input.read_text().splitlines()):
  r=json.loads(line); frame=r.get("frame_id"); seq=r.get("sequence"); obs=r.get("observation_id"); identity_status="authoritative" if frame is not None and seq is not None else "missing_native_identity"
  out.append({"schema":"phase1-trace-1.0","run_id":run,"frame_id":frame,"sequence":seq,"identity_status":identity_status,"timestamp_ns":r.get("timestamp_ns",r.get("timestamp")),"observation_id":obs,"hand_state":{"hand_count":len(r.get("hands",[]))},"interaction_event":r.get("event"),"scene_revision":r.get("scene_revision"),"object_state":r.get("resulting_objects",r.get("objects")),"presentation_state":{"scene_revision":r.get("scene_revision"),"objects":r.get("resulting_objects",r.get("objects"))},"render_event":{"status":"presentation_written","sequence":seq}})
 a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text("\n".join(json.dumps(x,separators=(",",":")) for x in out)+("\n" if out else "")); print(json.dumps({"schema":"phase1-trace-1.0","run_id":run,"entries":len(out),"artifact":str(a.output)}))
if __name__=="__main__": main()
