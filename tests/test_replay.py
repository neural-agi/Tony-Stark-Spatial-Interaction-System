import contextlib, io, json, tempfile, unittest
from pathlib import Path
from tools.interaction_replay import run

class ReplayTests(unittest.TestCase):
    def test_event_replay_applies_scene_events_and_preserves_independence(self):
        t={"timestamp_ns":1,"timestamp_domain":"test","timestamp_origin":"fixture"}
        events=[]
        def e(action,target,parameters={}):
            x=dict(t); x.update(action=action,target_id=target,parameters=parameters,confidence=1,authorized=True); return {"version":"1.0","event":x}
        events += [e("select","object-0"), e("translate","object-0",{"delta":[1,2,0]}), e("scale","object-0",{"factor":2}), e("rotate","object-0",{"rotation":[0.70710678,0,0,0.70710678]}), e("select","object-1"), e("visibility","object-2",{"visible":False}), e("reset","object-1"), e("visibility","object-2",{"visible":True})]
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"events.jsonl"; p.write_text("\n".join(json.dumps(x) for x in events))
            out=io.StringIO()
            with contextlib.redirect_stdout(out): run(p)
            result=json.loads(out.getvalue())
            self.assertEqual(result["status"],"REPLAY"); self.assertEqual(result["records"],8); self.assertEqual(result["objects"],3)
            first=next(x for x in result["final_objects"] if x["object_id"]=="object-0")
            self.assertEqual(first["translation"],[-0.5,2,0]); self.assertEqual(first["scale"],[2,2,2])
    def test_malformed_replay_fails(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"bad.jsonl"; p.write_text("not-json\n")
            with self.assertRaises(json.JSONDecodeError): run(p)
