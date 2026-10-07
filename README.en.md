# My Report Taste

A Codex skill for building your own presentation preferences: narrative, evidence, density, visual choices, review, and bilingual speaker scripts.

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

## Content before styling

The same rough notes contain Baseline 84% / 120 ms, Compact 86% / 85 ms and Large 86.5% / 160 ms. The organized result page retains every setting, unit and synthetic-data disclosure, separates percentage points from relative change, and keeps the unmeasured conditions visible.

The [before/after editing example](examples/synthetic-study/editing-case.md) also states what a request to enlarge the table should preserve. It is an authored teaching example, not an observed skill-on/off experiment.

![Synthetic result page with the complete accuracy and latency comparison](examples/synthetic-study/preview.png)

[Five-page PPTX, plan and bilingual scripts](examples/synthetic-study/README.md) · [Python-only HTML/Markdown rebuild](examples/portable-report/README.md) · [Task-level evaluation protocol and limits](docs/evaluation.md)

## Style gallery

The 35 text-only cards form an optional reference library. Their approval labels describe the author's evaluations, not your preferences. Supplied templates and your current request take precedence.

These **nine opt-in presets each have one representative content page**. They combine audience, content organization, density, and visual rules, rather than offering nine unrelated color schemes. Every preview comes from an actual editable page using the same original synthetic fixture. Click an image for full resolution.

A single page illustrates layout, not a complete narrative or cross-page rhythm. The wine academic preset combines `NAR-001 + GRD-010 + CLR-010`; NAR-001 is not merely a color theme. The reading report keeps its own page ratio.

[Preset definitions](skills/my-report-taste/references/author-presets.md) · [Images, editable pages, and builder source](examples/style-gallery/README.md)

### 01 · Bright blue research update

`author-light` — Research updates: highlight the main changes, then retain the complete comparison.

![Bright blue research update: original synthetic content-page preview](examples/style-gallery/pages/author-light.png)

> Use $my-report-taste with the `author-light` preset. Plan the content before creating the pages.

### 02 · Wine academic report

`academic-oral-wine` — Academic talks: wine headings, formal evidence, and visible provenance. This image demonstrates a result page only.

![Wine academic report: original synthetic content-page preview](examples/style-gallery/pages/academic-oral-wine.png)

> Use $my-report-taste with the `academic-oral-wine` preset. Plan the content before creating the pages.

### 03 · Experiment and performance review

`experiment-review` — Performance reviews: devote the canvas to a native chart, direct values, and an explicit comparison.

![Experiment and performance review: original synthetic content-page preview](examples/style-gallery/pages/experiment-review.png)

> Use $my-report-taste with the `experiment-review` preset. Plan the content before creating the pages.

### 04 · Light technical architecture

`technical-review-light` — Technical explanations: show input and output with a clear path and one emphasized stage.

![Light technical architecture: original synthetic content-page preview](examples/style-gallery/pages/technical-review-light.png)

> Use $my-report-taste with the `technical-review-light` preset. Plan the content before creating the pages.

### 05 · Dark technical review

`technical-review-dark` — Short technical reviews: a quiet petroleum-blue background and a continuous comparison table.

![Dark technical review: original synthetic content-page preview](examples/style-gallery/pages/technical-review-dark.png)

> Use $my-report-taste with the `technical-review-dark` preset. Plan the content before creating the pages.

### 06 · Green project update

`project-green` — Project updates: white content pages and a green focal point for the next milestone.

![Green project update: original synthetic content-page preview](examples/style-gallery/pages/project-green.png)

> Use $my-report-taste with the `project-green` preset. Plan the content before creating the pages.

### 07 · Blue and sand project summary

`project-summary-dual-semantics` — Project summaries: blue for existing evidence, a small sand accent for the next evidence needed.

![Blue and sand project summary: original synthetic content-page preview](examples/style-gallery/pages/project-summary-dual-semantics.png)

> Use $my-report-taste with the `project-summary-dual-semantics` preset. Plan the content before creating the pages.

### 08 · Neutral evidence review

`neutral-evidence-review` — Source and evidence reviews: neutral framing gives the source material priority.

![Neutral evidence review: original synthetic content-page preview](examples/style-gallery/pages/neutral-evidence-review.png)

> Use $my-report-taste with the `neutral-evidence-review` preset. Plan the content before creating the pages.

### 09 · Dense reading report

`dense-reading-report` — Independent reading: an A-series landscape ratio keeps data, mechanism, arithmetic, and limits together. Not the default for distant projection.

![Dense reading report: original synthetic content-page preview](examples/style-gallery/pages/dense-reading-report.png)

> Use $my-report-taste with the `dense-reading-report` preset. Plan the content before creating the pages.

Store your preferences in a project `.report-taste/profile.md` or an installed skill's `references/local-profile.md`; these files are not distributed.

## Validate

```bash
python3 skills/my-report-taste/scripts/doctor.py
python3 skills/my-report-taste/scripts/library.py route "research update" --preset author-light --template-state absent
python3 skills/my-report-taste/scripts/library.py route --card NAR-001 --template
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_public_release.py
```

Core checks use the standard library. Image color checks require Pillow. Optional PPTX/PDF conversion and inspection require external rendering tools; see [installation and limitations](docs/installation.md). Automatic checks do not replace source review, rendered-page inspection, translation review, or rehearsal.

Free-text routing now returns inactive visual candidates. After resolving the user's intent, pass `--preset` for a full preset or repeat `--card` for individual dimensions. Template state is explicitly `provided`, `absent` or `unknown`; `--template` means `provided`. These parameters record caller declarations, not user authorization. See [routing migration](skills/my-report-taste/references/routing.md) and [0.2.0 source changes](docs/release-notes-v0.2.0.md).

## License

Project code, original documentation, and synthetic examples are MIT-licensed. Third-party source decks, screenshots, logos, fonts, and private feedback are not bundled or relicensed. See [notices](THIRD_PARTY_NOTICES.md).
