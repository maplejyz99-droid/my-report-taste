# My Report Taste

A Codex skill for organizing reports through content tasks, evidence and density, then visual choices—with review and bilingual speaker scripts.

[中文](README.md) · [Style gallery](#style-gallery) · [Installation](docs/installation.md) · [Example](examples/synthetic-study/README.md)

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

### 01 · Bright blue research update

`author-light` — Bright blue and light editorial surfaces; this example uses changes and a comparison table.

![Bright blue research update: original synthetic content-page preview](examples/style-gallery/pages/author-light.png)

> Use $my-report-taste and borrow only the `author-light` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 02 · Wine academic report

`academic-oral-wine` — Wine headings, formal evidence, and visible sources. The full bundle also includes NAR-001; this is a result-page example.

![Wine academic report: original synthetic content-page preview](examples/style-gallery/pages/academic-oral-wine.png)

> Use $my-report-taste and borrow only the `academic-oral-wine` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 03 · Experiment and performance review

`experiment-review` — Large evidence areas and direct data labels; the material determines chart types and metric counts.

![Experiment and performance review: original synthetic content-page preview](examples/style-gallery/pages/experiment-review.png)

> Use $my-report-taste and borrow only the `experiment-review` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 04 · Light technical architecture

`technical-review-light` — Light grids, readable node hierarchy, and connectors; use an architecture diagram only when the task needs it.

![Light technical architecture: original synthetic content-page preview](examples/style-gallery/pages/technical-review-light.png)

> Use $my-report-taste and borrow only the `technical-review-light` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 05 · Dark technical review

`technical-review-dark` — Quiet petroleum-blue backgrounds, shared surfaces, and continuous tables; no decision-report structure is implied.

![Dark technical review: original synthetic content-page preview](examples/style-gallery/pages/technical-review-dark.png)

> Use $my-report-taste and borrow only the `technical-review-dark` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 06 · Green project update

`project-green` — White content pages with green navigation and focal points; no milestone or next-step section is required.

![Green project update: original synthetic content-page preview](examples/style-gallery/pages/project-green.png)

> Use $my-report-taste and borrow only the `project-green` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 07 · Blue and sand project summary

`project-summary-dual-semantics` — Blue primary evidence and a small sand accent when a second semantic role exists; no forced present/future split.

![Blue and sand project summary: original synthetic content-page preview](examples/style-gallery/pages/project-summary-dual-semantics.png)

> Use $my-report-taste and borrow only the `project-summary-dual-semantics` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 08 · Neutral evidence review

`neutral-evidence-review` — Neutral framing and readable source material; no company-introduction or recruiting narrative is implied.

![Neutral evidence review: original synthetic content-page preview](examples/style-gallery/pages/neutral-evidence-review.png)

> Use $my-report-taste and borrow only the `neutral-evidence-review` presentation rules. Follow the current content task and preserve the established argument and evidence.

### 09 · Dense reading report

`dense-reading-report` — Reading-oriented density, shown at an A-series landscape ratio; not a projection default or an automatic format change.

![Dense reading report: original synthetic content-page preview](examples/style-gallery/pages/dense-reading-report.png)

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
