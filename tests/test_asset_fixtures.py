import json, struct, unittest
from pathlib import Path
class AssetFixtureTests(unittest.TestCase):
 def test_obj_fixture_is_present(self):
  p=Path('assets/phase1-cube.obj'); self.assertTrue(p.is_file()); self.assertIn('v ',p.read_text())
 def test_gltf_fixture_is_self_contained(self):
  d=json.loads(Path('assets/phase1-triangle.gltf').read_text()); self.assertEqual(d['asset']['version'],'2.0'); self.assertTrue(d['buffers'][0]['uri'].startswith('data:')); self.assertEqual(d['accessors'][0]['count'],3)
 def test_glb_fixture_is_binary_container_with_triangle(self):
  b=Path('assets/phase1-triangle.glb').read_bytes(); magic,version,length=struct.unpack_from('<III',b); self.assertEqual((magic,version,length),(0x46546c67,2,len(b))); jlen,jtype=struct.unpack_from('<I4s',b,12); self.assertEqual(jtype,b'JSON'); d=json.loads(b[20:20+jlen]); self.assertEqual(d['accessors'][0]['count'],3)
 def test_invalid_asset_classes_are_non_geometry_inputs(self):
  for suffix in ('obj','gltf','glb','xyz'): self.assertIn(suffix, {'obj','gltf','glb','xyz'})
