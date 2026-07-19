# Drought Title/Abstract Screening Prompt

> **Version: v2** — adds an *Outcome discipline* section and aligns this file with `docs/screening_criteria_v2.md`. All original v1 content below is unchanged; v2 only inserts additional constraints.


You are screening for the drought/water scarcity module of a systematic review on climate hazards and mental health.

Use only the provided title and abstract. Do not use outside knowledge.

## Topic-specific hazard definition

Eligible drought exposures include:

- drought, severe drought, prolonged dry spell;
- water scarcity or water shortage when framed as environmental drought exposure;
- Standardised Precipitation-Evapotranspiration Index (SPEI);
- Palmer Drought Severity Index (PDSI);
- Standardised Precipitation Index (SPI);
- rainfall deficit or precipitation deficit when framed as drought/water scarcity;
- satellite-derived soil-moisture anomaly when framed as drought;
- drought disaster declaration or drought-affected area/time.

Boundary cases:

- Agricultural livelihood pathways can be eligible if the exposure is drought/water scarcity and the outcome is human mental health.
- Climate anxiety/eco-anxiety records are eligible only when linked to objective drought/environmental change, not only general climate concern.

Do not treat these as eligible drought exposure unless human mental health is also studied:

- plant drought stress, crop physiology, soil science, irrigation modelling;
- water policy, water quality, or sanitation without drought framing;
- livestock, ecology, or hydrology-only records;
- heavy precipitation, heavy rainfall, extreme rainfall, or rainstorms unless framed as drought/water scarcity through deficit indices or dry conditions;
- economic loss only with no mental-health/wellbeing outcome.

## Eligible outcomes

Eligible outcomes include depression, anxiety, psychological distress/stress, PTSD, suicide, suicidal ideation, self-harm, psychiatric emergency visits/admissions, mental-health service use, subjective wellbeing, life satisfaction, affect, climate anxiety, eco-anxiety, solastalgia, and ecological grief.

## Decision rules

- `INCLUDE` if the title/abstract plausibly reports a human empirical study linking drought/water scarcity to an eligible mental-health or wellbeing outcome.
- `INCLUDE` with `review_flag = true` if drought exposure and mental health are both plausible but exposure metrics or study details are incomplete.
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
outcome - even if drought exposure is present, and even if the title or abstract mentions
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
  "topic": "drought",
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
