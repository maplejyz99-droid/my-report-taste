# Style gallery / 风格预览

Nine independent content-page examples, not nine full decks. All values come from the [original synthetic fixture](../synthetic-study/source.json). No private presentation, source-deck screenshot, logo, external figure, or font file is included.

九个独立单页示例，不代表九套完整演讲稿。数值全部为教学合成值；项目进度页展示的是示意审阅顺序，不是真实项目状态。单页不能验证整套叙事、转场或远距投影效果。

## Browse and reuse

Each PNG is a 1.5× export of its editable PPTX page. The first eight pages use a 1280 × 720 canvas; the reading report uses 1400 × 990, approximately the A-series landscape ratio. The gallery deliberately uses English labels so both README languages can share the same images. A real Chinese deck needs its own typography and line-wrap check.

- **明亮蓝研究汇报 / Bright blue research update** (`author-light`): [PNG](pages/author-light.png) · [editable PPTX](pages/author-light.pptx) · [page plan](plans/author-light.md)
- **酒红学术报告 / Wine academic report** (`academic-oral-wine`): [PNG](pages/academic-oral-wine.png) · [editable PPTX](pages/academic-oral-wine.pptx) · [page plan](plans/academic-oral-wine.md)
- **实验与性能复盘 / Experiment and performance review** (`experiment-review`): [PNG](pages/experiment-review.png) · [editable PPTX](pages/experiment-review.pptx) · [page plan](plans/experiment-review.md)
- **浅色技术架构 / Light technical architecture** (`technical-review-light`): [PNG](pages/technical-review-light.png) · [editable PPTX](pages/technical-review-light.pptx) · [page plan](plans/technical-review-light.md)
- **深色技术评审 / Dark technical review** (`technical-review-dark`): [PNG](pages/technical-review-dark.png) · [editable PPTX](pages/technical-review-dark.pptx) · [page plan](plans/technical-review-dark.md)
- **鲜绿项目汇报 / Green project update** (`project-green`): [PNG](pages/project-green.png) · [editable PPTX](pages/project-green.pptx) · [page plan](plans/project-green.md)
- **深蓝与沙金项目总结 / Blue and sand project summary** (`project-summary-dual-semantics`): [PNG](pages/project-summary-dual-semantics.png) · [editable PPTX](pages/project-summary-dual-semantics.pptx) · [page plan](plans/project-summary-dual-semantics.md)
- **无彩证据复盘 / Neutral evidence review** (`neutral-evidence-review`): [PNG](pages/neutral-evidence-review.png) · [editable PPTX](pages/neutral-evidence-review.pptx) · [page plan](plans/neutral-evidence-review.md)
- **高密度阅读报告 / Dense reading report** (`dense-reading-report`): [PNG](pages/dense-reading-report.png) · [editable PPTX](pages/dense-reading-report.pptx) · [page plan](plans/dense-reading-report.md)

## Build

[build_gallery.mjs](build_gallery.mjs) reads [gallery.json](gallery.json) and the shared synthetic source. It requires a host that already provides `@oai/artifact-tool`; this package is not bundled and the Python installer does not install it. The checked-in PNG/PPTX files can be used without this builder.

```bash
node examples/style-gallery/build_gallery.mjs /path/to/new-gallery-directory
```

The builder refuses an existing output directory. It produces drafts; rendering and visual inspection remain necessary. Fonts: Arial, plus Courier New for the source excerpt. Font files are not redistributed. Cross-application editing can change font metrics.

## Provenance and limits

Preset rules come from the repository's [optional author presets](../../skills/my-report-taste/references/author-presets.md). These original pages translate those rules rather than reproducing the external source decks. Their original material is covered by the project license; the upstream sources are not relicensed or endorsed.

[Verification](verification.md) records the checks and known limits. The v0.1.0 release assets remain unchanged; this gallery was added to the main branch after that release.

