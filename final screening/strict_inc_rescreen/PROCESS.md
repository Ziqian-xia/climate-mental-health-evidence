# Strict INC Reassessment: Complete Process Record

## 1. Objective

The published two-pass screen retained 802 of 131,468 deduplicated records as `INCLUDE`. That screen
was intentionally recall-oriented. This reassessment applies a stricter causal meta-analysis standard
to all 802 records without changing the published screening files.

Two independent model systems assessed every title and abstract:

- GPT-5.6 Sol through eight Codex subagents; and
- DeepSeek V4 Pro through the official API.

The two outputs are retained separately. A deterministic merge creates an action table and a focused
disagreement queue. Model agreement is used for workflow prioritization, not as a substitute for a
human gold standard.

## 2. Frozen input and provenance

`prepare_inc_input.py` joins two sources by `dedup_id`:

1. the published `final-result.csv`, from which it selects records with `decision == INCLUDE`; and
2. `data/merged_deduplicated_records.csv.gz`, which supplies title, abstract, bibliographic metadata,
   source databases, and DOI values.

The script fails unless exactly 802 `INCLUDE` records are present, all identifiers join to the corpus,
all identifiers are unique, and every selected record has a non-empty abstract.

The frozen input is `results/input_802.csv`. Its SHA-256 is
`da1a5d2f8f428ce45cdc396a09ea048210c7589ea114d56933fadb9f36f7dcc6`.
`results/input_802_manifest.json` records the source paths and hashes used to build it.

## 3. Scientific decision standard

The complete standard is in `strict_inclusion_criteria_for_inc.md`. The executable prompt is
`strict_inc_prompt.md`. Both use criteria version `strict-inc-v1.0`.

The four decisions are:

- `META_ELIGIBLE`: the abstract affirmatively supports every hard requirement;
- `FULLTEXT_REVIEW`: the study is plausible, but the abstract omits a critical detail;
- `NARRATIVE_ONLY`: the topic is relevant, but the design cannot identify the required causal effect;
- `EXCLUDE`: the record clearly fails a basic scope requirement.

The critical difference from the broad screen is the identification requirement. Single-wave
cross-sectional studies, one-time post-event comparisons, exposed-only follow-up without a pre-event
outcome, and self-reported exposure without external linkage do not enter the main causal
meta-analysis.

## 4. GPT-5.6 Sol execution

The 802 rows were divided into eight ordered, non-overlapping partitions:

| Part | Source rows | Records |
|---|---:|---:|
| 01 | 1-100 | 100 |
| 02 | 101-200 | 100 |
| 03 | 201-300 | 100 |
| 04 | 301-400 | 100 |
| 05 | 401-500 | 100 |
| 06 | 501-600 | 100 |
| 07 | 601-700 | 100 |
| 08 | 701-802 | 102 |

Each Codex subagent was fixed to `gpt-5.6-sol` with high reasoning. Each agent read the same frozen
input, criteria, and prompt; assessed every assigned record individually; and wrote one JSON object
per record. The eight partition files are stored in `results/subagents/`.

`merge_and_compare.py` verifies that the partitions contain exactly 802 unique source rows, cover
rows 1-802 without gaps, match each source `dedup_id`, use the required enums, and identify the model
and criteria version correctly. The validated result is `results/strict_inc_gpt56_subagents.csv`.

## 5. DeepSeek V4 Pro execution

`screen_deepseek_v4_pro.py` calls the official OpenAI-compatible Chat Completions endpoint at
`https://api.deepseek.com/chat/completions` with:

- model: `deepseek-v4-pro`;
- thinking mode: enabled;
- reasoning effort: high;
- response format: JSON object;
- maximum output budget: 8,000 tokens; and
- 16 concurrent workers.

The API key is read only from `DEEPSEEK_API_KEY`. It is not written to a project file, result, log, or
checkpoint.

Every response is rejected and retried unless it is valid JSON, contains exactly the required fields,
matches the input `dedup_id`, uses only allowed enum values, supplies a non-empty reason of at most
500 characters, and supplies no more than five full-text checks of at most 200 characters each.

The append-only checkpoint binds the run to the input hash, prompt hash, model name, and criteria
version. A mismatched checkpoint is rejected instead of silently reused.

### Pilot correction

The first three pilot requests returned `finish_reason=length`. DeepSeek counts hidden reasoning and
visible JSON against `max_tokens`; the original 3,000-token limit was too small. The run was stopped
after 109 successful records and three exhausted records, the limit was raised to 8,000, and the run
resumed from the checkpoint. All 802 records then completed successfully.

Consequently, `results/strict_inc_deepseek_v4_pro.jsonl` has 805 lines: 802 completed records and
three retained failed attempts. The clean ordered file is `results/strict_inc_deepseek_v4_pro.csv`,
which has exactly 802 data rows.

The completed run used 1,365,009 input tokens, 1,990,396 output tokens, and 3,355,405 total tokens.
At the official off-peak price in effect on 2026-09-16, the estimated cost was approximately $4.84
if all input tokens were cache misses. Actual billing may be lower when input caching applies.
Pricing: https://api-docs.deepseek.com/quick_start/pricing/

## 6. Deterministic merge and comparison

`merge_and_compare.py` validates both complete model outputs and produces:

- `results/two_model_screening.csv`: both decisions, both reasons, and a recommended action;
- `results/model_disagreements.csv`: all exact disagreements, with a cross-boundary flag;
- `results/strict_inc_gpt56_subagents.csv`: the ordered GPT-5.6 result; and
- `results/model_comparison_summary.json`: counts, confusion matrix, agreement, and Cohen's kappa.

The recommended actions are deterministic:

- `PRIORITY_FULLTEXT`: both models return `META_ELIGIBLE`;
- `FULLTEXT_REVIEW`: both models advance the record, but not both as `META_ELIGIBLE`;
- `ADJUDICATE_PRIORITY`: one model advances and the other does not; and
- `DO_NOT_ADVANCE_MAIN_META`: neither model advances.

## 7. Results

| Decision | GPT-5.6 Sol | DeepSeek V4 Pro |
|---|---:|---:|
| META_ELIGIBLE | 139 | 160 |
| FULLTEXT_REVIEW | 336 | 307 |
| NARRATIVE_ONLY | 292 | 306 |
| EXCLUDE | 35 | 29 |
| Total | 802 | 802 |

Agreement statistics:

- exact four-category agreement: 82.7%;
- four-category Cohen's kappa: 0.739;
- advance/do-not-advance agreement: 92.0%;
- binary Cohen's kappa: 0.835;
- exact four-category disagreements: 139; and
- cross-boundary disagreements: 64.

| Recommended action | Records |
|---|---:|
| PRIORITY_FULLTEXT | 124 |
| FULLTEXT_REVIEW | 315 |
| ADJUDICATE_PRIORITY | 64 |
| DO_NOT_ADVANCE_MAIN_META | 299 |
| Total | 802 |

The union advanced by at least one model contains 503 records. The intersection advanced by both
models contains 439 records.

## 8. Interpretation and next step

1. Retrieve full text for the 503-record union advanced by at least one model.
2. Begin extraction with the 124 records both models classify as `META_ELIGIBLE`.
3. Human-adjudicate the 64 cross-boundary disagreements before excluding any of them.
4. Apply ordinary full-text eligibility assessment to the other 315 consensus-advance records.
5. Retain `NARRATIVE_ONLY` studies for an evidence map if that output remains in scope.
6. Manually review a preregistered random sample of the 299 consensus non-advance records to estimate
   false negatives. Agreement between two models is not a sensitivity estimate.

## 9. Reproduction

Run from this directory.

```bash
python3 prepare_inc_input.py \
  --final-result /path/to/final-result.csv \
  --corpus ../../data/merged_deduplicated_records.csv.gz \
  --out results/input_802.csv

python3 screen_gpt56.py --input results/input_802.csv --validate-only
python3 screen_deepseek_v4_pro.py --input results/input_802.csv --validate-only

export DEEPSEEK_API_KEY='set-outside-the-repository'
python3 screen_deepseek_v4_pro.py --input results/input_802.csv

python3 merge_and_compare.py
```

## 10. Limitations

- Decisions use titles and abstracts only. Missing methods require full-text review.
- Neither model is a human gold standard. Agreement cannot establish sensitivity or specificity.
- The standard is designed for a causal meta-analysis and intentionally moves many clinically
  informative post-event studies to `NARRATIVE_ONLY`.
- Duplicate cohorts and overlapping event samples require full-text resolution.
- Final inclusion requires full-text eligibility, effect extraction, and risk-of-bias assessment.
