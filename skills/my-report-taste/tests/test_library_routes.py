"""Routing regressions: scenario selection must not override supplied templates."""

import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("taste_library", ROOT / "scripts/library.py")
library = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(library)


class LibraryRouteTests(unittest.TestCase):
    def routes(self, request, **kwargs):
        return [row[0] for row in library.route_rows([request], 10, **kwargs)]

    def test_generic_academic_is_workflow_only(self):
        for request in ("学术 Oral", "帮我做学术oral的汇报", "论文答辩", "学术研讨会", "oral"):
            with self.subTest(request=request):
                routes = self.routes(request)
                self.assertEqual(routes[0]["id"], "academic-paper-oral")
                self.assertEqual(routes[0]["main"], [])
                self.assertNotIn("academic-oral-wine", [row["id"] for row in routes])

    def test_combined_official_template_request(self):
        route = self.routes("学术 Oral 官方模板，做一份英文报告")[0]
        self.assertEqual(route["id"], "academic-paper-oral")
        self.assertEqual(route["_visual_policy"], "preserve-provided-template")

    def test_explicit_academic_route_preserved(self):
        route = self.routes("学术 Oral 按 NAR-001 做")[0]
        self.assertEqual(route["id"], "academic-oral-wine")
        self.assertEqual(route["palette"], ["CLR-010"])

    def test_template_palette_override_does_not_mutate_library(self):
        route = self.routes("NAR-001 学术 Oral 官方模板")[0]
        self.assertEqual(route["main"], ["NAR-001"])
        self.assertEqual(route["palette"], [])
        self.assertTrue(route["gate_refs"])
        self.assertFalse(any(gate.startswith("clr-") for gate in route["gate_refs"]))
        self.assertEqual(self.routes("NAR-001")[0]["palette"], ["CLR-010"])

    def test_explicit_template_flag(self):
        route = self.routes("组会汇报", supplied_template=True)[0]
        self.assertEqual(route["palette"], [])
        self.assertEqual(route["_visual_policy"], "preserve-provided-template")

    def test_negated_style_not_selected(self):
        routes = self.routes("不要 NAR-001，做学术 Oral，用官方模板")
        self.assertEqual(routes[0]["id"], "academic-paper-oral")
        self.assertNotIn("academic-oral-wine", [row["id"] for row in routes])

    def test_opt_out(self):
        self.assertEqual(self.routes("不要使用我的风格，做学术 Oral"), [])

    def test_english_and_word_boundaries(self):
        route = self.routes("Make an ACADEMIC ORAL using the official template")[0]
        self.assertEqual(route["id"], "academic-paper-oral")
        self.assertEqual(route["palette"], [])
        self.assertFalse(library.request_mentions("oral", "coral reef"))
        self.assertEqual(self.routes("coral reef"), [])

    def test_general_research_does_not_impose_author_style(self):
        route = self.routes("研究进展")[0]
        self.assertEqual(route["id"], "research-content")
        self.assertEqual(route["palette"], [])
        route = self.routes("author-light 研究进展")[0]
        self.assertEqual(route["id"], "research-progress-light")
        self.assertEqual(route["palette"], ["CLR-002"])

    def test_negated_official_template_not_applied(self):
        route = self.routes("不要官方模板，使用 NAR-001")[0]
        self.assertEqual(route["palette"], ["CLR-010"])
        self.assertNotIn("_visual_policy", route)


if __name__ == "__main__":
    unittest.main()
