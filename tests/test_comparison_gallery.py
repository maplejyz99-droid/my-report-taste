import json
import re
import struct
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'examples/style-gallery/comparison'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main'}


def normalized(value):
    return ' '.join(value.split())


class ComparisonGalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((BASE / 'comparison.json').read_text())
        cls.copy = json.loads((BASE / 'content.json').read_text())
        cls.source = json.loads((BASE / cls.manifest['source']).read_text())

    def test_grouping_preserves_legacy_ids_without_counting_reading_as_a_theme(self):
        legacy = json.loads((BASE.parent / 'gallery.json').read_text())['items']
        groups = self.manifest['items']
        self.assertEqual(len(groups), 6)
        grouped = [key for group in groups for key in group['legacy_presets']]
        self.assertEqual(len(grouped), len(set(grouped)))
        self.assertEqual(set(grouped), {item['id'] for item in legacy} - {'dense-reading-report'})
        self.assertEqual(set(groups[0]['legacy_presets']),
                         {'author-light', 'experiment-review', 'technical-review-light'})
        self.assertEqual(self.manifest['reading_mode']['preset'], 'dense-reading-report')
        self.assertIsNone(self.manifest['reading_mode']['palette'])
        self.assertTrue(self.source['synthetic'] and self.manifest['synthetic'])
        for group in groups:
            original = next(item for item in legacy if item['id'] == group['preset'])
            self.assertIn(group['palette'], original['cards'])
            self.assertFalse(any(card.startswith('NAR-') for card in group['cards']))

    def test_bilingual_readmes_have_six_candidates_and_separate_palettes(self):
        for name in ['README.md', 'README.en.md']:
            text = (ROOT / name).read_text()
            self.assertEqual(len(re.findall(r'^### \d{2} · ', text, re.MULTILINE)), 6)
            for item in self.manifest['items']:
                base = f"examples/style-gallery/comparison/pages/{item['id']}"
                for filename in ['preview.png', 'result.png', 'mechanism.png', 'example.pptx']:
                    self.assertEqual(text.count(f'{base}/{filename}'), 1)
                self.assertIn(f"--visual {item['preset']}", text)
            reading = '## 独立阅读版式' if name == 'README.md' else '## Independent-reading layout'
            palette = '## 配色编号怎么看' if name == 'README.md' else '## Reading the palette IDs'
            self.assertIn(reading, text)
            self.assertIn(palette, text)

    def test_content_and_native_table_are_identical_across_candidates(self):
        expected_rows = [[r['name'], f"{r['accuracy']:.1f}", str(r['latency'])]
                         for r in self.source['rows']]
        copies = []
        for item in self.manifest['items']:
            with self.subTest(candidate=item['id']), zipfile.ZipFile(
                    BASE / 'pages' / item['id'] / 'example.pptx') as archive:
                self.assertEqual(len([n for n in archive.namelist()
                                      if re.fullmatch(r'ppt/slides/slide\d+\.xml', n)]), 2)
                texts = []
                for i, kind in enumerate(['result', 'mechanism'], 1):
                    slide = ET.fromstring(archive.read(f'ppt/slides/slide{i}.xml'))
                    text = normalized(' '.join(x.text or '' for x in slide.findall('.//a:t', NS)))
                    for value in self.copy[kind].values():
                        self.assertIn(normalized(value), text)
                    self.assertIn(self.copy['source'], text)
                    texts.append(text.replace('RESULTS ', '').replace('MECHANISM ', ''))
                    tables = slide.findall('.//a:tbl', NS)
                    self.assertEqual(len(tables), 1 if i == 1 else 0)
                    if tables:
                        matrix = [[''.join(t.text or '' for t in cell.findall('.//a:t', NS))
                                   for cell in row.findall('a:tc', NS)]
                                  for row in tables[0].findall('a:tr', NS)]
                        self.assertEqual(matrix[0], ['Setting', 'Accuracy (%)', 'Latency (ms/query)'])
                        self.assertEqual(matrix[1:], expected_rows)
                copies.append(texts)
        # Text order may change with composition; required exact phrases cannot.
        self.assertEqual(len(copies), 6)

    def test_mechanism_nodes_and_connector_direction(self):
        for item in self.manifest['items']:
            with self.subTest(candidate=item['id']), zipfile.ZipFile(
                    BASE / 'pages' / item['id'] / 'example.pptx') as archive:
                slide = ET.fromstring(archive.read('ppt/slides/slide2.xml'))
                labels = [''.join(t.text or '' for t in shape.findall('.//a:t', NS))
                          for shape in slide.findall('.//p:sp', NS)]
                for label in self.source['method']:
                    self.assertEqual(labels.count(label), 1)
                connectors = slide.findall('.//p:cxnSp', NS)
                self.assertEqual(len(connectors), 3)
                for connector in connectors:
                    tail = connector.find('.//a:tailEnd', NS)
                    self.assertIsNotNone(tail)
                    self.assertEqual(tail.get('type'), 'arrow')
                    head = connector.find('.//a:headEnd', NS)
                    self.assertTrue(head is None or head.get('type') == 'none')

    def test_plans_match_each_finalized_deck(self):
        for item in self.manifest['items']:
            folder = BASE / 'pages' / item['id']
            result = subprocess.run([sys.executable,
                                     str(ROOT / 'skills/my-report-taste/scripts/verify_deck_plan.py'),
                                     str(folder / 'slide-plan.md'), str(folder / 'example.pptx')],
                                    text=True, capture_output=True, timeout=20)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_exported_dimensions(self):
        for item in self.manifest['items']:
            folder = BASE / 'pages' / item['id']
            for name, size in [('result', (1600, 900)), ('mechanism', (1600, 900)),
                               ('preview', (3224, 900))]:
                data = (folder / f'{name}.png').read_bytes()
                self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
                self.assertEqual(struct.unpack('>II', data[16:24]), size)


if __name__ == '__main__':
    unittest.main()
