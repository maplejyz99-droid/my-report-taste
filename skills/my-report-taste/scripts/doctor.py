#!/usr/bin/env python3
"""Read-only capability discovery; detection is not an export or visual test."""
from __future__ import annotations

import argparse
import importlib.util
import json
import platform
import shutil
import subprocess
import sys
from pathlib import Path


def node_probe(node: str | None, project_dir: Path) -> dict:
    if not node:
        return {"status": "unavailable"}
    # Built-ins only: resolve a package location without importing its code.
    script = "console.log(JSON.stringify({version:process.version,artifact:(()=>{try{return !!require.resolve('@oai/artifact-tool')}catch{return false}})()}))"
    try:
        result = subprocess.run([node, "-e", script], cwd=project_dir, capture_output=True,
                                text=True, timeout=5, check=False)
        if result.returncode:
            return {"status": "probe_failed"}
        data = json.loads(result.stdout)
        return {"status": "detected", "version": data["version"],
                "artifact_tool_resolvable": bool(data["artifact"])}
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError):
        return {"status": "probe_failed"}


def inspect(project_dir: Path, probe_node: bool = False) -> dict:
    commands = {name: bool(shutil.which(name)) for name in
                ("node", "soffice", "pdfinfo", "pdffonts", "pdftotext", "pdftoppm")}
    pillow = importlib.util.find_spec("PIL") is not None
    node = node_probe(shutil.which("node"), project_dir) if probe_node else {"status": "not_probed"}
    standard = sys.version_info >= (3, 10)
    example_present = (Path(__file__).resolve().parents[3] / "examples/portable-report/build_report.py").is_file()
    return {
        "python": platform.python_version(), "platform": platform.system(),
        "python_supported": standard, "commands_detected": commands,
        "pillow_detected": pillow, "node_probe": node,
        "capabilities": {
            "library_plan_script_checks": "available" if standard else "unavailable",
            "stdlib_html_markdown_example": ("available_in_repository" if standard and example_present
                                               else "repository_example_not_available"),
            "color_check": "dependency_detected" if pillow else "dependency_missing",
            "pptx_pdf_export": "executable_detected_not_tested" if commands["soffice"] else "not_detected",
            "pdf_structure_check": "executables_detected_not_tested" if all(commands[k] for k in
                                      ("pdfinfo", "pdffonts", "pdftotext")) else "incomplete",
            "pdf_rasterization": "executable_detected_not_tested" if commands["pdftoppm"] else "not_detected",
            "artifact_gallery": "module_resolvable_not_tested" if node.get("artifact_tool_resolvable") else "not_verified",
        },
        "not_checked": ["font availability and embedding", "PPTX rendering and editability",
                        "browser rendering", "scientific correctness", "projector compatibility"],
        "notes": ["No packages are installed and no browser or Office application is started.",
                  "--probe-node executes one bounded Node built-in probe; it does not import artifact-tool.",
                  "Examples live in the repository, not in the installed skill folder.",
                  "A host-provided renderer can exist outside PATH; not_detected does not mean impossible."],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--project-dir", type=Path, default=Path.cwd())
    parser.add_argument("--probe-node", action="store_true")
    args = parser.parse_args()
    if not args.project_dir.is_dir():
        parser.error("--project-dir must be an existing directory")
    report = inspect(args.project_dir, args.probe_node)
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["python_supported"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
