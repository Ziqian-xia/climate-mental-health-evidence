# Candidate Hazard Topics Router

> **Version: v4.2** - clarified hazard identity and human topic review rules.

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

## Human topic review flag

The `needs_human_topic_review` flag concerns unresolved hazard identity or incomplete
routing coverage only. It is not a general uncertainty flag.

Set it to `true` only when ALL of the following conditions hold:

1. The supplied text supports a potentially eligible climate, weather, or disaster
   exposure. A generic reference such as `natural disaster` can provide this support
   when it describes the exposure being studied.
2. The record remains plausibly relevant to human mental health or wellbeing.
3. The hazard identity cannot be resolved from the supplied text, and the assigned
   candidate topics cannot adequately cover that unresolved exposure.

Set it to `false` when all plausible registered hazard interpretations can be evaluated
by the assigned candidate topics. Assign every supported candidate topic, including
multiple topics when needed. Low confidence must not prevent routing and does not,
by itself, justify setting the review flag. Confidence is descriptive, never a threshold.

Uncertainty about natural versus manufactured exposure, outcome eligibility, study
design, originality, effect-size extraction, or risk-of-bias details belongs to the
relevant hazard module and does not, by itself, justify human TOPIC review. An assigned
module may still return REVIEW under the unchanged eligibility criteria.

Distinguish an unidentified hazard from an absent hazard. An absent hazard mention,
an unrelated use of words such as `cold`, `stress`, or `fire`, or a clearly non-registered
exposure is not an unidentified eligible hazard. Do not infer an exposure that the
supplied text does not support. Human mental-health relevance alone is insufficient
to trigger the flag.

When the flag is `true`, use `one_line_reason` to identify the supported exposure and
the specific unresolved hazard information. Do not merely say that full text is needed.

Mental-health signals include depression, anxiety, distress, perceived stress, PTSD, suicide,
self-harm, psychiatric service use, subjective wellbeing, life satisfaction, affect, climate anxiety,
solastalgia, ecological grief, and person-level psychological resilience/coping/quality of life.

Return exactly one JSON object. The example illustrates the structure; replace all
example values with record-specific findings, including the review flag:

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
  "needs_human_topic_review": false,
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

## Empty topic lists

Use an empty topic list when no specific registered topic is supported as a plausible
candidate. Do not force an arbitrary topic to avoid an empty list.

- Empty list plus `needs_human_topic_review=true`: a potentially eligible hazard is
  supported, but its identity is unresolved. The downstream result is REVIEW.
- Empty list plus `needs_human_topic_review=false`: no registered hazard is supported,
  or the only identified exposure is clearly outside scope. The downstream result
  is EXCLUDE.

## Routing examples

These examples illustrate routing only. Module eligibility criteria are unchanged.

- PTSD after an unspecified `natural disaster`: `candidate_topics=[]`, flag `true`.
  Reason: `PTSD after a natural disaster; disaster type is not identified.`
- Perinatal factors and ADHD, with `cold with fever` referring to illness and no
  environmental hazard: `candidate_topics=[]`, flag `false`.
  Reason: `Perinatal factors and ADHD; no registered environmental hazard is reported.`
- Earthquake exposure only, with no additional potentially eligible hazard:
  `candidate_topics=[]`, flag `false`.
- A human cold-pressor experiment: `candidate_topics=["temperature"]`, flag `false`.
  The temperature module assesses manufactured-exposure eligibility.
- Explicit flooding and anxiety, with unclear study design:
  `candidate_topics=["flood"]`, flag `false`. The flood module may return REVIEW.
- A hurricane with explicitly reported flooding, with no additional unresolved
  hazard: `candidate_topics=["cyclone","flood"]`, flag `false`.
- An identified flood plus a separate unspecified natural disaster associated with
  psychological outcomes: `candidate_topics=["flood"]`, flag `true` if the second
  exposure cannot be covered by the assigned topic. Explain the unresolved disaster.

## Final consistency check

Before returning JSON, verify that every assigned topic has textual support and all
plausible registered topics are covered. If the flag is `true`, identify a supported,
potentially eligible exposure whose identity remains unresolved beyond that coverage.
Ensure the reason, evidence, candidate topics, and review flag are consistent.
Do not set the flag solely for absent hazard information or module-level uncertainty.
