# My Report Taste

A Codex skill for building your own presentation preferences: narrative, evidence, density, visual choices, review, and bilingual speaker scripts.

[中文](README.md) · [Installation](docs/installation.md) · [Example](examples/synthetic-study/README.md)

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

## Neutral by default

The 35 text-only reference cards are an optional example library. Their approval labels describe the library author's evaluations, not your preferences. No visual preset is automatically selected for a generic research update or academic oral.

Select `author-light` explicitly for the author's blue research preset, or `NAR-001` for the academic narrative preset. Supplied templates take precedence. Store personal preferences in a project `.report-taste/profile.md` or an installed skill's `references/local-profile.md`.

## Validate

```bash
python3 skills/my-report-taste/scripts/library.py validate --strict
python3 -m unittest discover -s skills/my-report-taste/tests -p 'test_*.py'
python3 -m unittest discover -s tests -p 'test_*.py'
python3 tools/check_public_release.py
```

Core checks use the standard library. Image color checks require Pillow. Optional PPTX/PDF conversion and inspection require external rendering tools; see [installation and limitations](docs/installation.md). Automatic checks do not replace source review, rendered-page inspection, translation review, or rehearsal.

The [synthetic example](examples/synthetic-study/README.md) includes input data, a brief, a slide plan, presentation output, two speaker scripts, and verification notes. Its numbers are educational fixtures, not research results.

## License

Project code, original documentation, and synthetic examples are MIT-licensed. Third-party source decks, screenshots, logos, fonts, and private feedback are not bundled or relicensed. See [notices](THIRD_PARTY_NOTICES.md).
