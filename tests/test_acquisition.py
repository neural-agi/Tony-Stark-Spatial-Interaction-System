import unittest
from dataclasses import FrozenInstanceError
from spatial_system.acquisition import *
from spatial_system.contracts import RawFrame, TimeRef, Validity
from spatial_system.instrumentation import BoundedBuffer
class FakeClock:
 def __init__(self): self.n=100
 def now(self): self.n+=10; return TimeRef(self.n,"test","fixed")
def frame(seq,ts,valid=Validity.VALID): return RawFrame(f"f{seq}","synthetic",TimeRef(ts,"test","fixed"),seq,2,2,"bytes","upright",False, payload=b"data",validity=valid)
class AcquisitionTests(unittest.TestCase):
 def test_raw_frame_payload_and_metadata_are_immutable(self):
  source=bytearray(b"x"); self.assertRaises(FrozenInstanceError,lambda:frame(1,1).__setattr__("payload",b"y")); self.assertRaises(TypeError,lambda:RawFrame("f","s",TimeRef(1,"d","o"),1,1,1,"b","u",False,payload=source)); f=RawFrame("f","s",TimeRef(1,"d","o"),1,1,1,"b","u",False,metadata={"x":1}); self.assertRaises(AttributeError,lambda:f.metadata.update({"x":2}))
 def test_synthetic_frame_metadata_and_buffer_metrics(self):
  src=SyntheticFrameSource([frame(1,1),frame(3,3)]); service=AcquisitionService(src,BoundedBuffer(1,True),FakeClock()); self.assertTrue(service.acquire_once()); self.assertTrue(service.acquire_once()); self.assertEqual(service.buffer.dropped,1); self.assertEqual(service.report.sequence.missing,1); self.assertEqual(service.buffer.depth,1); self.assertEqual(service.buffer.pop_latest()[0].payload,b"data"); self.assertTrue(service.sink.spans[0].trace.frame_id)
 def test_invalid_frame_is_not_buffered(self):
  service=AcquisitionService(SyntheticFrameSource([frame(1,1,Validity.INVALID)]),BoundedBuffer(2),FakeClock()); self.assertFalse(service.acquire_once()); self.assertEqual(service.report.invalid,1); self.assertEqual(service.buffer.depth,0)
 def test_source_termination_is_structured(self):
  service=AcquisitionService(SyntheticFrameSource([]),BoundedBuffer(1),FakeClock());
  with self.assertRaises(AcquisitionError) as ctx: service.acquire_once()
  self.assertEqual(ctx.exception.code,AcquisitionErrorCode.TERMINATED)
 def test_stale_queue_and_age(self):
  q=BoundedBuffer(2); q.put("old",TimeRef(1,"test","fixed")); q.put("new",TimeRef(90,"test","fixed")); q.discard_stale(TimeRef(100,"test","fixed"),20); self.assertEqual(q.stale_discarded,1); self.assertEqual(q.oldest_age(TimeRef(100,"test","fixed")),10)
 def test_capabilities_and_configuration_are_explicit(self):
  c=CameraConfiguration("cam","backend",640,480,"RGB",30,"cfg"); src=SyntheticFrameSource([],c); self.assertEqual(src.capabilities().resolutions,((640,480),)); self.assertEqual(c.requested_fps,30)
 def test_trace_sequence_actual_configuration_and_resources(self):
  c=CameraConfiguration("synthetic","synthetic",1,1,"bytes",30,"cfg"); service=AcquisitionService(SyntheticFrameSource([frame(4,1)],c),BoundedBuffer(1),FakeClock()); service.acquire_once(); span=service.sink.spans[0]; self.assertEqual(span.trace.sequence,4); self.assertEqual(service.report.actual_configuration.width,2); self.assertIn("status",service.resource_sample())
