import json, tempfile, unittest
from tools.evidence_harness import stats, SCHEMA, STAGE_PLANS
class EvidenceHarnessTests(unittest.TestCase):
 def test_statistics_distribution_and_empty(self):
  self.assertEqual(stats([])["count"],0); self.assertEqual(stats([1,2,3])["median"],2); self.assertEqual(stats([1,2,3])["p95"],3)
 def test_schema_constant_and_json_record_shape(self):
  self.assertEqual(SCHEMA,"phase1-evidence-1.0")
  from tools.evidence_harness import record
  x=record("r","camera","fps",30,3); self.assertEqual(json.loads(json.dumps(x))["schema"],SCHEMA); self.assertEqual(x["sample_count"],3)
 def test_stage_plans_declare_active_and_suppressed_stages(self):
  self.assertEqual(STAGE_PLANS["acquisition"]["suppressed_stages"], ["vision","ipc","interaction","render"])
  self.assertIn("camera", STAGE_PLANS["full"]["active_stages"])
  self.assertEqual(STAGE_PLANS["vision"]["isolation"], "PASS")
 def test_headless_stage_execution_suppresses_downstream_entries(self):
  from tools.stage_isolation_replay import execute
  expected={"acquisition":(0,0,0),"vision":(1,0,0),"ipc":(1,0,0),"interaction":(1,1,0),"render":(1,1,0),"full":(1,1,0)}
  for mode,(vision,interaction,render) in expected.items():
   c=execute(mode)["execution_counters"]
   self.assertEqual(c["vision_count"],vision,mode); self.assertEqual(c["interaction_count"],interaction,mode); self.assertEqual(c["render_count"],render,mode)
 def test_measurement_primitives(self):
  from spatial_system.measurement import FrameTiming, distribution, interval_statistics, rss_summary
  t=FrameTiming("f","cam",0,0,"synthetic",2_000_000,3_000_000,8_000_000,9_000_000,10_000_000,12_000_000,13_000_000,16_000_000)
  self.assertEqual(t.latency_samples()["vision_duration"],5.0)
  self.assertEqual(distribution([1,2,3])["p95"],3.0)
  self.assertAlmostEqual(interval_statistics([1,2,3])["population_stddev"],0.8164965809)
  self.assertEqual(rss_summary([100,101,102,104,105])["growth_bytes"],5)
 def test_timing_registry_is_bounded_and_requires_identity(self):
  from spatial_system.measurement import FrameTiming, FrameTimingRegistry
  r=FrameTimingRegistry(2); r.put(FrameTiming("a","s",1,1,"d")); r.put(FrameTiming("b","s",2,2,"d")); r.put(FrameTiming("c","s",3,3,"d"))
  self.assertIsNone(r.get("a")); self.assertEqual(r.evictions,1); self.assertEqual(len(r),2)
  with self.assertRaises(ValueError): r.put(FrameTiming(None,"s",0,0,"d"))
 def test_render_binding_cannot_cross_associate_frames(self):
  from spatial_system.measurement import FrameTiming, FrameTimingRegistry
  r=FrameTimingRegistry(); r.put(FrameTiming("a","s",1,1,"d")); r.put(FrameTiming("b","s",2,2,"d")); self.assertTrue(r.bind_render("a",10)); self.assertIsNone(r.get("b").render_ns); self.assertFalse(r.bind_render("missing",11))
 def test_resource_summary_missing_and_cpu_shape(self):
  from spatial_system.resource_monitor import cpu_record
  from spatial_system.measurement import rss_summary
  self.assertEqual(rss_summary([])["classification"],"inconclusive")
  self.assertIn("status",cpu_record(999999,"test",1.0))
 def test_summaries_recompute_from_retained_records(self):
  from spatial_system.measurement import FrameTiming, summarize_timings, interval_summary
  rows=[FrameTiming("a","cam",1,0,"d",1_000_000,2_000_000,4_000_000,5_000_000,6_000_000,7_000_000,8_000_000,9_000_000),FrameTiming("b","cam",2,10_000_000,"d",11_000_000,12_000_000,14_000_000,15_000_000,16_000_000,17_000_000,18_000_000,19_000_000)]
  s=summarize_timings(rows); self.assertEqual(s["vision_processing"]["median"],2.0); self.assertEqual(interval_summary(rows,"vision_complete_ns")["mean"],10.0)
