import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / "examples/evaluation"


class EvaluationCaseTests(unittest.TestCase):
    def test_case_inputs_and_checklists_are_complete(self):
        suite = json.loads((BASE / "cases.json").read_text())
        self.assertEqual(suite["status"], "not_run_with_agents")
        self.assertEqual(len(suite["cases"]), 4)
        ids = [case["id"] for case in suite["cases"]]
        self.assertEqual(len(set(ids)), len(ids))
        for case in suite["cases"]:
            self.assertTrue(case["prompt"])
            self.assertGreaterEqual(len(case["checks"]), 5)
            for key in case["inputs"]:
                path = (BASE / suite[key]).resolve()
                self.assertIn(ROOT, path.parents)
                self.assertTrue(path.is_file())
        self.assertGreaterEqual(len(suite["coverage_gaps"]), 3)


if __name__ == "__main__":
    unittest.main()
