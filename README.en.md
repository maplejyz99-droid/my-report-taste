# My Report Taste

A Codex skill for organizing reports through content tasks, evidence and density, then visual choices—with review and bilingual speaker scripts.

[中文](README.md) · [Style gallery](#style-gallery) · [Palette IDs](#reading-the-palette-ids) · [Installation](docs/installation.md) · [Example](examples/synthetic-study/README.md)

## What it does

- Organizes claims and evidence before choosing page layouts.
- Respects supplied conference templates and the current user's preferences.
- Keeps original readable figures, tables, and equations instead of redrawing everything.
- Checks slide plans and revisions without silently changing the intended conclusion.
- Separates spoken scripts from presenter notes and estimates English and Chinese timing independently.

This is a workflow and validation layer, not a bundled slide-rendering engine or a guarantee of scientific correctness or visual quality. It does not upload your files automatically.

## Install

Download this repository, then run with Python 3.10+:

```bash
git clone https://github.com/maplejyz99-droid/my-report-taste.git
cd my-report-taste
python3 tools/install.py
```

The installer copies the skill into `~/.agents/skills/my-report-taste`. Existing installations are preserved. For a project-specific location, use `--dest /path/to/project/.agents/skills`. Invoke `$my-report-taste` in Codex; restart if the new skill does not appear.

Example request:

> Use $my-report-taste to plan an English conference talk from this paper. Preserve the supplied conference template. Account for the key figures and tables before making slides.

> Use $my-report-taste to prepare English and Chinese scripts for this exact deck version. Exclude backup slides from the talk time and write an actual shorter version.

## Three content tasks, not nine story templates

Choose the communication task before the visual treatment:

| Task | Main question |
|---|---|
| Explain research or technology (`explain`) | What is being studied, how does it work, and what does the evidence support? |
| Report progress or results (`progress`) | What has the new evidence changed, and what remains unresolved? |
| Compare options or support a choice (`compare`) | What are the benefits, costs, and constraints under comparable conditions? |

Comparison does not imply recommendation. Give a conditional preference only when the user asks for a choice. A report can have one primary task and use another locally; none imposes a fixed outline, page count, three-bullet pattern, or future-work section.

Then choose evidence and density for the material and viewing distance, and apply the supplied template or an optional appearance. Green should not add milestones; wine should not invent a research agenda.

> Use $my-report-taste. The group already knows the background. Focus on what these new results changed. Borrow the project-green appearance without adding milestones or deployment advice.

> Use $my-report-taste. Compare the options without choosing a winner. Keep the existing content and borrow only the academic-oral-wine appearance.

For automation, `--content` selects the task, `--visual` borrows presentation only, `--preset` selects a full bundle, and `--card` selects individual dimensions. [Content rules](skills/my-report-taste/references/content-modes.md) · [Routing and compatibility](skills/my-report-taste/references/routing.md)

Less templated writing starts with editing: concrete evidence, less repeated background, and proportionate attention to difficult points. It is not a word blacklist or a requirement to change every layout. The checks do not guarantee that generated content is free of an “AI-written” feel.

## Content before styling

The same rough notes contain Baseline 84% / 120 ms, Compact 86% / 85 ms and Large 86.5% / 160 ms. The organized result page retains every setting, unit and synthetic-data disclosure, separates percentage points from relative change, and keeps the unmeasured conditions visible.

The [before/after editing example](examples/synthetic-study/editing-case.md) also states what a request to enlarge the table should preserve. It is an authored teaching example, not an observed skill-on/off experiment.

![Synthetic result page with the complete accuracy and latency comparison](examples/synthetic-study/preview.png)

[Five-page PPTX, plan and bilingual scripts](examples/synthetic-study/README.md) · [Python-only HTML/Markdown rebuild](examples/portable-report/README.md) · [Task-level evaluation protocol and limits](docs/evaluation.md)

## Style gallery

The 35 text-only cards form an optional reference library. Their approval labels describe the author's evaluations, not your preferences. Supplied templates and your current request take precedence.

These **nine opt-in presentation bundles each have one representative content page**. They retain differences in layout, density, evidence presentation, and color, but do not define nine independent content routes. Every preview comes from an actual editable page using the same original synthetic fixture. Click an image for full resolution.

A single page illustrates layout, not a complete narrative or cross-page rhythm. Its sections are example choices, not requirements. The full wine bundle combines `NAR-001 + GRD-010 + CLR-010`; presentation-only selection uses `GRD-010 + CLR-010` without the narrative card. The reading preview keeps its own ratio; the actual output medium still follows the task.

[Preset definitions](skills/my-report-taste/references/author-presets.md) · [Images, editable pages, and builder source](examples/style-gallery/README.md)

### Reading the palette IDs

`CLR` identifies a color card, `GRD` a layout/density card, and `NAR` a narrative card. Names such as `author-light` identify bundles. These are not rankings or nine distinct palettes: 01, 03, and 04 share `CLR-002`; 09 has no fixed palette.

Each preview below includes **key HEX values and their roles from the color card**. Follow its ID for the full shade range and rules. These are approximate reconstruction recipes, not official third-party brand tokens or a promise of pixel equality with the previews; individual pages select shades by role. Equal-sized swatches do not imply equal page-area proportions.

To select color without changing content or layout:

> Use $my-report-taste with only the CLR-006 palette. Keep the content, page order, and layout unchanged. Use an exception color only for a real risk.

### 01 · Bright blue research update

`author-light` — Bright blue and light editorial surfaces; this example uses changes and a comparison table.

![Bright blue research update: original synthetic content-page preview](examples/style-gallery/pages/author-light.png)

Palette: [CLR-002 · Bright blue](skills/my-report-taste/references/CLR-002.md)

![CLR-002: blue hierarchy, cool canvas, and dark gray body text](examples/style-gallery/palettes/CLR-002.svg)

- Primary `#0B6FCA`; dark `#075CA8`; light `#91C5F0`; pale fill `#DDE9F4`.
- Canvas `#F7F7F7`; surface `#FFFFFF`; body `#343A40`; muted `#6B737A`; line `#DCE3E8`.

Coral `#FE7265` is reserved for real risks/exceptions, not ordinary method categories.

> Use $my-report-taste and borrow only the `author-light` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 02 · Wine academic report

`academic-oral-wine` — Wine headings, formal evidence, and visible sources. The full bundle also includes NAR-001; this is a result-page example.

![Wine academic report: original synthetic content-page preview](examples/style-gallery/pages/academic-oral-wine.png)

Palette: [CLR-010 · Academic wine](skills/my-report-taste/references/CLR-010.md)

![CLR-010: wine title, pale wine fill, citation blue, and cool white surfaces](examples/style-gallery/palettes/CLR-010.svg)

- Title `#7D1E2F`; emphasis `#A12746`; pale wine `#FAE9EC`; citations/links `#0077CC`.
- Canvas `#FFFFFF`; surface `#F3F4F6`; body `#1F2430`; muted `#666A73`; line `#D9DCE3`.

Citation blue is not decorative. Purple/navy branch colors require a real semantic distinction; see the full card for values.

> Use $my-report-taste and borrow only the `academic-oral-wine` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 03 · Experiment and performance review

`experiment-review` — Large evidence areas and direct data labels; the material determines chart types and metric counts.

![Experiment and performance review: original synthetic content-page preview](examples/style-gallery/pages/experiment-review.png)

Palette: [CLR-002 · Bright blue](skills/my-report-taste/references/CLR-002.md), shared with 01. The evidence area and data labels distinguish this bundle, not a different palette.

![Shared CLR-002 palette: primary blue for current values and light blue for secondary series](examples/style-gallery/palettes/CLR-002.svg)

- Current value `#0B6FCA`; dark `#075CA8`; secondary series `#91C5F0`; pale fill `#DDE9F4`.
- Canvas `#F7F7F7`; surface `#FFFFFF`; body `#343A40`; muted `#6B737A`; line `#DCE3E8`.

Use `#FE7265` only for exceptions; normal comparisons do not need additional colored series.

> Use $my-report-taste and borrow only the `experiment-review` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 04 · Light technical architecture

`technical-review-light` — Light grids, readable node hierarchy, and connectors; use an architecture diagram only when the task needs it.

![Light technical architecture: original synthetic content-page preview](examples/style-gallery/pages/technical-review-light.png)

Palette: [CLR-002 · Bright blue](skills/my-report-taste/references/CLR-002.md), shared with 01 and 03. Node hierarchy and connectors carry the structural differences.

![Shared CLR-002 palette: blue main path, pale nodes, and gray structural lines](examples/style-gallery/palettes/CLR-002.svg)

- Main path `#0B6FCA`; dark `#075CA8`; light `#91C5F0`; pale node fill `#DDE9F4`.
- Canvas `#F7F7F7`; surface `#FFFFFF`; body `#343A40`; muted `#6B737A`; line `#DCE3E8`.

Reserve `#FE7265` for actual risk nodes; do not assign a different hue to every module.

> Use $my-report-taste and borrow only the `technical-review-light` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 05 · Dark technical review

`technical-review-dark` — Quiet petroleum-blue backgrounds, shared surfaces, and continuous tables; no decision-report structure is implied.

![Dark technical review: original synthetic content-page preview](examples/style-gallery/pages/technical-review-dark.png)

Palette: [CLR-003 · Dark petroleum](skills/my-report-taste/references/CLR-003.md)

![CLR-003: petroleum field anchors, blue-gray surfaces, and light body text](examples/style-gallery/palettes/CLR-003.svg)

- Field anchors `#071F29` → `#173F4B`, edge `#01080C`; surfaces `#1B313A` / `#243B45`.
- Body `#E7E9EA`; muted `#A5AFB2`; line `#536168`; low-saturation focus `#C5CBC9`.

These anchors describe soft background depth, not a segmented gradient strip. Gold is not the default; `#C9A84A` is conditional on a clearly justified single focus.

> Use $my-report-taste and borrow only the `technical-review-dark` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 06 · Green project update

`project-green` — White content pages with green navigation and focal points; no milestone or next-step section is required.

![Green project update: original synthetic content-page preview](examples/style-gallery/pages/project-green.png)

Palette: [CLR-006 · Fresh green and mint](skills/my-report-taste/references/CLR-006.md)

![CLR-006: fresh green, mint shades, and a white canvas](examples/style-gallery/palettes/CLR-006.svg)

- Primary `#00A273`; dark `#008C63`; mid `#31B58D`; light `#9FDBCA`; mint fill `#E5F6F1`.
- Canvas `#FFFFFF`; body `#171A18`; muted `#5F6763`; line `#CEDBD6`.

Orange `#F07F3C` is for exceptions. Yellow `#F2D84C` requires a separate second metric in the same chart; neither is a routine decoration.

> Use $my-report-taste and borrow only the `project-green` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 07 · Blue and sand project summary

`project-summary-dual-semantics` — Blue primary evidence and a small sand accent when a second semantic role exists; no forced present/future split.

![Blue and sand project summary: original synthetic content-page preview](examples/style-gallery/pages/project-summary-dual-semantics.png)

Palette: [CLR-007 · Blue and sand](skills/my-report-taste/references/CLR-007.md)

![CLR-007: primary blue, optional sand for a second semantic role, and white canvas](examples/style-gallery/palettes/CLR-007.svg)

- Primary `#284B7D`; mid `#5F86B8`; pale `#CBD9ED`; second-role sand `#E8CDA9`.
- Canvas `#FFFFFF`; body `#252525`; muted `#8E8E8E`; line `#D8DADD`.

`Second role *` means **use sand only when a second semantic role exists**, not a 50/50 blue-gold split or a risk indicator. Muted gray is for short labels; recheck contrast for projection.

> Use $my-report-taste and borrow only the `project-summary-dual-semantics` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 08 · Neutral evidence review

`neutral-evidence-review` — Neutral framing and readable source material; no company-introduction or recruiting narrative is implied.

![Neutral evidence review: original synthetic content-page preview](examples/style-gallery/pages/neutral-evidence-review.png)

Palette: [CLR-008 · Neutral](skills/my-report-taste/references/CLR-008.md)

![CLR-008: near-black, dark gray, white, and cool neutral gray](examples/style-gallery/palettes/CLR-008.svg)

- Body/key series `#222222`; strong surface `#555555`; muted `#707070`.
- Canvas `#FFFFFF` or `#F7F7F7`; line `#D0D0D0`.

There is no fixed chromatic accent. Photos and screenshots retain their original colors without turning them into global theme colors.

> Use $my-report-taste and borrow only the `neutral-evidence-review` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 09 · Dense reading report

`dense-reading-report` — Reading-oriented density, shown at an A-series landscape ratio; not a projection default or an automatic format change.

![Dense reading report: original synthetic content-page preview](examples/style-gallery/pages/dense-reading-report.png)

Palette: **no fixed CLR ID**. This bundle selects `GRD-004 + OTH-003` without binding a palette. The swatches below record the [current example builder](examples/style-gallery/build_gallery.mjs), not a new preset or `CLR-010`.

![Dense reading report example colors, with no fixed CLR ID](examples/style-gallery/palettes/dense-example.svg)

- Example emphasis `#96324A`; pale fill `#FAEFF2`; canvas `#FFFFFF`.
- Body `#27242A`; muted `#656068`; line `#E2DADF`.

Choose another color card or retain the user's/official template colors as needed; color does not determine reading density.

> Use $my-report-taste and borrow only the `dense-reading-report` presentation rules. Follow the current content task and preserve the established argument and evidence.

Store your preferences in a project `.report-taste/profile.md` or an installed skill's `references/local-profile.md`; these files are not distributed.

## Validate

```bash
python3 skills/my-report-taste/scripts/doctor.py
python3 skills/my-report-taste/scripts/library.py route --content explain --template
python3 skills/my-report-taste/scripts/library.py route --content progress --visual author-light --template-state absent
python3 skills/my-report-taste/scripts/library.py route --content compare --visual technical-review-dark --template-state absent
python3 skills/my-report-taste/scripts/library.py route --card NAR-001 --template
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_public_release.py
```

Core checks use the standard library. Image color checks require Pillow. Optional PPTX/PDF conversion and inspection require external rendering tools; see [installation and limitations](docs/installation.md). Automatic checks do not replace source review, rendered-page inspection, translation review, or rehearsal.

Free-text routing returns inactive candidates. Resolve intent first, then pass `--content` and, if needed, `--visual`, `--preset`, or repeated `--card` arguments. The nine existing preset IDs remain supported. Template state is explicitly `provided`, `absent` or `unknown`; `--template` means `provided`. Parameters record caller declarations, not authorization. See [routing migration](skills/my-report-taste/references/routing.md) and [0.3.0 changes and local validation](docs/release-notes-v0.3.0.md).

## License

Project code, original documentation, and synthetic examples are MIT-licensed. Third-party source decks, screenshots, logos, fonts, and private feedback are not bundled or relicensed. See [notices](THIRD_PARTY_NOTICES.md).
