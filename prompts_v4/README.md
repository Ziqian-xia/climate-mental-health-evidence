# Title/Abstract Screening Prompts - v4.1

This folder contains the corrected v4 prompt pipeline. It is still named `prompts_v4` so existing
paths continue to work, but every active component is marked `Version: v4.1`.

## Files

- `screening_criteria_v4.md`: human-readable master criteria.
- `00_candidate_topics_prompt.md`: loose, high-recall hazard router.
- `shared_module_rules.md`: one authoritative set of outcome, publication, design and decision rules.
- `01_temperature_prompt.md` through `05_drought_prompt.md`: hazard-specific definitions only.
- `screen_excel_v4_deepseek.py`: router, topic calls, conservative aggregation and audit log.
- `test_screening_logic_v4.py`: offline regression tests for routing and aggregation.

The script concatenates `shared_module_rules.md` with the relevant topic definition for each module
call. Do not copy shared eligibility rules into the five topic files; that was the source of rule
drift in the previous v4.

## Decisions

- `INCLUDE`: hazard, measured mental-health outcome, original human evidence and eligible design are
  all clear.
- `REVIEW`: nothing clearly fails, but any gate or topic is ambiguous, unstated or incomplete.
- `EXCLUDE`: at least one gate clearly fails.

The pipeline uses these three values everywhere. `MAYBE` and `review_flag` are retired.

An empty router topic list is EXCLUDE only when `needs_human_topic_review=false`. If that flag is
true, the pipeline returns REVIEW. Any invalid model output, unsupported topic, missing module result
or failed module call also makes the aggregate decision REVIEW.

For multi-topic records:

- any uncertainty/error -> REVIEW;
- otherwise, any INCLUDE -> INCLUDE;
- otherwise -> EXCLUDE.

## Design policy

Design is a title/abstract gate only when the abstract is explicit. Clearly descriptive single-wave,
qualitative-only, case-report, cross-sectional ecological and treatment-effect studies are excluded
as `wrong_design`. Unstated or ambiguous designs are REVIEW. Detailed identification and risk of
bias remain full-text tasks.

## Run

```bash
python prompts_v4/screen_excel_v4_deepseek.py \
  --prompts-dir prompts_v4 \
  --in review_packet_pairwise.xlsx \
  --out review_packet_pairwise_v4_ai.xlsx
```

Set `DEEPSEEK_API_KEY` first. Use `--limit 3` for a smoke test and `--ref <commit-sha>` to pin
remote prompts. The JSONL output is the audit and resume record; retain it with every run.

Run offline checks before screening:

```bash
python -m unittest prompts_v4/test_screening_logic_v4.py
python -m py_compile prompts_v4/screen_excel_v4_deepseek.py
```

## Validation requirement

Do not run the full 131,468-record corpus solely because these consistency defects are fixed. First
rerun the human-labeled 150-record packet and add targeted cases for generic unnamed disasters,
missing abstracts, manufactured temperature, ambiguous design, multi-topic disagreement, resilience
and quality of life. Report recall for human INCLUDE records and manually inspect a random sample of
model EXCLUDE records.

The two policy choices still requiring team confirmation are data-bearing conference abstracts and
the exact scope of person-level resilience, coping and health-related quality of life. Ambiguous
records stay in REVIEW until those choices are settled.
