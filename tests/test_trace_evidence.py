import json,tempfile,unittest
from pathlib import Path
from tools.trace_evidence import main
class TraceEvidenceTests(unittest.TestCase):
 def test_trace_has_stable_correlation_fields(self):
  with tempfile.TemporaryDirectory() as d:
   i=Path(d)/"i.jsonl"; o=Path(d)/"o.jsonl"; i.write_text(json.dumps({"frame_id":"f1","sequence":4,"timestamp_ns":8,"hands":[],"scene_revision":2,"objects":[]})+"\n")
   import sys; old=sys.argv; sys.argv=["trace","--input",str(i),"--output",str(o)]
   try: main()
   finally: sys.argv=old
   x=json.loads(o.read_text()); self.assertEqual(x["frame_id"],"f1"); self.assertEqual(x["sequence"],4); self.assertIn("presentation_state",x); self.assertIn("render_event",x)
