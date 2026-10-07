"""Regression checks using tiny OOXML packages, not rendered slide fixtures."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/verify_deck_plan.py"
A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
RECOMMENDATION = "先核验 E1，A 保留备选"


def page(slide_id="S01", role="main", title="先核验独立增量", **fields):
    return {
        "id": slide_id,
        "role": role,
        "title": title,
        "claim": RECOMMENDATION,
        "evidence": "实验协议与停止条件",
        "next": "结束",
        **fields,
    }


def plan_text(pages, mode="recommendation", status="proposed"):
    recommendation = RECOMMENDATION if mode == "recommendation" else "none"
    lines = [
        "---",
        f"stance_mode: {mode}",
        f"primary_recommendation: {recommendation}",
        f"user_decision_status: {status}",
        "---",
        "# Slide plan",
    ]
    for item in pages:
        lines.append(f"## {item['id']}")
        lines.extend(f"- {key}: {value}" for key, value in item.items() if key != "id")
    return "\n".join(lines) + "\n"


def xml_bytes(root):
    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def text_element(tag, text):
    root = ET.Element(tag)
    ET.SubElement(root, f"{{{A}}}t").text = text
    return root


def write_pptx(path, pages, *, order=None):
    """Only the XML parts consumed by the verifier; not a rendering fixture."""
    presentation = ET.Element(f"{{{P}}}presentation")
    listing = ET.SubElement(presentation, f"{{{P}}}sldIdLst")
    rels = ET.Element(f"{{{PKG}}}Relationships")
    for index in order or range(1, len(pages) + 1):
        ET.SubElement(listing, f"{{{P}}}sldId", {f"{{{R}}}id": f"rId{index}"})
        ET.SubElement(
            rels,
            f"{{{PKG}}}Relationship",
            {
                "Id": f"rId{index}",
                "Type": f"{R}/slide",
                "Target": f"slides/slide{index}.xml",
            },
        )
    with zipfile.ZipFile(path, "w") as archive:
        archive.writestr("ppt/presentation.xml", xml_bytes(presentation))
        archive.writestr("ppt/_rels/presentation.xml.rels", xml_bytes(rels))
        for index, item in enumerate(pages, 1):
            root = ET.Element(f"{{{P}}}sld")
            if "show" in item:
                root.set("show", item["show"])
            root.append(text_element(f"{{{P}}}sp", item["title"]))
            root.append(text_element(f"{{{P}}}sp", item.get("body", RECOMMENDATION)))
            archive.writestr(f"ppt/slides/slide{index}.xml", xml_bytes(root))
            markers = f"[slide-id:{item['id']}] [role:{item['role']}]"
            notes = item.get("notes", markers)
            note_root = text_element(f"{{{P}}}notes", notes)
            archive.writestr(
                f"ppt/notesSlides/notesSlide{index}.xml", xml_bytes(note_root)
            )
            note_rels = ET.Element(f"{{{PKG}}}Relationships")
            ET.SubElement(
                note_rels,
                f"{{{PKG}}}Relationship",
                {
                    "Id": "rId1",
                    "Type": f"{R}/notesSlide",
                    "Target": f"../notesSlides/notesSlide{index}.xml",
                },
            )
            archive.writestr(
                f"ppt/slides/_rels/slide{index}.xml.rels", xml_bytes(note_rels)
            )


class VerifyDeckPlanTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="taste-plan-test-")
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def run_check(
        self,
        pages=None,
        *,
        deck_pages=None,
        plan_only=False,
        mode="recommendation",
        status="proposed",
        extra=(),
        previous=None,
        current_text=None,
        order=None,
    ):
        pages = [page()] if pages is None else pages
        plan = self.root / "slide-plan.md"
        plan.write_text(
            current_text or plan_text(pages, mode, status), encoding="utf-8"
        )
        command = [sys.executable, str(SCRIPT), str(plan)]
        if not plan_only:
            deck = self.root / "deck.pptx"
            write_pptx(deck, pages if deck_pages is None else deck_pages, order=order)
            command.append(str(deck))
        if previous is not None:
            baseline = self.root / "previous-plan.md"
            baseline.write_text(previous, encoding="utf-8")
            command.extend(["--previous-plan", str(baseline)])
        command.extend(extra)
        result = subprocess.run(command, capture_output=True, text=True, timeout=10)
        try:
            report = json.loads(result.stdout)
        except json.JSONDecodeError:
            self.fail(f"No JSON report: {result.stderr}")
        return result, report

    def test_matching_deck(self):
        result, report = self.run_check()
        self.assertEqual(result.returncode, 0, report)
        self.assertIn("PASS", result.stderr)

    def test_plan_only_does_not_claim_artifact_verification(self):
        result, report = self.run_check(plan_only=True)
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["mode"], "plan-only")
        self.assertIsNone(report["pptx_visible_slide_count"])
        self.assertFalse(report["check_coverage"]["artifact_compared"])

    def test_optional_role_is_supported(self):
        result, report = self.run_check(
            [page(role="optional")], mode="factual", status="not_required"
        )
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["diagnostic_signals"]["optional_slide_ids"], ["S01"])

    def test_missing_markers_fail_by_default(self):
        result, report = self.run_check(deck_pages=[page(notes="")])
        self.assertEqual(result.returncode, 1, report)

    def test_wholly_missing_markers_collapse_to_one_warning(self):
        pages = [page(), page("S02", title="下一步")]
        result, report = self.run_check(
            pages,
            deck_pages=[{**item, "notes": ""} for item in pages],
            extra=("--notes-policy", "warn"),
        )
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(len(report["warnings"]), 1)
        self.assertFalse(report["check_coverage"]["stable_ids_and_roles"])

    def test_partial_markers_report_affected_page(self):
        pages = [page(), page("S02", title="下一步")]
        result, report = self.run_check(
            pages,
            deck_pages=[
                pages[0],
                {
                    **pages[1],
                    "notes": "[slide-id:S02]",
                },
            ],
        )
        self.assertEqual(result.returncode, 1, report)
        self.assertIn("S02", " ".join(report["errors"]))

    def test_wrong_markers_are_not_reported_as_absent(self):
        pages = [page(), page("S02", title="下一步")]
        result, report = self.run_check(
            pages,
            deck_pages=[
                {**item, "notes": "[slide-id:OTHER] [role:backup]"} for item in pages
            ],
            extra=("--notes-policy", "warn"),
        )
        self.assertEqual(result.returncode, 1, report)
        self.assertIn("role mismatch", " ".join(report["errors"]))
        self.assertNotIn("no slide carries", " ".join(report["errors"]))

    def test_ambiguous_marker_does_not_pass_by_containing_expected_value(self):
        result, report = self.run_check(
            deck_pages=[
                page(notes="[slide-id:S01] [slide-id:OTHER] [role:main] [role:backup]")
            ]
        )
        self.assertEqual(result.returncode, 1, report)
        self.assertIn("ambiguous", " ".join(report["errors"]))

    def test_ignore_policy_reports_disabled_checks(self):
        result, report = self.run_check(extra=("--notes-policy", "ignore"))
        self.assertEqual(result.returncode, 0, report)
        self.assertFalse(report["check_coverage"]["stable_ids_and_roles"])
        self.assertTrue(report["warnings"])

    def test_recommendation_in_notes_only_fails(self):
        result, report = self.run_check(
            deck_pages=[
                page(
                    body="请老师选择",
                    notes=f"[slide-id:S01] [role:main] {RECOMMENDATION}",
                )
            ]
        )
        self.assertEqual(result.returncode, 1, report)
        self.assertIn("visible main-slide text", " ".join(report["errors"]))

    def test_recommendation_only_in_backup_fails(self):
        pages = [page(), page("S02", role="backup", title="备查")]
        result, report = self.run_check(
            pages,
            deck_pages=[
                {**pages[0], "body": "请老师选择"},
                pages[1],
            ],
        )
        self.assertEqual(result.returncode, 1, report)

    def test_recommendation_removed_requires_explicit_decision(self):
        previous = plan_text([page()])
        result, report = self.run_check(mode="menu", previous=previous)
        self.assertEqual(result.returncode, 1, report)
        self.assertTrue(report["protected_diff"])

    def test_confirmed_menu_is_structurally_valid_not_proof_of_authorization(self):
        result, report = self.run_check(
            mode="menu", status="confirmed", previous=plan_text([page()])
        )
        self.assertEqual(result.returncode, 0, report)
        self.assertFalse(report["check_coverage"]["user_authorization_verified"])

    def test_page_diff_includes_claim_evidence_role_and_order(self):
        previous_pages = [page(), page("S02", title="第二页")]
        pages = [
            page(
                "S02",
                title="第二页",
                claim="新证据限定结论",
                evidence="原文图 2",
                role="optional",
                page_role="boundary",
            ),
            page(),
        ]
        result, report = self.run_check(pages, previous=plan_text(previous_pages))
        self.assertEqual(result.returncode, 0, report)
        diff = report["slide_diff"]
        self.assertEqual(diff["order"]["after"], ["S02", "S01"])
        changes = next(row["fields"] for row in diff["changed"] if row["id"] == "S02")
        self.assertTrue({"claim", "evidence", "role", "page_role"} <= set(changes))
        self.assertTrue(report["warnings"])

    def test_page_diff_includes_additions_and_removals(self):
        old = plan_text([page(), page("S02", title="移除")])
        result, report = self.run_check(
            [page(), page("S03", title="新增")], previous=old
        )
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["slide_diff"]["added"], ["S03"])
        self.assertEqual(report["slide_diff"]["removed"], ["S02"])

    def test_duplicate_protected_field_fails(self):
        text = plan_text([page()]).replace(
            "stance_mode: recommendation",
            "stance_mode: menu\nstance_mode: recommendation",
        )
        result, report = self.run_check(current_text=text)
        self.assertEqual(result.returncode, 1, report)

    def test_duplicate_page_field_fails(self):
        text = plan_text([page()]) + "- role: main\n"
        result, report = self.run_check(current_text=text)
        self.assertEqual(result.returncode, 1, report)

    def test_fenced_examples_do_not_become_pages(self):
        text = plan_text([page()]) + "\n```markdown\n## S99\n- role: backup\n```\n"
        result, report = self.run_check(current_text=text)
        self.assertEqual(result.returncode, 0, report)
        self.assertEqual(report["plan_slide_count"], 1)

    def test_empty_plan_fails(self):
        result, report = self.run_check(
            [], plan_only=True, mode="factual", status="not_required"
        )
        self.assertEqual(result.returncode, 1, report)

    def test_duplicate_slide_ids_fail(self):
        result, report = self.run_check([page(), page()], plan_only=True)
        self.assertEqual(result.returncode, 1, report)

    def test_hidden_slides_excluded_for_both_boolean_forms(self):
        for show in ("0", "false"):
            with self.subTest(show=show):
                result, report = self.run_check(
                    deck_pages=[
                        page("S00", title="隐藏页", show=show),
                        page(),
                    ]
                )
                self.assertEqual(result.returncode, 0, report)
                self.assertEqual(report["hidden_pptx_slides"], [1])

    def test_relationship_order_not_part_filename_order(self):
        pages = [page(), page("S02", title="第二页")]
        result, report = self.run_check(
            pages, deck_pages=list(reversed(pages)), order=[2, 1]
        )
        self.assertEqual(result.returncode, 0, report)

    def test_title_mismatch_fails(self):
        result, report = self.run_check(deck_pages=[page(title="另一结论")])
        self.assertEqual(result.returncode, 1, report)

    def test_width_and_whitespace_normalization(self):
        result, report = self.run_check(
            deck_pages=[page(title="先 核验 独立增量", body="先核验 Ｅ１，Ａ 保留备选")]
        )
        self.assertEqual(result.returncode, 0, report)


if __name__ == "__main__":
    unittest.main()
