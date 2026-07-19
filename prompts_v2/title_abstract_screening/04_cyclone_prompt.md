# Tropical Cyclone Title/Abstract Screening Prompt

> **Version: v2** — adds an *Outcome discipline* section and aligns this file with `docs/screening_criteria_v2.md`. All original v1 content below is unchanged; v2 only inserts additional constraints.


You are screening for the tropical cyclone/hurricane/typhoon module of a systematic review on climate hazards and mental health.

Use only the provided title and abstract. Do not use outside knowledge.

## Topic-specific hazard definition

Eligible cyclone exposures include:

- tropical cyclone, hurricane, typhoon, tropical storm;
- named storms when framed as hurricanes/typhoons/tropical cyclones;
- storm track, landfall, wind speed, central pressure, storm intensity;
- Saffir-Simpson category or IBTrACS.
- exposed versus unexposed populations before/after a hurricane, typhoon, or tropical cyclone.

Boundary cases:

- If the record is about hurricane-related flooding or storm surge and mental health, it can be eligible for both `cyclone` and `flood`.
- If outcomes are pooled across hurricane, flood, and other disaster exposures with no hazard-specific information in the abstract, `INCLUDE` with `review_flag = true`.

Do not treat these as eligible cyclone exposure unless clearly linked to a tropical cyclone/hurricane/typhoon:

- generic storms, thunderstorms, winter storms, tornadoes;
- meteorological forecasting only;
- official disaster declarations that do not identify a tropical cyclone, hurricane, typhoon, or tropical storm;
- physical injury, mortality, or infrastructure damage only;
- disaster preparedness opinions or protocols with no original human mental-health data.

## Eligible outcomes

Eligible outcomes include PTSD, depression, anxiety, psychological distress/stress, suicide, suicidal ideation, self-harm, psychiatric emergency visits/admissions, mental-health service use, subjective wellbeing, life satisfaction, affect, climate anxiety, eco-anxiety, solastalgia, and ecological grief.

## Decision rules

- `INCLUDE` if the title/abstract plausibly reports a human empirical study linking a tropical cyclone/hurricane/typhoon to an eligible mental-health or wellbeing outcome.
- `INCLUDE` with `review_flag = true` if cyclone exposure and mental health are both plausible but hazard-specific estimates or study details are incomplete.
- Do not exclude only because the abstract does not prove objective exposure linkage, within-unit temporal design, or extractable effect estimate.

## v2 additions (apply these when deciding INCLUDE / EXCLUDE above)

These refine the Decision rules above and align this prompt with the shared criteria
(`docs/screening_criteria_v2.md`). Where the shared criteria say MAYBE, output `INCLUDE` with
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
outcome - even if tropical cyclone exposure is present, and even if the title or abstract mentions
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
- a record where an eligible mental-health outcome is plausibly present but the abstract is
  incomplete - use `INCLUDE` with `review_flag = true`, do not EXCLUDE.

Return exactly one JSON object:

```json
{
  "dedup_id": "string",
  "topic": "cyclone",
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
