import io, json, struct, unittest
from spatial_system.acquisition import MacOSAVFoundationSource, AcquisitionError, AcquisitionErrorCode
class FakeProcess:
 def __init__(self,data,returncode=None): self.stdout=io.BytesIO(data); self._returncode=returncode
 def poll(self): return self._returncode
class ProtocolTests(unittest.TestCase):
 def source(self,data,code=None):
  s=MacOSAVFoundationSource.__new__(MacOSAVFoundationSource); s.process=FakeProcess(data,code); return s
 def header(self,**kw):
  payload=kw.pop("payload",b"12345678"); h={"frame_id":"f","source_id":"cam","sequence":1,"timestamp_ns":2,"timestamp_domain":"media","timestamp_origin":"test","width":2,"height":1,"pixel_format":"BGRA8","orientation":"native","mirrored":False,"bytes_per_row":8,"payload_size":len(payload)}; h.update(kw); return (json.dumps(h)+"\n").encode()+struct.pack("<I",len(payload))+payload
 def test_valid_payload_and_stride_metadata(self):
  f=self.source(self.header()).read(); self.assertEqual((f.metadata["bytes_per_row"],len(f.payload)),(8,8)); self.assertEqual(f.time.domain,"media")
 def test_rejects_zero_truncated_and_bad_stride(self):
  self.assertRaises(AcquisitionError,lambda:self.source(self.header(payload=b"")).read()); self.assertRaises(AcquisitionError,lambda:self.source(self.header(payload=b"1")).read()); self.assertRaises(AcquisitionError,lambda:self.source(self.header(bytes_per_row=4)).read())
 def test_eof_and_helper_failure_are_distinct(self):
  with self.assertRaises(AcquisitionError) as a: self.source(b"",0).read()
  self.assertEqual(a.exception.code,AcquisitionErrorCode.TERMINATED)
  with self.assertRaises(AcquisitionError) as b: self.source(b"",7).read()
  self.assertEqual(b.exception.code,AcquisitionErrorCode.READ)
