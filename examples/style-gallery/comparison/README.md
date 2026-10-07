# Same-content presentation comparison / 同内容呈现对照

Six candidate presentation directions use the same result page and mechanism page. These are controlled examples, not six validated independent themes or six content routes. The main README merges the three blue entries, and places independent reading outside this comparison.

六个候选方向使用完全相同的结果页与机制页，帮助判断哪些区别来自排版，哪些只是配色或导航变体。没有预设“六个必须都保留”的结论，也不改变 explain／progress／compare 三类内容任务。

## What stays fixed

- The [original synthetic fixture](../../synthetic-study/source.json), all three rows, and metric units.
- The [shared copy](content.json): exact titles, two deltas, limitations and source disclosure.
- The four conceptual mechanism nodes, three directed connections, local explanations, and scope.
- 1280 × 720 canvas, two pages per candidate, and design-selected Arial. No font files, animations, external figures, or brand assets.

What can change: evidence placement, alignment, type scale, surfaces, navigation, and role-based color. This deliberately holds content and page purpose constant. It does not test a full story, chapter transitions, images, formulas, a projector, or audience comprehension. Two required examples are a comparison protocol, not a mandatory template for real reports.

## Browse

The paired thumbnail puts results on the left and mechanism on the right. Open the individual PNGs for readable detail. Each `example.pptx` contains two editable slides with a native table and connectors.

- **浅色编辑式 / Light editorial**: [result](pages/light-editorial/result.png), [mechanism](pages/light-editorial/mechanism.png), [PPTX](pages/light-editorial/example.pptx), [plan](pages/light-editorial/slide-plan.md).
- **学术证据式 / Academic evidence**: [result](pages/academic-evidence/result.png), [mechanism](pages/academic-evidence/mechanism.png), [PPTX](pages/academic-evidence/example.pptx), [plan](pages/academic-evidence/slide-plan.md).
- **深色编辑式 / Dark editorial**: [result](pages/dark-editorial/result.png), [mechanism](pages/dark-editorial/mechanism.png), [PPTX](pages/dark-editorial/example.pptx), [plan](pages/dark-editorial/slide-plan.md).
- **轻导航浅色 / Light navigation**: [result](pages/green-navigation/result.png), [mechanism](pages/green-navigation/mechanism.png), [PPTX](pages/green-navigation/example.pptx), [plan](pages/green-navigation/slide-plan.md).
- **侧轨证据式 / Rail evidence**: [result](pages/rail-evidence/result.png), [mechanism](pages/rail-evidence/mechanism.png), [PPTX](pages/rail-evidence/example.pptx), [plan](pages/rail-evidence/slide-plan.md).
- **无彩编辑式 / Neutral editorial**: [result](pages/neutral-editorial/result.png), [mechanism](pages/neutral-editorial/mechanism.png), [PPTX](pages/neutral-editorial/example.pptx), [plan](pages/neutral-editorial/slide-plan.md).

## What the comparison currently shows

These are design judgments from inspecting the examples, not user-study results:

- Light editorial combines metric surfaces with an open table; light navigation keeps similar evidence grammar and adds a small navigation system. Their overlap remains visible.
- Academic evidence and rail evidence both support continuous evidence plus side explanation. Source placement, navigation and surface treatment differ, but two pages do not establish independent full themes.
- Dark editorial has the clearest change in luminance hierarchy and page composition. The vertical mechanism keeps explanations aligned to their actual nodes.
- Neutral editorial removes chromatic emphasis and container fills. Its image-led and chapter-page behavior is outside this small fixture.

观察结论：浅色／绿色、学术／侧轨仍有重叠；这次如实保留，而不通过额外装饰制造区别。是否继续合并，需依据实际使用反馈。六套 CLR 配色卡仍可独立使用。

## Compatibility

[comparison.json](comparison.json) maps documentation display IDs to existing invocation IDs. Display names are not new CLI routes. The three blue IDs retain their original rules: only the gallery entry is merged. `dense-reading-report` remains supported as an independent-reading option with no fixed CLR card. Original previews are retained in the [legacy gallery](../README.md).

## Rebuild and limits

[build_comparison.mjs](build_comparison.mjs) requires a host-provided `@oai/artifact-tool`; the package and rendering runtime are not bundled. It writes six draft PPTX files to a new directory and refuses an existing one:

```bash
node examples/style-gallery/comparison/build_comparison.mjs /path/to/new-draft-directory
```

Draft export is not finalization. The checked-in previews were rendered after reimporting finalized PPTX files. Inspect every rendered slide and preserve content equivalence before publishing a rebuild. Fonts can reflow in other applications. See [verification](verification.md); automated checks do not prove visual distinctiveness.
