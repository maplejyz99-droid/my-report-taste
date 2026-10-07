"""Content, presentation and template selection regressions."""
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
    def routes(self, request="", **kwargs):
        return [row[0] for row in library.route_rows([request], 20, **kwargs)]

    def test_three_content_tasks_and_nine_presets(self):
        routes = library.load_routes()["routes"]
        self.assertEqual({r["id"] for r in routes if r.get("type") == "workflow"},
                         {"explain", "progress", "compare"})
        self.assertEqual(len([r for r in routes if r.get("type") != "workflow"]), 9)

    def test_plain_requests_are_inactive_candidates(self):
        for request, expected in (("学术 Oral", "explain"), ("研究进展", "progress"),
                                  ("技术选型", "compare"), ("系统介绍", "explain")):
            with self.subTest(request=request):
                rows = self.routes(request)
                self.assertEqual(rows[0]["id"], expected)
                for row in rows:
                    self.assertIn(row["_selection"], {"candidate", "workflow-candidate"})
                    for field in (*library.ROUTE_CARD_FIELDS, *library.ROUTE_FILE_FIELDS, "gate_refs"):
                        self.assertEqual(row[field], [])
                    self.assertIn("_candidate_config", row)

    def test_content_only_never_selects_visuals(self):
        for content in ("explain", "progress", "compare"):
            route = self.routes(content=content)[0]
            self.assertEqual(route["id"], content)
            self.assertEqual(route["_scope"], "content-only")
            self.assertEqual(route["_selection"], "selected")
            for field in (*library.ROUTE_CARD_FIELDS, "gate_refs"):
                self.assertEqual(route[field], [])
            self.assertEqual(route["references"], ["references/content-modes.md"])

    def test_comparison_does_not_assign_stance(self):
        route = self.routes(content="compare")[0]
        self.assertNotIn("stance_mode", route)
        self.assertNotIn("primary_recommendation", route)

    def test_legacy_content_aliases(self):
        self.assertEqual(self.routes(content="academic-paper-oral")[0]["id"], "explain")
        self.assertEqual(self.routes(content="research-content")[0]["id"], "progress")

    def test_legacy_preset_ids_remain_selectable(self):
        for row in library.load_routes()["routes"]:
            if row.get("type") == "workflow":
                continue
            with self.subTest(preset=row["id"]):
                selected = self.routes(preset=row["id"])[0]
                self.assertEqual(selected["id"], row["id"])
                self.assertEqual(selected["_scope"], "full-preset")
        self.assertEqual(self.routes(preset="author-light")[0]["id"], "research-progress-light")

    def test_explicit_academic_bundle_preserved(self):
        route = self.routes(preset="academic-oral-wine")[0]
        self.assertEqual(route["main"], ["NAR-001"])
        self.assertEqual(route["auxiliary"], ["GRD-010"])
        self.assertEqual(route["palette"], ["CLR-010"])

    def test_wine_presentation_excludes_narrative_and_paper_workflow(self):
        route = self.routes(visual="academic-oral-wine")[0]
        self.assertEqual(route["main"], ["GRD-010"])
        self.assertEqual(route["palette"], ["CLR-010"])
        self.assertFalse(any(g.startswith("nar-") for g in route["gate_refs"]))
        self.assertNotIn("references/NAR-001.md", route["references"])
        self.assertNotIn("references/academic-paper-oral-workflow.md", route["references"])

    def test_each_visual_preserves_content_and_medium(self):
        for row in library.load_routes()["routes"]:
            if row.get("type") == "workflow":
                continue
            selected = self.routes(visual=row["id"])[0]
            self.assertEqual(selected["_content_policy"], "preserve-existing-content")
            self.assertEqual(selected["_medium_policy"], "preserve-requested-medium")
            self.assertEqual(selected["contracts"], [])
            self.assertNotIn("NAR-001", selected["main"] + selected["auxiliary"])

    def test_content_invariant_under_all_visuals(self):
        for content in ("explain", "progress", "compare"):
            original = self.routes(content=content)[0]
            for row in library.load_routes()["routes"]:
                if row.get("type") == "workflow":
                    continue
                selected = self.routes(content=content, visual=row["id"])
                self.assertEqual(len(selected), 2)
                self.assertEqual(selected[0], original)

    def test_declarations_not_dropped_by_search_limit(self):
        rows = library.route_rows([], 1, content="progress", visual="project-green")
        self.assertEqual(len(rows), 2)

    def test_presentation_alone_does_not_infer_content(self):
        rows = self.routes("学术 Oral", visual="project-green")
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["id"], "project-green")

    def test_narrative_only_has_no_color_or_density(self):
        route = self.routes(cards=["NAR-001"])[0]
        self.assertEqual(route["main"], ["NAR-001"])
        self.assertEqual(route["auxiliary"], [])
        self.assertEqual(route["palette"], [])
        self.assertEqual(route["references"], ["references/NAR-001.md"])
        self.assertTrue(all(g.startswith("nar-001.") for g in route["gate_refs"]))

    def test_card_dimensions_and_duplicates(self):
        route = self.routes(cards=["nar-001", "CLR-002", "NAR-001"])[0]
        self.assertEqual(route["main"], ["NAR-001"])
        self.assertEqual(route["palette"], ["CLR-002"])

    def test_content_can_combine_with_individual_cards(self):
        rows = self.routes(content="explain", cards=["NAR-001"])
        self.assertEqual([r["id"] for r in rows], ["explain", "selected-cards"])

    def test_template_suppresses_palette_only_and_does_not_mutate(self):
        for selection in ({"preset": "academic-oral-wine"}, {"visual": "academic-oral-wine"},
                          {"cards": ["NAR-001", "GRD-010", "CLR-010"]}):
            route = self.routes(template_state="provided", **selection)[0]
            self.assertEqual(route["palette"], [])
            self.assertFalse(any(g.startswith("clr-010.") for g in route["gate_refs"]))
            self.assertNotIn("references/CLR-010.md", route["references"])
            self.assertEqual(route["_visual_policy"], "preserve-provided-template")
            self.assertEqual(self.routes(template_state="absent", **selection)[0]["palette"], ["CLR-010"])

    def test_template_shorthand(self):
        self.assertEqual(self.routes(content="explain", supplied_template=True)[0]["_template_state"],
                         "provided")

    def test_text_cannot_prove_template_presence(self):
        for request in ("已有官方模板，使用 author-light", "没有官方模板", "不要官方模板",
                        "Make an ACADEMIC ORAL using the official template"):
            for row in self.routes(request):
                self.assertEqual(row["_template_state"], "unknown")
                self.assertNotIn("_visual_policy", row)

    def test_comparison_or_affirmative_text_never_activates_style(self):
        for request in ("比较 author-light 和 academic-oral-wine", "使用 academic-oral-wine"):
            self.assertTrue(all(r["_selection"] != "selected" for r in self.routes(request)))

    def test_negated_style_not_retrieved(self):
        rows = self.routes("不要 NAR-001，做学术 Oral")
        self.assertEqual(rows[0]["id"], "explain")
        self.assertNotIn("academic-oral-wine", [r["id"] for r in rows])

    def test_postposed_rejection(self):
        rows = self.routes("academic-oral-wine 这次不要用，先讲论文")
        self.assertNotIn("academic-oral-wine", [r["id"] for r in rows])

    def test_opt_out(self):
        self.assertEqual(self.routes("不要使用我的风格，做学术 Oral"), [])

    def test_english_word_boundaries(self):
        self.assertFalse(library.request_mentions("oral", "coral reef"))
        self.assertEqual(self.routes("coral reef"), [])

    def test_invalid_or_conflicting_selections(self):
        for kwargs in ({"content": "missing"}, {"preset": "missing"}, {"visual": "missing"},
                       {"cards": ["NAR-999"]}, {"preset": "NAR-001"},
                       {"content": "academic-oral-wine"}, {"preset": "explain"},
                       {"visual": "project-green", "preset": "author-light"},
                       {"visual": "project-green", "cards": ["CLR-006"]},
                       {"preset": "author-light", "cards": ["CLR-002"]},
                       {"template_state": "invalid"},
                       {"supplied_template": True, "template_state": "absent"}):
            with self.subTest(kwargs=kwargs), self.assertRaises(SystemExit):
                self.routes(**kwargs)

    def test_cli_content_and_visual(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/library.py"), "route",
                                 "--content", "progress", "--visual", "author-light",
                                 "--template-state", "absent", "--json"], capture_output=True,
                                text=True, timeout=10, check=True)
        rows = json.loads(result.stdout)
        self.assertEqual([r["id"] for r in rows], ["progress", "research-progress-light"])
        self.assertEqual(rows[1]["palette"], ["CLR-002"])

    def test_cli_template_flags_are_exclusive(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/library.py"), "route",
                                 "--template", "--template-state", "absent"], capture_output=True,
                                text=True, timeout=10)
        self.assertNotEqual(result.returncode, 0)

    def test_validate_rejects_fourth_content_task(self):
        from unittest.mock import patch
        data = library.load_routes()
        data["routes"].append({**data["routes"][0], "id": "fourth"})
        entries = {e["id"]: e["status"] for e in library.catalog_entries()}
        paths = {e["id"]: ROOT / e["pattern_file"] for e in library.catalog_entries()}
        errors = []
        owners = library.collect_gate_ids(paths, errors)
        with patch.object(library, "load_routes", return_value=data):
            library.validate_routes(entries, owners, errors)
        self.assertTrue(any("exactly the explain" in error for error in errors))

    def test_public_research_request_does_not_impose_author_style(self):
        rows = self.routes("研究进展")
        self.assertEqual(rows[0]["id"], "progress")
        self.assertTrue(all(row["_selection"] != "selected" for row in rows))
        self.assertTrue(all(row["palette"] == [] for row in rows))

    def test_alternative_is_not_negated_with_previous_option(self):
        rows = self.routes("不用 author-light 而用 academic-oral-wine")
        self.assertIn("academic-oral-wine", [row["id"] for row in rows])
        self.assertNotIn("research-progress-light", [row["id"] for row in rows])
        self.assertTrue(all(row["_selection"] != "selected" for row in rows))

    def test_compare_presets_retains_two_inactive_configs(self):
        rows = self.routes("比较 author-light 和 academic-oral-wine，暂时不选择")
        candidates = [row for row in rows if row["_selection"] == "candidate"]
        self.assertEqual({row["id"] for row in candidates},
                         {"research-progress-light", "academic-oral-wine"})
        for row in candidates:
            self.assertEqual(row["palette"], [])
            self.assertTrue(row["_candidate_config"]["palette"])

    def test_template_preserves_individually_selected_narrative_and_grid(self):
        row = self.routes(cards=["NAR-001", "GRD-010", "CLR-010"], template_state="provided")[0]
        self.assertEqual(row["main"], ["NAR-001", "GRD-010"])
        self.assertEqual(row["palette"], [])
        self.assertIn("references/GRD-010.md", row["references"])

    def test_cli_individual_card_selection(self):
        result = subprocess.run([sys.executable, str(ROOT / "scripts/library.py"), "route",
                                 "--card", "NAR-001", "--template-state", "absent", "--json"],
                                capture_output=True, text=True, timeout=10, check=True)
        row = json.loads(result.stdout)[0]
        self.assertEqual(row["_selection"], "selected")
        self.assertEqual(row["main"], ["NAR-001"])
        self.assertEqual(row["palette"], [])
        self.assertEqual(row["_template_state"], "absent")


if __name__ == "__main__":
    unittest.main()
