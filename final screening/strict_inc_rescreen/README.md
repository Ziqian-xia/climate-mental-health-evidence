# Strict Reassessment of the 802 Broad-Screen INCLUDE Records

This directory contains the complete criteria, prompts, model outputs, validation code, and audit
record for the strict reassessment of the 802 records retained by the published broad screen.

The reassessment does not overwrite the published two-pass screening result. It applies a stricter
causal meta-analysis standard and compares two independent model systems: GPT-5.6 Sol and DeepSeek
V4 Pro.

## Start here

- `strict_inclusion_criteria_for_inc.md`: complete scientific eligibility standard.
- `strict_inc_prompt.md`: executable title-and-abstract screening prompt.
- `PROCESS.md`: complete provenance, execution, validation, failure, and interpretation record.
- `results/strict_inc_screening_report.md`: concise results report.
- `results/two_model_screening.csv`: primary 802-row action table.
- `results/model_disagreements.csv`: 139 exact disagreements, including 64 cross-boundary decisions.
- `results/human_review_queue.xlsx`: formatted manual adjudication workbook with priority and optional
  review queues.

## Main result

| Recommended action | Records |
|---|---:|
| `PRIORITY_FULLTEXT` | 124 |
| `FULLTEXT_REVIEW` | 315 |
| `ADJUDICATE_PRIORITY` | 64 |
| `DO_NOT_ADVANCE_MAIN_META` | 299 |
| Total | 802 |

The recall-protective full-text pool is the 503-record union advanced by at least one model. Human
adjudication should begin with the 64 records where the models disagree across the full-text boundary.

## Directory contents

### Criteria and prompts

- `strict_inclusion_criteria_for_inc.md`: version `strict-inc-v1.0`.
- `strict_inc_prompt.md`: shared model instructions and decision rules.

### Scripts

- `prepare_inc_input.py`: reconstructs and freezes the exact 802-record input.
- `screen_gpt56.py`: OpenAI API runner for a reproducible GPT-5.6 screening run.
- `screen_deepseek_v4_pro.py`: resumable DeepSeek V4 Pro runner with strict JSON validation.
- `merge_and_compare.py`: validates GPT partitions, merges both model outputs, and calculates
  agreement statistics.
- `requirements.txt`: optional OpenAI client dependency for `screen_gpt56.py`.

### Results

- `results/input_802.csv`: frozen screening input.
- `results/input_802_manifest.json`: source hashes and input hash.
- `results/subagents/`: eight GPT-5.6 Sol partition files.
- `results/strict_inc_gpt56_subagents.csv`: validated GPT-5.6 result.
- `results/strict_inc_deepseek_v4_pro.jsonl`: append-only DeepSeek checkpoint and audit log.
- `results/strict_inc_deepseek_v4_pro.csv`: clean 802-row DeepSeek result.
- `results/deepseek_v4_pro_summary.json`: DeepSeek counts, hashes, and token usage.
- `results/two_model_screening.csv`: primary combined action table.
- `results/model_disagreements.csv`: disagreement review queue.
- `results/human_review_queue.xlsx`: manual review workbook with validated decision, reason-code,
  confidence, reviewer, notes, and date fields.
- `results/model_comparison_summary.json`: agreement statistics and confusion matrix.
- `results/strict_inc_screening_report.md`: concise scientific summary and recommended next step.

## Reproduce the deterministic outputs

Run from this directory:

```bash
python3 screen_gpt56.py --input results/input_802.csv --validate-only
python3 screen_deepseek_v4_pro.py --input results/input_802.csv --validate-only
python3 merge_and_compare.py
```

API keys must be supplied through environment variables and must never be saved in this repository.
See `PROCESS.md` for the full execution protocol and interpretation limits.
