import unittest
from spatial_system.contracts import *
T=TimeRef(10,"test","monotonic")
class ContractTests(unittest.TestCase):
 def test_frame_metadata_schema_and_timestamp(self):
  f=RawFrame("f","cam",T,1,640,480,"rgb","upright",False); self.assertEqual(f.schema_version,"1.0"); self.assertEqual(f.time.domain,"test"); self.assertEqual(f.source_id,"cam")
 def test_landmarks_metadata_and_validity_confidence(self):
  h=HandLandmarks("h",((0.,0.,0.),),"image",T,.5,Validity.DEGRADED,trace=TraceRef("cam","f","o")); self.assertEqual(h.trace.frame_id,"f"); self.assertNotEqual(Validity.INVALID,Validity.DEGRADED); self.assertRaises(ValueError,lambda:HandLandmarks("h",(),"",T,1.2,Validity.VALID))
 def test_hand_state_freshness_units_continuity(self):
  s=HandState("s","h",(0,0,0),(1,0,0,0),"world",T,.8,Validity.VALID,0,TemporalStatus.OBSERVED,"continuous",units="meters"); self.assertEqual(s.units,"meters"); self.assertEqual(s.freshness_ns,0)
 def test_gesture_and_trace_references(self):
  g=GestureHypothesis("g","select","onset",.9,T,True,False,False,(10,10),"s"); self.assertEqual(g.source_state_id,"s"); self.assertEqual(TraceRef("c","f",sequence if False else None).source_id,"c")
