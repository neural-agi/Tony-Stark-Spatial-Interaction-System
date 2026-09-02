import unittest
from spatial_system.contracts import TimeRef,TraceRef
from spatial_system.instrumentation import *
class ObservabilityTests(unittest.TestCase):
 def test_trace_and_stage_span(self):
  sink=Sink(); trace=TraceContext("cam","f",4); clock=Clock();
  with StageTimer("capture",clock,sink,trace): pass
  self.assertEqual(sink.spans[0].trace.frame_id,"f"); self.assertEqual(sink.spans[0].stage,"capture")
 def test_timestamps_latency_and_invalid_order(self):
  a=TimeRef(10,"d","o"); b=TimeRef(20,"d","o"); self.assertEqual(duration_ns(a,b),10); self.assertIsNone(duration_ns(b,a)); self.assertIsNone(duration_ns(a,TimeRef(20,"other","o"))); self.assertEqual(observation_age(b,a),10)
 def test_sequence_tracker_and_bounded_latest_buffer(self):
  tr=SequenceTracker(); self.assertEqual(tr.observe(1),"first"); self.assertEqual(tr.observe(3),"missing"); self.assertEqual(tr.missing,1); self.assertEqual(tr.observe(3),"duplicate"); self.assertEqual(tr.observe(2),"reordered")
  q=BoundedBuffer(2,latest_wins=True); q.put("a",TimeRef(1,"d","o")); q.put("b",TimeRef(2,"d","o")); q.put("c",TimeRef(3,"d","o")); self.assertEqual(q.depth,2); self.assertEqual(q.dropped,1); self.assertEqual(q.pop_latest()[0],"c"); q.discard_stale(TimeRef(100,"d","o"),50); self.assertEqual(q.stale_discarded,1)
 def test_metrics_statistics_and_benchmark_metadata(self):
  s=statistics([1,2,3,4,5]); self.assertEqual((s.count,s.minimum,s.maximum,s.median,s.p95,s.p99),(5,1,5,3,5,5)); sink=Sink(); sink.record_metric(metric("latency",2,"ns",TimeRef(1,"d","o"),"capture",TraceRef("c","f"))); self.assertEqual(sink.metrics[0].trace.frame_id,"f"); m=BenchmarkMetadata("r",TimeRef(1,"d","o"),"v",None,"M5","OS",{},None,None,"scene","env",10,"transient"); self.assertEqual(m.hardware_id,"M5")
