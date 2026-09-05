import unittest
import math
from tools.live_demo import signed_angle_delta, PinchRotationController, TwoHandScaleController
from spatial_system.contracts import TimeRef
from spatial_system.interaction import *
T=TimeRef(1,"test","mono")
class InteractionTests(unittest.TestCase):
 def hand(self,wrist,pinch,ident="h"):
  lm=[(wrist,0,0)]*21; lm[4]=(wrist+pinch,0,0); lm[8]=(wrist,0,0); return {"hand_id":ident,"landmarks":lm,"confidence":1}
 def test_pinch_hysteresis_and_horizontal_rotation(self):
  c=PinchRotationController(); self.assertFalse(c.update([self.hand(.4,.08)])["pinching"])
  self.assertTrue(c.update([self.hand(.4,.02)])["pinching"]); self.assertAlmostEqual(c.update([self.hand(.45,.02)])["delta"],.05)
  self.assertAlmostEqual(c.update([self.hand(.50,.02)])["delta"],.05); self.assertFalse(c.update([self.hand(.50,.08)])["pinching"])
 def test_pinch_deadzone_vertical_and_controller_isolation(self):
  c=PinchRotationController(); c.update([self.hand(.4,.02,"a")]); self.assertEqual(c.update([self.hand(.404,.02,"a")])["delta"],0)
  self.assertEqual(c.update([self.hand(.404,.02,"a")])["delta"],0)
  c.reset(); c.update([self.hand(.4,.02,"a"),self.hand(.8,.20,"b")]); self.assertAlmostEqual(c.update([self.hand(.45,.02,"a"),self.hand(.9,.20,"b")])["delta"],.05)
 def test_pinch_release_resets_and_two_hand_scale(self):
  c=PinchRotationController(); c.update([self.hand(.4,.02)]); c.update([]); self.assertFalse(c.pinching); self.assertIsNone(c.controller_id)
  s=TwoHandScaleController(); hands=[self.hand(.2,.2,"a"),self.hand(.8,.2,"b")]; self.assertIsNotNone(s.update(hands)); hands=[self.hand(.1,.2,"a"),self.hand(.9,.2,"b")]; self.assertGreater(s.update(hands),1)
 def test_no_pinch_two_hand_horizontal_motion(self):
  c=PinchRotationController(); hands=[self.hand(.2,.2,"a"),self.hand(.8,.2,"b")]; self.assertFalse(c.update(hands)["pinching"]); hands=[self.hand(.3,.2,"a"),self.hand(.9,.2,"b")]; self.assertFalse(c.update(hands)["pinching"])
 def test_signed_angle_delta_unwraps_boundaries(self):
  self.assertAlmostEqual(signed_angle_delta(0.1,2*math.pi-0.1),0.2)
  self.assertAlmostEqual(signed_angle_delta(2*math.pi-0.1,0.1),-0.2)
  self.assertAlmostEqual(signed_angle_delta(math.pi,-math.pi),0.0)
 def test_signed_angle_delta_continuous_multi_frame_rotation(self):
  angles=[6.1,6.2,0.05,0.15]; total=sum(signed_angle_delta(b,a) for a,b in zip(angles,angles[1:])); self.assertAlmostEqual(total,0.333185307,6)
 def test_deterministic_hand_lifecycle(self):
  s=InteractionState(); s.update(1); self.assertEqual(s.mode,HandMode.ONE); s.update(2); self.assertEqual(s.mode,HandMode.TWO); s.update(0,False); self.assertEqual(s.mode,HandMode.LOST); s.update(1); self.assertEqual(s.mode,HandMode.ONE); self.assertRaises(ValueError,lambda:s.update(3))
 def test_event_actions_and_authorization(self):
  s=InteractionState();
  for action in ("select","translate","rotate","scale"): self.assertEqual(s.event(action,"o",T,{},.8,True,"state").action,action)
  self.assertRaises(ValueError,lambda:s.event("bad",None,T,{}))
