# LLM Agent README: Title/Abstract Screening Prompts

This directory contains the prompt set for LLM-assisted title/abstract screening after DOI/title deduplication.

Use this README when another LLM agent is asked to run, revise, audit, or explain the prompts.

## Source Of Truth

The final PROSPERO files are the source of truth:

- `PROSPERO/PROSPERO.pdf`
- `PROSPERO/SM-search formula.pdf`

Only five registered hazard modules are allowed:

1. `temperature`
2. `wildfire`
3. `flood`
4. `cyclone`
5. `drought`

Do not add a sixth topic unless the project lead explicitly approves a protocol amendment. In particular, heavy precipitation, heavy rainfall, extreme rainfall, rainstorm, downpour, and pluvial rainfall are not standalone registered modules. They are relevant to `flood` only when the title/abstract also indicates flooding, inundation, storm surge, river overflow, flood extent/depth, flood victims/shelters, property flooding, or documented flood attribution.

## Prompt Files

- `00_candidate_topics_prompt.md`: assigns one or more candidate topics from the five registered modules. This is routing only, not inclusion/exclusion.
- `01_temperature_prompt.md`: screens ambient heat/cold and mental health.
- `02_wildfire_prompt.md`: screens wildfire/fire-smoke exposure and mental health.
- `03_flood_prompt.md`: screens flooding/inundation and mental health.
- `04_cyclone_prompt.md`: screens tropical cyclone/hurricane/typhoon exposure and mental health.
- `05_drought_prompt.md`: screens drought/water scarcity and mental health.

## Required Input

Pass one deduplicated record at a time. Minimum fields:

```json
{
  "dedup_id": "D0000001",
  "title": "string",
  "abstract": "string",
  "year": "string",
  "journal": "string"
}
```

If the abstract is missing, pass an empty string. Do not invent abstract content.

## Required Workflow

1. Run `00_candidate_topics_prompt.md` on every deduplicated record.
2. For each topic in `candidate_topics`, run the matching topic-specific prompt.
3. If `candidate_topics` is empty and `needs_human_topic_review = true`, send the record to human topic review.
4. Keep the record if any topic-specific prompt returns `INCLUDE`.
5. Human-review every record with `review_flag = true`.
6. Exclude only when all applicable topic-specific prompts clearly return `EXCLUDE`.

## Screening Philosophy

Use high recall at title/abstract screening.

Do not exclude only because the abstract does not prove:

- objective environmental exposure linkage;
- within-unit temporal identification;
- extractable effect estimate;
- exact exposure contrast;
- full-text availability;
- peer-reviewed status.

Those are full-text or extraction-stage questions unless the title/abstract clearly rules out eligibility.

## Registered Outcome Families

The prompts treat these as eligible mental-health/wellbeing outcomes:

- common mental disorders: depression, anxiety, psychological distress, psychological stress;
- severe outcomes: PTSD, post-traumatic stress, suicide, suicidal ideation, self-harm;
- psychiatric service use: psychiatric ED visits, inpatient admissions, mental-health service contacts;
- subjective wellbeing: life satisfaction, positive/negative affect, self-rated wellbeing;
- climate-related psychological responses: climate anxiety, eco-anxiety, solastalgia, ecological grief.

Physical health outcomes alone are not eligible.

## Handling Unclear Records

At candidate-topic assignment:

- If a registered hazard is plausible, assign the topic.
- If the hazard is ambiguous but could be one of the registered modules, use `needs_human_topic_review = true`.
- If only unregistered hazards are present, do not assign a registered topic.

At topic-specific screening:

- If the registered hazard and eligible outcome are both plausible but details are incomplete, return `INCLUDE` with `review_flag = true`.
- Return `EXCLUDE` only for clearly wrong hazard, clearly wrong outcome, non-human/non-empirical content, non-original records, or animal/lab-only records.

## Expected Behavior On The Jacob 100 Pilot

The four currently included records should remain included:

- summer temperature variability and depressive symptoms;
- wildfire disaster and psychological effects;
- Hurricane Florence and youth crisis text patterns;
- flood victims/shelters and mental health.

Most other records should be excluded for wrong outcome, wrong exposure, non-human/non-empirical content, or non-original status. Some records may route to a candidate topic first and then be excluded by the topic-specific prompt; that is expected.

## Output Discipline

Each prompt requires exactly one JSON object per record. Do not add prose before or after the JSON when running the prompt in production.

Preserve these fields for auditing:

- `dedup_id`
- `candidate_topics` or `topic`
- `decision`
- `confidence`
- `review_flag` or `needs_human_topic_review`
- `exclusion_code`
- `one_line_reason`
- `notes_for_human_review`

Do not use model confidence as the screening decision. Confidence is an audit field only.
