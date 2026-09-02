from dataclasses import dataclass
from pathlib import Path

SUPPORTED={".glb",".gltf",".obj"}
@dataclass(frozen=True)
class AssetValidationResult:
    accepted: bool; path: str; format: str | None; reason: str; unsupported_features: tuple[str,...]=()
def validate_asset(path):
    p=Path(path); ext=p.suffix.lower()
    if ext not in SUPPORTED: return AssetValidationResult(False,str(p),None,"unsupported extension")
    if not p.is_file(): return AssetValidationResult(False,str(p),ext[1:],"missing file")
    data=p.read_bytes()
    if not data: return AssetValidationResult(False,str(p),ext[1:],"empty file")
    if ext==".glb" and data[:4] != b"glTF": return AssetValidationResult(False,str(p),"glb","invalid glB magic")
    if ext==".gltf" and data[:1] not in (b"{",): return AssetValidationResult(False,str(p),"gltf","invalid JSON boundary")
    if ext==".obj" and not any(line.lstrip().startswith(("v ","o ","g ")) for line in data.decode("utf-8",errors="ignore").splitlines()): return AssetValidationResult(False,str(p),"obj","no recognizable geometry declarations")
    return AssetValidationResult(True,str(p),ext[1:],"extension and boundary validation passed")

