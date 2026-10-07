// Optional PPTX builder for a host that already provides @oai/artifact-tool.
// Export is a draft, not evidence of visual or PowerPoint validation.
import fs from 'node:fs/promises';
import path from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import { Presentation, PresentationFile } from '@oai/artifact-tool';

const here = path.dirname(fileURLToPath(import.meta.url));
export async function buildDeck(fontFamily = 'Arial') {
  const source = JSON.parse(await fs.readFile(path.join(here, 'source.json'), 'utf8'));
  if (!source.synthetic) throw new Error('This builder is only for the synthetic teaching fixture.');
  const plan = await fs.readFile(path.join(here, 'slide-plan.md'), 'utf8');
  const titles = [...plan.matchAll(/^- title: (.+)$/gm)].map(match => match[1]);
  const presentation = Presentation.create({slideSize: {width: 1280, height: 720}});
  const blue = '#2257B8', ink = '#182C45', muted = '#526279', pale = '#EAF0FA';
  function text(slide, value, x, y, w, h, size = 28, color = ink, bold = false) {
    const shape = slide.shapes.add({geometry: 'textbox', position: {left: x, top: y, width: w, height: h}, fill: 'none', line: {fill: 'none', width: 0}});
    shape.text = value;
    shape.text.style = {typeface: fontFamily, fontSize: size, color, bold, autoFit: 'none'};
    return shape;
  }
  function slide(index) {
    const page = presentation.slides.add();
    page.background.fill = '#FFFFFF';
    text(page, titles[index - 1], 72, 54, 1136, 116, 40, blue, true);
    text(page, 'Synthetic teaching data · no real experiment or deployment claim', 72, 660, 1020, 30, 17, muted);
    text(page, `${index} / 5`, 1130, 660, 78, 30, 17, muted);
    const id = `S${String(index).padStart(2, '0')}`;
    page.speakerNotes.textFrame.setText(`[slide-id:${id}] [role:${index === 5 ? 'backup' : 'main'}]\nSource: source.json (candidate-filter-fixture-v1). All values are synthetic.\nScripts: script-en.md and script-zh.md, matching ${id}.`);
    return page;
  }
  let page = slide(1);
  text(page, 'How does selecting candidates before ranking\nchange answer quality and time per query?', 72, 222, 1070, 132, 38);
  text(page, 'Accuracy', 72, 428, 510, 48, 30, blue, true);
  text(page, 'Correct top results (%)', 72, 489, 510, 48, 27);
  text(page, 'Latency', 684, 428, 510, 48, 30, blue, true);
  text(page, 'Milliseconds per query', 684, 489, 510, 48, 27);

  page = slide(2);
  const labels = ['Query', 'Candidate\nfilter', 'Ranker', 'Top result'];
  labels.forEach((label, index) => {
    const x = 72 + index * 298;
    text(page, label, x, 263, 218, 112, 31, index === 1 ? blue : ink, index === 1);
    if (index < 3) text(page, '→', x + 218, 280, 70, 62, 42, muted);
  });
  text(page, 'The ranker can only order the candidates it receives.', 72, 453, 1136, 54, 31, blue, true);
  text(page, 'A conceptual sequence; candidate recall and actual savings are unmeasured.', 72, 540, 1120, 72, 25, muted);

  page = slide(3);
  const values = [['Setting', 'Accuracy (%)', 'Latency (ms / query)'],
    ...source.rows.map(row => [row.name, row.accuracy.toFixed(1), String(row.latency)])];
  const table = page.tables.add({rows: 4, columns: 3, left: 72, top: 210, width: 1136, height: 296, columnWidths: [480, 270, 386], values});
  table.borders.assign({width: 0.7, fill: '#D6DEEA', style: 'solid'});
  table.cells.block({row: 0, column: 0, rowCount: 4, columnCount: 3}).assign({textStyle: {typeface: fontFamily, fontSize: 28, color: ink}, fill: '#FFFFFF', margins: {left: 20, right: 16, top: 18, bottom: 14}});
  table.cells.block({row: 0, column: 0, rowCount: 1, columnCount: 3}).assign({textStyle: {typeface: fontFamily, fontSize: 25, bold: true, color: blue}, fill: pale});
  table.cells.block({row: 2, column: 0, rowCount: 1, columnCount: 3}).assign({textStyle: {typeface: fontFamily, fontSize: 28, bold: true, color: ink}, fill: '#F3F6FC'});
  const [baseline, compact] = source.rows;
  text(page, `Compact vs. baseline: +${(compact.accuracy - baseline.accuracy).toFixed(1)} percentage points; ${baseline.latency - compact.latency} ms less per query`, 72, 546, 1136, 58, 28, blue, true);

  page = slide(4);
  text(page, 'What the fixture shows', 72, 206, 505, 48, 29, blue, true);
  text(page, 'The compact setting has higher\naccuracy and lower latency\nthan the baseline in these values.', 72, 282, 530, 180, 30);
  text(page, 'Still unmeasured', 700, 206, 508, 48, 29, blue, true);
  text(page, 'Repeatability\nHardware and workload variation\nMemory use\nCandidate recall', 700, 282, 508, 236, 28);
  text(page, 'The synthetic values establish no real deployment advantage.', 72, 558, 1136, 58, 28, ink, true);

  page = slide(5);
  text(page, 'Accuracy', 72, 205, 320, 48, 30, blue, true);
  text(page, 'Correct top results, expressed as a percentage', 402, 205, 806, 48, 27);
  text(page, '86.0% − 84.0% = 2.0 percentage points', 402, 278, 806, 48, 30, ink, true);
  text(page, 'Latency', 72, 397, 320, 48, 30, blue, true);
  text(page, '120 − 85 = 35 ms less per query', 402, 397, 806, 48, 30, ink, true);
  text(page, '35 / 120 ≈ 29.2% lower relative to the baseline', 402, 475, 806, 48, 28);
  return presentation;
}

if (process.argv[1] && import.meta.url === pathToFileURL(path.resolve(process.argv[1])).href) {
  if (!process.argv[2]) throw new Error('Usage: node build_deck.mjs /path/to/new-draft.pptx [font-family]');
  const output = path.resolve(process.argv[2]);
  try { await fs.access(output); throw new Error('Output already exists; use a new draft filename.'); }
  catch (error) { if (error.code !== 'ENOENT') throw error; }
  await fs.mkdir(path.dirname(output), {recursive: true});
  await (await PresentationFile.exportPptx(await buildDeck(process.argv[3]))).save(output);
  console.log(`Draft exported: ${output}. Inspect and validate before use.`);
}
