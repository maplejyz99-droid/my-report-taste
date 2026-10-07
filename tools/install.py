#!/usr/bin/env python3
"""Install the skill without replacing an existing personal installation."""
import argparse
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
NAME = 'my-report-taste'


def install(parent: Path) -> Path:
    target = parent.expanduser().resolve() / NAME
    source = ROOT / 'skills' / NAME
    if target.exists() or target.is_symlink():
        raise ValueError(f'Existing installation preserved: {target}')
    legacy = Path.home() / '.codex/skills' / NAME
    if parent.expanduser().resolve() == (Path.home() / '.agents/skills').resolve() and legacy.exists():
        raise ValueError('A legacy personal skill with the same name exists; use an isolated --dest or migrate it manually first.')
    if source == target or source in target.parents:
        raise ValueError('Destination must be outside the source skill.')
    if any(path.is_symlink() for path in source.rglob('*')):
        raise ValueError('Unexpected symlink in source; inspect it before installing.')
    if not (source / 'SKILL.md').is_file():
        raise ValueError('Source skill is incomplete.')
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(source, target, ignore=shutil.ignore_patterns(
        '__pycache__', '*.pyc', 'local-profile.md', 'local', '.git', '.env',
        '.env.*', '.DS_Store', 'private', 'diagnostics', '.venv', 'node_modules'))
    for name in ('LICENSE', 'THIRD_PARTY_NOTICES.md'):
        shutil.copy2(ROOT / name, target / name)
    return target


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--dest', type=Path, default=Path.home() / '.agents/skills', help='Parent skills directory; default: ~/.agents/skills')
    args = parser.parse_args()
    if sys.version_info < (3, 10):
        parser.error('Python 3.10+ is required.')
    try:
        target = install(args.dest)
    except (ValueError, OSError) as exc:
        parser.exit(1, f'{exc}\n')
    print(f'Installed: {target}')
    print('Invoke $my-report-taste; if it is not listed, restart Codex. No account or global config was modified.')


if __name__ == '__main__':
    main()
