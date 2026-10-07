#!/usr/bin/env python3
"""Check structured Markdown speaker scripts; estimates are not rehearsals."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path


PAGE = re.compile(r"^##\s+(S\d+)\b[^\n]*$", re.MULTILINE)
FIELD = re.compile(r"^\s*-\s*(role|target_seconds):\s*(.*?)\s*$", re.MULTILINE)
SECTION = re.compile(r"^###\s+([^\n]+)$", re.MULTILINE)
WORDS = re.compile(r"[A-Za-z0-9]+(?:[’'\-][A-Za-z0-9]+)*")
CJK = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff]")
NUMBERS = re.compile(r"(?<![A-Za-z0-9_.])[-+]?\d+(?:\.\d+)?%?")
MATH = re.compile(r"\$\$.*?\$\$|\\\[.*?\\\]|\\\(.*?\\\)|(?<!\\)\$[^$\n]+\$", re.DOTALL)
ROLES = {"main", "optional", "backup"}


def parse_script(text: str) -> tuple[list[dict], list[str]]:
    pages, errors, seen = [], [], set()
    headings = list(PAGE.finditer(text))
    if not headings:
        return [], ["No page headings found; expected '## S01 — Title'."]
    for index, match in enumerate(headings):
        page_id = match.group(1)
        if page_id in seen:
            errors.append(f"{page_id}: duplicate page ID.")
        seen.add(page_id)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
        body = text[match.end():end]
        sections = list(SECTION.finditer(body))
        metadata = body[:sections[0].start()] if sections else body
        fields = {}
        for field, value in FIELD.findall(metadata):
            if field in fields:
                errors.append(f"{page_id}: duplicate {field}.")
            fields[field] = value
        role = fields.get("role", "")
        if role not in ROLES:
            errors.append(f"{page_id}: role must be main, optional or backup.")
        target = None
        if "target_seconds" in fields:
            try:
                target = float(fields["target_seconds"])
                if not 0 < target < float("inf"):
                    raise ValueError
            except ValueError:
                errors.append(f"{page_id}: target_seconds must be finite and positive.")
                target = None
        elif role != "backup":
            errors.append(f"{page_id}: missing target_seconds.")
        content = {}
        for j, heading in enumerate(sections):
            name = heading.group(1).strip().lower()
            tail = sections[j + 1].start() if j + 1 < len(sections) else len(body)
            if name in content:
                errors.append(f"{page_id}: duplicate section {name}.")
            content[name] = body[heading.end():tail].strip()
        spoken = content.get("script", "") or (content.get("answer", "") if role == "backup" else "")
        if not spoken:
            errors.append(f"{page_id}: missing spoken Script (or backup Answer).")
        pages.append({"id": page_id, "role": role, "target_seconds": target,
                      "sections": content, "full_script": spoken})
    return pages, errors


def spoken_text(page: dict, short: bool) -> tuple[str, list[str]]:
    sections, warnings = page["sections"], []
    script = page["full_script"]
    transition = sections.get("transition", "")
    if short:
        if sections.get("short script", ""):
            script = sections["short script"]
            if transition and not sections.get("short transition", ""):
                warnings.append("Short transition missing; full transition included.")
            transition = sections.get("short transition", "") or transition
        else:
            warnings.append("Short script missing; full script and transition included.")
    return script + "\n" + transition, warnings


def clean_spoken(text: str) -> tuple[str, list[str]]:
    warnings = []
    if MATH.search(text):
        warnings.append("Math source excluded from counts; supply its spoken explanation.")
    text = MATH.sub(" ", text)
    # Explicit stage-direction lines are not speech. Other prose is counted.
    text = re.sub(r"^\s*\[(?:Cue|Action|提示|动作):[^\n]*\]\s*$", "", text,
                  flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"\[([^]\n]+)\]\([^)\n]+\)", r"\1", text)
    if re.search(r"\b(?:TODO|TBD)\b|\[(?:Name|Affiliation|待填)[^]]*\]", text, re.IGNORECASE):
        warnings.append("Unfilled placeholder found in spoken text.")
    return text, warnings


def analyze(pages: list[dict], language: str, *, short: bool = False,
            include_optional: bool = False, wpm=(130.0, 150.0),
            cpm=(200.0, 260.0), pause_seconds: float = 5.0,
            minutes: float | None = None) -> dict:
    rows, warnings = [], []
    for page in pages:
        if page["role"] != "main" and not (include_optional and page["role"] == "optional"):
            continue
        text, local = spoken_text(page, short)
        text, clean_warnings = clean_spoken(text)
        local.extend(clean_warnings)
        words, chars = len(WORDS.findall(text)), len(CJK.findall(text))
        if language == "en" and chars:
            local.append("CJK text in English script; estimated separately using cpm.")
        fast = 60 * (words / wpm[1] + chars / cpm[1]) + pause_seconds
        slow = 60 * (words / wpm[0] + chars / cpm[0]) + pause_seconds
        target = page["target_seconds"]
        if not short and target is not None and fast > target:
            local.append("Page budget is below the fast-end estimate.")
        rows.append({"id": page["id"], "role": page["role"], "latin_words": words,
                     "cjk_chars": chars, "target_seconds": target,
                     "estimated_seconds": [round(fast, 1), round(slow, 1)]})
        warnings.extend(f"{page['id']}: {message}" for message in local)
    fast = sum(row["estimated_seconds"][0] for row in rows)
    slow = sum(row["estimated_seconds"][1] for row in rows)
    budget = sum(row["target_seconds"] or 0 for row in rows)
    if not rows:
        warnings.append("No selected main/optional pages; no talk duration estimated.")
    if minutes is not None:
        if fast > minutes * 60:
            warnings.append("Even the fast-end estimate exceeds the talk target.")
        elif slow > minutes * 60:
            warnings.append("The slow-end estimate exceeds the talk target.")
        if not short and budget > minutes * 60:
            warnings.append("Sum of page budgets exceeds the talk target.")
    return {"language": language, "mode": "short" if short else "full",
            "assumptions": {"wpm": list(wpm), "cpm": list(cpm), "pause_seconds_per_page": pause_seconds,
                            "optional_included": include_optional, "target_minutes": minutes},
            "pages": rows, "total_latin_words": sum(row["latin_words"] for row in rows),
            "total_cjk_chars": sum(row["cjk_chars"] for row in rows),
            "estimated_minutes": [round(fast / 60, 2), round(slow / 60, 2)],
            "page_budget_minutes": None if short else round(budget / 60, 2),
            "warnings": warnings}


def compare_pair(left: list[dict], right: list[dict], short: bool) -> tuple[list[str], list[str]]:
    errors, warnings = [], []
    if [(p["id"], p["role"]) for p in left] != [(p["id"], p["role"]) for p in right]:
        errors.append("Paired page IDs, order or roles differ.")
    right_by_id = {page["id"]: page for page in right}
    for page in left:
        other = right_by_id.get(page["id"])
        if other is None:
            continue
        first = clean_spoken(spoken_text(page, short)[0])[0]
        second = clean_spoken(spoken_text(other, short)[0])[0]
        if sorted(NUMBERS.findall(first)) != sorted(NUMBERS.findall(second)):
            warnings.append(f"{page['id']}: numeric cues differ; review manually (words may spell out numbers).")
    return errors, warnings


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("script", type=Path)
    parser.add_argument("--language", required=True, choices=["en", "zh"])
    parser.add_argument("--paired", type=Path)
    parser.add_argument("--paired-language", choices=["en", "zh"])
    parser.add_argument("--minutes", type=float)
    parser.add_argument("--short", action="store_true")
    parser.add_argument("--include-optional", action="store_true")
    parser.add_argument("--wpm", nargs=2, type=float, default=[130, 150], metavar=("SLOW", "FAST"))
    parser.add_argument("--cpm", nargs=2, type=float, default=[200, 260], metavar=("SLOW", "FAST"))
    parser.add_argument("--pause-seconds", type=float, default=5)
    args = parser.parse_args()
    if bool(args.paired) != bool(args.paired_language):
        parser.error("--paired and --paired-language must be used together")
    if any(not 0 < rate[0] <= rate[1] < float("inf") for rate in (args.wpm, args.cpm)):
        parser.error("speaking rates must be finite positive slow/fast pairs")
    if not 0 <= args.pause_seconds < float("inf") or (args.minutes is not None and not 0 < args.minutes < float("inf")):
        parser.error("pause must be finite and nonnegative; target minutes must be finite and positive")
    settings = dict(short=args.short, include_optional=args.include_optional, wpm=args.wpm,
                    cpm=args.cpm, pause_seconds=args.pause_seconds, minutes=args.minutes)
    errors, results, pairing_warnings = [], [], []
    parsed = []
    for path, language in [(args.script, args.language)] + ([(args.paired, args.paired_language)] if args.paired else []):
        try:
            pages, local_errors = parse_script(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeError) as exc:
            pages, local_errors = [], [str(exc)]
        parsed.append(pages)
        errors.extend(f"{path.name}: {message}" for message in local_errors)
        report = analyze(pages, language, **settings)
        report["file"] = str(path)
        results.append(report)
    if args.paired:
        pair_errors, pairing_warnings = compare_pair(*parsed, short=args.short)
        errors.extend(pair_errors)
    has_warnings = pairing_warnings or any(report["warnings"] for report in results)
    result = {"status": "ERROR" if errors else "WARN" if has_warnings else "STRUCTURE_OK",
              "scope": "Deterministic structure/count checks only; content, translation, slide match and rehearsal not verified.",
              "errors": errors, "pairing_warnings": pairing_warnings, "scripts": results}
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
