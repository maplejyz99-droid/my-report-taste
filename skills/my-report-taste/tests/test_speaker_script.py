"""Count only spoken sections; preserve timing uncertainty and paired roles."""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/check_speaker_script.py"
SPEC = importlib.util.spec_from_file_location("speaker_script", SCRIPT)
speaker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(speaker)


def page(page_id="S01", role="main", script="Two spoken words.", transition="", extra="", budget=40):
    return (f"## {page_id} — Title\n- role: {role}\n- target_seconds: {budget}\n"
            f"### Script\n{script}\n### Transition\n{transition}\n"
            f"### Presenter notes\nDo not count these fifty 50 words.\n{extra}\n")


class SpeakerScriptTests(unittest.TestCase):
    def test_only_spoken_sections_counted(self):
        pages, errors = speaker.parse_script(page(transition="Next page."))
        report = speaker.analyze(pages, "en", pause_seconds=0)
        self.assertEqual(errors, [])
        self.assertEqual(report["total_latin_words"], 5)
        self.assertEqual(report["total_cjk_chars"], 0)

    def test_main_optional_and_backup(self):
        pages, errors = speaker.parse_script(page() + page("S02", "optional") + page("S03", "backup"))
        self.assertEqual(errors, [])
        self.assertEqual(len(speaker.analyze(pages, "en")["pages"]), 1)
        self.assertEqual(len(speaker.analyze(pages, "en", include_optional=True)["pages"]), 2)

    def test_chinese_and_latin_timed_separately(self):
        pages, _ = speaker.parse_script(page(script="研究结果很好 OPD works"))
        report = speaker.analyze(pages, "zh", wpm=(120, 120), cpm=(240, 240), pause_seconds=0)
        self.assertEqual(report["total_cjk_chars"], 6)
        self.assertEqual(report["total_latin_words"], 2)
        self.assertEqual(report["pages"][0]["estimated_seconds"], [2.5, 2.5])

    def test_short_is_actual_text_and_transition(self):
        pages, _ = speaker.parse_script(page(transition="Next page.", extra="### Short script\nShort.\n### Short transition\nThen."))
        report = speaker.analyze(pages, "en", short=True)
        self.assertEqual(report["total_latin_words"], 2)
        self.assertIsNone(report["page_budget_minutes"])
        self.assertEqual(report["warnings"], [])

    def test_short_fallback_does_not_silently_drop_speech(self):
        pages, _ = speaker.parse_script(page(transition="Next page."))
        report = speaker.analyze(pages, "en", short=True)
        self.assertEqual(report["total_latin_words"], 5)
        self.assertTrue(any("Short script missing" in warning for warning in report["warnings"]))
        pages, _ = speaker.parse_script(page(transition="Next page.", extra="### Short script\nShort."))
        report = speaker.analyze(pages, "en", short=True)
        self.assertEqual(report["total_latin_words"], 3)
        self.assertTrue(any("Short transition missing" in warning for warning in report["warnings"]))

    def test_budget_and_target_overrun_reported(self):
        pages, _ = speaker.parse_script(page(script="word " * 150, budget=10))
        report = speaker.analyze(pages, "en", minutes=0.1)
        self.assertTrue(any("Page budget" in warning for warning in report["warnings"]))
        self.assertTrue(any("fast-end estimate exceeds" in warning for warning in report["warnings"]))
        self.assertTrue(any("Sum of page budgets" in warning for warning in report["warnings"]))

    def test_duplicate_ids_invalid_roles_and_budget(self):
        _, errors = speaker.parse_script(page() + page(role="hidden", budget="nan"))
        self.assertTrue(any("duplicate page ID" in error for error in errors))
        self.assertTrue(any("role must" in error for error in errors))
        self.assertTrue(any("finite and positive" in error for error in errors))

    def test_pair_order_roles_and_numbers(self):
        left, _ = speaker.parse_script(page(script="Result is 72.62."))
        right, _ = speaker.parse_script(page(script="结果为72.62。"))
        self.assertEqual(speaker.compare_pair(left, right, False), ([], []))
        changed, _ = speaker.parse_script(page(role="optional", script="结果为 60.92。"))
        errors, warnings = speaker.compare_pair(left, changed, False)
        self.assertTrue(errors)
        self.assertTrue(warnings)

    def test_math_and_cues_not_counted(self):
        text, warnings = speaker.clean_spoken("Explain \\(x^2\\) and \\[y=3\\].\n[Cue: point left]\nDone.")
        self.assertNotIn("x^2", text)
        self.assertNotIn("left", text)
        self.assertTrue(warnings)

    def test_cli_json_and_missing_pair_language(self):
        with tempfile.TemporaryDirectory(prefix="taste-script-test-") as directory:
            path = Path(directory) / "script.md"
            path.write_text(page(), encoding="utf-8")
            result = subprocess.run([sys.executable, str(SCRIPT), str(path), "--language", "en"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "STRUCTURE_OK")
            bad = subprocess.run([sys.executable, str(SCRIPT), str(path), "--language", "en", "--paired", str(path)], capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)

    def test_cli_missing_input_is_error_not_verified(self):
        with tempfile.TemporaryDirectory(prefix="taste-missing-test-") as directory:
            result = subprocess.run([sys.executable, str(SCRIPT), str(Path(directory) / "missing.md"), "--language", "en"], capture_output=True, text=True)
            self.assertEqual(result.returncode, 1)
            self.assertEqual(json.loads(result.stdout)["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
