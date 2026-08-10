# Pilot title/abstract screening — v3 criteria, single-prompt, 300-record sample

A separate 300-record pilot, independent of `pilot_screening_v3/` (the router + 5
hazard-module pipeline). This one applies the full `screening_criteria_v3.md` text
(INCLUDE / MAYBE / EXCLUDE, including the v3 design gate G5 and its `wrong_design`
exclusion code) in a **single combined prompt per record**, to a random 300-record sample
of `merged_deduplicated_records.parquet`, using `deepseek-v4-flash` via DeepSeek's
OpenAI-compatible API, with requests sent concurrently. Criteria content is byte-identical
to `prompts_v3/screening_criteria_v3.md` (verified 2026-08-09).

## Files

```
pilot_screening_v3_singleprompt_300/
  README.md                            <- this file
  scripts/
    screening_v3_pilot_300.py          <- draws the sample, runs the screen, writes the xlsx
  results/
    screening_v3_pilot_300_results.xlsx  <- per-record decisions + run_info sheet
    screening_v3_pilot_300_prompt.txt    <- example system/user prompt sent to the model
```

## Run parameters

- Sample size: 300, `RANDOM_SEED = 42` (reproducible — same code path as the earlier pilot
  notebooks, just with `SAMPLE_SIZE=300` and `CRITERIA_MD=screening_criteria_v3.md`)
- Model: `deepseek-v4-flash`, `temperature=0`
- Concurrency: 15 in-flight requests, up to 3 retries per record on invalid output

## Result

300/300 records completed with a valid decision (0 malformed, 0 needed a retry).

| Decision | n |
|---|---|
| EXCLUDE | 287 |
| MAYBE | 10 |
| INCLUDE | 3 |

## Output columns (`results/screening_v3_pilot_300_results.xlsx`, sheet `screening_results`)

| Column | Meaning |
|---|---|
| `dedup_id` | Record ID (join key back to the corpus) |
| `title`, `year`, `journal`, `sources`, `abstract` | Record metadata, for reviewer context |
| `decision` | INCLUDE / MAYBE / EXCLUDE |
| `confidence` | Model's confidence in its own decision (0–1) |
| `exposure_or_intervention_tag`, `outcome_tag` | v3 vocabulary tags |
| `human_empirical_signal` | yes / no / unclear |
| `one_line_reason` | Short rationale, grounded in title/abstract |
| `exclusion_code` | `NA` unless decision is EXCLUDE (v3 codes, including `wrong_design`) |
| `notes_for_human_review` | Flags boundary reasoning, missing abstract, etc. |
| `attempts_needed` | How many attempts it took the model to return a valid decision |
| `co_investigator_agree_y_n`, `co_investigator_comments` | Blank — for manual review |

A `run_info` sheet records the criteria version, model, sample size, seed, and screening
timestamp.

## Caveat — worth checking before treating this as representative

v3's own documentation expects a **large MAYBE bucket** as correct, recall-preserving
behaviour ("This screen is intentionally over-inclusive... Expect a large MAYBE bucket; that
is correct behaviour, not a failure."). This run's MAYBE share (10/300, ~3%) is much smaller
than that framing implies, and the EXCLUDE rate (287/300, ~96%) is correspondingly high —
higher than the earlier binary-decision v1 pilot on the same corpus. Worth spot-checking a
sample of EXCLUDEs against the gate sequence before treating this run as a reliable estimate
of the true include/maybe rate at full scale; `deepseek-v4-flash` may be resolving ambiguity
itself rather than routing to MAYBE as instructed.
