# Stricter Inclusion Criteria for Broad-Screen INCLUDE Records

Version: `strict-inc-v1.0`

Population: the 802 records classified as `INCLUDE` by the published broad screen

Stage: strict title-and-abstract reassessment before full-text screening and causal meta-analysis

## 1. Target evidence

The target is original quantitative human research that uses objectively measured or externally
verifiable variation in a registered climate hazard to estimate an effect on a measured mental-health
outcome. The design must provide a credible temporal or quasi-experimental counterfactual, and the
study must report, or clearly appear to report in the full text, an extractable quantitative effect
with uncertainty.

This stage does not alter the published broad-screen decisions. It creates a stricter classification
of the 802 broad-screen `INCLUDE` records.

## 2. Decision categories

### `META_ELIGIBLE`

The title and abstract affirmatively support all six hard requirements:

1. Original quantitative human evidence.
2. One of the five registered climate hazards is the main exposure.
3. Exposure is objectively measured or externally verifiable.
4. An eligible mental-health outcome is measured.
5. The design uses within-unit temporal variation or a credible quasi-experimental counterfactual.
6. A quantitative hazard effect and its uncertainty are reported, or the abstract clearly indicates
   that an extractable adjusted effect is available.

This label means priority for full-text retrieval and extraction. It is not a final inclusion decision.

### `FULLTEXT_REVIEW`

The study plausibly satisfies the target, but the abstract does not resolve at least one critical item:

- the exposure data source or whether exposure is objective;
- whether the analysis uses within-unit temporal variation, a pre-event baseline, or a credible
  counterfactual;
- whether the hazard is the main explanatory variable;
- whether an effect estimate and uncertainty are extractable; or
- whether hazard-specific results can be separated in a multi-hazard analysis.

Missing information is not positive evidence and cannot support `META_ELIGIBLE`.

### `NARRATIVE_ONLY`

The study is relevant to climate hazards and mental health but cannot identify the causal effect
required for the main meta-analysis. Examples include:

- a single-wave cross-sectional survey, including post-event exposed/unexposed comparisons;
- only post-event measurement, with no pre-event outcome or credible counterfactual;
- exposed-only follow-up in which exposure does not vary during follow-up;
- exposure measured only through participant recall or perceived severity, without external linkage;
- qualitative evidence without an eligible quantitative analysis;
- prevalence, symptom trajectories, correlates, predictors, or risk factors without a hazard effect; or
- outcomes limited to preparedness, community resilience, coping behavior, or non-mental-health
  quality of life.

These studies may remain useful for a narrative evidence map but do not enter the main causal
meta-analysis.

### `EXCLUDE`

The record clearly fails a basic scope requirement:

- non-human, non-original, or non-empirical research;
- a hazard outside the registered five topics, or a hazard used only as background or a covariate;
- manufactured temperature exposure;
- no measured eligible mental-health outcome;
- review, meta-analysis, protocol, commentary, editorial, or methods-only paper; or
- projection or simulation only, without an original empirical hazard-effect estimate.

## 3. Hard eligibility requirements

### G1. Original quantitative human evidence

Eligible units include individual participants and human-population administrative or health-service
data. The article must report original quantitative analysis.

Purely qualitative studies, case reports or case series, reviews, protocols, editorials, commentaries,
guidelines, news items, and methods papers without original results are ineligible for the main
meta-analysis.

### G2. A registered climate hazard is the main exposure

Eligible hazards are:

- `temperature`: naturally occurring ambient heat or cold, heatwaves, cold spells, daily temperature,
  apparent temperature, heat index, WBGT, humidex, or diurnal temperature range;
- `wildfire`: wildfire, bushfire, forest fire, fire-attributed smoke or PM2.5, burned area,
  perimeter or proximity, or an official wildfire evacuation;
- `flood`: flood, inundation, river overflow, coastal flooding, storm-surge flooding, flood depth or
  extent, or official flood attribution;
- `cyclone`: tropical cyclone, hurricane, typhoon, tropical storm, landfall, track, or intensity; and
- `drought`: drought, SPEI, PDSI, SPI, an explicit drought-related precipitation deficit, soil-moisture
  anomaly, or an official drought declaration.

The hazard must be a main explanatory variable, not only a covariate, effect modifier, seasonal
control, or contextual description.

### G3. Objective or externally verifiable exposure

Eligible exposure sources include:

- weather stations, reanalysis, satellites, remote sensing, monitors, or modeled exposure linked to
  observed environmental data;
- geocoded event boundaries, tracks, perimeters, declarations, or administrative disaster records; and
- explicit time-and-place linkage that can be verified against external hazard data.

Participant recall of exposure, subjective damage severity, perceived heat, or perceived disaster
exposure alone is insufficient for the main meta-analysis. Mental-health outcomes may be self-reported
when measured using an identifiable scale or instrument.

### G4. Eligible mental-health outcome

Eligible outcomes include:

- depression, anxiety, psychological distress, or perceived psychological stress;
- PTSD or post-traumatic stress;
- suicide, suicidal ideation, self-harm, or NSSI;
- psychiatric emergency visits, admissions, or mental-health service use;
- individual subjective wellbeing, life satisfaction, or positive or negative affect;
- climate anxiety, eco-anxiety, solastalgia, or ecological grief; and
- person-level psychological resilience, coping, or health-related quality of life only when clearly
  measured as a mental-health or subjective-wellbeing outcome.

A mental-health term used only as background, a covariate, prior history, sample definition, or effect
modifier is not an eligible measured outcome.

### G5. Credible identification design

Designs eligible for the main meta-analysis include:

- time-series, interrupted time-series, case-crossover, and distributed-lag designs;
- repeated-measures or panel studies in which hazard exposure changes over time within the same
  individual, household, region, or institution;
- longitudinal cohorts with a pre-exposure outcome baseline and a defined hazard change;
- difference-in-differences, event-study, or fixed-effects panel designs;
- natural experiments, regression discontinuity, or instrumental variables; and
- other designs that establish temporal ordering and a credible counterfactual.

For flood, cyclone, and wildfire event studies, a post-event gradient in damage or a single
affected/unaffected comparison is not sufficient by itself. Ordinarily, the study needs a pre-event
outcome, before-after control, difference-in-differences, event study, interrupted time series, or an
equivalent counterfactual.

The following do not enter the main meta-analysis:

- single-wave cross-sectional studies;
- single post-event prevalence surveys;
- one-time post-event exposed/unexposed comparisons;
- exposed-only post-event follow-up without a pre-event outcome;
- repeated symptom trajectories in which hazard exposure does not vary; and
- purely spatial or cross-country ecological correlations without within-unit temporal variation.

### G6. Quantitative effect and extractability

The study must estimate the effect of the hazard on the mental-health outcome rather than only report
prevalence or describe post-event symptoms. Full-text extraction ultimately requires:

- an effect estimate or convertible raw statistic;
- uncertainty, such as a standard error, confidence interval, or standard deviation;
- sample size;
- exposure contrast;
- outcome definition; and
- time window.

If the abstract supports an eligible design but does not report these details, classify the record as
`FULLTEXT_REVIEW`, not `META_ELIGIBLE`.

## 4. Special rules

- Retain multiple papers from the same cohort, event, or population at this stage, but flag potential
  sample overlap. Duplicate samples must not be counted more than once in a meta-analysis.
- For multi-hazard studies, at least one hazard must independently satisfy all requirements. An
  inseparable pooled multi-hazard estimate is `FULLTEXT_REVIEW` or `NARRATIVE_ONLY`.
- A paper containing both an empirical estimate and a future projection may be retained for the
  empirical estimate. Projection-only papers are excluded.
- A conference abstract can be `META_ELIGIBLE` only when it provides enough information to establish
  every hard requirement and the result is retrievable; otherwise use `FULLTEXT_REVIEW`.
- Decisions use only the supplied title and abstract. Do not use outside knowledge to fill missing
  methods or results.

## 5. Required output fields

Every record must contain:

- `dedup_id`
- `strict_decision`
- `primary_topic`
- `exposure_measurement`
- `design_class`
- `counterfactual_status`
- `effect_extractability`
- `outcome_status`
- `primary_reason_code`
- `confidence`
- `reason`
- `full_text_checks`
- `overlap_flag`

The standard is intentionally stricter than the broad screen, but it does not convert missing abstract
information into an exclusion. Use `FULLTEXT_REVIEW` when a plausible study lacks critical details.
