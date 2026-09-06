import unittest
from spatial_system.contracts import *
from spatial_system.geometry import *
from spatial_system.interaction import InteractionState
from spatial_system.scene import Scene
T=TimeRef(1,"test","mono")
class SceneTests(unittest.TestCase):
 def setUp(self): self.scene=Scene({k:SceneObjectState(k,None,Transform.identity("world"),False,True,"mesh",{"asset":k}) for k in ("a","b")})
 def test_identity_selection_visibility_and_revision(self):
  self.scene.select("b"); self.assertTrue(self.scene.objects["b"].selected); self.assertFalse(self.scene.objects["a"].selected); self.assertGreater(self.scene.revision,0); self.assertTrue(self.scene.objects["a"].visible)
 def test_transform_actions_and_hierarchy_invariant(self):
  self.scene.apply(InteractionState().event("translate","b",T,{"delta":(1,0,0)})); self.assertEqual(self.scene.objects["b"].transform.translation,Vec3(1,0,0)); self.assertRaises(ValueError,lambda:Scene({"a":SceneObjectState("a","missing",Transform.identity("world"),False,True,"mesh")}))
 def test_keyboard_scene_management_is_scene_owned(self):
  self.scene.set_visibility("b",False); self.assertFalse(self.scene.objects["b"].visible)
  self.scene.set_visibility("b",True); self.scene.reset_object("b")
  self.assertTrue(self.scene.objects["b"].visible); self.assertEqual(self.scene.objects["b"].transform.translation,Vec3(0,0,0)); self.assertEqual(self.scene.objects["b"].transform.scale,Vec3(1,1,1))
 def test_visibility_is_independent_from_selection(self):
  self.scene.select("b"); before=self.scene.revision
  self.scene.set_visibility("b",False)
  self.assertFalse(self.scene.objects["b"].visible); self.assertTrue(self.scene.objects["b"].selected); self.assertGreater(self.scene.revision,before)
  self.scene.set_visibility("a",True); self.assertTrue(self.scene.objects["b"].selected); self.assertFalse(self.scene.objects["a"].selected)
