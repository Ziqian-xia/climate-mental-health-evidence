# Pilot title/abstract screening — v3, router + 5 hazard-module pipeline, 300-record sample

Uses the actual `prompts_v3/` router + 5 hazard-module pipeline (same prompts and aggregation
rule as `prompts_v3/screen_excel_v3_deepseek.py`: router assigns candidate hazard topics, each
topic's prompt returns INCLUDE/MAYBE/EXCLUDE + `review_flag`, then any INCLUDE → INCLUDE (or
REVIEW if that topic also flagged), any MAYBE/`review_flag` → REVIEW, else EXCLUDE) — but applied
to a **fresh random 300-record sample** of `merged_deduplicated_records.parquet` instead of the
fixed reviewer packet, so it isn't limited to the 150-record `packet150_v3` set already in the
repo.

This supersedes the earlier `pilot_screening_v3_singleprompt_300` attempt, which applied the v3
criteria in one combined prompt per record rather than through the router + module pipeline your
collaborator built. That approach was reverted.

## Files

```
pilot_screening_v3_router5category_300/
  README.md                                  <- this file
  scripts/
    screening_v3_pipeline_300.py             <- draws the sample, runs router+modules, writes the xlsx
  results/
    screening_v3_pipeline_300_results.xlsx   <- per-record decisions + run_info sheet
```

## Run parameters

- Sample size: 300, `RANDOM_SEED = 42` (same 300 records as the earlier single-prompt attempt,
  so the two are directly comparable on the same records — only the pipeline differs)
- Prompts: `prompts_v3/00_candidate_topics_prompt.md` (router) + `01`–`05` hazard modules, loaded
  from a local clone of this repo (each carries the `**Version: v3**` marker; the script asserts
  this before running)
- Model: `deepseek-v4-flash`, `temperature=0`
- Concurrency: 10 records in flight at once; within a record, the router call and its topic
  calls run sequentially (topic selection depends on the router's output)
- `max_tokens=3000` per call — see *Note on token budget* below

## Result

300/300 records resolved to a decision (1 record needed a manual retry at a higher token budget
after an initial truncation; folded into the totals below).

| Decision | n |
|---|---|
| EXCLUDE | 296 |
| REVIEW | 2 |
| INCLUDE | 2 |

## Note on token budget (worth knowing before extending this script)

The first full run used `max_tokens=800` (matching `screen_excel_v3_deepseek.py`'s default) and
produced empty or truncated router/module replies on 46/300 records (~15%). `deepseek-v4-flash`
spends part of its `max_tokens` budget on internal reasoning tokens before writing the final JSON
(confirmed via `usage.completion_tokens_details.reasoning_tokens` on a direct test call); at 800
tokens, longer or more ambiguous records routinely ran out of budget mid-reasoning. Raising
`max_tokens` to 3000 fixed all but one record; that last one (a pig/livestock husbandry study)
needed 6000 to complete, and resolved to `candidate_topics: []` → EXCLUDE, which is the correct
call. If running this at larger scale, consider raising `max_tokens` further or adding a
truncation-specific retry with an escalating budget.

## Output columns (`results/screening_v3_pipeline_300_results.xlsx`, sheet `screening_results`)

| Column | Meaning |
|---|---|
| `dedup_id` | Record ID (join key back to the corpus) |
| `title`, `year`, `journal`, `sources`, `abstract` | Record metadata, for reviewer context |
| `candidate_topics` | Hazard topic(s) the router assigned |
| `decision` | INCLUDE / REVIEW / EXCLUDE |
| `reason` | Per-topic decision, exclusion code, and one-line reason, pipe-separated |
| `criteria_version`, `model_name`, `screened_at` | Provenance |
| `co_investigator_agree_y_n`, `co_investigator_comments` | Blank — for manual review |

A `run_info` sheet records the criteria version, model, sample size, seed, and screening
timestamp.

## Comparison with the single-prompt attempt (same 300 records, seed=42)

| Decision | Single-prompt (reverted) | Router + 5 modules (this run) |
|---|---|---|
| INCLUDE | 3 | 2 |
| MAYBE / REVIEW | 10 | 2 |
| EXCLUDE | 287 | 296 |

Both pipelines land on a similarly small INCLUDE count on this sample, but the router pipeline
routes far fewer records to REVIEW than the single-prompt version did to MAYBE. Worth spot-checking
a sample of EXCLUDEs against the gate sequence before treating either run as a reliable estimate of
the true include/review rate at full scale — v3's own documentation expects a large MAYBE/REVIEW
bucket as correct, recall-preserving behaviour, and neither run produced one on this sample.
