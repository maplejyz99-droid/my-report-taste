#!/usr/bin/env python3
"""Bounded distribution, local-link and privacy-pattern checks (not a security audit)."""
from __future__ import annotations

import argparse
import os
import re
import sys
import zipfile
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
TOP_FILES = {
    '.gitignore', 'README.md', 'README.en.md', 'LICENSE', 'VERSION',
    'THIRD_PARTY_NOTICES.md', 'CONTRIBUTING.md',
}
TOP_DIRS = {'skills', 'tools', 'tests', 'docs', 'examples', '.github'}
EXCLUDED = {'.git', '__pycache__', '.venv', 'node_modules', '.report-taste',
            'local', 'private', 'diagnostics', 'dist', '.DS_Store'}
TEXT_SUFFIXES = {'.md', '.py', '.json', '.yaml', '.yml', '.txt', '.mjs', '.html', '.css', '.svg'}
REQUIRED = {
    'README.md', 'README.en.md', 'LICENSE', 'VERSION', 'THIRD_PARTY_NOTICES.md',
    'tools/install.py', 'tools/check_public_release.py', 'tools/package_release.py',
    'skills/my-report-taste/SKILL.md', 'skills/my-report-taste/agents/openai.yaml',
    'docs/installation.md', 'docs/release-verification.md',
    'examples/synthetic-study/README.md', 'examples/synthetic-study/source.json',
    'examples/synthetic-study/slide-plan.md', 'examples/synthetic-study/script-en.md',
    'examples/synthetic-study/script-zh.md', '.github/workflows/ci.yml',
}
PATTERNS = {
    'personal absolute path': re.compile(r'/(?:Users|home)/[A-Za-z0-9_.-]+/'),
    'macOS private temporary path': re.compile(r'/(?:private/)?var/folders/[^\s]+'),
    'private chat reference': re.compile(r'(?:codex|thread)://threads?/|wxid_[A-Za-z0-9]+'),
    'credential-like token': re.compile(r'\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,}|sk-[A-Za-z0-9_-]{24,})\b'),
    'private-key block': re.compile(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----'),
}
LINK = re.compile(r'!?\[[^\]\n]*\]\(([^\s)]+)(?:\s+"[^"]*")?\)')


def excluded(name: str) -> bool:
    return name in EXCLUDED or name == 'local-profile.md' or name.startswith('.env') or name.endswith(('.pyc', '.log'))


def release_files(root: Path) -> list[Path]:
    """Select only documented release roots, without following symlinks."""
    files = []
    for base, dirs, names in os.walk(root, followlinks=False):
        base = Path(base)
        dirs[:] = sorted(d for d in dirs if not excluded(d) and (base != root or d in TOP_DIRS))
        for name in dirs:
            if (base / name).is_symlink():
                raise ValueError(f'Symlink directory in release: {(base / name).relative_to(root)}')
        for name in sorted(names):
            if excluded(name) or (base == root and name not in TOP_FILES):
                continue
            file = base / name
            if file.is_symlink():
                raise ValueError(f'Symlink file in release: {file.relative_to(root)}')
            if file.stat().st_size > 8 * 1024 * 1024:
                raise ValueError(f'Oversized file needs explicit review: {file.relative_to(root)}')
            files.append(file)
            if len(files) > 1000:
                raise ValueError('Release exceeds the 1000-file review limit.')
    return sorted(files)


def check_text(text: str, label: str) -> list[str]:
    # Report locations/categories, never echo a possible secret.
    return [f'{label}: {name}' for name, regex in PATTERNS.items() if regex.search(text)]


def check(root: Path) -> tuple[list[str], int]:
    root = root.resolve()
    errors = []
    try:
        files = release_files(root)
    except (OSError, ValueError) as exc:
        return [str(exc)], 0
    selected = {p.relative_to(root).as_posix() for p in files}
    errors.extend(f'Missing required file: {name}' for name in sorted(REQUIRED - selected))
    for file in files:
        relative = file.relative_to(root).as_posix()
        if file.suffix in TEXT_SUFFIXES or file.name in TOP_FILES:
            try:
                text = file.read_text(encoding='utf-8')
            except UnicodeError:
                errors.append(f'Unexpected non-UTF-8 text: {relative}')
                continue
            errors.extend(check_text(text, relative))
            if file.suffix == '.md':
                for target in LINK.findall(text):
                    target = target.strip('<>')
                    parsed = urlsplit(target)
                    if parsed.scheme or parsed.netloc or not parsed.path:
                        continue
                    dest = (file.parent / unquote(parsed.path)).resolve()
                    if root not in dest.parents or not dest.exists():
                        errors.append(f'{relative}: broken/out-of-tree Markdown link: {target}')
        elif file.suffix == '.pptx' and relative.startswith('examples/'):
            try:
                with zipfile.ZipFile(file) as archive:
                    members = archive.infolist()
                    if len(members) > 1000 or sum(m.file_size for m in members) > 32 * 1024 * 1024:
                        errors.append(f'{relative}: package exceeds inspection limits')
                        continue
                    for member in members:
                        if member.filename.endswith(('.xml', '.rels')):
                            errors.extend(check_text(archive.read(member).decode('utf-8'), f'{relative}:{member.filename}'))
            except (zipfile.BadZipFile, UnicodeError) as exc:
                errors.append(f'{relative}: invalid PPTX text: {exc}')
        elif file.suffix not in {'.png', '.pdf'} or not relative.startswith('examples/'):
            errors.append(f'Unexpected release file type: {relative}')
    return errors, len(files)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args()
    errors, count = check(args.root)
    for error in errors:
        print(f'ERROR: {error}', file=sys.stderr)
    if errors:
        return 1
    print(f'PASS: {count} selected files; required files, relative links and bounded privacy patterns checked.')
    print('Not checked: remote link availability, legal clearance, arbitrary secrets or complete binary metadata.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
