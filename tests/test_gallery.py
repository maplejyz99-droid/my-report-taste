import json
import struct
import subprocess
import sys
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'examples/style-gallery'
NS = {'a': 'http://schemas.openxmlformats.org/drawingml/2006/main',
      'p': 'http://schemas.openxmlformats.org/presentationml/2006/main',
      'c': 'http://schemas.openxmlformats.org/drawingml/2006/chart'}


class GalleryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.gallery = json.loads((BASE / 'gallery.json').read_text())
        cls.source = json.loads((BASE / cls.gallery['source']).read_text())

    def test_preset_coverage_and_readme_links(self):
        items = self.gallery['items']
        self.assertEqual(len(items), 9)
        self.assertEqual(len({item['id'] for item in items}), 9)
        self.assertTrue(self.gallery['synthetic'] and self.source['synthetic'])
        # Legacy previews remain accessible, but are no longer nine theme entries.
        readme = (BASE / 'README.md').read_text()
        for item in items:
            self.assertEqual(readme.count(f"pages/{item['id']}.png"), 1)
        for name in ['README.md', 'README.en.md']:
            self.assertIn('examples/style-gallery/README.md', (ROOT / name).read_text())

    def test_png_dimensions_and_page_ratio(self):
        for item in self.gallery['items']:
            with self.subTest(preset=item['id']):
                data = (BASE / 'pages' / f"{item['id']}.png").read_bytes()
                self.assertEqual(data[:8], b'\x89PNG\r\n\x1a\n')
                self.assertGreater(len(data), 5000)
                self.assertEqual(struct.unpack('>II', data[16:24]),
                                 (round(item['width'] * 1.5), round(item['height'] * 1.5)))
                if item['id'] == 'dense-reading-report':
                    self.assertAlmostEqual(item['width'] / item['height'], 2 ** .5, places=2)
                else:
                    self.assertAlmostEqual(item['width'] / item['height'], 16 / 9)

    def test_each_deck_matches_its_plan(self):
        verifier = ROOT / 'skills/my-report-taste/scripts/verify_deck_plan.py'
        for item in self.gallery['items']:
            with self.subTest(preset=item['id']):
                result = subprocess.run([sys.executable, str(verifier),
                                         str(BASE / 'plans' / f"{item['id']}.md"),
                                         str(BASE / 'pages' / f"{item['id']}.pptx")],
                                        text=True, capture_output=True, timeout=20)
                self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_native_tables_and_synthetic_labels(self):
        table_count = 0
        expected = [[r['name'], f"{r['accuracy']:.1f}", str(r['latency'])]
                    for r in self.source['rows']]
        for item in self.gallery['items']:
            with zipfile.ZipFile(BASE / 'pages' / f"{item['id']}.pptx") as archive:
                slide = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
                content = ' '.join(x.text or '' for x in slide.findall('.//a:t', NS))
                self.assertIn('SYNTHETIC TEACHING DATA', content)
                self.assertIn(item['title'], content)
                for table in slide.findall('.//a:tbl', NS):
                    table_count += 1
                    matrix = [[''.join(t.text or '' for t in cell.findall('.//a:t', NS))
                               for cell in row.findall('a:tc', NS)]
                              for row in table.findall('a:tr', NS)]
                    self.assertEqual(matrix[1:], expected)
        self.assertEqual(table_count, 5)

    def test_chart_preserves_latency_values(self):
        with zipfile.ZipFile(BASE / 'pages/experiment-review.pptx') as archive:
            chart_files = [n for n in archive.namelist()
                           if n.startswith(('ppt/charts/chart', 'ppt/slides/charts/chart'))
                           and n.endswith('.xml')]
            self.assertEqual(len(chart_files), 1)
            chart = ET.fromstring(archive.read(chart_files[0]))
            values = [float(x.text) for x in chart.findall('.//c:ser/c:val//c:pt/c:v', NS)]
            self.assertEqual(values, [r['latency'] for r in self.source['rows']])
            self.assertTrue(any(n.startswith('ppt/embeddings/') and n.endswith('.xlsx')
                                for n in archive.namelist()))

    def test_architecture_arrows_point_to_destination(self):
        with zipfile.ZipFile(BASE / 'pages/technical-review-light.pptx') as archive:
            slide = ET.fromstring(archive.read('ppt/slides/slide1.xml'))
            arrows = slide.findall('.//p:cxnSp', NS)
            self.assertEqual(len(arrows), 3)
            for arrow in arrows:
                tail = arrow.find('.//a:tailEnd', NS)
                head = arrow.find('.//a:headEnd', NS)
                self.assertIsNotNone(tail)
                self.assertEqual(tail.get('type'), 'arrow')
                self.assertTrue(head is None or head.get('type') == 'none')


if __name__ == '__main__':
    unittest.main()
