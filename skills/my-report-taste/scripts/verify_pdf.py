#!/usr/bin/env python3
"""Verify a PDF exported from PPTX: pages, embedded fonts, Unicode, and CJK text."""

from __future__ import annotations

import argparse
import json
import os
import posixpath
import re
import shutil
import subprocess
import sys
import unicodedata
import zipfile
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET


NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
}
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
CJK_RE = re.compile(r"[\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff]")
FONT_LINE_RE = re.compile(
    r"^(?P<name>\S+)\s+(?P<type>.+?)\s+(?P<encoding>\S+)\s+"
    r"(?P<emb>yes|no)\s+(?P<sub>yes|no)\s+(?P<uni>yes|no)\s+"
    r"(?P<object>\d+)\s+(?P<generation>\d+)\s*$",
    re.IGNORECASE,
)
SUBSET_PREFIX_RE = re.compile(r"^[A-Z]{6}\+")
REL_TYPE_SUFFIXES = {"slideLayout", "slideMaster", "theme", "fontTable"}


@dataclass
class FontRecord:
    name: str
    base_name: str
    font_type: str
    encoding: str
    embedded: bool
    subset: bool
    unicode: bool


@dataclass
class PptxEvidence:
    total_slides: int
    visible_slides: int
    hidden_slide_numbers: list[int]
    visible_text_by_slide: list[str]
    explicit_used_fonts: list[str]
    inherited_font_candidates: list[str]
    declared_font_candidates: list[str]
    unresolved_theme_fonts: list[str]


@dataclass
class VerificationReport:
    pdf: str
    source_pptx: str | None = None
    pdf_pages: int | None = None
    expected_visible_slides: int | None = None
    hidden_slide_numbers: list[int] = field(default_factory=list)
    expected_fonts: list[str] = field(default_factory=list)
    inherited_font_candidates: list[str] = field(default_factory=list)
    declared_font_candidates: list[str] = field(default_factory=list)
    unresolved_theme_fonts: list[str] = field(default_factory=list)
    pdf_fonts: list[FontRecord] = field(default_factory=list)
    cjk_source_characters: int = 0
    cjk_extracted_characters: int = 0
    cjk_coverage: float | None = None
    low_coverage_pages: list[dict[str, Any]] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


def find_tool(name: str) -> Path:
    configured = os.environ.get(name.upper())
    if configured:
        path = Path(configured).expanduser().resolve()
        if path.is_file():
            return path
        raise SystemExit(f"{name.upper()} points to a missing executable: {path}")
    discovered = shutil.which(name)
    if discovered:
        return Path(discovered).resolve()
    runtime_candidates = (
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override" / name,
        Path.home() / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback" / name,
    )
    for candidate in runtime_candidates:
        if candidate.is_file():
            return candidate.resolve()
    raise SystemExit(f"Required command not found: {name}; set {name.upper()} or add it to PATH")


def run_tool(command: list[str]) -> str:
    proc = subprocess.run(command, text=True, capture_output=True, errors="replace", check=False)
    if proc.returncode != 0:
        detail = (proc.stderr or proc.stdout or "unknown command failure").strip()
        raise RuntimeError(f"{Path(command[0]).name} failed: {detail}")
    return proc.stdout


def rels_part_name(part_name: str) -> str:
    directory = posixpath.dirname(part_name)
    filename = posixpath.basename(part_name)
    return posixpath.join(directory, "_rels", f"{filename}.rels")


def relationship_map(archive: zipfile.ZipFile, part_name: str) -> dict[str, tuple[str, str]]:
    rels_name = rels_part_name(part_name)
    if rels_name not in archive.namelist():
        return {}
    root = ET.fromstring(archive.read(rels_name))
    output: dict[str, tuple[str, str]] = {}
    for relationship in root.findall(f"{{{REL_NS}}}Relationship"):
        if relationship.get("TargetMode") == "External":
            continue
        rel_id = relationship.get("Id")
        target = relationship.get("Target")
        rel_type = relationship.get("Type", "")
        if not rel_id or not target:
            continue
        if target.startswith("/"):
            resolved = target.lstrip("/")
        else:
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(part_name), target))
        output[rel_id] = (resolved, rel_type)
    return output


def related_part(
    archive: zipfile.ZipFile,
    part_name: str,
    rel_type_suffix: str,
) -> str | None:
    for target, rel_type in relationship_map(archive, part_name).values():
        if rel_type.endswith("/" + rel_type_suffix):
            return target
    return None


def xml_root(archive: zipfile.ZipFile, part_name: str) -> ET.Element | None:
    if part_name not in archive.namelist():
        return None
    return ET.fromstring(archive.read(part_name))


def theme_font_map(root: ET.Element | None) -> tuple[dict[str, str], set[str]]:
    if root is None:
        return {}, set()
    mapping: dict[str, str] = {}
    declared: set[str] = set()
    font_scheme = root.find(".//a:fontScheme", NS)
    if font_scheme is None:
        return mapping, declared
    for group_name, prefix in (("majorFont", "+mj"), ("minorFont", "+mn")):
        group = font_scheme.find(f"a:{group_name}", NS)
        if group is None:
            continue
        script_fonts = {
            element.get("script", ""): element.get("typeface", "")
            for element in group.findall("a:font", NS)
            if element.get("typeface")
        }
        for node_name, suffix in (("latin", "lt"), ("ea", "ea"), ("cs", "cs")):
            node = group.find(f"a:{node_name}", NS)
            typeface = node.get("typeface", "") if node is not None else ""
            if not typeface and suffix == "ea":
                typeface = script_fonts.get("Hans") or script_fonts.get("Hant") or ""
            if typeface:
                mapping[f"{prefix}-{suffix}"] = typeface
                declared.add(typeface)
        declared.update(value for value in script_fonts.values() if value)
    return mapping, declared


def resolve_typeface(typeface: str, mapping: dict[str, str], unresolved: set[str]) -> str | None:
    value = typeface.strip()
    if not value:
        return None
    if value.startswith("+"):
        resolved = mapping.get(value.casefold())
        if not resolved:
            unresolved.add(value)
            return None
        return resolved
    return value


def text_scripts(text: str) -> set[str]:
    scripts: set[str] = set()
    if CJK_RE.search(text):
        scripts.add("ea")
    if re.search(r"[A-Za-z0-9]", text):
        scripts.add("latin")
    if re.search(r"[\u0590-\u08ff]", text):
        scripts.add("cs")
    return scripts


def fonts_from_properties(
    properties: ET.Element | None,
    text: str,
    theme_mapping: dict[str, str],
    unresolved: set[str],
) -> set[str]:
    if properties is None:
        return set()
    scripts = text_scripts(text)
    fonts: set[str] = set()
    for script in scripts:
        element = properties.find(f"a:{script}", NS)
        if element is None:
            continue
        typeface = element.get("typeface", "")
        resolved = resolve_typeface(typeface, theme_mapping, unresolved)
        if resolved:
            fonts.add(resolved)
    return fonts


def explicit_fonts_for_slide(
    root: ET.Element,
    theme_mapping: dict[str, str],
    unresolved: set[str],
) -> set[str]:
    fonts: set[str] = set()
    for paragraph in root.findall(".//a:p", NS):
        paragraph_text = "".join(node.text or "" for node in paragraph.findall(".//a:t", NS))
        default_properties = paragraph.find("a:pPr/a:defRPr", NS)
        fonts.update(fonts_from_properties(default_properties, paragraph_text, theme_mapping, unresolved))
        for run in paragraph.findall("a:r", NS):
            run_text = "".join(node.text or "" for node in run.findall("a:t", NS))
            fonts.update(fonts_from_properties(run.find("a:rPr", NS), run_text, theme_mapping, unresolved))
    return fonts


def candidate_fonts_from_part(
    root: ET.Element | None,
    theme_mapping: dict[str, str],
    unresolved: set[str],
) -> set[str]:
    if root is None:
        return set()
    fonts: set[str] = set()
    for element in root.findall(".//*[@typeface]"):
        typeface = element.get("typeface", "")
        resolved = resolve_typeface(typeface, theme_mapping, unresolved)
        if resolved:
            fonts.add(resolved)
    return fonts


def inspect_pptx(path: Path) -> PptxEvidence:
    try:
        archive = zipfile.ZipFile(path)
    except (FileNotFoundError, zipfile.BadZipFile) as exc:
        raise RuntimeError(f"cannot open PPTX {path}: {exc}") from exc
    with archive:
        presentation = xml_root(archive, "ppt/presentation.xml")
        if presentation is None:
            raise RuntimeError("PPTX is missing ppt/presentation.xml")
        presentation_rels = relationship_map(archive, "ppt/presentation.xml")
        slide_parts: list[str] = []
        for slide_id in presentation.findall(".//p:sldIdLst/p:sldId", NS):
            rel_id = slide_id.get(f"{{{NS['r']}}}id")
            if rel_id and rel_id in presentation_rels:
                slide_parts.append(presentation_rels[rel_id][0])

        hidden_numbers: list[int] = []
        visible_text: list[str] = []
        explicit_fonts: set[str] = set()
        inherited_fonts: set[str] = set()
        declared_fonts: set[str] = set()
        unresolved: set[str] = set()

        for slide_number, slide_part in enumerate(slide_parts, start=1):
            slide_root = xml_root(archive, slide_part)
            if slide_root is None:
                raise RuntimeError(f"PPTX references missing slide part: {slide_part}")
            if slide_root.get("show", "1").casefold() in {"0", "false", "off"}:
                hidden_numbers.append(slide_number)
                continue

            layout_part = related_part(archive, slide_part, "slideLayout")
            master_part = related_part(archive, layout_part, "slideMaster") if layout_part else None
            theme_part = related_part(archive, master_part, "theme") if master_part else None
            theme_root = xml_root(archive, theme_part) if theme_part else None
            mapping, theme_declared = theme_font_map(theme_root)
            declared_fonts.update(theme_declared)

            slide_text = "\n".join(node.text or "" for node in slide_root.findall(".//a:t", NS))
            visible_text.append(slide_text)
            explicit_fonts.update(explicit_fonts_for_slide(slide_root, mapping, unresolved))
            for related in (layout_part, master_part):
                if related:
                    inherited_fonts.update(
                        candidate_fonts_from_part(xml_root(archive, related), mapping, unresolved)
                    )

        font_table = "ppt/fontTable.xml"
        if font_table in archive.namelist():
            font_root = xml_root(archive, font_table)
            if font_root is not None:
                declared_fonts.update(
                    element.get("typeface", "")
                    for element in font_root.findall(".//*[@typeface]")
                    if element.get("typeface")
                )

        return PptxEvidence(
            total_slides=len(slide_parts),
            visible_slides=len(visible_text),
            hidden_slide_numbers=hidden_numbers,
            visible_text_by_slide=visible_text,
            explicit_used_fonts=sorted(explicit_fonts),
            inherited_font_candidates=sorted(inherited_fonts - explicit_fonts),
            declared_font_candidates=sorted(declared_fonts - explicit_fonts),
            unresolved_theme_fonts=sorted(unresolved),
        )


def parse_pdf_pages(output: str) -> int:
    match = re.search(r"^Pages:\s+(\d+)\s*$", output, re.MULTILINE)
    if not match:
        raise RuntimeError("pdfinfo output does not contain a Pages field")
    return int(match.group(1))


def base_font_name(name: str) -> str:
    return SUBSET_PREFIX_RE.sub("", name)


def parse_pdf_fonts(output: str) -> list[FontRecord]:
    records = []
    for line in output.splitlines():
        match = FONT_LINE_RE.match(line.strip())
        if not match:
            continue
        records.append(
            FontRecord(
                name=match.group("name"),
                base_name=base_font_name(match.group("name")),
                font_type=match.group("type").strip(),
                encoding=match.group("encoding"),
                embedded=match.group("emb").casefold() == "yes",
                subset=match.group("sub").casefold() == "yes",
                unicode=match.group("uni").casefold() == "yes",
            )
        )
    return records


def normalize_font_name(value: str) -> str:
    value = unicodedata.normalize("NFKC", base_font_name(value)).casefold()
    value = re.sub(r"(?:bolditalic|boldoblique|semibold|demibold|medium|regular|italic|oblique)$", "", value)
    return re.sub(r"[^\w]+", "", value, flags=re.UNICODE)


def parse_aliases(values: list[str]) -> dict[str, str]:
    aliases: dict[str, str] = {}
    for value in values:
        if "=" not in value:
            raise SystemExit(f"font alias must use EXPECTED=PDF_NAME: {value}")
        expected, actual = value.split("=", 1)
        aliases[normalize_font_name(expected)] = normalize_font_name(actual)
    return aliases


def font_matches(expected: str, actual: str, aliases: dict[str, str]) -> bool:
    expected_norm = normalize_font_name(expected)
    actual_norm = normalize_font_name(actual)
    expected_norm = aliases.get(expected_norm, expected_norm)
    if expected_norm == actual_norm:
        return True
    return len(expected_norm) >= 5 and (expected_norm in actual_norm or actual_norm in expected_norm)


def any_font_matches(expected: str, actual_fonts: list[FontRecord], aliases: dict[str, str]) -> bool:
    return any(font_matches(expected, record.base_name, aliases) for record in actual_fonts)


def cjk_characters(value: str) -> str:
    return "".join(char for char in unicodedata.normalize("NFKC", value) if CJK_RE.fullmatch(char))


def multiset_coverage(source: str, extracted: str) -> float:
    source_counter = Counter(source)
    if not source_counter:
        return 1.0
    extracted_counter = Counter(extracted)
    matched = sum(min(count, extracted_counter[char]) for char, count in source_counter.items())
    return matched / sum(source_counter.values())


def verify(args: argparse.Namespace) -> VerificationReport:
    pdf = args.pdf.expanduser().resolve()
    if not pdf.is_file() or pdf.suffix.casefold() != ".pdf":
        raise SystemExit(f"PDF does not exist: {pdf}")
    report = VerificationReport(pdf=str(pdf))
    aliases = parse_aliases(args.font_alias)

    pptx_evidence: PptxEvidence | None = None
    if args.source_pptx:
        source_pptx = args.source_pptx.expanduser().resolve()
        if not source_pptx.is_file() or source_pptx.suffix.casefold() != ".pptx":
            raise SystemExit(f"source PPTX does not exist: {source_pptx}")
        report.source_pptx = str(source_pptx)
        try:
            pptx_evidence = inspect_pptx(source_pptx)
        except RuntimeError as exc:
            report.errors.append(str(exc))
        if pptx_evidence:
            report.expected_visible_slides = pptx_evidence.visible_slides
            report.hidden_slide_numbers = pptx_evidence.hidden_slide_numbers
            report.inherited_font_candidates = pptx_evidence.inherited_font_candidates
            report.declared_font_candidates = pptx_evidence.declared_font_candidates
            report.unresolved_theme_fonts = pptx_evidence.unresolved_theme_fonts

    try:
        report.pdf_pages = parse_pdf_pages(run_tool([str(find_tool("pdfinfo")), str(pdf)]))
    except (RuntimeError, SystemExit) as exc:
        report.errors.append(str(exc))
    if (
        report.pdf_pages is not None
        and report.expected_visible_slides is not None
        and report.pdf_pages != report.expected_visible_slides
    ):
        report.errors.append(
            f"page count mismatch: PDF has {report.pdf_pages}, PPTX has "
            f"{report.expected_visible_slides} visible slides"
        )

    try:
        report.pdf_fonts = parse_pdf_fonts(
            run_tool([str(find_tool("pdffonts")), str(pdf)])
        )
    except (RuntimeError, SystemExit) as exc:
        report.errors.append(str(exc))
    if not report.pdf_fonts:
        report.warnings.append("pdffonts reported no fonts; the PDF may contain only outlines or images")

    allow_unembedded = args.allow_unembedded_font
    allow_no_unicode = args.allow_no_unicode_font
    for record in report.pdf_fonts:
        if not record.embedded and not any(
            font_matches(pattern, record.base_name, aliases) for pattern in allow_unembedded
        ):
            report.errors.append(f"font is not embedded: {record.name}")
        if not record.unicode and not any(
            font_matches(pattern, record.base_name, aliases) for pattern in allow_no_unicode
        ):
            report.warnings.append(f"font has no Unicode map: {record.name}")
        if any(font_matches(pattern, record.base_name, aliases) for pattern in args.deny_font):
            report.errors.append(f"denied or known-substitute font appears in PDF: {record.name}")

    expected_fonts = list(args.expect_font)
    if pptx_evidence and not args.no_auto_fonts:
        expected_fonts.extend(pptx_evidence.explicit_used_fonts)
    report.expected_fonts = sorted(dict.fromkeys(expected_fonts))
    for expected in report.expected_fonts:
        if not any_font_matches(expected, report.pdf_fonts, aliases):
            report.errors.append(f"expected font not found in PDF: {expected}")

    if pptx_evidence and report.expected_fonts:
        allowed = list(args.allow_font)
        unexpected = [
            record.base_name
            for record in report.pdf_fonts
            if not any(font_matches(expected, record.base_name, aliases) for expected in report.expected_fonts)
            and not any(font_matches(pattern, record.base_name, aliases) for pattern in allowed)
        ]
        if unexpected:
            report.warnings.append(
                "PDF contains fonts outside the explicit PPTX expectation set: "
                + ", ".join(sorted(set(unexpected)))
            )

    extracted_text = ""
    try:
        extracted_text = run_tool(
            [str(find_tool("pdftotext")), "-layout", "-enc", "UTF-8", str(pdf), "-"]
        )
    except (RuntimeError, SystemExit) as exc:
        report.errors.append(str(exc))

    if pptx_evidence:
        source_pages = [cjk_characters(text) for text in pptx_evidence.visible_text_by_slide]
        source_cjk = "".join(source_pages)
        extracted_pages = [cjk_characters(text) for text in extracted_text.split("\f")]
        extracted_cjk = "".join(extracted_pages)
        report.cjk_source_characters = len(source_cjk)
        report.cjk_extracted_characters = len(extracted_cjk)
        if source_cjk:
            report.cjk_coverage = multiset_coverage(source_cjk, extracted_cjk)
            if report.cjk_coverage < args.cjk_error_threshold:
                report.errors.append(
                    f"CJK extraction coverage is too low: {report.cjk_coverage:.1%} "
                    f"< {args.cjk_error_threshold:.1%}"
                )
            elif report.cjk_coverage < args.cjk_warning_threshold:
                report.warnings.append(
                    f"CJK extraction coverage is limited: {report.cjk_coverage:.1%} "
                    f"< {args.cjk_warning_threshold:.1%}"
                )
            for index, source_text in enumerate(source_pages):
                if len(source_text) < args.min_cjk_page_chars:
                    continue
                extracted_page = extracted_pages[index] if index < len(extracted_pages) else ""
                coverage = multiset_coverage(source_text, extracted_page)
                if coverage < args.cjk_warning_threshold:
                    report.low_coverage_pages.append(
                        {
                            "visible_page": index + 1,
                            "coverage": round(coverage, 4),
                            "source_cjk_characters": len(source_text),
                            "extracted_cjk_characters": len(extracted_page),
                        }
                    )
            if report.low_coverage_pages:
                report.warnings.append(
                    f"{len(report.low_coverage_pages)} visible pages have low page-level CJK extraction coverage"
                )
        elif not extracted_text.strip():
            report.warnings.append("both source PPTX and PDF expose no extractable text")
    elif args.require_text and not extracted_text.strip():
        report.errors.append("PDF text extraction is empty")

    if report.unresolved_theme_fonts:
        report.warnings.append(
            "unresolved PPTX theme-font placeholders: "
            + ", ".join(report.unresolved_theme_fonts)
        )
    return report


def print_human(report: VerificationReport) -> None:
    status = "PASS" if not report.errors else "FAIL"
    print(f"{status}: {report.pdf}")
    if report.expected_visible_slides is not None:
        print(
            f"pages: PDF={report.pdf_pages} visible-PPTX={report.expected_visible_slides} "
            f"hidden={report.hidden_slide_numbers or '-'}"
        )
    else:
        print(f"pages: PDF={report.pdf_pages}")
    if report.pdf_fonts:
        for font in report.pdf_fonts:
            print(
                f"font: {font.name} | emb={'yes' if font.embedded else 'no'} | "
                f"sub={'yes' if font.subset else 'no'} | uni={'yes' if font.unicode else 'no'}"
            )
    if report.expected_fonts:
        print("expected fonts: " + ", ".join(report.expected_fonts))
    if report.cjk_coverage is not None:
        print(
            f"CJK extraction: coverage={report.cjk_coverage:.1%} "
            f"source={report.cjk_source_characters} extracted={report.cjk_extracted_characters}"
        )
    for warning in report.warnings:
        print(f"WARNING: {warning}", file=sys.stderr)
    for error in report.errors:
        print(f"ERROR: {error}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("pdf", type=Path)
    parser.add_argument("--source-pptx", type=Path)
    parser.add_argument("--expect-font", action="append", default=[])
    parser.add_argument("--allow-font", action="append", default=[])
    parser.add_argument("--deny-font", action="append", default=[])
    parser.add_argument("--font-alias", action="append", default=[], metavar="EXPECTED=PDF_NAME")
    parser.add_argument("--allow-unembedded-font", action="append", default=[])
    parser.add_argument("--allow-no-unicode-font", action="append", default=[])
    parser.add_argument("--no-auto-fonts", action="store_true")
    parser.add_argument("--require-text", action="store_true")
    parser.add_argument("--cjk-warning-threshold", type=float, default=0.75)
    parser.add_argument("--cjk-error-threshold", type=float, default=0.45)
    parser.add_argument("--min-cjk-page-chars", type=int, default=8)
    parser.add_argument("--json", action="store_true", dest="as_json")
    args = parser.parse_args()
    if not 0 <= args.cjk_error_threshold <= args.cjk_warning_threshold <= 1:
        parser.error("CJK thresholds must satisfy 0 <= error <= warning <= 1")
    if args.min_cjk_page_chars < 1:
        parser.error("--min-cjk-page-chars must be positive")

    report = verify(args)
    if args.as_json:
        print(json.dumps(asdict(report), ensure_ascii=False, indent=2))
    else:
        print_human(report)
    return 1 if report.errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
