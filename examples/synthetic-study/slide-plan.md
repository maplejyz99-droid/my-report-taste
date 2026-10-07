---
stance_mode: factual
primary_recommendation: none
user_decision_status: not_required
---

# Candidate filtering — synthetic study

事实源：[source.json](source.json)。成品页 ID 固定，备注包含身份标记。主讲预算共 180 秒，备份页不计入。蓝色为本示例主动选择，不是公开 skill 默认。

## Communication job

让读者看清准确率与延迟必须同时比较，以及合成数值能支持的范围。

## Source of truth

`source.json`，ID 为 `candidate-filter-fixture-v1`。数值为作者编写的教学数据，不属于真实研究结果。

## Scope

5 页，其中 4 页主讲、1 页备份；不补造实验设置，不声称部署优势，不含动画。

## Taste

本例选择 `author-light` 的白底、蓝色强调和内容驱动布局，不复用任何品牌资产。

## S01

- role: main
- title: Candidate filtering: accuracy and latency
- claim: The comparison concerns accuracy and time per query; all values are synthetic.
- evidence: source.json question, metrics and synthetic warning.
- next: Explain which stage changes between settings.
- page_role: opening
- density_mode: concise

## S02

- role: main
- title: A filter selects candidates before ranking
- claim: The filter narrows what the ranker receives; omitted candidates cannot be recovered by ranking.
- evidence: source.json method; a conceptual linear flow, not a measured mechanism diagram.
- next: Compare all three settings on both metrics.
- page_role: mechanism
- density_mode: diagram-led

## S03

- role: main
- title: The compact setting reaches 86.0% at 85 ms
- claim: Relative to the baseline, the compact setting adds 2.0 percentage points and uses 35 ms less per query in this fixture.
- evidence: All three source.json rows; direct subtraction only; no statistical claim.
- next: Separate the observed fixture comparison from unmeasured deployment conditions.
- page_role: result
- density_mode: evidence-led

## S04

- role: main
- title: The comparison still needs repeated measurements
- claim: These invented values establish no deployment advantage; repeatability, workload variation, memory and candidate recall remain unmeasured.
- evidence: source.json unmeasured and exclusions.
- next: End the main talk; use S05 only if asked about units or arithmetic.
- page_role: conclusion
- density_mode: text-led

## S05

- role: backup
- title: Metric definitions and arithmetic
- claim: Accuracy differences use percentage points; latency differences use milliseconds per query.
- evidence: 86.0 minus 84.0 equals 2.0 percentage points; 120 minus 85 equals 35 ms; 35 divided by 120 is about 29.2%.
- next: Return to S03 for the complete comparison.
- page_role: backup
- density_mode: reference
