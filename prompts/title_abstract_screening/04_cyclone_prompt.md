# Tropical Cyclone Title/Abstract Screening Prompt

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
