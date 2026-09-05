# Candidate Hazard Topics Router

> **Version: v4.1** - consistency and safety revision of v4.

Assign every plausibly present registered hazard topic using only the supplied title and abstract.
This is routing, not final eligibility screening. Be liberal at this step.

## Topics

- `temperature`: ambient/environmental heat or cold, heatwave/cold spell, daily temperature,
  apparent temperature, heat index, WBGT, humidex, or temperature variability. Also route explicit
  human climate-chamber or manufactured thermal studies to this module so it can record
  `wrong_exposure`; do not route body temperature, fever, cellular heat stress, or heat-shock proteins.
- `wildfire`: wildfire/bushfire/forest or landscape fire, wildfire smoke, fire-attributed PM2.5,
  smoke day, burn area/perimeter/proximity, or fire evacuation. Do not route generic pollution,
  tobacco/cooking smoke, structural fires, burn injuries, or fire ecology.
- `flood`: flood, inundation, river overflow, storm-surge flooding, flood extent/depth, flood victims,
  shelters, property flooding, or documented flood attribution. Heavy precipitation/rainfall alone
  is not a registered topic.
- `cyclone`: tropical cyclone, hurricane, typhoon, tropical storm, named tropical storm, landfall,
  storm track or cyclone intensity. Do not route generic storms, thunderstorms, winter storms or tornadoes.
- `drought`: drought, environmental water scarcity, prolonged dry spell, SPEI/PDSI/SPI, rainfall
  deficit framed as drought, or drought-framed soil-moisture anomaly.

Multiple topics are allowed. Cyclone records receive `flood` too only when flooding or storm surge
is mentioned.

If a record plausibly concerns humans and mental health but says only `natural disaster`, `extreme
weather`, `climate event`, or another unnamed hazard, return no forced topic and set
`needs_human_topic_review=true`. If a plausible named topic is ambiguous, assign it regardless of
low confidence and set the review flag. Confidence is descriptive and is never a routing threshold.

Mental-health signals include depression, anxiety, distress, perceived stress, PTSD, suicide,
self-harm, psychiatric service use, subjective wellbeing, life satisfaction, affect, climate anxiety,
solastalgia, ecological grief, and person-level psychological resilience/coping/quality of life.

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

Use an empty topic list only when no named topic is even plausible. The downstream pipeline must
return REVIEW, not EXCLUDE, when that empty list is paired with `needs_human_topic_review=true`.
