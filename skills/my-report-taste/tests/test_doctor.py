import importlib.util
import subprocess
import unittest
from pathlib import Path
from unittest import mock

SPEC = importlib.util.spec_from_file_location("taste_doctor", Path(__file__).resolve().parents[1] / "scripts/doctor.py")
doctor = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(doctor)


class DoctorTests(unittest.TestCase):
    def test_missing_optional_tools_do_not_disable_standard_library(self):
        with mock.patch.object(doctor.shutil, "which", return_value=None), \
             mock.patch.object(doctor.importlib.util, "find_spec", return_value=None), \
             mock.patch.object(doctor.subprocess, "run") as run:
            result = doctor.inspect(Path.cwd())
        run.assert_not_called()
        self.assertTrue(result["python_supported"])
        self.assertEqual(result["capabilities"]["library_plan_script_checks"], "available")
        self.assertEqual(result["capabilities"]["pptx_pdf_export"], "not_detected")
        self.assertEqual(result["capabilities"]["artifact_gallery"], "not_verified")

    def test_detected_does_not_mean_tested(self):
        with mock.patch.object(doctor.shutil, "which", return_value="fixture-executable"), \
             mock.patch.object(doctor.importlib.util, "find_spec", return_value=object()):
            result = doctor.inspect(Path.cwd())
        self.assertEqual(result["capabilities"]["pptx_pdf_export"], "executable_detected_not_tested")
        self.assertEqual(result["node_probe"]["status"], "not_probed")

    def test_optional_probe_is_bounded_and_does_not_import_package(self):
        response = subprocess.CompletedProcess([], 0, '{"version":"v22.0.0","artifact":true}', '')
        with mock.patch.object(doctor.subprocess, "run", return_value=response) as run:
            result = doctor.node_probe("node", Path.cwd())
        self.assertTrue(result["artifact_tool_resolvable"])
        self.assertEqual(run.call_args.kwargs["timeout"], 5)
        self.assertIn("require.resolve", run.call_args.args[0][-1])

    def test_probe_failure_does_not_leak_child_output(self):
        for response in (subprocess.CompletedProcess([], 1, "private output", "private error"),
                         subprocess.CompletedProcess([], 0, "not json", "")):
            with mock.patch.object(doctor.subprocess, "run", return_value=response):
                self.assertEqual(doctor.node_probe("node", Path.cwd()), {"status": "probe_failed"})
        with mock.patch.object(doctor.subprocess, "run", side_effect=subprocess.TimeoutExpired("node", 5)):
            self.assertEqual(doctor.node_probe("node", Path.cwd()), {"status": "probe_failed"})


if __name__ == "__main__":
    unittest.main()
