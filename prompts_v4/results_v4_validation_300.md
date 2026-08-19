# v4 validation on the 300-paper human-review set

## Run specification

- **Model:** `deepseek-v4-flash`
- **Prompt set:** v4 router `00` plus hazard modules `01`–`05`
- **Criteria:** outcome discipline, within-unit design discipline, and the v4 temperature-setting requirement
- **Input:** `screening_v3_pipeline_300_BLINDED_for_human_review (1).xlsx`
- **Sample:** 300 unique papers, represented by 600 labeled rows across the Jacob and Tony sheets
- **Human labels:** the existing `human_decision` values were not modified
- **Run result:** 300/300 papers screened; 0 API or parsing errors

The pairwise workbook contains one AI decision per unique paper. That decision was copied to both
assigned human-rater rows in the output workbook.

## AI decision distribution

| AI decision | n | Share |
|---|---:|---:|
| EXCLUDE | 272 | 90.7% |
| REVIEW | 20 | 6.7% |
| INCLUDE | 8 | 2.7% |
| **Total** | **300** | **100.0%** |

## Human decision distribution

| Rater | EXCLUDE | REVIEW-equivalent* | INCLUDE | Total |
|---|---:|---:|---:|---:|
| Jacob | 270 | 22 | 8 | 300 |
| Tony | 274 | 11 | 15 | 300 |

\* Human `MAYBE` was mapped to `REVIEW` for agreement analysis, so both sources use the same
three categories: `EXCLUDE`, `REVIEW`, and `INCLUDE`.

## Cohen's kappa

Kappa was calculated as:

`κ = (observed agreement − expected agreement) / (1 − expected agreement)`

| Comparison | n | Exact agreements | Observed agreement | Cohen's κ |
|---|---:|---:|---:|---:|
| AI vs Jacob | 300 | 282 | 94.0% | **0.664** |
| AI vs Tony | 300 | 284 | 94.7% | **0.683** |
| **AI vs pooled human labels** | **600** | **566** | **94.3%** | **0.673** |
| Human vs human (benchmark) | 300 | 276 | 92.0% | **0.540** |

The pooled AI–human value, **κ = 0.673**, is the primary alignment result. It treats the two
human labels for each paper as two independent AI–human comparison pairs; it does not collapse
disagreements into an inferred consensus label.

## Reproducibility files

The completed workbook and raw per-record JSONL provenance log were produced outside this prompt
folder in the pilot results directory:

- `pilot_screening_v3/pilot_screening_v3/results/screening_v4_flash_300_ai.xlsx`
- `pilot_screening_v3/pilot_screening_v3/results/screening_v4_flash_300_records.jsonl`

The JSONL contains the model, criteria version, router output, module outputs, aggregated decision,
and timing for every unique paper. The workbook contains the human labels plus `AI Suggestion (v4)`
and `AI Reason (v4)` columns.
