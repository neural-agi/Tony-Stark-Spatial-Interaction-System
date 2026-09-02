import math,unittest
from spatial_system.geometry import *
class GeometryTests(unittest.TestCase):
 def test_vec3_arithmetic_and_finite_values(self):
  a=Vec3(1,2,3); self.assertEqual(a+Vec3(1,1,1),Vec3(2,3,4)); self.assertEqual(a-Vec3(1,1,1),Vec3(0,1,2)); self.assertEqual(a.scale(2),Vec3(2,4,6)); self.assertRaises(ValueError,lambda:Vec3(math.nan,0,0))
 def test_quaternion_normalization_and_rotation(self):
  q=Quaternion(2,0,0,0); self.assertEqual(q.normalized(),Quaternion(1,0,0,0)); self.assertRaises(ValueError,lambda:Quaternion(0,0,0,0).normalized()); z=Quaternion(math.cos(math.pi/4),0,0,math.sin(math.pi/4)).rotate(Vec3(1,0,0)); self.assertAlmostEqual(z.x,0,7); self.assertAlmostEqual(z.y,1,7)
 def test_transform_identity_translation_scale_and_inverse(self):
  p=Vec3(1,2,3); self.assertEqual(Transform.identity("world").apply(p),p); t=Transform("object_local","world",Vec3(1,2,3)); self.assertEqual(t.apply(p),Vec3(2,4,6)); s=Transform("world","world",scale=Vec3(2,2,2)); self.assertEqual(s.inverse().apply(s.apply(p)),p)
 def test_rotation_uniform_scale_composition_and_inverse(self):
  p=Vec3(1,2,3); q=Quaternion(math.cos(math.pi/4),0,0,math.sin(math.pi/4)); r=Transform("world","world",rotation=q,scale=Vec3(2,2,2)); x=r.inverse().apply(r.apply(p)); self.assertTrue(all(math.isclose(a,b,abs_tol=1e-7) for a,b in zip((x.x,x.y,x.z),(p.x,p.y,p.z)))); a=Transform("object_local","world",Vec3(1,0,0)); b=Transform("world","camera",Vec3(0,2,0)); y=a.then(b).apply(p); z=b.apply(a.apply(p)); self.assertTrue(all(math.isclose(u,v,abs_tol=1e-7) for u,v in zip((y.x,y.y,y.z),(z.x,z.y,z.z))))
 def test_spaces_and_unsupported_combinations(self):
  q=Quaternion(math.cos(math.pi/4),0,0,math.sin(math.pi/4)); self.assertRaises(ValueError,lambda:Transform("unknown","world")); self.assertRaises(ValueError,lambda:Transform("a","b").then(Transform("c","d"))); self.assertRaises(NotImplementedError,lambda:Transform("world","world",rotation=q,scale=Vec3(1,2,1)))
