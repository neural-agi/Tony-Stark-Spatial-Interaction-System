import unittest
from spatial_system.contracts import TimeRef
from spatial_system.interaction import *
T=TimeRef(1,"test","mono")
class InteractionTests(unittest.TestCase):
 def test_deterministic_hand_lifecycle(self):
  s=InteractionState(); s.update(1); self.assertEqual(s.mode,HandMode.ONE); s.update(2); self.assertEqual(s.mode,HandMode.TWO); s.update(0,False); self.assertEqual(s.mode,HandMode.LOST); s.update(1); self.assertEqual(s.mode,HandMode.ONE); self.assertRaises(ValueError,lambda:s.update(3))
 def test_event_actions_and_authorization(self):
  s=InteractionState();
  for action in ("select","translate","rotate","scale"): self.assertEqual(s.event(action,"o",T,{},.8,True,"state").action,action)
  self.assertRaises(ValueError,lambda:s.event("bad",None,T,{}))
