import json
import re
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'examples/style-gallery'
NS = {'s': 'http://www.w3.org/2000/svg'}


class PaletteDocsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.items = json.loads((BASE / 'gallery.json').read_text())['items']

    def test_each_preset_uses_its_existing_color_card(self):
        for filename in ['README.md', 'README.en.md']:
            readme = (ROOT / filename).read_text()
            palette_ids = {card for item in self.items for card in item['cards']
                           if card.startswith('CLR-')}
            for palette in palette_ids | {'dense-example'}:
                with self.subTest(readme=filename, palette=palette):
                    self.assertEqual(readme.count(
                        f'examples/style-gallery/palettes/{palette}.svg'), 1)
                    if palette in palette_ids:
                        self.assertIn(f'references/{palette}.md', readme)
                    else:
                        self.assertIn('无固定 CLR 编号' if filename == 'README.md'
                                      else 'no fixed CLR ID', readme)
                    svg = ET.parse(BASE / 'palettes' / f'{palette}.svg').getroot()
                    for chip in svg.findall('.//s:g[@data-color]', NS):
                        self.assertIn(f"`{chip.get('data-color')}`", readme)

    def test_swatches_match_source_and_visible_hex_labels(self):
        files = sorted((BASE / 'palettes').glob('*.svg'))
        self.assertEqual({p.stem for p in files},
                         {'CLR-002', 'CLR-003', 'CLR-006', 'CLR-007',
                          'CLR-008', 'CLR-010', 'dense-example'})
        builder = (BASE / 'build_gallery.mjs').read_text()
        for path in files:
            with self.subTest(palette=path.stem):
                if path.stem == 'dense-example':
                    source = re.search(r'const report = \{([^}]+)\}', builder).group(1)
                else:
                    source = (ROOT / 'skills/my-report-taste/references' /
                              f'{path.stem}.md').read_text()
                source_colors = set(re.findall(r'#[0-9A-Fa-f]{6}\b', source))
                svg = ET.parse(path).getroot()
                self.assertEqual(svg.get('data-palette'), path.stem)
                self.assertIsNotNone(svg.find('s:title', NS))
                self.assertIsNotNone(svg.find('s:desc', NS))
                chips = svg.findall('.//s:g[@data-color]', NS)
                self.assertGreaterEqual(len(chips), 6)
                for chip in chips:
                    color = chip.get('data-color')
                    self.assertIn(color, source_colors)
                    self.assertEqual(chip.find('s:rect', NS).get('fill'), color)
                    self.assertEqual(chip.find('s:text', NS).text, color)

    def test_svg_is_self_contained_and_geometry_is_in_bounds(self):
        allowed = {'svg', 'title', 'desc', 'g', 'rect', 'text'}
        for path in (BASE / 'palettes').glob('*.svg'):
            with self.subTest(palette=path.stem):
                svg = ET.parse(path).getroot()
                width, height = float(svg.get('width')), float(svg.get('height'))
                for node in svg.iter():
                    self.assertIn(node.tag.split('}')[-1], allowed)
                    for key in node.attrib:
                        self.assertNotIn('href', key)
                        self.assertFalse(key.lower().startswith('on'))
                    for value in node.attrib.values():
                        self.assertNotIn('url(', value)
                    if node.tag.endswith('}rect'):
                        x, y = float(node.get('x', 0)), float(node.get('y', 0))
                        self.assertGreaterEqual(min(x, y), 0)
                        self.assertLessEqual(x + float(node.get('width')), width)
                        self.assertLessEqual(y + float(node.get('height')), height)


if __name__ == '__main__':
    unittest.main()
