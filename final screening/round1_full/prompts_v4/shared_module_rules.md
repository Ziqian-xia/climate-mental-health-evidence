# Shared Topic-Screening Rules

> **Version: v4.1** - consistency and safety revision of v4.

Screen the supplied title and abstract for the topic named in the accompanying topic definition.
Use no outside knowledge.

Apply these gates in order:

1. The record plausibly reports original empirical human or human-population data.
2. The topic's eligible hazard is studied as an exposure.
3. An eligible mental-health/wellbeing construct is measured as an outcome.
4. The design plausibly estimates an association/effect of variation in that hazard.

Eligible outcomes are depression, anxiety, psychological distress or perceived stress; PTSD;
suicide, suicidal ideation or self-harm; psychiatric service use; individual subjective wellbeing,
life satisfaction or affect; climate anxiety, eco-anxiety, solastalgia or ecological grief; and
person-level psychological resilience, coping or health-related quality of life when clearly used
as a mental-health/wellbeing outcome.

Do not count infrastructure/community/ecosystem resilience, economic recovery, preparedness,
coping behaviour, or physical quality of life alone. A psychiatric term used only as background,
covariate, comorbidity, risk factor or sample definition is not a measured outcome.

Exclude reviews, evidence syntheses, protocols, editorials, commentaries, guidelines, news,
methods-only papers and non-data meeting items as `non_original`. Data-bearing conference abstracts
and preprints may proceed.

Design decisions:

- INCLUDE clearly eligible time-series, interrupted time-series, case-crossover, distributed-lag,
  repeated-measures/panel, hazard-varying longitudinal cohort, difference-in-differences, event-study,
  fixed-effects, natural-experiment, regression-discontinuity, instrumental-variable, or another
  explicit temporal/quasi-experimental exposure contrast.
- EXCLUDE as `wrong_design` a clearly single-wave cross-sectional/post-event prevalence survey with
  no eligible exposure contrast; qualitative-only study; case report/series; purely descriptive
  study; cross-sectional ecological correlation; or treatment trial estimating treatment rather
  than hazard effects.
- REVIEW an unstated or ambiguous design, a generic design label without enough detail, repeated
  post-event follow-ups lacking a pre-event baseline, or any plausible title-only record.

Decision rules:

- `INCLUDE`: all four gates are clearly satisfied.
- `REVIEW`: no gate clearly fails, but any gate is ambiguous, incomplete or unstated.
- `EXCLUDE`: a gate clearly fails. Uncertainty never becomes EXCLUDE.

For EXCLUDE, use the first applicable code:
`not_human_empirical`, `non_original`, `wrong_exposure`, `wrong_outcome`, `wrong_design`.
For INCLUDE or REVIEW, use `NA`.

Return exactly one JSON object:

```json
{
  "dedup_id": "string",
  "topic": "topic supplied by the topic definition",
  "decision": "INCLUDE | REVIEW | EXCLUDE",
  "confidence": 0.0,
  "hazard_signal": "yes | no | unclear",
  "outcome_signal": "yes | no | unclear",
  "human_empirical_signal": "yes | no | unclear",
  "original_report_signal": "yes | no | unclear",
  "design_signal": "eligible | ineligible | unclear",
  "exclusion_code": "NA | not_human_empirical | non_original | wrong_exposure | wrong_outcome | wrong_design",
  "one_line_reason": "string, <=25 words",
  "notes_for_human_review": "string"
}
```

Confidence is confidence in the decision, not eligibility probability.
