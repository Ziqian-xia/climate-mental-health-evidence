# Strict INC Rescreen Prompt

Criteria version: strict-inc-v1.0

You are reassessing one record previously retained by a broad title/abstract screen. Use only the
supplied title and abstract. Do not use outside knowledge and do not infer unreported methods.

The target evidence is an original quantitative human study that uses objectively measured or
externally verifiable variation in one registered climate hazard to estimate its effect on a measured
mental-health outcome with a credible temporal or quasi-experimental counterfactual and an extractable
quantitative effect.

Registered hazards: naturally occurring ambient temperature; wildfire/fire-attributed smoke; flood
or inundation; tropical cyclone/hurricane/typhoon; drought or an explicit drought index.

Eligible outcomes: depression, anxiety, psychological distress/stress, PTSD, suicide/suicidality/
self-harm, psychiatric service use, individual subjective wellbeing/life satisfaction/affect,
climate anxiety/solastalgia/ecological grief, and person-level psychological resilience/coping/
health-related quality of life only when clearly measured as mental health or subjective wellbeing.

## Decision rules

Return `META_ELIGIBLE` only when the abstract affirmatively supports all of:

1. original quantitative human or human-population data;
2. a registered hazard is the main exposure;
3. exposure is objective or externally verifiable rather than self-report alone;
4. an eligible mental-health outcome is measured;
5. design uses within-unit temporal exposure variation or a credible quasi-experimental
   counterfactual;
6. a quantitative hazard effect and uncertainty are reported, or the abstract explicitly indicates
   that an extractable adjusted effect is reported.

Return `FULLTEXT_REVIEW` when the study plausibly satisfies the target but the abstract does not
resolve exposure source, counterfactual, baseline, hazard-specific estimate, or effect extractability.
Missing information is not positive evidence.

Return `NARRATIVE_ONLY` when the topic is relevant but the abstract clearly shows a design unsuitable
for the causal meta-analysis: single-wave cross-sectional; post-event prevalence; exposed/unexposed
single post-event comparison; damage-severity association only; exposed-only follow-up without a
pre-event outcome; self-reported exposure only; qualitative-only evidence; or descriptive
prevalence/trajectory/predictor analysis without a hazard effect.

Return `EXCLUDE` for a wrong/non-primary hazard, wrong outcome, non-original publication, non-human
study, manufactured temperature exposure, or projection/simulation-only study.

Eligible design examples include time-series, interrupted time-series, case-crossover, distributed
lag, repeated-measures/panel with changing hazard exposure, longitudinal pre/post exposure with a
pre-exposure outcome, difference-in-differences, event study, fixed effects, natural experiment,
regression discontinuity, and instrumental variables.

For flood/cyclone/wildfire event studies, a post-event exposure gradient or affected-versus-unaffected
comparison alone is not a credible counterfactual. Do not call a study causal merely because it reports
regression, odds ratios, adjusted associations, a cohort, or multiple post-event waves.

Choose one primary reason code:

- `eligible`
- `unclear_exposure_measurement`
- `unclear_design`
- `unclear_effect_extractability`
- `cross_sectional`
- `no_pre_event_baseline`
- `no_hazard_variation`
- `self_report_exposure_only`
- `descriptive_or_predictor_only`
- `qualitative_only`
- `wrong_exposure`
- `wrong_outcome`
- `non_original`
- `not_human_empirical`
- `projection_only`
- `multiple_issues`

The reason must state concrete evidence from the supplied text. For `FULLTEXT_REVIEW`, list the exact
facts that full text must establish. Be conservative about `META_ELIGIBLE`.
