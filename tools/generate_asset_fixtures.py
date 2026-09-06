"""Generate deterministic minimal glTF/GLB triangle fixtures."""
import base64, json, struct
from pathlib import Path
ROOT=Path(__file__).parents[1]/"assets"
positions=struct.pack("<9f",0.0,0.0,0.0,1.0,0.0,0.0,0.0,1.0,0.0)
uri="data:application/octet-stream;base64,"+base64.b64encode(positions).decode()
doc={"asset":{"version":"2.0","generator":"phase1-deterministic"},"scene":0,"scenes":[{"nodes":[0]}],"nodes":[{"mesh":0}],"meshes":[{"primitives":[{"attributes":{"POSITION":0}}]}],"buffers":[{"byteLength":len(positions),"uri":uri}],"bufferViews":[{"buffer":0,"byteOffset":0,"byteLength":len(positions)}],"accessors":[{"bufferView":0,"componentType":5126,"count":3,"type":"VEC3","min":[0,0,0],"max":[1,1,0]}]}
ROOT.joinpath("phase1-triangle.gltf").write_text(json.dumps(doc,separators=(",",":"))+"\n")
json_doc=dict(doc); json_doc["buffers"]=[{"byteLength":len(positions)}]
json_bytes=json.dumps(json_doc,separators=(",",":")).encode(); json_bytes += b" "*((4-len(json_bytes)%4)%4); bin_bytes=positions+b"\0"*((4-len(positions)%4)%4)
glb=struct.pack("<III",0x46546C67,2,12+8+len(json_bytes)+8+len(bin_bytes))+struct.pack("<I4s",len(json_bytes),b"JSON")+json_bytes+struct.pack("<I4s",len(bin_bytes),b"BIN\0")+bin_bytes
ROOT.joinpath("phase1-triangle.glb").write_bytes(glb)
