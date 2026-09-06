import json,tempfile,unittest
from pathlib import Path
from tools.phase1_scenarios import main
class ScenarioTests(unittest.TestCase):
 def test_matrix_is_versioned_and_separates_operator_rows(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d)/"scenarios.jsonl"; import sys
   old=sys.argv; sys.argv=["phase1_scenarios","--output",str(p)]
   try: main()
   finally: sys.argv=old
   rows=[json.loads(x) for x in p.read_text().splitlines()]; self.assertTrue(rows); self.assertTrue(all(x["schema"]=="phase1-scenarios-1.0" for x in rows)); self.assertTrue(any(x["result"]=="OPERATOR_REQUIRED" for x in rows)); self.assertTrue(any(x["evidence"]=="AUTOMATED_REPLAY" for x in rows))
