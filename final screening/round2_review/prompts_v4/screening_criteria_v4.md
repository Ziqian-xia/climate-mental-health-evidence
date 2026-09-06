# Title/Abstract Screening Criteria: Climate Hazards and Mental Health

> **Version: v4.2** - team-confirmed missing-abstract policy integrated into the master criteria.

Criteria version: v4.2 (team amendment, 2026-09-05)
Stage: LLM-assisted title/abstract screening.

## Purpose

Keep records that plausibly estimate an eligible climate hazard's effect on a measured human
mental-health or subjective-wellbeing outcome. This is a recall-oriented screen: ambiguity goes to
`REVIEW`, never to `EXCLUDE`.

Use only the supplied title and abstract. Do not use outside knowledge.

## Eligible hazards

- `temperature`: naturally occurring ambient heat or cold, heatwave, cold spell, daily temperature,
  apparent temperature, heat index, WBGT, humidex, or diurnal temperature range. Laboratory,
  climate-chamber, therapeutic, sauna/cryotherapy, cold-pressor, water-immersion, refrigerated-room,
  or otherwise manufactured thermal exposure is not eligible. Outdoor workers and indoor exposure
  to outdoor-origin heat or cold remain eligible.
- `wildfire`: wildfire, bushfire, forest/landscape fire, wildfire smoke, fire-attributed PM2.5,
  smoke days, burn area/perimeter/proximity, or fire evacuation.
- `flood`: flood, flash/riverine/coastal flood, inundation, river overflow, storm-surge flooding,
  flood depth/extent, flood victims/shelters, or documented flood attribution. Rainfall or heavy
  precipitation alone is not an eligible flood exposure.
- `cyclone`: tropical cyclone, hurricane, typhoon, tropical storm, named tropical storm, landfall,
  storm track, or cyclone intensity.
- `drought`: drought, environmentally caused water scarcity, prolonged dry spell, drought disaster,
  SPEI/PDSI/SPI, precipitation deficit framed as drought, or soil-moisture anomaly framed as drought.

Generic `natural disaster`, `extreme weather`, or `climate event` may conceal an eligible hazard.
When paired with a plausible human mental-health outcome, route it to `REVIEW` for topic resolution.

## Eligible outcomes

The study must measure at least one of:

- depression, anxiety, psychological distress or perceived psychological stress;
- PTSD/post-traumatic stress, suicide, suicidal ideation, self-harm or NSSI;
- psychiatric emergency visits, admissions, or mental-health service use;
- individual subjective wellbeing, life satisfaction, or positive/negative affect;
- climate anxiety, eco-anxiety, solastalgia, or ecological grief;
- individual psychological resilience, disaster-related psychological resilience, coping, or
  health-related quality of life when measured as a person-level mental-health/wellbeing outcome.

Named instruments such as PHQ-9, GAD-7, K6/K10, PCL-5, IES-R, PSS and CES-D are outcome signals.
Infrastructure/community/ecosystem resilience, economic recovery, preparedness, coping behaviour,
or physical quality-of-life measures alone are not eligible outcomes. A psychiatric term used only
as background, a covariate, comorbidity, risk factor, or sample definition is not a measured outcome.

## Original human evidence

The record must plausibly report original empirical data involving humans or human population/service
data. Exclude reviews, meta-analyses, protocols, editorials, commentaries, guidelines, news, methods-only
papers and non-data meeting items. A data-bearing conference abstract or preprint can proceed.

## Design gate

The design must plausibly estimate an association or effect of variation in the eligible hazard,
rather than only describe mental health after an event.

`INCLUDE` when the abstract clearly reports one of the following:

- time-series, interrupted time-series, case-crossover, distributed-lag or related area-time design;
- repeated measures/panel or longitudinal cohort with exposure occurring or varying over follow-up;
- difference-in-differences, event study, fixed-effects panel, natural experiment, regression
  discontinuity, instrumental-variable or another explicit quasi-experimental contrast;
- a design with a clearly stated temporal or exposure contrast capable of estimating the hazard-outcome
  relationship, even if the exact estimator is not named.

`EXCLUDE` as `wrong_design` only when the supplied title or abstract clearly reports:

- a single-wave cross-sectional or post-disaster prevalence survey with no eligible exposure contrast;
- qualitative interviews/focus groups/ethnography only;
- a case report, case series, or purely descriptive account;
- a cross-country or spatial ecological correlation with no temporal or quasi-experimental contrast;
- a treatment/intervention trial estimating treatment efficacy rather than the hazard effect.

`REVIEW` when design is unstated or ambiguous; when `prospective`, `longitudinal`, `cohort`, or
`ecological` is named without enough detail; or when repeated post-event follow-ups have no pre-event
baseline. Do not infer an ineligible design from silence. This design gate is the rule used at
title/abstract screening; detailed identification, exposure measurement, effect extraction and risk
of bias remain full-text tasks.

## Decision sequence

Apply gates in this order and stop at the first clear failure:

1. Human/original empirical evidence.
2. Eligible hazard exposure.
3. Measured eligible outcome.
4. Eligible or plausibly eligible design.

- `INCLUDE`: an abstract is available and every gate is clearly satisfied. Never INCLUDE from a title alone.
- `REVIEW`: no gate clearly fails, but at least one gate is ambiguous, unstated, or title-only.
- `EXCLUDE`: at least one gate clearly fails.

Uncertainty between INCLUDE and REVIEW becomes REVIEW. Uncertainty between REVIEW and EXCLUDE also
becomes REVIEW. Plausible non-English records become REVIEW.

## Records without an abstract

When the supplied abstract is empty, use only the supplied title. Do not invent an abstract
or use outside knowledge. Apply the same hazard, human/original evidence, measured outcome,
and design criteria above.

- EXCLUDE if the title itself clearly demonstrates an exclusion criterion, e.g. explicitly
  a review/meta-analysis/protocol, an animal-only or laboratory study, a clearly unrelated
  exposure/outcome, or an explicitly ineligible design. Use the exclusion-code precedence below.
- REVIEW when the title is potentially relevant or information is insufficient.
  Absence of words in a short title is not proof a criterion fails.
- Do not return INCLUDE from a title alone. Potentially eligible records require an abstract,
  full text, or human review.
- If both title and abstract are empty, return REVIEW; no eligibility judgement can be made.

Missing an abstract is not by itself a reason to send every record to REVIEW.
The title must first be assessed for a clear exclusion; uncertainty remains REVIEW.

## Exclusion-code precedence

Use the first applicable code in gate order:

1. `not_human_empirical`: no human/human-population empirical evidence.
2. `non_original`: clearly a review, protocol, commentary or other non-original publication.
3. `wrong_exposure`: no eligible hazard, including manufactured temperature exposure.
4. `wrong_outcome`: no measured eligible mental-health/wellbeing outcome.
5. `wrong_design`: on-topic human original study with a clearly ineligible design.

`animal_or_lab_only` is retired because it overlapped `not_human_empirical` and `wrong_exposure`.

## Output

Return exactly one JSON object using the schema for the supplied record's abstract availability.
For a hazard-specific module call with an abstract, use the separately supplied module schema.

### No abstract: title-only or no text

```json
{
  "dedup_id": "copy the supplied ID exactly",
  "decision": "EXCLUDE | REVIEW",
  "exclusion_code": "NA | not_human_empirical | non_original | wrong_exposure | wrong_outcome | wrong_design",
  "one_line_reason": "brief reason based only on the title, or state that no text is available",
  "notes_for_human_review": "uncertainty or missing information, if any"
}
```

For REVIEW use exclusion_code=NA. Return your screening decision directly.

### Abstract available: general screening

Return the following general schema unless a hazard-specific module schema is supplied:

```json
{
  "dedup_id": "string",
  "decision": "INCLUDE | REVIEW | EXCLUDE",
  "confidence": 0.0,
  "exposure_or_intervention_tag": "temperature | wildfire | flood | cyclone | drought | multiple | unclear | none",
  "outcome_tag": "common_mental_disorder | severe_outcome | service_utilisation | subjective_wellbeing | climate_psychological | multiple | unclear | none",
  "human_empirical_signal": "yes | no | unclear",
  "original_report_signal": "yes | no | unclear",
  "design_signal": "eligible | ineligible | unclear",
  "exclusion_code": "NA | not_human_empirical | non_original | wrong_exposure | wrong_outcome | wrong_design",
  "one_line_reason": "string, <=25 words",
  "notes_for_human_review": "string"
}
```

`exclusion_code` must be `NA` for INCLUDE and REVIEW. Confidence is confidence in the decision,
not estimated eligibility probability.

## Unresolved policy choices

Before production screening, the team should confirm whether data-bearing conference abstracts are
eligible publications and whether person-level psychological resilience, coping and health-related
quality of life are all intended outcomes. Until confirmed, ambiguous examples go to REVIEW.
