# Speaker script — English

Version: synthetic-study v1; 4 main slides, 1 backup. All values are invented. Target: 3 minutes including pauses; this is a budget, not a rehearsal result.

## S01 — Candidate filtering: accuracy and latency

- role: main
- target_seconds: 35

### Script

This example compares accuracy and latency for a retrieval pipeline. The question is whether selecting candidates before ranking changes the balance between answer quality and time per query. All numbers in this talk are synthetic teaching values. They are not results from a real benchmark, and they do not support a deployment recommendation.

### Transition

First, let us locate the part of the pipeline that changes.

### Short script

We compare accuracy and latency for candidate filtering. These are synthetic teaching values, not a real benchmark.

### Short transition

Here is the pipeline.

## S02 — A filter selects candidates before ranking

- role: main
- target_seconds: 45

### Script

A query reaches a candidate filter before the ranker. The filter selects a smaller set, and the ranker orders only the items it receives. The top ranked item becomes the result. This gives the filter an important responsibility: once a useful item is omitted, the downstream ranker cannot recover it. This diagram explains the conceptual sequence. It does not establish how much work is saved, or whether recall remains acceptable.

### Transition

We therefore need to look at both metrics rather than latency alone.

### Short script

The filter selects candidates; the ranker orders them. Filtering can remove useful items, so the diagram alone does not establish a benefit.

### Short transition

Let us compare both metrics.

## S03 — The compact setting reaches 86.0% at 85 ms

- role: main
- target_seconds: 60

### Script

The table includes every setting in the fixture. The baseline has 84.0 percent accuracy and takes 120 milliseconds per query. The compact filter reaches 86.0 percent at 85 milliseconds. That is an increase of 2.0 percentage points and a reduction of 35 milliseconds relative to the baseline. The large filter reaches 86.5 percent but takes 160 milliseconds. It has the highest accuracy of the three, but also the highest latency. None of these invented differences has an uncertainty estimate.

### Transition

That last limitation matters when deciding what the comparison can support.

### Short script

The compact filter reaches 86.0 percent at 85 milliseconds: 2.0 percentage points higher and 35 milliseconds faster than the baseline. The large filter is more accurate but slower.

### Short transition

The values still lack uncertainty estimates.

## S04 — The comparison still needs repeated measurements

- role: main
- target_seconds: 40

### Script

In this fixture, the compact setting has a favorable accuracy and latency comparison against the baseline. A real study would need repeated measurements, workload and hardware variation, memory use, and candidate recall. Those measurements are absent here. The useful takeaway is the structure of the comparison: show all settings, preserve the units, and keep the claim within the evidence. The synthetic values establish no real deployment advantage.

### Transition

Thank you. The backup slide contains the metric definitions and calculations.

### Short script

A real study still needs repeatability, workload variation, memory use, and candidate recall. The synthetic values establish no deployment advantage.

### Short transition

Thank you. The calculations are in the backup slide.

## S05 — Metric definitions and arithmetic

- role: backup

### Answer

Accuracy is the percentage of correct top results. The difference between 86.0 and 84.0 percent is 2.0 percentage points, not a two percent relative increase. Latency is milliseconds per query. The absolute reduction is 35 milliseconds; dividing that by the baseline of 120 milliseconds gives about 29.2 percent. All calculations use the synthetic fixture.
