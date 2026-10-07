# Style gallery verification

Scope: nine independent single-page preset demonstrations for the Chinese and English README. The user explicitly approved one image per preset. This is an addition to the public documentation, not a change to personal preferences or a replacement of the v0.1.0 release.

## Sources and scope

- Numerical source: `candidate-filter-fixture-v1`, shared with the existing synthetic study.
- Three source rows remain unchanged: baseline 84.0% / 120 ms, compact 86.0% / 85 ms, large 86.5% / 160 ms.
- Differences: compact versus baseline is +2.0 percentage points and 35 ms less (29.2% relative reduction). Large versus compact is +0.5 percentage points and 75 ms more.
- All pages visibly identify the data as synthetic. The project-review sequence is explicitly illustrative.
- Each preset has its own plan, native editable PPTX and PNG. A one-page gallery cannot validate research narrative, chapter transitions or full-deck density rhythm.

## Inspection record

Initial renders revealed reversed architecture arrows, default black table borders and overlapping chart ticks. The builder was corrected: destination-side arrowheads, visually quiet table borders, and a column chart with an explicit value axis. The source citation was moved away from the footer rule. The revised summary title avoids treating invented values as real deployment evidence.

## Final local checks — 2026-10-07

- All nine editable PPTX files passed the artifact finalizer's integrity, import, layout and font-policy checks. The final PNGs were exported after reimporting those finalized PPTX files, rather than from a separate mockup.
- All nine final PNGs were inspected individually. No visible clipping, label collision or wrong-way process arrow remained in those renders.
- The library's 45 unit tests and the distribution/gallery's 15 tests passed (60 total). Gallery tests cover all nine presets in both READMEs, PNG dimensions, plan-to-PPTX agreement, five native tables, the native chart's source values and embedded workbook, synthetic labels, and the three directional connectors.
- Strict library validation passed: 35 entries, 11 routes, 31 gates, no warnings.
- Strict UI color checks passed for all nine PNGs. This is a hue-budget check, not a guarantee of visual quality.
- The public-distribution scanner passed for 121 selected files, including local relative links and bounded privacy patterns. It does not establish complete secret detection, legal clearance or remote-link availability.

No claim of Windows, PowerPoint, Google Slides, printer, projector or live presentation testing is made. Editing in another application can change font metrics and therefore needs its own inspection. The gallery does not validate a complete oral narrative or cross-page rhythm.
