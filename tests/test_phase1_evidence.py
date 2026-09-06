import json, tempfile, unittest
from pathlib import Path
from tools.phase1_evidence import manifest, scenario_record, spatial_jitter, generate_suite, SCENARIO_GROUPS, sustained_summary, classify_ceiling
class Phase1EvidenceTests(unittest.TestCase):
 def test_manifest_and_scenario_never_fabricate_pass(self):
  m=manifest(mode="full"); s=scenario_record(m["run_id"],"environment","reduced_lighting"); self.assertEqual(s["result"],"OPERATOR_REQUIRED"); self.assertEqual(m["telemetry"]["gpu"]["status"],"NOT_MEASURABLE")
 def test_spatial_jitter_fixture(self):
  x=spatial_jitter([(0,0),(1,1),(2,2)]); self.assertEqual(x["sample_count"],3); self.assertAlmostEqual(x["rms"],(2/3)**.5); self.assertEqual(x["p95_displacement"],2**.5)
 def test_sustained_and_ceiling_are_conservative(self):
  self.assertEqual(sustained_summary([])["status"],"NOT_MEASURABLE"); self.assertEqual(classify_ceiling([])["status"],"NOT_MEASURABLE"); self.assertEqual(classify_ceiling([{"rate":30,"stable":True}])["ceiling"],30)
 def test_complete_scenario_groups_are_versioned(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"suite.jsonl"; generate_suite(p); rows=[json.loads(x) for x in p.read_text().splitlines()]; self.assertEqual(rows[0]["schema"],"phase1-evidence-suite-1.0"); self.assertEqual(sum(len(x) for x in SCENARIO_GROUPS.values()),len(rows)-1)
