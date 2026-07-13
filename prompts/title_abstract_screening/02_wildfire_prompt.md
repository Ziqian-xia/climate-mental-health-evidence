# Wildfire Title/Abstract Screening Prompt

You are screening for the wildfire module of a systematic review on climate hazards and mental health.

Use only the provided title and abstract. Do not use outside knowledge.

## Topic-specific hazard definition

Eligible wildfire exposures include:

- wildfire, bushfire, forest fire, landscape fire;
- wildfire smoke or fire-attributed PM2.5;
- smoke-day products or smoke plume exposure explicitly linked to wildfire;
- fire radiative power, burn area, fire perimeter/proximity;
- official evacuation orders or disaster declarations with fire attribution;
- binary fire presence in a defined area/time unit.

Do not treat these as eligible wildfire exposure unless explicit wildfire/fire attribution is present:

- generic PM2.5, air pollution, haze, or smoke with no fire attribution;
- tobacco smoke, marijuana smoke, cooking smoke, indoor smoke;
- structural fires, house fires, industrial fires, burn injuries;
- fire ecology, forest management, animal habitat, or firefighter physiology with no human mental-health outcome.

## Eligible outcomes

Eligible outcomes include depression, anxiety, psychological distress/stress, PTSD, suicide, suicidal ideation, self-harm, psychiatric emergency visits/admissions, mental-health service use, subjective wellbeing, life satisfaction, affect, climate anxiety, eco-anxiety, solastalgia, and ecological grief.

## Decision rules

- `INCLUDE` if the title/abstract plausibly reports a human empirical study linking wildfire exposure to an eligible mental-health or wellbeing outcome.
- `INCLUDE` with `review_flag = true` if wildfire exposure and mental health are both plausible but exposure attribution or study details are incomplete.
- `EXCLUDE` generic air pollution/PM2.5 records unless the title/abstract explicitly links exposure to wildfire, fire smoke, fire season attribution, fire perimeter, burn area, or official fire events.
- Do not exclude only because the abstract does not prove objective exposure linkage, within-unit temporal design, or extractable effect estimate.

Return exactly one JSON object:

```json
{
  "dedup_id": "string",
  "topic": "wildfire",
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
