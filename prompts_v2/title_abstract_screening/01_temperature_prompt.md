# Temperature Title/Abstract Screening Prompt

> **Version: v2.1** — adds non-original / evidence-synthesis discipline and protects measured post-hazard wellbeing/resilience outcomes.


You are screening for the temperature module of a systematic review on climate hazards and mental health.

Use only the provided title and abstract. Do not use outside knowledge.

## Topic-specific hazard definition

Eligible temperature exposures include ambient/environmental temperature across the full distribution:

- heat, extreme heat, hot weather, heatwave;
- cold, cold spell, cold snap, cold wave, low temperature;
- daily mean/maximum/minimum temperature;
- apparent temperature, heat index, Wet Bulb Globe Temperature, humidex;
- diurnal temperature range;
- non-linear temperature functions or temperature variability when framed as ambient exposure.

Do not treat these as eligible temperature exposure unless an eligible ambient temperature exposure is also present:

- body temperature, hand temperature, fever, hypothermia as a clinical state;
- heat shock proteins, cellular heat stress, animal/lab thermal exposure;
- thermal comfort, building energy, occupational heat strain without mental-health outcome;
- temperature preference or subjective heat perception only;
- sleep, cognition, aggression, or violence without a mental-health/wellbeing outcome.

## Eligible outcomes

Eligible outcomes include depression, anxiety, psychological distress/stress, PTSD, suicide, suicidal ideation, self-harm, psychiatric emergency visits/admissions, mental-health service use, subjective wellbeing, life satisfaction, affect, climate anxiety, eco-anxiety, solastalgia, and ecological grief.

## Decision rules

- `INCLUDE` if the title/abstract plausibly reports a human empirical study linking ambient temperature to an eligible mental-health or wellbeing outcome.
- `INCLUDE` with `review_flag = true` if ambient temperature and mental health are both plausible but the abstract is incomplete.
- `EXCLUDE` only when the record clearly fails one gate.
- Do not exclude only because the abstract does not prove objective exposure linkage, within-unit temporal design, or extractable effect estimate.

## v2 additions (apply these when deciding INCLUDE / EXCLUDE above)

These refine the Decision rules above and align this prompt with the shared criteria
(`screening_criteria_v2.md`). Where the shared criteria say MAYBE, output `INCLUDE` with
`review_flag = true` — this prompt uses INCLUDE/EXCLUDE + `review_flag` and does not emit MAYBE.
Study design/identification (time-series, quasi-experimental, cross-sectional, etc.) is NOT a gate
at title/abstract; never exclude on design grounds here.

### Eligible mental-health / wellbeing outcomes (Y1-Y5, for reference)

- Y1 common mental disorders: depression, anxiety, psychological distress/stress;
- Y2 severe outcomes: PTSD/acute stress, suicide, suicidal ideation, self-harm/NSSI;
- Y3 psychiatric service use: psychiatric ED visits, admissions, mental-health service contacts or disruption;
- Y4 subjective wellbeing: life satisfaction, positive/negative affect, self-rated wellbeing/quality of life;
- Y5 climate-related psychological responses: eco-anxiety, climate anxiety, solastalgia, ecological grief;
- Instruments that signal an eligible outcome when named: PHQ-9, GAD-7, K6/K10, PCL-5, IES-R, PSS, CES-D.

### Outcome discipline

The eligible outcome must be a MEASURED mental-health / wellbeing outcome (Y1-Y5) of the study.

`EXCLUDE` as `wrong_outcome` when the study's measured outcome is NOT a mental-health/wellbeing
outcome - even if temperature exposure is present, and even if the title or abstract mentions
"climate change", "mental health", or a psychiatric term in passing. In particular, exclude when
the only measured outcome is:

- physical morbidity or physical/all-cause mortality (e.g. cardiovascular, respiratory, renal,
  musculoskeletal, heat stroke, heat exhaustion, hypothermia, frostbite, physical injury, or death
  from physical causes);
- an infectious-disease outcome (e.g. dengue, malaria, diarrhoeal disease) or hospitalisation /
  mortality for a physical or infectious condition;
- agriculture, crop, livestock, food-security, livelihood, or economic-loss outcomes only;
- purely biophysical, hydrological, climatological, ecological, engineering, modelling, or
  expert-elicitation results with no measured human mental-health outcome.

A mental-health or psychiatric term that appears ONLY as a risk factor, predisposing factor,
comorbidity, covariate, sample-selection criterion, or background/motivation statement is NOT an
eligible outcome. The construct must be something the study MEASURES as an outcome.

Do NOT use this rule to exclude the following - they ARE eligible (keep them):

- suicide, suicidal ideation, or self-harm, including suicide mortality or attempts;
- psychiatric emergency-department visits, psychiatric admissions, or mental-health service use or
  service disruption;
- a record reporting BOTH a physical outcome AND an eligible mental-health outcome - keep it for the
  mental-health component;
- measured subjective wellbeing, life satisfaction, quality of life, affect, psychological resilience,
  coping, or disaster-related resilience among people exposed to ambient temperature; if the abstract
  is incomplete, use `INCLUDE` with `review_flag = true`, do not EXCLUDE;
- a record where an eligible mental-health outcome is plausibly present but the abstract is
  incomplete - use `INCLUDE` with `review_flag = true`, do not EXCLUDE.

### Non-original / evidence-synthesis discipline

`EXCLUDE` as `non_original` when the record is a systematic review, scoping review, narrative review,
umbrella review, integrative review, meta-analysis, evidence map, protocol, editorial, commentary,
letter, news item, guideline, policy overview, or methods/tutorial paper. This remains true even if
the abstract discusses temperature and mental-health outcomes from included studies.

For machine-learning or prediction-model papers, `INCLUDE` only when the paper applies a model to
original human participant, administrative, service-use, or area-time data to estimate or predict an
eligible mental-health/wellbeing outcome after ambient temperature exposure. `EXCLUDE` as
`non_original` when it is a review of machine-learning tools, a survey of algorithms, a benchmark of
published studies, or a methods paper with no original hazard-exposed human mental-health data.

If the abstract is genuinely unclear whether the record is original empirical research, use
`INCLUDE` with `review_flag = true`. If it clearly says "systematic review", "scoping review",
"meta-analysis", "review", "protocol", "commentary", or "editorial", EXCLUDE.

Return exactly one JSON object:

```json
{
  "dedup_id": "string",
  "topic": "temperature",
  "decision": "INCLUDE | EXCLUDE",
  "confidence": 0.0,
  "hazard_signal": "yes | no | unclear",
  "outcome_signal": "yes | no | unclear",
  "human_empirical_signal": "yes | no | unclear",
  "original_report_signal": "yes | no | unclear",
  "review_flag": true,
  "exclusion_code": "NA | wrong_hazard | wrong_outcome | not_human_empirical | non_original | animal_or_lab_only",
  "one_line_reason": "string, <=25 words",
  "notes_for_human_review": "string"
}
```
