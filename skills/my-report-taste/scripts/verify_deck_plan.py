#!/usr/bin/env python3
"""Preflight a slide plan; optionally compare a PPTX and a prior plan.

The check is deliberately narrow: it verifies fields that have a deterministic
counterpart. It prints judgment-heavy signals such as the title chain without
pretending to score their quality.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import unicodedata
import zipfile
from dataclasses import dataclass
from pathlib import Path
from xml.etree import ElementTree as ET


DRAWING_NS = "http://schemas.openxmlformats.org/drawingml/2006/main"
PRESENTATION_NS = "http://schemas.openxmlformats.org/presentationml/2006/main"
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OFFICE_REL_NS = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PROTECTED_FIELDS = (
    "stance_mode",
    "primary_recommendation",
    "user_decision_status",
)
STANCE_MODES = {"recommendation", "menu", "factual"}
DECISION_STATUSES = {"proposed", "confirmed", "not_required"}
SLIDE_ROLES = {"main", "optional", "backup"}
EMPTY_RECOMMENDATIONS = {"", "none", "null", "无"}
SLIDE_HEADING = re.compile(r"^##\s+([A-Za-z][A-Za-z0-9_-]*\d[A-Za-z0-9_-]*)\s*$")
SLIDE_FIELD = re.compile(
    r"^\s*-\s+(role|title|claim|evidence|next|page_role|density_mode):\s*(.*?)\s*$",
    re.IGNORECASE,
)
NOTE_MARKER = re.compile(r"\[(slide-id|role):([^\]]*)\]", re.IGNORECASE)
PAGE_FIELDS = (
    "role",
    "title",
    "claim",
    "evidence",
    "next",
    "page_role",
    "density_mode",
)


@dataclass(frozen=True)
class PlannedSlide:
    slide_id: str
    role: str
    title: str
    claim: str
    evidence: str
    next_step: str
    page_role: str = ""
    density_mode: str = ""

    def fields(self) -> dict[str, str]:
        return {
            key: getattr(self, "next_step" if key == "next" else key)
            for key in PAGE_FIELDS
        }


@dataclass(frozen=True)
class SlidePlan:
    path: Path
    protected: dict[str, str]
    slides: list[PlannedSlide]


@dataclass(frozen=True)
class PptxSlide:
    source_index: int
    text: str
    text_runs: tuple[str, ...]
    notes: str
    shape_count: int
    picture_count: int
    graphic_frame_count: int
    table_count: int

    @property
    def layout_signature(self) -> str:
        # Object counts are a diagnostic, not geometric layout equivalence.
        return (
            f"shapes={self.shape_count};pictures={self.picture_count};"
            f"graphic_frames={self.graphic_frame_count};tables={self.table_count}"
        )


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).casefold()
    return re.sub(r"\s+", "", value)


def scalar(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'"}:
        if value[0] == '"':
            try:
                decoded = json.loads(value)
                if isinstance(decoded, str):
                    return decoded
            except json.JSONDecodeError:
                pass
        return value[1:-1]
    return value


def parse_plan(path: Path) -> SlidePlan:
    text = path.read_text(encoding="utf-8")
    lines = text.splitlines()
    protected: dict[str, str] = {}

    body_start = 0
    if lines and lines[0].strip() == "---":
        for index in range(1, len(lines)):
            line = lines[index]
            if line.strip() == "---":
                body_start = index + 1
                break
            if ":" not in line or line.lstrip().startswith("#"):
                continue
            key, value = line.split(":", 1)
            key = key.strip()
            if key in PROTECTED_FIELDS:
                if key in protected:
                    raise ValueError(f"{path}: duplicate protected field: {key}")
                protected[key] = scalar(value)
        else:
            raise ValueError(f"{path}: YAML frontmatter is not closed")

    raw_slides: list[tuple[str, dict[str, str]]] = []
    current_id: str | None = None
    current_fields: dict[str, str] = {}
    fence: tuple[str, int] | None = None
    for line in lines[body_start:]:
        fence_match = re.match(r"^\s{0,3}(`{3,}|~{3,})(.*)$", line)
        if fence_match:
            marker, tail = fence_match.groups()
            if fence is None:
                fence = (marker[0], len(marker))
            elif marker[0] == fence[0] and len(marker) >= fence[1] and not tail.strip():
                fence = None
            continue
        if fence is not None:
            continue
        heading = SLIDE_HEADING.match(line)
        if heading:
            if current_id is not None:
                raw_slides.append((current_id, current_fields))
            current_id = heading.group(1)
            current_fields = {}
            continue
        if re.match(r"^#{1,2}\s", line):
            if current_id is not None:
                raw_slides.append((current_id, current_fields))
            current_id, current_fields = None, {}
            continue
        if current_id is None:
            continue
        field_match = SLIDE_FIELD.match(line)
        if field_match:
            key = field_match.group(1).lower()
            if key in current_fields:
                raise ValueError(f"{path}: {current_id}: duplicate field: {key}")
            current_fields[key] = scalar(field_match.group(2))
    if fence is not None:
        raise ValueError(f"{path}: Markdown code fence is not closed")
    if current_id is not None:
        raw_slides.append((current_id, current_fields))

    slides = [
        PlannedSlide(
            slide_id=slide_id,
            role=fields.get("role", ""),
            title=fields.get("title", ""),
            claim=fields.get("claim", ""),
            evidence=fields.get("evidence", ""),
            next_step=fields.get("next", ""),
            page_role=fields.get("page_role", ""),
            density_mode=fields.get("density_mode", ""),
        )
        for slide_id, fields in raw_slides
    ]
    return SlidePlan(path=path, protected=protected, slides=slides)


def xml_text(root: ET.Element) -> str:
    return " ".join(node.text or "" for node in root.findall(f".//{{{DRAWING_NS}}}t"))


def notes_for_slide(archive: zipfile.ZipFile, slide_path: str) -> str:
    filename = posixpath.basename(slide_path)
    rels_path = posixpath.join(
        posixpath.dirname(slide_path),
        "_rels",
        f"{filename}.rels",
    )
    try:
        rels_root = ET.fromstring(archive.read(rels_path))
    except KeyError:
        return ""
    for relation in rels_root.findall(f".//{{{REL_NS}}}Relationship"):
        if relation.get("Type", "").endswith("/notesSlide"):
            target = relation.get("Target", "")
            notes_path = posixpath.normpath(
                posixpath.join(posixpath.dirname(slide_path), target)
            ).lstrip("/")
            try:
                return xml_text(ET.fromstring(archive.read(notes_path)))
            except KeyError:
                return ""
    return ""


def ordered_slide_paths(archive: zipfile.ZipFile) -> list[tuple[int, str]]:
    presentation_path = "ppt/presentation.xml"
    relationships_path = "ppt/_rels/presentation.xml.rels"
    try:
        presentation = ET.fromstring(archive.read(presentation_path))
        relationships = ET.fromstring(archive.read(relationships_path))
    except KeyError as exc:
        raise ValueError(f"PPTX is missing required part: {exc}") from exc

    targets = {
        relation.get("Id", ""): relation.get("Target", "")
        for relation in relationships.findall(f".//{{{REL_NS}}}Relationship")
        if relation.get("Type", "").endswith("/slide")
    }
    ordered: list[tuple[int, str]] = []
    slide_ids = presentation.findall(f".//{{{PRESENTATION_NS}}}sldId")
    for ordinal, slide_id in enumerate(slide_ids, start=1):
        relationship_id = slide_id.get(f"{{{OFFICE_REL_NS}}}id", "")
        target = targets.get(relationship_id)
        if not target:
            raise ValueError(
                f"PPTX slide {ordinal} has no relationship target: "
                f"{relationship_id!r}"
            )
        slide_path = posixpath.normpath(
            posixpath.join(posixpath.dirname(presentation_path), target)
        ).lstrip("/")
        ordered.append((ordinal, slide_path))
    return ordered


def read_pptx(path: Path) -> tuple[list[PptxSlide], list[int]]:
    visible: list[PptxSlide] = []
    hidden: list[int] = []
    with zipfile.ZipFile(path) as archive:
        for source_index, slide_path in ordered_slide_paths(archive):
            try:
                slide_xml = archive.read(slide_path)
            except KeyError as exc:
                raise ValueError(
                    f"PPTX slide {source_index} target is missing: {slide_path}"
                ) from exc
            root = ET.fromstring(slide_xml)
            if root.get("show", "").casefold() in {"0", "false"}:
                hidden.append(source_index)
                continue
            text_runs = tuple(
                (node.text or "").strip()
                for node in root.findall(f".//{{{DRAWING_NS}}}t")
                if (node.text or "").strip()
            )
            visible.append(
                PptxSlide(
                    source_index=source_index,
                    text=" ".join(text_runs),
                    text_runs=text_runs,
                    notes=notes_for_slide(archive, slide_path),
                    shape_count=len(root.findall(f".//{{{PRESENTATION_NS}}}sp")),
                    picture_count=len(root.findall(f".//{{{PRESENTATION_NS}}}pic")),
                    graphic_frame_count=len(
                        root.findall(f".//{{{PRESENTATION_NS}}}graphicFrame")
                    ),
                    table_count=len(root.findall(f".//{{{DRAWING_NS}}}tbl")),
                )
            )
    return visible, hidden


def validate_contract(
    plan: SlidePlan,
    errors: list[str],
    label: str = "plan",
) -> None:
    missing = [field for field in PROTECTED_FIELDS if field not in plan.protected]
    if missing:
        errors.append(f"{label} is missing protected fields: {', '.join(missing)}")
        return

    mode = plan.protected["stance_mode"]
    recommendation = normalized(plan.protected["primary_recommendation"])
    status = plan.protected["user_decision_status"]
    if mode not in STANCE_MODES:
        errors.append(f"{label} has invalid stance_mode: {mode!r}")
    if status not in DECISION_STATUSES:
        errors.append(f"{label} has invalid user_decision_status: {status!r}")
    if mode == "recommendation" and recommendation in EMPTY_RECOMMENDATIONS:
        errors.append(
            f"{label}: recommendation mode requires a concrete "
            "primary_recommendation"
        )
    if mode in {"menu", "factual"} and recommendation not in EMPTY_RECOMMENDATIONS:
        errors.append(f"{label}: {mode} mode requires primary_recommendation: none")
    if mode == "menu" and status != "confirmed":
        errors.append(f"{label}: menu mode requires user_decision_status: confirmed")
    if mode == "factual" and status == "proposed":
        errors.append(
            f"{label}: factual mode cannot use user_decision_status: proposed"
        )


def compare_plans(
    previous: SlidePlan | None,
    current: SlidePlan,
    errors: list[str],
) -> list[dict[str, str]]:
    if previous is None:
        return []
    diff: list[dict[str, str]] = []
    for field in PROTECTED_FIELDS:
        before = previous.protected.get(field, "<missing>")
        after = current.protected.get(field, "<missing>")
        if before != after:
            diff.append({"field": field, "before": before, "after": after})
    semantic_fields = {item["field"] for item in diff}
    if semantic_fields & {"stance_mode", "primary_recommendation"}:
        if current.protected.get("user_decision_status") != "confirmed":
            errors.append(
                "protected stance or recommendation changed without "
                "user_decision_status: confirmed"
            )
    return diff


def slide_plan_diff(
    previous: SlidePlan | None,
    current: SlidePlan,
) -> dict[str, object] | None:
    """Expose textual changes; do not infer semantic equivalence or approval."""
    if previous is None:
        return None
    before = {slide.slide_id: slide for slide in previous.slides}
    after = {slide.slide_id: slide for slide in current.slides}
    changed = []
    for slide_id in after.keys() & before.keys():
        old_fields, new_fields = before[slide_id].fields(), after[slide_id].fields()
        fields = {
            key: {"before": old_fields[key], "after": new_fields[key]}
            for key in PAGE_FIELDS
            if old_fields[key] != new_fields[key]
        }
        if fields:
            changed.append({"id": slide_id, "fields": fields})
    old_order, new_order = list(before), list(after)
    return {
        "added": [key for key in after if key not in before],
        "removed": [key for key in before if key not in after],
        "changed": sorted(changed, key=lambda item: new_order.index(item["id"])),
        "order": (
            {"before": old_order, "after": new_order}
            if old_order != new_order
            else None
        ),
    }


def validate_plan_slides(
    plan: SlidePlan,
    errors: list[str],
    warnings: list[str],
) -> None:
    if not plan.slides:
        errors.append(f"{plan.path}: plan contains no slides")
    seen_ids: set[str] = set()
    for planned in plan.slides:
        if planned.slide_id in seen_ids:
            errors.append(f"duplicate slide id: {planned.slide_id}")
        seen_ids.add(planned.slide_id)
        if planned.role not in SLIDE_ROLES:
            errors.append(
                f"{planned.slide_id}: role must be main, optional or backup, "
                f"got {planned.role!r}"
            )
        if not planned.title:
            errors.append(f"{planned.slide_id}: missing title")
        for field_name in ("claim", "evidence", "next"):
            if not planned.fields()[field_name]:
                warnings.append(f"{planned.slide_id}: missing {field_name}")


def note_markers(notes: str) -> dict[str, set[str]]:
    markers: dict[str, set[str]] = {"slide-id": set(), "role": set()}
    for key, value in NOTE_MARKER.findall(normalized(notes)):
        markers[key].add(value)
    return markers


def validate_slides(
    plan: SlidePlan,
    pptx_slides: list[PptxSlide],
    notes_policy: str,
    errors: list[str],
    warnings: list[str],
) -> bool:
    """Return whether stable IDs and roles were fully compared successfully."""
    if len(plan.slides) != len(pptx_slides):
        errors.append(
            f"visible slide count differs: plan={len(plan.slides)}, "
            f"pptx={len(pptx_slides)}"
        )

    marker_gaps: list[tuple[PlannedSlide, PptxSlide, list[str]]] = []
    markers_valid = len(plan.slides) == len(pptx_slides) and bool(plan.slides)
    if notes_policy == "ignore":
        warnings.append(
            "note marker checks explicitly disabled by --notes-policy ignore"
        )
        markers_valid = False
    for index, planned in enumerate(plan.slides, start=1):
        if index > len(pptx_slides):
            continue
        actual = pptx_slides[index - 1]
        if planned.title and normalized(planned.title) not in normalized(actual.text):
            errors.append(
                f"{planned.slide_id}: planned title not found on PPTX slide "
                f"{actual.source_index}: {planned.title!r}"
            )

        if notes_policy == "ignore":
            continue
        markers = note_markers(actual.notes)
        missing_markers = []
        for key, expected in (("slide-id", planned.slide_id), ("role", planned.role)):
            values = markers[key]
            if not values:
                missing_markers.append(f"[{key}:{expected}]")
                markers_valid = False
            elif len(values) > 1:
                errors.append(
                    f"{planned.slide_id}: PPTX slide {actual.source_index} "
                    f"ambiguous {key} markers: {', '.join(sorted(values))}"
                )
                markers_valid = False
            elif values != {normalized(expected)}:
                errors.append(
                    f"{planned.slide_id}: PPTX slide {actual.source_index} "
                    f"{key} mismatch: plan says {expected}, "
                    f"deck notes say {next(iter(values))}"
                )
                markers_valid = False
        if missing_markers:
            marker_gaps.append((planned, actual, missing_markers))

    if marker_gaps and notes_policy != "ignore":
        sink = errors if notes_policy == "required" else warnings
        deck_has_no_markers = bool(pptx_slides) and all(
            not any(note_markers(slide.notes).values()) for slide in pptx_slides
        )
        if deck_has_no_markers and len(plan.slides) > 1:
            sink.append(
                f"no slide carries [slide-id:*] or [role:*] note markers "
                f"({len(pptx_slides)} slides); stable id and main/optional/backup role "
                "checks are inactive for this deck"
            )
        else:
            for planned, actual, missing in marker_gaps:
                sink.append(
                    f"{planned.slide_id}: PPTX slide {actual.source_index} "
                    "notes missing " + ", ".join(missing)
                )
    return markers_valid


def recommendation_locations(
    plan: SlidePlan,
    pptx_slides: list[PptxSlide],
) -> list[int]:
    if plan.protected.get("stance_mode") != "recommendation":
        return []
    recommendation = normalized(plan.protected.get("primary_recommendation", ""))
    if recommendation in EMPTY_RECOMMENDATIONS:
        return []
    return [
        slide.source_index
        for planned, slide in zip(plan.slides, pptx_slides)
        if planned.role == "main" and recommendation in normalized(slide.text)
    ]


def diagnostic_signals(
    plan: SlidePlan,
    pptx_slides: list[PptxSlide],
) -> dict[str, object]:
    question_titles = [
        {"id": slide.slide_id, "title": slide.title}
        for slide in plan.slides
        if slide.title.rstrip().endswith(("?", "？"))
    ]
    evidence_chain = [
        {"id": slide.slide_id, "role": slide.role, "evidence": slide.evidence}
        for slide in plan.slides
    ]
    main_ids = [slide.slide_id for slide in plan.slides if slide.role == "main"]
    backup_ids = [slide.slide_id for slide in plan.slides if slide.role == "backup"]
    optional_ids = [slide.slide_id for slide in plan.slides if slide.role == "optional"]

    no_native_evidence: list[dict[str, object]] = []
    signatures: dict[str, list[str]] = {}
    repeated_runs: dict[str, tuple[str, list[str]]] = {}
    for planned, actual in zip(plan.slides, pptx_slides):
        if (
            planned.role == "main"
            and actual.picture_count == 0
            and actual.graphic_frame_count == 0
            and actual.table_count == 0
        ):
            no_native_evidence.append(
                {"id": planned.slide_id, "pptx_slide": actual.source_index}
            )
        signatures.setdefault(actual.layout_signature, []).append(planned.slide_id)
        seen_on_slide: set[str] = set()
        for run in actual.text_runs:
            key = normalized(run)
            if key in seen_on_slide or not 6 <= len(key) <= 100:
                continue
            if not any(character.isalpha() for character in key):
                continue
            seen_on_slide.add(key)
            _, slide_ids = repeated_runs.setdefault(key, (run, []))
            slide_ids.append(planned.slide_id)

    repeated_layout_signatures = [
        {"signature": signature, "slide_ids": slide_ids}
        for signature, slide_ids in signatures.items()
        if len(slide_ids) >= 3
    ]
    repeated_text_fragments = sorted(
        [
            {"text": text, "slide_ids": slide_ids}
            for text, slide_ids in repeated_runs.values()
            if len(slide_ids) >= 3
        ],
        key=lambda item: (-len(item["slide_ids"]), item["text"]),
    )
    return {
        "main_slide_ids": main_ids,
        "optional_slide_ids": optional_ids,
        "backup_slide_ids": backup_ids,
        "question_titles": question_titles,
        "evidence_chain": evidence_chain,
        "main_slides_without_picture_table_or_graphic_frame": no_native_evidence,
        "repeated_layout_signatures": repeated_layout_signatures,
        "repeated_text_fragments": repeated_text_fragments,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Preflight a slide plan, optionally comparing a PPTX and prior plan."
    )
    parser.add_argument("plan", type=Path)
    parser.add_argument(
        "pptx",
        type=Path,
        nargs="?",
        help="Omit for plan-only preflight before visual production.",
    )
    parser.add_argument("--previous-plan", type=Path)
    parser.add_argument(
        "--notes-policy",
        choices=("required", "warn", "ignore"),
        default="required",
        help=(
            "How to handle missing [slide-id:*] and [role:*] note markers. "
            "Defaults to required so a missing marker fails loudly; pass warn "
            "for legacy missing markers. Contradictory markers still fail. "
            "ignore disables all marker checks and reports that limitation."
        ),
    )
    return parser


def emit_console_summary(
    plan: str,
    pptx: str,
    errors: list[str],
    warnings: list[str],
) -> None:
    """Mirror the verdict on stderr so a terminal run needs no JSON parsing."""
    status = "FAIL" if errors else "PASS"
    print(f"{status}: {plan} vs {pptx} (warnings={len(warnings)})", file=sys.stderr)
    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)


def main() -> int:
    args = build_parser().parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    try:
        current = parse_plan(args.plan)
        previous = parse_plan(args.previous_plan) if args.previous_plan else None
        pptx_slides, hidden_slides = read_pptx(args.pptx) if args.pptx else ([], [])
    except (OSError, ValueError, zipfile.BadZipFile, ET.ParseError) as exc:
        print(
            json.dumps(
                {"errors": [str(exc)], "warnings": []},
                ensure_ascii=False,
                indent=2,
            )
        )
        emit_console_summary(str(args.plan), str(args.pptx), [str(exc)], [])
        return 1

    validate_contract(current, errors)
    validate_plan_slides(current, errors, warnings)
    if previous is not None:
        validate_contract(previous, errors, label="previous plan")
        validate_plan_slides(previous, errors, warnings)
    protected_diff = compare_plans(previous, current, errors)
    page_diff = slide_plan_diff(previous, current)
    if page_diff and any(page_diff.values()):
        warnings.append(
            "page plan changed; review slide_diff against task authorization and "
            "record impact in verification.md; this is not a semantic approval"
        )
    markers_checked = False
    if args.pptx:
        markers_checked = validate_slides(
            current,
            pptx_slides,
            args.notes_policy,
            errors,
            warnings,
        )
    recommendation_slides = recommendation_locations(current, pptx_slides)
    if (
        args.pptx
        and current.protected.get("stance_mode") == "recommendation"
        and not recommendation_slides
    ):
        errors.append(
            "primary_recommendation was not found in visible main-slide text; "
            "notes, optional pages and backup pages cannot carry it alone"
        )
    if hidden_slides:
        warnings.append(
            "hidden PPTX slides excluded from comparison: "
            + ", ".join(str(index) for index in hidden_slides)
        )

    report = {
        "mode": "pptx-comparison" if args.pptx else "plan-only",
        "plan": str(current.path),
        "pptx": str(args.pptx) if args.pptx else None,
        "previous_plan": str(previous.path) if previous else None,
        "protected": current.protected,
        "protected_diff": protected_diff,
        "slide_diff": page_diff,
        "plan_slide_count": len(current.slides),
        "pptx_visible_slide_count": len(pptx_slides) if args.pptx else None,
        "hidden_pptx_slides": hidden_slides,
        "primary_recommendation_pptx_slides": recommendation_slides,
        "title_chain": [
            {"id": slide.slide_id, **slide.fields()} for slide in current.slides
        ],
        "diagnostic_signals": diagnostic_signals(current, pptx_slides),
        "check_coverage": {
            "artifact_compared": args.pptx is not None,
            "previous_plan_compared": previous is not None,
            "stable_ids_and_roles": markers_checked,
            "user_authorization_verified": False,
            "claim_semantics_verified": False,
            "rendering_verified": False,
        },
        "limitations": [
            "confirmed is a declared status, not verified user authorization; "
            "check the decision source in verification.md",
            "text presence does not prove visibility, title hierarchy, factual "
            "accuracy or semantic agreement; inspect the rendered artifact",
            "repeated_layout_signatures group object counts only; no pictures "
            "does not mean no evidence (formulas and native diagrams may qualify)",
        ],
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    emit_console_summary(
        str(current.path),
        str(args.pptx) if args.pptx else "plan-only",
        errors,
        warnings,
    )
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
