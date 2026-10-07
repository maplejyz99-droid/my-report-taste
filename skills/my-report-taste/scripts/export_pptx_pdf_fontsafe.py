#!/usr/bin/env python3
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import tempfile
from pathlib import Path
from xml.sax.saxutils import escape


RUNTIME_SOFFICE_CANDIDATES = (
    Path.home()
    / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/override/soffice",
    Path.home()
    / ".cache/codex-runtimes/codex-primary-runtime/dependencies/bin/fallback/soffice",
)


def find_soffice(explicit: str | None) -> Path:
    if explicit:
        path = Path(explicit).expanduser().resolve()
        if path.exists():
            return path
        raise SystemExit(f"soffice not found: {path}")
    configured = os.environ.get("SOFFICE")
    if configured:
        path = Path(configured).expanduser().resolve()
        if path.exists():
            return path
        raise SystemExit(f"SOFFICE points to a missing executable: {path}")
    discovered = shutil.which("soffice") or shutil.which("libreoffice")
    if discovered:
        return Path(discovered).resolve()
    for candidate in RUNTIME_SOFFICE_CANDIDATES:
        if candidate.exists():
            return candidate.resolve()
    raise SystemExit(
        "No soffice executable found; pass --soffice, set SOFFICE, or add soffice/libreoffice to PATH"
    )


def write_fontconfig(path: Path, font_dirs: list[Path], cache_dir: Path) -> None:
    dirs = [
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
        Path("/usr/share/fonts"),
        Path("/usr/local/share/fonts"),
        Path.home() / ".local/share/fonts",
        Path.home() / ".fonts",
    ]
    dirs.extend(font_dirs)
    unique = []
    seen = set()
    for item in dirs:
        resolved = item.expanduser().resolve()
        if resolved.exists() and resolved not in seen:
            seen.add(resolved)
            unique.append(resolved)
    lines = [
        '<?xml version="1.0"?>',
        '<!DOCTYPE fontconfig SYSTEM "urn:fontconfig:fonts.dtd">',
        "<fontconfig>",
    ]
    lines.extend(f"  <dir>{escape(str(item))}</dir>" for item in unique)
    lines.append(f"  <cachedir>{escape(str(cache_dir))}</cachedir>")
    lines.append("</fontconfig>")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Export PPTX to PDF with an isolated font-aware LibreOffice profile")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--font-dir", type=Path, action="append", default=[])
    parser.add_argument("--soffice")
    args = parser.parse_args()

    source = args.input.expanduser().resolve()
    if not source.exists() or source.suffix.lower() != ".pptx":
        raise SystemExit(f"input must be an existing PPTX: {source}")
    output_dir = args.output_dir.expanduser().resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    soffice = find_soffice(args.soffice)

    with tempfile.TemporaryDirectory(prefix="report_soffice_profile_") as profile_raw:
        with tempfile.TemporaryDirectory(prefix="report_font_cache_") as cache_raw:
            with tempfile.TemporaryDirectory(prefix="report_fontconfig_") as config_raw:
                profile = Path(profile_raw)
                cache = Path(cache_raw)
                config = Path(config_raw) / "fonts.conf"
                write_fontconfig(config, [p.expanduser().resolve() for p in args.font_dir], cache)
                env = os.environ.copy()
                env["FONTCONFIG_FILE"] = str(config)
                env["XDG_CACHE_HOME"] = str(cache)
                cmd = [
                    str(soffice),
                    f"-env:UserInstallation={profile.as_uri()}",
                    "--headless",
                    "--convert-to",
                    "pdf",
                    "--outdir",
                    str(output_dir),
                    str(source),
                ]
                proc = subprocess.run(cmd, env=env, text=True, capture_output=True, check=False)
                if proc.returncode != 0:
                    raise SystemExit((proc.stderr or proc.stdout or "LibreOffice export failed").strip())

    output = output_dir / f"{source.stem}.pdf"
    if not output.exists():
        raise SystemExit(f"LibreOffice returned success but output is missing: {output}")
    print(output)


if __name__ == "__main__":
    main()
