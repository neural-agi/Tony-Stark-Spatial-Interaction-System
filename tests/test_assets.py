import tempfile,unittest
from pathlib import Path
from spatial_system.assets import validate_asset
class AssetTests(unittest.TestCase):
 def test_supported_valid_assets(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); (p/"a.obj").write_text("v 0 0 0\n",encoding="utf8"); (p/"a.gltf").write_text("{}",encoding="utf8"); (p/"a.glb").write_bytes(b"glTFxxxx"); self.assertTrue(validate_asset(p/"a.obj").accepted); self.assertTrue(validate_asset(p/"a.gltf").accepted); self.assertTrue(validate_asset(p/"a.glb").accepted)
 def test_rejected_assets_have_reason(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d); (p/"bad.gltf").write_text("not-json",encoding="utf8"); self.assertFalse(validate_asset(p/"bad.gltf").accepted); self.assertFalse(validate_asset(p/"missing.obj").accepted); self.assertFalse(validate_asset(p/"x.zip").accepted); self.assertTrue(validate_asset(p/"x.zip").reason)
