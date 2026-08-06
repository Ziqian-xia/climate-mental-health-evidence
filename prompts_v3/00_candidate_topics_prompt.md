# Candidate Topics Labeling Prompt

> **Version: v3** — adds a *Design discipline* section (gate G5: the study must exploit
> within-unit variation in hazard exposure) and aligns this file with `screening_criteria_v3.md`.
> All original v2 content below is unchanged; v3 only inserts additional constraints.


> **Version: v2** — adds an *Outcome discipline* section and aligns this file with `screening_criteria_v2.md`. All original v1 content below is unchanged; v2 only inserts additional constraints.


You are labeling candidate hazard topics for title/abstract records in a systematic review on climate hazards and mental health.

Use only the provided title and abstract. Do not use outside knowledge.

Your task is NOT to decide final inclusion or exclusion. Your task is only to assign one or more candidate hazard topics so that the record can be sent to the correct topic-specific screening prompt.

This prompt follows the final PROSPERO registration and supplementary search formula, but it is a routing prompt, not a final eligibility prompt. Use a loose, high-recall standard within the five registered hazard modules.

## Candidate topics

Return any topic that is plausibly present in the title or abstract:

- `temperature`
- `wildfire`
- `flood`
- `cyclone`
- `drought`

Records may receive multiple topics. Do not force exactly one topic.

## Topic definitions

### temperature

Use `temperature` for ambient/environmental heat or cold exposure:

- heat, extreme heat, hot weather, heatwave;
- cold, cold spell, cold snap, cold wave, low temperature;
- daily mean/maximum/minimum temperature;
- apparent temperature, heat index, Wet Bulb Globe Temperature, humidex;
- diurnal temperature range;
- non-linear ambient temperature functions;
- temperature variability when framed as ambient/environmental exposure.

Do not assign `temperature` for body temperature, fever, hand temperature, clinical hypothermia, heat shock proteins, cellular heat stress, or lab-only thermal exposure unless ambient/environmental temperature is also present.

### wildfire

Use `wildfire` for wildfire/fire-smoke exposure:

- wildfire, bushfire, forest fire, landscape fire;
- wildfire smoke, fire smoke, smoke plume explicitly linked to fire;
- fire-attributed PM2.5;
- smoke-day products;
- fire radiative power, burn area, fire perimeter/proximity;
- fire evacuation or official fire disaster declaration.

Do not assign `wildfire` for generic PM2.5, generic air pollution, haze, tobacco smoke, cooking smoke, structural fire, house fire, burn injuries, or fire ecology unless wildfire/fire-smoke exposure is explicit.

### flood

Use `flood` for flooding or inundation:

- flood, flooding, flash flood, riverine flood, coastal flood;
- inundation, flood extent, flood depth, flooded area;
- river gauge exceedance, remotely sensed inundation;
- storm surge flooding;
- flood shelter, flood victims, flood-affected population;
- government disaster declaration with flood attribution.

For hurricane/typhoon records, also assign `flood` only when flood, inundation, storm surge, or flood-specific exposure/outcome is mentioned.

Do not assign `flood` for heavy precipitation, heavy rainfall, extreme rainfall, rainstorm, downpour, pluvial rainfall, monsoon rain, rainfall anomalies, or rainfall-runoff modeling unless the title/abstract also indicates flooding, inundation, storm surge, river overflow, flood extent/depth, flood victims/shelters, property flooding, or documented flood attribution.

### cyclone

Use `cyclone` for tropical cyclone/hurricane/typhoon exposure:

- tropical cyclone, hurricane, typhoon, tropical storm;
- named storms framed as hurricanes, typhoons, or tropical cyclones;
- storm track, landfall, wind speed, central pressure, storm intensity;
- Saffir-Simpson category or IBTrACS.

Do not assign `cyclone` for generic storms, thunderstorms, winter storms, tornadoes, or meteorological forecasting unless a tropical cyclone/hurricane/typhoon exposure is explicit.

### drought

Use `drought` for drought or water scarcity:

- drought, severe drought, prolonged dry spell;
- water scarcity or water shortage when framed as environmental drought exposure;
- SPEI, PDSI, SPI, Palmer Drought Severity Index, Standardised/Standardized Precipitation Index;
- rainfall deficit or precipitation deficit when framed as drought/water scarcity;
- satellite-derived soil-moisture anomaly when framed as drought;
- drought disaster declaration or drought-affected area/time.

Do not assign `drought` for plant drought stress, crop physiology, irrigation modelling, soil science, water quality, sanitation, or water policy unless human environmental drought/water scarcity exposure is also present.

## Mental-health signal

Also label whether the title/abstract contains a mental-health or wellbeing signal:

- depression, anxiety, psychological distress, psychological stress;
- PTSD or post-traumatic stress;
- suicide, suicidal ideation, self-harm;
- psychiatric emergency visit, psychiatric admission, mental-health service use;
- subjective wellbeing, life satisfaction, affect;
- climate anxiety, eco-anxiety, solastalgia, ecological grief.

This field is only for prioritisation and audit. Do not use it to remove candidate topics.

## Labeling rules

- Assign every plausible registered topic. A record can be `["cyclone", "flood"]`, `["temperature", "wildfire"]`, etc.
- If no eligible or plausibly eligible hazard topic is present, return an empty list for `candidate_topics`.
- If the abstract says only "natural disaster", "climate event", or "extreme weather" without naming a specific hazard, return an empty `candidate_topics` list and set `needs_human_topic_review = true`.
- If the title contains a topic signal but the abstract is missing or vague, assign the topic and set `needs_human_topic_review = true`.
- If a term is ambiguous, prefer a broad candidate label with `needs_human_topic_review = true` rather than dropping a potentially eligible topic.
- Heavy precipitation/rainfall terms alone are not a registered topic. Do not assign a candidate topic for them unless one of the five registered hazards is also present.
- Do not decide final inclusion/exclusion in this prompt.

## v2 additions

- Do NOT assign a specific hazard topic to a record that refers only to a generic "natural
  disaster", "extreme weather event", "climate change", or "environmental disaster" without naming
  or clearly implying one of the five hazards. Return an empty `candidate_topics` list and set
  `needs_human_topic_review = true` instead of force-fitting a specific topic.
- Set `needs_human_topic_review = true` only for records that plausibly concern a human population
  AND carry either a mental-health/wellbeing signal or a genuine unnamed-disaster cue. A record with
  no mental-health/wellbeing signal and no eligible hazard needs no topic review: return empty
  `candidate_topics` and `needs_human_topic_review = false`.

## Output

Return exactly one JSON object:

```json
{
  "dedup_id": "string",
  "candidate_topics": ["temperature", "flood"],
  "mental_health_signal": "yes | no | unclear",
  "human_population_signal": "yes | no | unclear",
  "topic_confidence": {
    "temperature": 0.0,
    "wildfire": 0.0,
    "flood": 0.0,
    "cyclone": 0.0,
    "drought": 0.0
  },
  "needs_human_topic_review": true,
  "topic_evidence": {
    "temperature": "short evidence phrase or empty string",
    "wildfire": "short evidence phrase or empty string",
    "flood": "short evidence phrase or empty string",
    "cyclone": "short evidence phrase or empty string",
    "drought": "short evidence phrase or empty string"
  },
  "one_line_reason": "string, <=25 words"
}
```

Rules for confidence:

- Use 0.90-1.00 only when the topic is explicit and unambiguous.
- Use 0.60-0.85 when the topic is plausible but incomplete or context-dependent.
- Use 0.00 for topics that are clearly absent.
- If confidence is below 0.60, do not include the topic in `candidate_topics`; instead explain the ambiguity in `one_line_reason` and set `needs_human_topic_review = true` if the record may still be relevant.

The downstream screening script should run the topic-specific prompt for each value in `candidate_topics`. If `candidate_topics` is empty but `needs_human_topic_review = true`, send the record to human topic review rather than automatically excluding it.
