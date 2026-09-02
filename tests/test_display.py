import unittest
from spatial_system.scene import Scene
from spatial_system.display import RecordingDisplay
class DisplayTests(unittest.TestCase):
 def test_presentation_and_scene_revision_propagate(self):
  d=RecordingDisplay(); s=Scene({}); p=s.presentation(d.backend_id,d.capabilities); self.assertEqual(p.scene_revision,s.revision); self.assertTrue(d.present(p).startswith("presentation-")); self.assertEqual(d.frames[0],p)
