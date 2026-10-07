#!/usr/bin/env python3
"""Search, route, inspect, and validate the my-report-taste library."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any


SKILL_ROOT = Path(__file__).resolve().parents[1]
REFERENCES_DIR = SKILL_ROOT / "references"
ASSETS_DIR = SKILL_ROOT / "assets"
CATALOG_PATH = REFERENCES_DIR / "catalog.json"
ROUTES_PATH = REFERENCES_DIR / "routes.json"

ID_RE = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
ROUTE_ID_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
GATE_RE = re.compile(r"`gate:([a-z0-9][a-z0-9.-]+)`")
TEX_MACRO_RE = re.compile(r"\\(?:text|mathrm|times)\b")
MATH_SPAN_RE = re.compile(r"\\\(.*?\\\)|\\\[.*?\\\]", re.DOTALL)
FENCED_CODE_RE = re.compile(r"```.*?```", re.DOTALL)
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
DASH_RE = re.compile(r"[‐‑‒–—―−〜～]")
ARROW_RE = re.compile(r"[→⇒⇢➜⟶⟹]+")

ALLOWED_KINDS = {
    "editable-template",
    "external-artifact",
    "generated-output",
    "image-reference",
    "owned-artifact",
    "video-reference",
    "web-reference",
}
ALLOWED_CATEGORIES = {
    "agenda",
    "appendix",
    "color",
    "comparison",
    "cover",
    "data",
    "grid",
    "key-message",
    "method",
    "narrative",
    "other",
    "pagination",
    "process",
    "result",
    "section-divider",
    "summary",
    "timeline",
    "typography",
}
ALLOWED_FORMATS = {
    "html-deck",
    "image",
    "keynote",
    "md",
    "mixed",
    "pdf",
    "ppt",
    "pptx",
    "video",
}
ALLOWED_STATUSES = {"approved", "candidate", "deprecated", "rejected", "validated"}
ALLOWED_PREFERENCES = {"confirmed", "hypothesis", "negative"}
ALLOWED_REUSE_MODES = {
    "adapt-generated-output",
    "recreate-principles-only",
    "reuse-owned-asset",
    "use-template-with-license",
    "visual-reference-only",
}
REQUIRED_ENTRY_KEYS = {
    "asset_paths",
    "category",
    "collected_at",
    "formats",
    "id",
    "kind",
    "license",
    "pattern_file",
    "preference",
    "reuse_mode",
    "source_locator",
    "source_url",
    "status",
    "tags",
    "title",
    "use_cases",
}
REQUIRED_PATTERN_HEADINGS = {
    "## 元数据",
    "## 用户明确偏好",
    "## 来源与定位",
    "## 已验证事实",
    "## 设计推断",
    "## 内容与叙事规则",
    "## 视觉与版式配方",
    "## 媒介适配",
    "## 反模式与边界",
    "## 验收标准",
}
ROUTE_CARD_FIELDS = ("main", "auxiliary", "palette")
ROUTE_FILE_FIELDS = ("contracts", "references")
SEARCH_FIELD_WEIGHTS = {
    "id": 5.0,
    "title": 3.5,
    "tags": 3.0,
    "use_cases": 3.0,
    "source_locator": 1.5,
    "body": 1.0,
}
STATUS_BONUS = {"validated": 1.5, "approved": 1.0, "candidate": 0.2}


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        raise SystemExit(f"{label} not found: {path}")
    except json.JSONDecodeError as exc:
        raise SystemExit(f"Invalid JSON in {path}: {exc}")
    if not isinstance(data, dict):
        raise SystemExit(f"{label} root must be a JSON object")
    return data


def load_catalog() -> dict[str, Any]:
    return load_json(CATALOG_PATH, "Catalog")


def load_routes() -> dict[str, Any]:
    return load_json(ROUTES_PATH, "Routes")


def safe_relative_path(value: str) -> Path | None:
    path = Path(value)
    if not value or path.is_absolute() or ".." in path.parts:
        return None
    root = SKILL_ROOT.resolve()
    resolved = (SKILL_ROOT / path).resolve()
    try:
        resolved.relative_to(root)
    except ValueError:
        return None
    return resolved


def normalize_standard(value: str) -> str:
    """Normalize width, case, dash variants, arrows, and repeated whitespace."""
    text = unicodedata.normalize("NFKC", value).casefold()
    text = DASH_RE.sub("-", text)
    text = ARROW_RE.sub(" ", text)
    return re.sub(r"\s+", " ", text).strip()


def normalize_compact(value: str) -> str:
    """Compact view for Chinese phrases; the standard view keeps word boundaries."""
    return re.sub(r"[^\w]+", "", normalize_standard(value), flags=re.UNICODE)


def cjk_bigrams(value: str) -> set[str]:
    grams: set[str] = set()
    for chars in re.findall(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]+", normalize_standard(value)):
        grams.update(chars[index : index + 2] for index in range(max(0, len(chars) - 1)))
    return grams


def entry_fields(entry: dict[str, Any]) -> dict[str, str]:
    body = ""
    pattern_file = entry.get("pattern_file")
    if isinstance(pattern_file, str):
        path = safe_relative_path(pattern_file)
        if path is not None and path.is_file():
            body = path.read_text(encoding="utf-8")
    return {
        "id": str(entry.get("id", "")),
        "title": str(entry.get("title", "")),
        "tags": "\n".join(str(item) for item in entry.get("tags", [])),
        "use_cases": "\n".join(str(item) for item in entry.get("use_cases", [])),
        "source_locator": str(entry.get("source_locator", "")),
        "body": body,
    }


def term_match(term: str, field_value: str) -> tuple[float, str] | None:
    standard_term = normalize_standard(term)
    compact_term = normalize_compact(term)
    standard_field = normalize_standard(field_value)
    compact_field = normalize_compact(field_value)
    if not standard_term:
        return None
    if standard_term in standard_field:
        return 10.0 + min(len(standard_term), 30) / 30, "phrase"
    if len(compact_term) >= 2 and compact_term in compact_field:
        return 8.0 + min(len(compact_term), 30) / 30, "compact"
    query_grams = cjk_bigrams(term)
    if len(query_grams) >= 2:
        field_grams = cjk_bigrams(field_value)
        overlap = len(query_grams & field_grams)
        coverage = overlap / len(query_grams)
        if overlap >= 2 and coverage >= 0.30:
            return 6.0 * coverage, f"cjk-{coverage:.0%}"
    return None


def score_entry(entry: dict[str, Any], terms: list[str]) -> tuple[float, list[str]] | None:
    if not terms:
        return 0.0, []
    fields = entry_fields(entry)
    total = STATUS_BONUS.get(str(entry.get("status")), 0.0)
    reasons: list[str] = []
    for term in terms:
        candidates: list[tuple[float, str, str]] = []
        for name, value in fields.items():
            match = term_match(term, value)
            if match is None:
                continue
            raw_score, mode = match
            candidates.append((raw_score * SEARCH_FIELD_WEIGHTS[name], name, mode))
        if not candidates:
            return None
        score, field, mode = max(candidates, key=lambda row: row[0])
        total += score
        reasons.append(f"{term}:{field}/{mode}")
    return total, reasons


def catalog_entries() -> list[dict[str, Any]]:
    entries = load_catalog().get("entries", [])
    if not isinstance(entries, list):
        raise SystemExit("Catalog 'entries' must be a list")
    return [entry for entry in entries if isinstance(entry, dict)]


def passes_metadata_filters(entry: dict[str, Any], args: argparse.Namespace) -> bool:
    if args.kind and entry.get("kind") != args.kind:
        return False
    if args.category and entry.get("category") != args.category:
        return False
    if args.status and entry.get("status") != args.status:
        return False
    if args.preference and entry.get("preference") != args.preference:
        return False
    if args.format and args.format not in entry.get("formats", []):
        return False
    if args.tag:
        expected = normalize_standard(args.tag)
        if expected not in {normalize_standard(str(tag)) for tag in entry.get("tags", [])}:
            return False
    return True


def filter_entries(
    args: argparse.Namespace,
    *,
    rank: bool,
) -> list[tuple[dict[str, Any], float, list[str]]]:
    terms = [term for term in getattr(args, "query", []) if term.strip()]
    results: list[tuple[dict[str, Any], float, list[str]]] = []
    for entry in catalog_entries():
        if not passes_metadata_filters(entry, args):
            continue
        if (
            rank
            and not args.status
            and not getattr(args, "include_rejected", False)
            and entry.get("status") in {"rejected", "deprecated"}
        ):
            continue
        scored = score_entry(entry, terms)
        if scored is None:
            continue
        score, reasons = scored
        results.append((entry, score, reasons))
    if rank:
        results.sort(key=lambda row: (-row[1], str(row[0].get("id", ""))))
        configured_ratio = getattr(args, "min_score_ratio", None)
        if configured_ratio is None:
            score_ratio = 0.0 if getattr(args, "include_rejected", False) else 0.60
        else:
            score_ratio = float(configured_ratio)
        if results and score_ratio > 0:
            minimum_score = results[0][1] * score_ratio
            results = [row for row in results if row[1] >= minimum_score]
    return results[: args.limit]


def print_entries(
    rows: list[tuple[dict[str, Any], float, list[str]]],
    as_json: bool,
    explain: bool,
) -> None:
    if as_json:
        output = []
        for entry, score, reasons in rows:
            item = dict(entry)
            if explain:
                item["_score"] = round(score, 3)
                item["_matched"] = reasons
            output.append(item)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return
    if not rows:
        print("No matching entries")
        return
    for entry, score, reasons in rows:
        formats = ",".join(entry.get("formats", []))
        tags = ", ".join(entry.get("tags", []))
        suffix = ""
        if explain:
            suffix = f" | score={score:.2f} | match={'; '.join(reasons)}"
        print(
            f"{entry.get('id')} | {entry.get('status')} | {entry.get('preference')} | "
            f"{entry.get('category')} | {formats} | {entry.get('title')} | {tags}{suffix}"
        )


def print_counts(field: str, allowed: set[str], as_json: bool) -> None:
    counts = {value: 0 for value in sorted(allowed)}
    for entry in catalog_entries():
        values = entry.get(field, []) if field == "formats" else [entry.get(field)]
        for value in values if isinstance(values, list) else []:
            if value in counts:
                counts[value] += 1
    rows = [{field.rstrip("s"): key, "count": value} for key, value in counts.items()]
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for row in rows:
        print(f"{row[field.rstrip('s')]} | {row['count']}")


def print_vocab(field: str, contains: str | None, min_count: int, as_json: bool) -> None:
    if field == "use-cases":
        field = "use_cases"
    selected = ("tags", "use_cases") if field == "all" else (field,)
    rows: list[dict[str, Any]] = []
    needle = normalize_standard(contains or "")
    for key in selected:
        counter: Counter[str] = Counter()
        for entry in catalog_entries():
            values = entry.get(key, [])
            if isinstance(values, list):
                counter.update(str(value) for value in values)
        for value, count in sorted(counter.items(), key=lambda item: (-item[1], item[0])):
            if count < min_count or (needle and needle not in normalize_standard(value)):
                continue
            rows.append({"field": key, "value": value, "count": count})
    if as_json:
        print(json.dumps(rows, ensure_ascii=False, indent=2))
        return
    for row in rows:
        print(f"{row['field']} | {row['count']} | {row['value']}")


def route_fields(route: dict[str, Any]) -> dict[str, list[str]]:
    return {
        "id": [str(route.get("id", ""))],
        "title": [str(route.get("title", ""))],
        "triggers": [str(item) for item in route.get("triggers", [])],
        "use_cases": [str(item) for item in route.get("use_cases", [])],
        "description": [str(route.get("description", ""))],
    }


def request_mentions(value: str, request: str) -> bool:
    """Match a named phrase in a request, excluding nearby explicit negation.

    This is a bounded keyword helper, not a general intent or preference parser.
    """
    value = normalize_standard(value)
    request = normalize_standard(request)
    if not value:
        return False
    pattern = re.escape(value).replace(r"\ ", r"\s*")
    if value[0].isascii() and value[0].isalnum():
        pattern = r"(?<![a-z0-9])" + pattern
    if value[-1].isascii() and value[-1].isalnum():
        pattern += r"(?![a-z0-9])"
    for match in re.finditer(pattern, request):
        prefix = request[max(0, match.start() - 32) : match.start()]
        clause = re.split(r"[,，。;；.!?！？]|但是|不过|而是|改用|\bbut\b|\binstead\b", prefix)[-1]
        if re.search(r"不要|不用|不采用|不使用|别用|无需|\b(?:not|no|without|avoid)\b", clause):
            continue
        return True
    return False


def score_route(route: dict[str, Any], terms: list[str]) -> tuple[float, list[str]] | None:
    if not terms:
        return 0.0, []
    request = " ".join(terms)
    # A request may include delivery constraints alongside its actual scenario.
    # Match known phrases inside that request rather than requiring every word
    # to occur together in one catalog field.
    selectors = [str(route.get("id", "")), *route.get("triggers", [])]
    if route.get("requires_explicit", False):
        selectors.extend(card for key in ROUTE_CARD_FIELDS for card in route.get(key, []))
    hits = [value for value in selectors if request_mentions(value, request)]
    if hits:
        strongest = max(hits, key=len)
        score = 50.0 + min(len(normalize_standard(strongest)), 30)
        if route.get("requires_explicit", False):
            score += 100.0
        return score, [f"{strongest}:request/explicit-phrase"]
    if route.get("requires_explicit", False):
        return None
    weights = {"id": 5.0, "title": 4.0, "triggers": 4.0, "use_cases": 3.0, "description": 1.0}
    fields = route_fields(route)
    total = 0.0
    reasons: list[str] = []
    for term in terms:
        matches = []
        for name, values in fields.items():
            for value in values:
                match = term_match(term, value)
                if not match or not request_mentions(term, value):
                    continue
                raw_score, mode = match
                if normalize_standard(term) == normalize_standard(value):
                    raw_score += 2.0
                    mode = "exact"
                matches.append((raw_score * weights[name], name, mode))
        if not matches:
            return None
        score, field, mode = max(matches, key=lambda row: row[0])
        total += score
        reasons.append(f"{term}:{field}/{mode}")
    return total, reasons


def route_rows(
    terms: list[str], limit: int, *, supplied_template: bool = False
) -> list[tuple[dict[str, Any], float, list[str]]]:
    routes = load_routes().get("routes", [])
    if not isinstance(routes, list):
        raise SystemExit("Routes 'routes' must be a list")
    request = " ".join(terms)
    if request and any(request_mentions(value, request) for value in (
        "不要使用我的风格", "不用我的风格", "do not use my style", "without my style"
    )):
        return []
    supplied_template = supplied_template or any(
        request_mentions(value, request) for value in (
            "官方模板", "会议模板", "已有模板", "现有模板", "提供的模板", "用户母版",
            "official template", "conference template", "provided template", "existing template",
        )
    )
    rows = []
    for route in routes:
        if not isinstance(route, dict):
            continue
        scored = score_route(route, terms)
        if scored is not None:
            selected = dict(route)
            if supplied_template:
                selected["_visual_policy"] = "preserve-provided-template"
                selected["_configured_palette"] = list(route.get("palette", []))
                selected["palette"] = []
                palette_prefixes = tuple(card.casefold() + "." for card in route.get("palette", []))
                selected["gate_refs"] = [
                    gate for gate in route.get("gate_refs", [])
                    if not gate.startswith(palette_prefixes)
                ]
            rows.append((selected, scored[0], scored[1]))
    rows.sort(
        key=lambda row: (
            -row[1],
            -int(row[0].get("priority", 0)),
            str(row[0].get("id", "")),
        )
    )
    return rows[:limit]


def print_routes(rows: list[tuple[dict[str, Any], float, list[str]]], as_json: bool) -> None:
    if as_json:
        output = []
        for route, score, reasons in rows:
            item = dict(route)
            item["_score"] = round(score, 3)
            item["_matched"] = reasons
            output.append(item)
        print(json.dumps(output, ensure_ascii=False, indent=2))
        return
    if not rows:
        print("No matching routes")
        return
    for route, score, reasons in rows:
        print(
            f"{route.get('id')} | {route.get('title')} | "
            f"main={','.join(route.get('main', [])) or '-'} | "
            f"aux={','.join(route.get('auxiliary', [])) or '-'} | "
            f"palette={','.join(route.get('palette', [])) or '-'} | "
            f"score={score:.2f}"
        )
        if reasons:
            print(f"  match: {'; '.join(reasons)}")
        if route.get("type") == "workflow":
            print(f"  workflow: {', '.join(route.get('references', []))}; visual style: not selected")
        if route.get("_visual_policy"):
            print("  visual policy: preserve provided template; apply only compatible layout/semantic rules")
        if route.get("gate_refs"):
            print(f"  gates: {', '.join(route['gate_refs'])}")


def validate_string_list(entry: dict[str, Any], key: str, label: str, errors: list[str]) -> None:
    value = entry.get(key)
    if not isinstance(value, list) or not all(isinstance(item, str) for item in value):
        errors.append(f"{label}.{key} must be a list of strings")


def shared_asset_paths(data: dict[str, Any], errors: list[str]) -> set[str]:
    shared = data.get("shared_assets", [])
    if not isinstance(shared, list):
        errors.append("shared_assets must be a list")
        return set()
    paths: set[str] = set()
    for index, item in enumerate(shared):
        label = f"shared_assets[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{label} must be an object")
            continue
        path = item.get("path")
        purpose = item.get("purpose")
        if not isinstance(path, str):
            errors.append(f"{label}.path must be a string")
            continue
        if not isinstance(purpose, str) or not purpose.strip():
            errors.append(f"{label}.purpose must be a non-empty string")
        resolved = safe_relative_path(path)
        if resolved is None or not resolved.is_file():
            errors.append(f"{label}.path is missing or unsafe: {path!r}")
        paths.add(path)
    return paths


def collect_gate_ids(pattern_by_id: dict[str, Path], errors: list[str]) -> dict[str, str]:
    owners: dict[str, str] = {}
    for entry_id, path in pattern_by_id.items():
        text = path.read_text(encoding="utf-8")
        for gate_id in GATE_RE.findall(text):
            if not gate_id.startswith(entry_id.casefold() + "."):
                errors.append(f"gate {gate_id!r} in {entry_id} must start with {entry_id.casefold()}.")
            if gate_id in owners:
                errors.append(f"duplicate gate id {gate_id!r} in {owners[gate_id]} and {entry_id}")
            owners[gate_id] = entry_id
    return owners


def validate_routes(
    entry_status: dict[str, str],
    gate_owners: dict[str, str],
    errors: list[str],
) -> None:
    try:
        data = load_routes()
    except SystemExit as exc:
        errors.append(str(exc))
        return
    if data.get("schema_version") != 1:
        errors.append("routes.schema_version must be 1")
    updated_at = data.get("updated_at")
    if not isinstance(updated_at, str) or not DATE_RE.fullmatch(updated_at):
        errors.append("routes.updated_at must use YYYY-MM-DD")
    routes = data.get("routes")
    if not isinstance(routes, list):
        errors.append("routes.routes must be a list")
        return
    seen_routes: set[str] = set()
    for index, route in enumerate(routes):
        label = f"routes[{index}]"
        if not isinstance(route, dict):
            errors.append(f"{label} must be an object")
            continue
        route_id = route.get("id")
        if not isinstance(route_id, str) or not ROUTE_ID_RE.fullmatch(route_id):
            errors.append(f"{label}.id has invalid format: {route_id!r}")
        elif route_id in seen_routes:
            errors.append(f"duplicate route id: {route_id}")
        else:
            seen_routes.add(route_id)
        for key in ("title", "description"):
            if not isinstance(route.get(key), str) or not route[key].strip():
                errors.append(f"{label}.{key} must be a non-empty string")
        priority = route.get("priority")
        if not isinstance(priority, int) or isinstance(priority, bool):
            errors.append(f"{label}.priority must be an integer")
        for key in ("triggers", "use_cases", *ROUTE_CARD_FIELDS, *ROUTE_FILE_FIELDS, "gate_refs"):
            validate_string_list(route, key, label, errors)
        route_type = route.get("type", "visual")
        if route_type not in {"visual", "workflow"}:
            errors.append(f"{label}.type must be visual or workflow")
        if "requires_explicit" in route and not isinstance(route["requires_explicit"], bool):
            errors.append(f"{label}.requires_explicit must be boolean")
        if route_type == "workflow":
            if any(route.get(key) for key in (*ROUTE_CARD_FIELDS, "gate_refs")):
                errors.append(f"{label}: workflow routes must not select visual cards or gates")
            if not route.get("references"):
                errors.append(f"{label}: workflow routes require a workflow reference")
        elif isinstance(route.get("main"), list) and len(route["main"]) != 1:
            errors.append(f"{label}.main must contain exactly one card")
        if isinstance(route.get("auxiliary"), list) and len(route["auxiliary"]) > 2:
            errors.append(f"{label}.auxiliary may contain at most two cards")
        if isinstance(route.get("palette"), list) and len(route["palette"]) > 1:
            errors.append(f"{label}.palette may contain at most one card")
        referenced_cards: list[str] = []
        for key in ROUTE_CARD_FIELDS:
            value = route.get(key, [])
            if isinstance(value, list):
                referenced_cards.extend(str(item) for item in value)
        for card_id in referenced_cards:
            if card_id not in entry_status:
                errors.append(f"{label} references unknown card id: {card_id}")
            elif entry_status[card_id] in {"rejected", "deprecated"}:
                errors.append(f"{label} references non-positive card {card_id}: {entry_status[card_id]}")
        if len(referenced_cards) != len(set(referenced_cards)):
            errors.append(f"{label} repeats a card across main/auxiliary/palette")
        for key in ROUTE_FILE_FIELDS:
            value = route.get(key, [])
            for item in value if isinstance(value, list) else []:
                resolved = safe_relative_path(item)
                if resolved is None or not resolved.is_file():
                    errors.append(f"{label}.{key} is missing or unsafe: {item!r}")
        value = route.get("gate_refs", [])
        for gate_ref in value if isinstance(value, list) else []:
            if gate_ref not in gate_owners:
                errors.append(f"{label}.gate_refs references unknown gate: {gate_ref}")
            elif gate_owners[gate_ref] not in referenced_cards:
                errors.append(
                    f"{label}.gate_refs uses {gate_ref} from unselected card {gate_owners[gate_ref]}"
                )


def lint_reference_tex(errors: list[str]) -> None:
    for path in sorted(REFERENCES_DIR.glob("*.md")):
        text = FENCED_CODE_RE.sub("", path.read_text(encoding="utf-8"))
        outside_math = MATH_SPAN_RE.sub("", text)
        for match in TEX_MACRO_RE.finditer(outside_math):
            line = outside_math.count("\n", 0, match.start()) + 1
            errors.append(f"{path.relative_to(SKILL_ROOT)}:{line} has TeX macro outside math delimiters")


def validate_catalog(strict_warnings: bool = False) -> int:
    data = load_catalog()
    errors: list[str] = []
    warnings: list[str] = []
    if data.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    updated_at = data.get("updated_at")
    if not isinstance(updated_at, str) or not DATE_RE.fullmatch(updated_at):
        errors.append("updated_at must use YYYY-MM-DD")
    entries = data.get("entries")
    if not isinstance(entries, list):
        errors.append("entries must be a list")
        entries = []

    seen_ids: set[str] = set()
    entry_status: dict[str, str] = {}
    pattern_by_id: dict[str, Path] = {}
    tracked_assets = shared_asset_paths(data, errors)
    collected_dates: list[str] = []
    vocab: dict[str, list[str]] = {"tags": [], "use_cases": []}

    for index, entry in enumerate(entries):
        label = f"entries[{index}]"
        if not isinstance(entry, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED_ENTRY_KEYS - entry.keys()
        if missing:
            errors.append(f"{label} missing keys: {', '.join(sorted(missing))}")

        entry_id = entry.get("id")
        if not isinstance(entry_id, str) or not ID_RE.fullmatch(entry_id):
            errors.append(f"{label}.id has invalid format: {entry_id!r}")
        elif entry_id in seen_ids:
            errors.append(f"duplicate id: {entry_id}")
        else:
            seen_ids.add(entry_id)
            entry_status[entry_id] = str(entry.get("status", ""))

        if entry.get("kind") not in ALLOWED_KINDS:
            errors.append(f"{label}.kind is invalid: {entry.get('kind')!r}")
        if entry.get("category") not in ALLOWED_CATEGORIES:
            errors.append(f"{label}.category is invalid: {entry.get('category')!r}")
        if entry.get("status") not in ALLOWED_STATUSES:
            errors.append(f"{label}.status is invalid: {entry.get('status')!r}")
        if entry.get("preference") not in ALLOWED_PREFERENCES:
            errors.append(f"{label}.preference is invalid: {entry.get('preference')!r}")
        if entry.get("reuse_mode") not in ALLOWED_REUSE_MODES:
            errors.append(f"{label}.reuse_mode is invalid: {entry.get('reuse_mode')!r}")
        collected_at = entry.get("collected_at")
        if not isinstance(collected_at, str) or not DATE_RE.fullmatch(collected_at):
            errors.append(f"{label}.collected_at must use YYYY-MM-DD")
        else:
            collected_dates.append(collected_at)
        for key in ("formats", "use_cases", "tags", "asset_paths"):
            validate_string_list(entry, key, label, errors)
        for key in ("tags", "use_cases"):
            value = entry.get(key, [])
            if isinstance(value, list):
                vocab[key].extend(str(item) for item in value)
        formats = entry.get("formats", [])
        if isinstance(formats, list):
            invalid_formats = sorted(set(formats) - ALLOWED_FORMATS)
            if invalid_formats:
                errors.append(f"{label}.formats has invalid values: {', '.join(invalid_formats)}")
        for key in ("source_url", "source_locator", "title"):
            if not isinstance(entry.get(key), str):
                errors.append(f"{label}.{key} must be a string")

        pattern_file = entry.get("pattern_file")
        pattern_path = safe_relative_path(pattern_file) if isinstance(pattern_file, str) else None
        if pattern_path is None or not pattern_path.is_file():
            errors.append(f"{label}.pattern_file is missing or unsafe: {pattern_file!r}")
        else:
            if isinstance(entry_id, str):
                pattern_by_id[entry_id] = pattern_path
            pattern_text = pattern_path.read_text(encoding="utf-8")
            missing_headings = sorted(
                heading for heading in REQUIRED_PATTERN_HEADINGS if heading not in pattern_text
            )
            if missing_headings:
                errors.append(f"{label}.pattern_file missing headings: {', '.join(missing_headings)}")
            category_marker = f"- 分类：`{entry.get('category')}`"
            if category_marker not in pattern_text:
                errors.append(f"{label}.pattern_file missing category marker: {category_marker}")

        asset_paths = entry.get("asset_paths", [])
        if isinstance(asset_paths, list):
            for asset_path in asset_paths:
                resolved = safe_relative_path(asset_path) if isinstance(asset_path, str) else None
                if resolved is None or not resolved.is_file():
                    errors.append(f"{label}.asset_paths is missing or unsafe: {asset_path!r}")
                if isinstance(asset_path, str):
                    tracked_assets.add(asset_path)

        license_data = entry.get("license")
        if not isinstance(license_data, dict):
            errors.append(f"{label}.license must be an object")
        else:
            for key in ("name", "source", "policy"):
                if key not in license_data or not isinstance(license_data[key], str):
                    errors.append(f"{label}.license.{key} must be a string")

    if isinstance(updated_at, str) and collected_dates and updated_at < max(collected_dates):
        errors.append(f"updated_at {updated_at} is older than latest collected_at {max(collected_dates)}")

    all_assets = {
        path.relative_to(SKILL_ROOT).as_posix()
        for path in ASSETS_DIR.rglob("*")
        if path.is_file() and not any(part.startswith(".") for part in path.relative_to(ASSETS_DIR).parts)
    }
    for orphan in sorted(all_assets - tracked_assets):
        errors.append(f"orphan asset is not cataloged: {orphan}")
    for missing_asset in sorted(tracked_assets - all_assets):
        errors.append(f"cataloged asset does not exist: {missing_asset}")

    for key, values in vocab.items():
        normalized: dict[str, set[str]] = {}
        for value in values:
            normalized.setdefault(normalize_standard(value), set()).add(value)
        for variants in normalized.values():
            if len(variants) > 1:
                warnings.append(f"{key} has normalized variants: {', '.join(sorted(variants))}")

    gate_owners = collect_gate_ids(pattern_by_id, errors)
    validate_routes(entry_status, gate_owners, errors)
    lint_reference_tex(errors)

    for warning in warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    if strict_warnings and warnings:
        print(
            f"ERROR: strict validation rejects {len(warnings)} warning(s)",
            file=sys.stderr,
        )
        return 1
    route_count = len(load_routes().get("routes", []))
    print(
        f"OK: {len(entries)} entries, {route_count} routes, {len(gate_owners)} gates, "
        f"and {len(all_assets)} assets are valid; warnings={len(warnings)}"
    )
    return 0


def next_id(prefix: str) -> str:
    normalized = prefix.strip().upper()
    if not re.fullmatch(r"[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*", normalized):
        raise SystemExit("Prefix must use uppercase letters, digits, and hyphens")
    highest = 0
    for entry in catalog_entries():
        match = re.fullmatch(rf"{re.escape(normalized)}-(\d{{3}})", str(entry.get("id", "")))
        if match:
            highest = max(highest, int(match.group(1)))
    if highest >= 999:
        raise SystemExit(f"ID range exhausted for prefix {normalized}")
    return f"{normalized}-{highest + 1:03d}"


def add_filters(parser: argparse.ArgumentParser, include_query: bool) -> None:
    if include_query:
        parser.add_argument("query", nargs="+", help="Natural-language terms; every term must match")
    else:
        parser.set_defaults(query=[])
    parser.add_argument("--kind", choices=sorted(ALLOWED_KINDS))
    parser.add_argument("--category", choices=sorted(ALLOWED_CATEGORIES))
    parser.add_argument("--status", choices=sorted(ALLOWED_STATUSES))
    parser.add_argument("--preference", choices=sorted(ALLOWED_PREFERENCES))
    parser.add_argument("--format", choices=sorted(ALLOWED_FORMATS))
    parser.add_argument("--tag")
    parser.add_argument("--limit", type=int, default=20)
    parser.add_argument("--json", action="store_true", dest="as_json")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    search_parser = subparsers.add_parser("search", help="Rank metadata and pattern-card matches")
    add_filters(search_parser, include_query=True)
    search_parser.add_argument(
        "--include-rejected",
        action="store_true",
        help="Include rejected and deprecated cards; excluded by default",
    )
    search_parser.add_argument(
        "--min-score-ratio",
        type=float,
        default=None,
        metavar="RATIO",
        help=(
            "Keep results scoring at least this fraction of the top score; 0 disables "
            "(default: 0.60, or 0 with --include-rejected)"
        ),
    )

    list_parser = subparsers.add_parser("list", help="List catalog entries without search ranking")
    add_filters(list_parser, include_query=False)

    categories_parser = subparsers.add_parser("categories", help="List category counts")
    categories_parser.add_argument("--json", action="store_true", dest="as_json")

    formats_parser = subparsers.add_parser("formats", help="List format counts")
    formats_parser.add_argument("--json", action="store_true", dest="as_json")

    vocab_parser = subparsers.add_parser("vocab", help="List searchable tags and use-case vocabulary")
    vocab_parser.add_argument(
        "--field",
        choices=("all", "tags", "use_cases", "use-cases"),
        default="all",
    )
    vocab_parser.add_argument("--contains")
    vocab_parser.add_argument("--min-count", type=int, default=1)
    vocab_parser.add_argument("--json", action="store_true", dest="as_json")

    route_parser = subparsers.add_parser("route", help="Resolve a personal reporting scenario")
    route_parser.add_argument("query", nargs="*", help="Scenario words; omit to list every route")
    route_parser.add_argument("--limit", type=int, default=5)
    route_parser.add_argument("--json", action="store_true", dest="as_json")
    route_parser.add_argument(
        "--template", action="store_true",
        help="Preserve a supplied template and suppress preset palette selection",
    )

    next_parser = subparsers.add_parser("next-id", help="Return the next ID for a prefix")
    next_parser.add_argument("prefix")

    validate_parser = subparsers.add_parser(
        "validate", help="Validate catalog, routes, gates, references, and assets"
    )
    validate_parser.add_argument(
        "--strict",
        action="store_true",
        help="Treat validation warnings as failures",
    )
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "validate":
        return validate_catalog(args.strict)
    if args.command == "next-id":
        print(next_id(args.prefix))
        return 0
    if args.command == "categories":
        print_counts("category", ALLOWED_CATEGORIES, args.as_json)
        return 0
    if args.command == "formats":
        print_counts("formats", ALLOWED_FORMATS, args.as_json)
        return 0
    if args.command == "vocab":
        print_vocab(args.field, args.contains, args.min_count, args.as_json)
        return 0
    if args.command == "route":
        print_routes(route_rows(args.query, args.limit, supplied_template=args.template), args.as_json)
        return 0
    if args.command == "search":
        if args.min_score_ratio is not None and not 0 <= args.min_score_ratio <= 1:
            raise SystemExit("--min-score-ratio must be between 0 and 1")
        print_entries(filter_entries(args, rank=True), args.as_json, explain=True)
        return 0
    print_entries(filter_entries(args, rank=False), args.as_json, explain=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
