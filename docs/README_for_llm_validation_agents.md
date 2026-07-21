# README for LLM Validation Agents

This note is for future LLM agents or collaborators continuing the climate change and mental
health title/abstract screening workflow.

## Current Task Context

The project has a deduplicated screening pool of 131,468 records. The current screening plan uses
a lower-cost production model, such as DeepSeek Flash, for large-scale screening and a stronger
model, such as Claude Opus or another advanced LLM, for proxy validation.

The current prompt set is:

```text
prompts_v2/title_abstract_screening/
```

The prompt version has been revised to `v2.1`. The main purpose of v2.1 is to reduce false
positives from non-original papers while protecting likely eligible wellbeing/resilience studies.

## Important Files

```text
prompts_v2/title_abstract_screening/screening_criteria_v2.md
prompts_v2/title_abstract_screening/00_candidate_topics_prompt.md
prompts_v2/title_abstract_screening/01_temperature_prompt.md
prompts_v2/title_abstract_screening/02_wildfire_prompt.md
prompts_v2/title_abstract_screening/03_flood_prompt.md
prompts_v2/title_abstract_screening/04_cyclone_prompt.md
prompts_v2/title_abstract_screening/05_drought_prompt.md
docs/llm_proxy_validation_statistical_plan.md
pilot_screening_v2/results/comparison_v1_vs_v2_deepseek_1000.md
```

## Prompt v2.1 Changes

Prompt v2.1 adds stricter exclusion for non-original or evidence-synthesis records:

```text
systematic review
scoping review
narrative review
umbrella review
integrative review
meta-analysis
evidence map
protocol
editorial
commentary
letter
news item
guideline
policy overview
methods/tutorial paper without original hazard-exposed human mental-health data
```

This change targets a known false positive:

```text
D0054409
Use of machine learning tools to predict health risks from climate-sensitive extreme weather
events: A scoping review
```

The prompt should exclude this as `non_original`.

Prompt v2.1 also protects measured post-hazard wellbeing and resilience outcomes, including:

```text
subjective wellbeing
life satisfaction
quality of life
affect
coping
psychological resilience
disaster-related resilience
```

This change targets a known false negative:

```text
D0012580
Predicting patterns of disaster-related resiliency among older adult Typhoon Haiyan survivors
```

The prompt should keep this as `INCLUDE` or `HUMAN_REVIEW`, not exclude it solely because the
outcome is framed as resilience.

## Validation Design

Use DeepSeek as the production screening model and Opus or another advanced model as a proxy
comparator.

Recommended workflow:

```text
1. Run DeepSeek on all deduplicated records.
2. Collapse DeepSeek decisions:
   - positive = INCLUDE or HUMAN_REVIEW
   - negative = EXCLUDE
3. Draw a stratified validation sample.
4. Run Opus on the validation sample using the same prompt set.
5. Build the DeepSeek x Opus table.
6. Estimate false includes and missed records relative to Opus.
7. If possible, human-check model disagreements and a random sample of agreements.
```

Recommended strata:

```text
A. DeepSeek positive
B. DeepSeek negative with candidate_topics present
C. DeepSeek negative with no candidate_topics
D. Known borderline or pilot-disagreement records
```

Use the statistical details in:

```text
docs/llm_proxy_validation_statistical_plan.md
```

## Statistical Interpretation

If Opus replaces human checking, the result is:

```text
DeepSeek error relative to Opus
```

It is not:

```text
DeepSeek error relative to true human eligibility
```

Report these as model-disagreement or proxy-validation estimates unless humans adjudicate a
subset.

For nonzero error counts, use a binomial confidence interval, preferably Wilson. The `3/n` rule
is only a shortcut for the special case where zero errors are found.

General estimate:

```text
p_hat = x / n
estimated errors = N * p_hat
95% CI for errors = N * 95% CI(p_hat)
```

where:

```text
x = number of proxy errors in the sample
n = number sampled in that stratum
N = number of full-corpus records in that stratum
```

## Agent Guidance

- Do not treat Opus as a human gold standard.
- Do not use a simple random sample only; eligible studies are rare, and easy excludes will
  dominate.
- Do not pool stratified samples without weighting by stratum size.
- Prioritize false negatives among DeepSeek-excluded records.
- Always preserve `dedup_id`, prompt version, model name, and timestamp in outputs.
- If prompt changes are made, rerun the fixed pilot sample before recommending a full-corpus run.
- Keep known calibration records `D0012580` and `D0054409` in any regression check.

## Recommended Next Agent Action

If continuing from this state, the next useful step is to create a validation script that:

```text
1. reads the full DeepSeek screening output,
2. constructs the validation strata,
3. samples records reproducibly with a fixed seed,
4. runs Opus or the selected advanced comparator,
5. outputs the DeepSeek x Opus table,
6. calculates Wilson confidence intervals and projected counts by stratum.
```
