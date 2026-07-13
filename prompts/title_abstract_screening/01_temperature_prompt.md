# Temperature Title/Abstract Screening Prompt

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
