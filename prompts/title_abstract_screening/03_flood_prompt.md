# Flood Title/Abstract Screening Prompt

You are screening for the flooding/inundation module of a systematic review on climate hazards and mental health.

Use only the provided title and abstract. Do not use outside knowledge.

## Topic-specific hazard definition

Eligible flood exposures include:

- flood, flooding, flash flood, riverine flood, coastal flood;
- inundation, flood extent, flood depth, flooded area;
- river gauge exceedance or remotely sensed inundation;
- storm surge flooding;
- flood shelters, flood victims, flood-affected populations;
- government disaster declarations with documented flood attribution.

Heavy precipitation, heavy rainfall, extreme rainfall, rainstorm, downpour, pluvial rainfall, or monsoon rain are not eligible flood exposures by themselves under the final PROSPERO exposure definition. They support the flood module only when the title/abstract also indicates flooding, inundation, storm surge, river overflow, flood extent/depth, flood victims/shelters, property flooding, or documented flood attribution.

Boundary cases:

- Hurricane/typhoon records should be routed to `flood` only if the title/abstract contains a flood-specific exposure, flood-specific outcome, storm surge flooding, or flood framing.
- Generic natural disaster records with mental health but no named hazard should be `INCLUDE` only if flood is plausible from the abstract; otherwise set `review_flag = true`.

Do not treat these as eligible flood exposure unless human mental health is also studied:

- hydrology-only flood modelling;
- flood engineering, drainage, river management, rainfall-runoff models;
- heavy precipitation, extreme rainfall, rainstorms, downpours, or pluvial rainfall without flooding/inundation, storm surge, river overflow, flood disaster, or flood-attribution pathway;
- flood risk perception with no mental-health/wellbeing outcome;
- physical injury, infectious disease, or property damage only.

## Eligible outcomes

Eligible outcomes include PTSD, depression, anxiety, psychological distress/stress, suicide, suicidal ideation, self-harm, psychiatric emergency visits/admissions, mental-health service use, subjective wellbeing, life satisfaction, affect, climate anxiety, eco-anxiety, solastalgia, and ecological grief.

## Decision rules

- `INCLUDE` if the title/abstract plausibly reports a human empirical study linking flooding/inundation to an eligible mental-health or wellbeing outcome.
- `INCLUDE` with `review_flag = true` if flooding and mental health are both plausible but exposure attribution or study details are incomplete.
- `EXCLUDE` as `wrong_hazard` if the title/abstract studies heavy precipitation/rainfall as the exposure without a flood, inundation, storm surge, river overflow, disaster declaration, displacement, sheltering, property flooding, or flood-attribution pathway.
- Do not exclude only because the abstract does not prove objective exposure linkage, within-unit temporal design, or extractable effect estimate.

Return exactly one JSON object:

```json
{
  "dedup_id": "string",
  "topic": "flood",
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
