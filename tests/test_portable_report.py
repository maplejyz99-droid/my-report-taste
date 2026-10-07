import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("portable_report", ROOT / "examples/portable-report/build_report.py")
report = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(report)


class PortableReportTests(unittest.TestCase):
    def test_complete_deterministic_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, second = Path(tmp) / "first", Path(tmp) / "second"
            result = report.build(report.DEFAULT_SOURCE, first)
            report.build(report.DEFAULT_SOURCE, second)
            self.assertFalse(result["rendered"])
            self.assertFalse(result["skill_effectiveness_tested"])
            for name in result["outputs"]:
                self.assertEqual((first / name).read_bytes(), (second / name).read_bytes())
            html = (first / "report.html").read_text()
            for value in ("84.0", "86.0", "86.5", "120", "85", "160", "+2.0", "-35", "-29.2%", "+75"):
                self.assertIn(value, html)
            self.assertIn("SYNTHETIC TEACHING DATA", html)
            self.assertIn("百分点", html)
            self.assertNotIn("<script", html)
            self.assertNotIn("https://", html)

    def test_output_refuses_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            out = Path(tmp) / "out"
            report.build(report.DEFAULT_SOURCE, out)
            before = (out / "report.html").read_bytes()
            with self.assertRaises(FileExistsError):
                report.build(report.DEFAULT_SOURCE, out)
            self.assertEqual((out / "report.html").read_bytes(), before)

    def test_text_is_escaped_and_numbers_come_from_source(self):
        data = json.loads(report.DEFAULT_SOURCE.read_text())
        data["rows"][1].update(name="<script>example</script>", accuracy=87, latency=90)
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp) / "input.json"
            source.write_text(json.dumps(data))
            out = Path(tmp) / "out"
            report.build(source, out)
            html = (out / "report.html").read_text()
            self.assertNotIn("<script>", html)
            self.assertIn("&lt;script&gt;", html)
            self.assertIn("+3.0 个百分点", html)
            self.assertIn("-25.0%", html)

    def test_invalid_inputs_fail_before_creating_output(self):
        for field, value in (("synthetic", False), ("rows", []), ("unmeasured", "unknown"),
                             ("metrics", {"accuracy": "fraction", "latency": "seconds"})):
            with self.subTest(field=field), tempfile.TemporaryDirectory() as tmp:
                data = json.loads(report.DEFAULT_SOURCE.read_text())
                data[field] = value
                source, out = Path(tmp) / "input.json", Path(tmp) / "out"
                source.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    report.build(source, out)
                self.assertFalse(out.exists())

    def test_invalid_metric_values_are_rejected(self):
        for metric, value in (("latency", 0), ("latency", float("nan")), ("accuracy", True), ("accuracy", 101)):
            with self.subTest(metric=metric, value=value), tempfile.TemporaryDirectory() as tmp:
                data = json.loads(report.DEFAULT_SOURCE.read_text())
                data["rows"][0][metric] = value
                source = Path(tmp) / "input.json"
                source.write_text(json.dumps(data))
                with self.assertRaises(ValueError):
                    report.build(source, Path(tmp) / "out")


if __name__ == "__main__":
    unittest.main()
