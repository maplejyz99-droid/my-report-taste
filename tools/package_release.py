#!/usr/bin/env python3
"""Build a deterministic ZIP from the public allowlist; no git history or local profile."""
from __future__ import annotations

import argparse
import hashlib
import re
import zipfile
from pathlib import Path

from check_public_release import ROOT, check, release_files


def build(root: Path, output: Path) -> tuple[Path, str]:
    errors, _ = check(root)
    if errors:
        raise ValueError('Release checks failed:\n' + '\n'.join(errors))
    version = (root / 'VERSION').read_text().strip()
    if not re.fullmatch(r'\d+\.\d+\.\d+(?:-[A-Za-z0-9.-]+)?', version):
        raise ValueError('Invalid VERSION.')
    output.mkdir(parents=True, exist_ok=True)
    archive = output / f'my-report-taste-v{version}.zip'
    # Only this tool-owned output filename is replaced on rebuild.
    with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as dest:
        for file in release_files(root):
            name = f'my-report-taste-v{version}/{file.relative_to(root).as_posix()}'
            info = zipfile.ZipInfo(name, date_time=(2026, 1, 1, 0, 0, 0))
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = 0o100644 << 16
            dest.writestr(info, file.read_bytes(), compresslevel=9)
    digest = hashlib.sha256(archive.read_bytes()).hexdigest()
    (output / f'{archive.name}.sha256').write_text(f'{digest}  {archive.name}\n', encoding='utf-8')
    return archive, digest


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output-dir', type=Path, default=ROOT / 'dist')
    args = parser.parse_args()
    try:
        archive, digest = build(ROOT, args.output_dir.resolve())
    except (OSError, ValueError) as exc:
        parser.exit(1, f'{exc}\n')
    print(archive)
    print(f'SHA256: {digest}')


if __name__ == '__main__':
    main()
