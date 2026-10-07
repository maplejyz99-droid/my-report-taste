"""Routing regressions: scenario selection must not override supplied templates."""

import importlib.util
import json
import subprocess
import sys
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
        self.assertEqual(route["_template_state"], "unknown")
        self.assertNotIn("_visual_policy", route)

    def test_explicit_academic_route_preserved(self):
        route = self.routes("学术 Oral", preset="academic-oral-wine")[0]
        self.assertEqual(route["id"], "academic-oral-wine")
        self.assertEqual(route["palette"], ["CLR-010"])

    def test_template_palette_override_does_not_mutate_library(self):
        route = self.routes("学术 Oral", preset="academic-oral-wine", supplied_template=True)[0]
        self.assertEqual(route["main"], ["NAR-001"])
        self.assertEqual(route["palette"], [])
        self.assertTrue(route["gate_refs"])
        self.assertFalse(any(gate.startswith("clr-") for gate in route["gate_refs"]))
        self.assertEqual(self.routes("", preset="academic-oral-wine")[0]["palette"], ["CLR-010"])

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
        route = self.routes("Make an ACADEMIC ORAL using the official template", template_state="provided")[0]
        self.assertEqual(route["id"], "academic-paper-oral")
        self.assertEqual(route["palette"], [])
        self.assertFalse(library.request_mentions("oral", "coral reef"))
        self.assertEqual(self.routes("coral reef"), [])

    def test_general_research_does_not_impose_author_style(self):
        route = self.routes("研究进展")[0]
        self.assertEqual(route["id"], "research-content")
        self.assertEqual(route["palette"], [])
        route = self.routes("研究进展", preset="author-light")[0]
        self.assertEqual(route["id"], "research-progress-light")
        self.assertEqual(route["palette"], ["CLR-002"])

    def test_negated_official_template_not_applied(self):
        route = self.routes("不要官方模板", cards=["NAR-001", "CLR-010"], template_state="absent")[0]
        self.assertEqual(route["palette"], ["CLR-010"])
        self.assertNotIn("_visual_policy", route)

    def test_text_never_declares_template_presence(self):
        for request in ("没有官方模板，使用 author-light", "不需要官方模板，使用 author-light",
                        "官方模板这次没有，使用 author-light", "已有官方模板，使用 author-light"):
            with self.subTest(request=request):
                for route in self.routes(request):
                    self.assertEqual(route["_template_state"], "unknown")
                    self.assertNotIn("_visual_policy", route)

    def test_postposed_rejection_is_not_a_style_hit(self):
        routes = self.routes("author-light 这次不要用，先按官方模板")
        self.assertNotIn("research-progress-light", [r["id"] for r in routes])

    def test_comparison_returns_inactive_candidates(self):
        routes = self.routes("比较 author-light 和 academic-oral-wine，暂时不选择")
        candidates = [r for r in routes if r["_selection"] == "candidate"]
        self.assertEqual({r["id"] for r in candidates}, {"research-progress-light", "academic-oral-wine"})
        for route in candidates:
            for field in ("main", "auxiliary", "palette", "contracts", "references", "gate_refs"):
                self.assertEqual(route[field], [])
            self.assertTrue(route["_candidate_config"]["palette"])

    def test_even_affirmative_text_is_not_structured_selection(self):
        route = self.routes("使用 author-light")[0]
        self.assertEqual(route["_selection"], "candidate")
        self.assertEqual(route["palette"], [])
        selected = self.routes("", preset="author-light", template_state="absent")[0]
        self.assertEqual(selected["_selection"], "selected")
        self.assertEqual(selected["palette"], ["CLR-002"])

    def test_alternative_is_not_negated_with_previous_option(self):
        routes = self.routes("不用 author-light 而用 academic-oral-wine")
        self.assertIn("academic-oral-wine", [r["id"] for r in routes])
        self.assertNotIn("research-progress-light", [r["id"] for r in routes])
        self.assertTrue(all(r["_selection"] != "selected" for r in routes))

    def test_narrative_card_does_not_select_color_or_density(self):
        route = self.routes("这次只用 NAR-001 的叙事，不用酒红配色", cards=["NAR-001"])[0]
        self.assertEqual(route["main"], ["NAR-001"])
        self.assertEqual(route["palette"], [])
        self.assertEqual(route["auxiliary"], [])
        self.assertFalse(any(g.startswith("clr-") or g.startswith("grd-") for g in route["gate_refs"]))

    def test_individual_dimensions_and_duplicate_ids(self):
        route = self.routes("", cards=["nar-001", "GRD-010", "CLR-002", "NAR-001"])[0]
        self.assertEqual(route["main"], ["NAR-001", "GRD-010"])
        self.assertEqual(route["palette"], ["CLR-002"])

    def test_template_suppresses_only_palette(self):
        route = self.routes("", cards=["NAR-001", "GRD-010", "CLR-010"], template_state="provided")[0]
        self.assertEqual(route["main"], ["NAR-001", "GRD-010"])
        self.assertEqual(route["palette"], [])
        self.assertNotIn("references/CLR-010.md", route["references"])
        self.assertFalse(any(g.startswith("clr-") for g in route["gate_refs"]))

    def test_unknown_or_conflicting_declarations_fail(self):
        for kwargs in ({"preset": "missing"}, {"cards": ["NAR-999"]}, {"preset": "NAR-001"},
                       {"preset": "author-light", "cards": ["NAR-001"]},
                       {"template_state": "invalid"}, {"supplied_template": True, "template_state": "absent"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(SystemExit):
                self.routes("", **kwargs)

    def test_cli_explicit_selection(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/library.py"), "route",
                                 "--card", "NAR-001", "--template-state", "absent", "--json"],
                                capture_output=True, text=True, timeout=10, check=True)
        route = json.loads(result.stdout)[0]
        self.assertEqual(route["_selection"], "selected")
        self.assertEqual(route["main"], ["NAR-001"])
        self.assertEqual(route["palette"], [])
        self.assertEqual(route["_template_state"], "absent")


if __name__ == "__main__":
    unittest.main()
