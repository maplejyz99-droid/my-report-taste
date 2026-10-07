# Controlled comparison verification

## Scope and baseline

The user approved merging the three blue gallery entries, moving independent reading outside theme selection, preserving color cards, and comparing the remaining candidates with the same result and mechanism pages. This changes documentation navigation and adds examples. It does not remove old IDs, change routing, replace private preferences, or overwrite the nine original PNG/PPTX examples.

- Baseline: the original nine-page gallery and plans remain untouched in the parent directory.
- New examples: six pairs, two slides each, with stable IDs S01 and S02. No cover or animation.
- Display grouping: author-light, experiment-review and technical-review-light share one entry. Their routes and specialist rules remain intact.
- Dense-reading-report stays available separately, with no fixed CLR card.
- No winner or default was selected. Six candidates do not establish six independent themes.

## Source and plan comparison

The [source fixture](../../synthetic-study/source.json) is synthetic. Required copy comes from [content.json](content.json). All candidates retain baseline 84.0% / 120 ms, compact 86.0% / 85 ms and large 86.5% / 160 ms. The highlighted comparison is compact versus baseline: 2.0 percentage points higher accuracy and 35 ms lower latency. Both pages visibly disclose the synthetic source.

All six plans have factual stance, no recommendation, and no user-decision requirement. The title chain is identical: Compact filtering improves both fixture metrics; Candidate filtering before ranking. The old single-page plans remain historical examples rather than being rewritten to pretend the new controlled comparison was the original intent.

## Checks actually performed

- All six plans passed preflight and plan-to-final-PPTX checks, including S01/S02 and main-role notes.
- Six finalized PPTX files passed structural package, geometry, declared Arial font policy, native-table and first-party import checks. These are not native Office rendering tests.
- All twelve final pages were rendered after reimporting finalized PPTX. Eleven images match the individually inspected earlier render byte-for-byte; the changed dark mechanism page was inspected again.
- Initial dark mechanism explanations were too high relative to their nodes. They now align with Candidate filter and Ranker. No remaining clipping, text collision or reversed connector was observed.
- Strict UI hue-budget checks passed for all twelve pages. This does not score visual quality or establish theme distinctiveness.
- The six paired previews combine the exact final result and mechanism renders without cropping. Full-size images and editable files remain linked separately.
- Repository regression tests cover bilingual navigation, the six candidate groups, every retained legacy ID, palette mapping, exact required copy, all native table values/units, four mechanism labels, three destination arrowheads, slide identity and PNG dimensions.
- Full local regression: 71 skill tests and 31 repository tests passed (102 total). Strict library validation passed with 35 cards, 12 routes, 31 gates and zero warnings. The bounded distribution/link/privacy-pattern scan passed for 185 selected files; it does not prove complete secret detection or legal clearance.

## Design findings and limits

Light navigation still overlaps with light editorial. Rail evidence and academic evidence also share a broad evidence-plus-explanation pattern. Neutral styling changes emphasis more than content grammar. These observations remain visible in the documentation; no decorative features were added solely to inflate the number of themes.

The two-page fixture cannot validate image-led layouts, formulas, chapter pages, full-deck rhythm, presentation comprehension or real research use. Native PowerPoint, Google Slides, projector, printer and full GitHub browser-render checks were not run. Font files are not bundled. Original theme cards are approximate reconstruction guidance, not official third-party brand assets.
