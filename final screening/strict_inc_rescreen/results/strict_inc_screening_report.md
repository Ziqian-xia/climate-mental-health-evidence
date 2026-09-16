# Strict reassessment of the 802 broad-screen INCLUDE records

Date: 2026-09-16

Criteria: `strict-inc-v1.0`

Models: `gpt-5.6-sol` and `deepseek-v4-pro`

## Purpose

This stage applies the stricter causal meta-analysis criteria to all 802 records retained by the
broad screen. It does not overwrite the published broad-screen result. `META_ELIGIBLE` and
`FULLTEXT_REVIEW` both advance to full-text assessment; neither is a final meta-analysis inclusion.

## Model results

| Decision | GPT-5.6 | DeepSeek V4 Pro |
|---|---:|---:|
| META_ELIGIBLE | 139 | 160 |
| FULLTEXT_REVIEW | 336 | 307 |
| NARRATIVE_ONLY | 292 | 306 |
| EXCLUDE | 35 | 29 |
| Total | 802 | 802 |

DeepSeek V4 Pro used high reasoning and returned 802 valid records with no final errors. It used
1,365,009 input tokens and 1,990,396 output tokens. Based on the official price at run time, the
estimated off-peak cost is about $4.84 if all input tokens were cache misses. Actual billing may be
lower if input caching applied. Pricing source: https://api-docs.deepseek.com/quick_start/pricing/

## Agreement

- Exact four-category agreement: 82.7%.
- Four-category Cohen's kappa: 0.739.
- Agreement on advance versus do not advance: 92.0%.
- Binary Cohen's kappa: 0.835.
- Exact four-category disagreements: 139.
- Cross-boundary disagreements: 64.
- Both models advance: 439.
- Both models do not advance: 299.
- At least one model advances: 503.
- Both models label `META_ELIGIBLE`: 124.

The two models are not a human gold standard. Agreement measures reproducibility between models,
not sensitivity or specificity against true study eligibility.

## DeepSeek results by topic

| Topic | META_ELIGIBLE | FULLTEXT_REVIEW | NARRATIVE_ONLY | EXCLUDE | Total |
|---|---:|---:|---:|---:|---:|
| Temperature | 126 | 161 | 22 | 7 | 316 |
| Cyclone | 9 | 64 | 126 | 10 | 209 |
| Flood | 10 | 34 | 105 | 7 | 156 |
| Wildfire | 6 | 21 | 41 | 1 | 69 |
| Drought | 6 | 9 | 2 | 0 | 17 |
| Multiple | 3 | 18 | 10 | 3 | 34 |
| Unclear | 0 | 0 | 0 | 1 | 1 |

The event topics contain many single-wave post-event and cross-sectional studies, so the stricter
counterfactual requirement moves a large share to `NARRATIVE_ONLY`. Temperature studies more often
use time-series, case-crossover or panel designs and therefore advance more often.

## Recommended next step

1. Retrieve full text for the 503-record union where at least one model advances. This protects
   recall while reducing the 802-record pool by 299.
2. Start extraction with the 124 records both models label `META_ELIGIBLE`.
3. Human-adjudicate the 64 cross-boundary disagreements before excluding any of them from full-text
   review. These are the highest-priority validation records.
4. Use the remaining 315 consensus-advance records for ordinary full-text eligibility assessment.
5. Retain `NARRATIVE_ONLY` records for the evidence map if that output remains in scope.
6. Randomly audit a preregistered sample of the 299 consensus non-advance records. Model agreement
   alone cannot estimate the false-negative rate.

The API key used for this run was not written to any project file. Because it was disclosed in chat,
it should be revoked and replaced.
