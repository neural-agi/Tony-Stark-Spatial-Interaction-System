import unittest
from spatial_system.perception import *
class PerceptionTests(unittest.TestCase):
 def test_scenarios_and_comparable_evaluation(self):
  ms=PerceptionMeasurement("single_hand",1,.9,0,0,0,1,1,0,0,1,2,None,None,None,0); e=PerceptionEvaluation("candidate-a",{"mode":"test"},(ms,),"run-1"); self.assertEqual(e.measurements[0].scenario,"single_hand"); self.assertRaises(ValueError,lambda:PerceptionEvaluation("x",{},(PerceptionMeasurement("unknown",0,None,None,None,None,None,None,0,None,None,None,None,None,None,None),),"r"))
