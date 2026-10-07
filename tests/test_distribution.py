import json
import sys
import tempfile
import unittest
import zipfile
from xml.etree import ElementTree as ET
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))
from check_public_release import check, check_text, release_files
from install import install
from package_release import build


class DistributionTests(unittest.TestCase):
    def test_public_tree(self):
        errors, count = check(ROOT)
        self.assertEqual(errors, [])
        self.assertGreater(count, 60)

    def test_install_and_refuse_overwrite(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = install(Path(tmp) / 'skills')
            self.assertTrue((target / 'SKILL.md').is_file())
            self.assertTrue((target / 'LICENSE').is_file())
            marker = target / 'my-personal-content.md'
            marker.write_text('keep me')
            with self.assertRaises(ValueError):
                install(Path(tmp) / 'skills')
            self.assertEqual(marker.read_text(), 'keep me')

    def test_legacy_install_is_preserved(self):
        with tempfile.TemporaryDirectory() as tmp:
            fake_home = Path(tmp)
            old = fake_home / '.codex/skills/my-report-taste'
            old.mkdir(parents=True)
            with mock.patch('install.Path.home', return_value=fake_home):
                with self.assertRaises(ValueError):
                    install(fake_home / '.agents/skills')
            self.assertTrue(old.is_dir())

    def test_public_selection_ignores_private_inputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for relative in ['README.md', 'tools/test.py', '.git/config', '.env', 'private/notes.md', 'skills/demo/references/local-profile.md', 'dist/archive.zip']:
                file = root / relative
                file.parent.mkdir(parents=True, exist_ok=True)
                file.write_text('fixture')
            self.assertEqual({p.relative_to(root).as_posix() for p in release_files(root)}, {'README.md', 'tools/test.py'})

    def test_symlinks_are_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'tools').mkdir()
            try:
                (root / 'tools/link').symlink_to(root / 'missing')
            except OSError:
                self.skipTest('Symlink creation unavailable on this platform.')
            with self.assertRaises(ValueError):
                release_files(root)

    def test_scanner_redacts_matches(self):
        fake = '/' + 'Users' + '/example-person/private/'
        errors = check_text(fake, 'fixture')
        self.assertEqual(errors, ['fixture: personal absolute path'])
        self.assertNotIn(fake, str(errors))

    def test_archive_is_repeatable(self):
        with tempfile.TemporaryDirectory() as tmp:
            first, digest1 = build(ROOT, Path(tmp) / 'a')
            second, digest2 = build(ROOT, Path(tmp) / 'b')
            self.assertEqual(digest1, digest2)
            self.assertEqual(first.read_bytes(), second.read_bytes())
            with zipfile.ZipFile(first) as archive:
                self.assertTrue(any(name.endswith('/LICENSE') for name in archive.namelist()))
                self.assertFalse(any('/.git/' in name or '__pycache__' in name or 'local-profile.md' in name for name in archive.namelist()))

    def test_synthetic_numbers_and_scope(self):
        source = json.loads((ROOT / 'examples/synthetic-study/source.json').read_text())
        self.assertTrue(source['synthetic'])
        baseline, compact, large = source['rows']
        self.assertAlmostEqual(compact['accuracy'] - baseline['accuracy'], 2.0)
        self.assertEqual(baseline['latency'] - compact['latency'], 35)
        self.assertGreater(large['latency'], baseline['latency'])
        self.assertEqual(len(source['unmeasured']), 4)

    def test_native_table_matches_source(self):
        base = ROOT / 'examples/synthetic-study'
        source = json.loads((base / 'source.json').read_text())
        ns = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main'}
        with zipfile.ZipFile(base / 'demo.pptx') as archive:
            slide = ET.fromstring(archive.read('ppt/slides/slide3.xml'))
            rows = slide.findall('.//a:tbl/a:tr', ns)
            matrix = [[''.join(text.text or '' for text in cell.findall('.//a:t', ns))
                       for cell in row.findall('a:tc', ns)] for row in rows]
            expected = [[row['name'], f"{row['accuracy']:.1f}", str(row['latency'])] for row in source['rows']]
            self.assertEqual(matrix[1:], expected)
            for index in range(1, 6):
                content = archive.read(f'ppt/slides/slide{index}.xml').decode()
                self.assertIn('Synthetic teaching data', content)


if __name__ == '__main__':
    unittest.main()
