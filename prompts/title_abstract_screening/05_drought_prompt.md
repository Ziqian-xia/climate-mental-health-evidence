# Drought Title/Abstract Screening Prompt

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
