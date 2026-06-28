# Title/Abstract Screening Criteria: Causal Impacts of Diverse Climate Hazards on Global Mental Health

Criteria version: v1 (DRAFT — pending project review)
Derived from: Protocol "Causal impacts of diverse climate hazards on global mental health" (PRISMA-P 2015).
Stage: Title/abstract screening only. This is a recall-first screen. Final design eligibility,
risk of bias, and quantitative eligibility are decided at FULL TEXT by two human reviewers — NOT here.

---

## Screening philosophy (read first)

This title/abstract pass exists to remove records that are clearly out of scope while keeping
everything that plausibly meets the protocol. The protocol deliberately runs ONE broad search
per database with no design-term filter, because no validated search filter exists for
time-series / quasi-experimental designs and abstracts frequently omit the design. Design
eligibility is therefore applied at full text, not here.

Consequence for this screen: **do not EXCLUDE a record merely because it does not state an
eligible study design, sample, exposure metric, or effect estimate in the abstract.** Those
are full-text decisions. At this stage we gate only on the two things an abstract reliably
reveals: (1) a relevant climate hazard exposure and (2) a relevant mental-health/wellbeing
outcome. When in doubt, route to MAYBE.

---

## Review question

Does this record report (or plausibly report) an empirical study estimating the effect of one
of five climate hazards — extreme temperature, wildfire, flooding, tropical cyclone, or drought
— on a human mental-health or wellbeing outcome?

---

## Vocabulary

- **X = eligible climate hazard exposure**, one of five modules:
  - X1 Temperature: ambient heat OR cold, heatwave, cold spell/snap, heat index, Wet Bulb Globe
    Temperature, apparent temperature, diurnal temperature range. (Full distribution — cold is in scope.)
  - X2 Wildfire: wildfire, bushfire, forest fire, landscape fire, wildfire smoke, fire-attributable
    PM2.5, smoke day, fire perimeter/proximity, fire evacuation.
  - X3 Flooding: flood, flash flood, riverine/coastal flooding, inundation, storm surge flooding.
  - X4 Tropical cyclone: hurricane, typhoon, tropical cyclone/storm (named storms count).
  - X5 Drought: drought, water scarcity, prolonged dry spell, drought indices (SPEI, PDSI, SPI),
    soil-moisture anomaly framed as drought.
- **Y = eligible mental-health / wellbeing outcome**, five families:
  - Y1 Common mental disorders: depression, anxiety, psychological distress, psychological stress.
  - Y2 Severe outcomes: PTSD/post-traumatic stress, suicide, suicidal ideation, self-harm, NSSI.
  - Y3 Psychiatric service utilisation: psychiatric ED visits, hospitalisation/admission, mental-health
    service contacts.
  - Y4 Subjective wellbeing: life satisfaction, positive/negative affect, self-rated wellbeing.
  - Y5 Climate-related psychological responses: eco-anxiety, climate anxiety, solastalgia, ecological grief.
  - Validated instruments that signal Y when named: PHQ-9, GAD-7, K6/K10, PCL-5, IES-R, PSS, CES-D, etc.
- **Z = design/identification cue (informational only at this stage, NOT an exclude gate):**
  time-series, case-crossover, distributed lag (DLM/DLNM), panel/fixed-effects, difference-in-differences,
  event study, interrupted time-series, longitudinal cohort with spatiotemporal climate linkage.
  Cross-sectional / ecological / case-control are eligible to PASS this screen (they are sorted at full text
  into the narrative stratum or excluded there).

---

## Gate sequence

```
G1 Human-relevant record?        -> NO: EXCLUDE (animal-only / lab-only / plant / pure physical-science)
   |
G2 Eligible hazard exposure X?   -> NO: EXCLUDE (wrong_exposure)
   |                                 UNCLEAR: MAYBE
G3 Eligible MH/wellbeing out. Y?  -> NO: EXCLUDE (wrong_outcome)
   |                                 UNCLEAR: MAYBE
G4 Empirical study (not review/   -> NO: EXCLUDE (non_original)
   editorial/protocol/news)?         UNCLEAR: MAYBE
   |
=> INCLUDE
```

Each gate routing:
- **YES** → pass to next gate.
- **NO** → EXCLUDE with the matching exclusion_code (only when clearly true).
- **UNCLEAR** → MAYBE (do not advance, do not exclude), except G1 which excludes only when the record
  is clearly non-human (e.g. a rodent thermoregulation study, a materials-science fire paper).

Design (Z) is NOT a gate. Risk of bias, exposure-metric objectivity, comparator, and presence of a
quantitative effect estimate are NOT gates at title/abstract. They are recorded at full text.

---

## Include

Mark **INCLUDE** when the title or abstract clearly indicates ALL of:
1. The record concerns a human population (any age, sex, location, health status).
2. An eligible climate hazard exposure X (X1–X5) is present as a studied exposure.
3. An eligible mental-health/wellbeing outcome Y (Y1–Y5) is present as a studied outcome.
4. The record appears to be an empirical/original study (reports or describes data, analysis,
   participants, a cohort, an area-time series, counts, rates, or effect estimates).

A record meeting 1–4 is INCLUDE even if the design is unstated, the exposure metric is not
described as objective, the effect contrast is unusual, or the abstract is terse. Those are
adjudicated at full text.

---

## Maybe

Mark **MAYBE** (route forward, never discard) when any of:
1. Hazard X is clearly present but the outcome is ambiguous (e.g. "mental health impacts" implied
   but not specified; "wellbeing" used loosely; outcome could be physical rather than mental).
2. Outcome Y is clearly present but the exposure is ambiguous (e.g. "natural disaster," "extreme
   weather," "climate change," "environmental stressor" without specifying which hazard — these
   plausibly map to X1–X5 and must NOT be excluded).
3. The abstract is missing and the title is potentially relevant. (~5% of pool has no abstract;
   judge on title alone and lean toward MAYBE rather than EXCLUDE.)
4. The record is non-English and relevance cannot be confirmed but appears plausible.
5. It is unclear whether the record is an empirical study vs. a review/commentary, but the topic
   is on-target.
6. Borderline exposure terms that may or may not be in scope: air pollution/PM2.5 WITHOUT fire
   attribution (eligible only under wildfire if fire-attributed), general "weather," "seasonality,"
   "temperature" in a non-ambient sense (e.g. body temperature). Route to MAYBE for human resolution.
7. Composite disaster studies ("floods and storms," "multiple hazards") where at least one component
   is an eligible hazard.

---

## Exclude

Mark **EXCLUDE** only when clearly true. Use the matching exclusion_code.
1. `not_human_empirical` — animal-only, in-vitro/laboratory-only, plant/agronomy-only, or pure
   physical/earth-science with no human mental-health outcome.
2. `wrong_exposure` — no eligible climate hazard X at all (e.g. earthquakes, volcanic eruptions,
   air pollution with no fire attribution, pandemics, war, generic "stress" with no climate hazard).
   NOTE: earthquakes, tsunamis, and volcanic events are NOT eligible hazards (not climate hazards).
3. `wrong_outcome` — no eligible mental-health/wellbeing outcome Y (e.g. purely physical morbidity/
   mortality such as cardiovascular or respiratory outcomes with no mental-health measure).
4. `non_original` — systematic review, meta-analysis, scoping/narrative review, editorial, commentary,
   letter, opinion, protocol, conference abstract that is clearly not a primary study, erratum, or news item.
   (If genuinely unsure whether it is primary, use MAYBE, not EXCLUDE.)
5. `animal_or_lab_only` — explicitly animal or laboratory model of heat/cold/etc. with no human outcome.

Do NOT exclude for: unstated study design; cross-sectional/ecological/case-control design (sorted at
full text); self-reported exposure (sorted at full text); missing effect estimate; non-English language;
preprint status (medRxiv/SSRN preprints are eligible); old publication date (no date restriction).

---

## Boundary cases

- Uncertain between INCLUDE and MAYBE → choose **MAYBE**.
- Uncertain between MAYBE and EXCLUDE → choose **MAYBE**.
- Do not exclude only because the design is not described.
- "Natural disaster" / "extreme weather event" / "climate change" with a mental-health outcome →
  MAYBE (do not exclude as wrong_exposure; the specific hazard is resolvable at full text).
- Air pollution + mental health, no fire mention → MAYBE (could be wildfire-attributed on full text).
- Heat + mortality where mortality may include suicide, or "self-harm" buried under injury → MAYBE.
- Temperature affecting sleep, cognition, aggression, or violence → MAYBE (overlaps Y families;
  let full text decide).
- Reviews that may contain extractable primary data → still `non_original` EXCLUDE at this stage;
  the protocol harvests reviews separately via citation tracking, not via this screen.
- Earthquake/tsunami/volcano + mental health → EXCLUDE `wrong_exposure` (these are clearly not among
  the five climate hazards), UNLESS co-reported with an eligible hazard (then MAYBE).
- Conference abstracts: many appear in this pool (esp. Embase). If it describes original data on X and Y,
  treat as INCLUDE/MAYBE (full text/author contact decides); if it is purely a meeting announcement or
  non-data abstract, EXCLUDE `non_original`.

---

## Output schema

Return exactly one JSON object per record:

```json
{
  "dedup_id": "string",
  "decision": "INCLUDE | MAYBE | EXCLUDE",
  "confidence": 0.00,
  "exposure_or_intervention_tag": "temperature | wildfire | flood | cyclone | drought | multiple | unclear | none",
  "outcome_tag": "common_mental_disorder | severe_outcome | service_utilisation | subjective_wellbeing | climate_psychological | multiple | unclear | none",
  "human_empirical_signal": "yes | no | unclear",
  "one_line_reason": "string (<= 25 words, grounded only in title/abstract)",
  "exclusion_code": "NA | not_human_empirical | wrong_exposure | wrong_outcome | non_original | animal_or_lab_only",
  "notes_for_human_review": "string (optional; flag boundary reasoning, language, missing abstract)"
}
```

Rules for fields:
- `confidence` is the model's confidence in its own decision (0–1), not relevance probability.
- `exclusion_code` MUST be `NA` whenever decision is INCLUDE or MAYBE.
- Tags use `unclear` when the dimension is ambiguous, `none` when clearly absent.
- Decisions and reasons must rest ONLY on the provided title and abstract — never external knowledge
  of the paper.

---

## Notes for human audit

- This screen is intentionally over-inclusive. Expect a large MAYBE bucket; that is correct behaviour,
  not a failure. Human reviewers (two, independent, per protocol) resolve MAYBE at full text.
- The protocol's harder eligibility criteria — within-unit temporal identification, objective exposure
  measurement, quantitative effect estimate with uncertainty, ROBINS-E risk of bias — are deliberately
  NOT enforced here. Auditors should confirm that excluded records were removed for hazard/outcome/
  non-original reasons only, never for design or metric reasons.
- Priority audit targets (consistent with SOP Part 4): all MAYBE; all confidence < 0.60; records where
  title and abstract appear inconsistent; records flagged non-English; the ~6,857 records with no abstract;
  and any record in doi_conflict_title_groups.csv.
- Known noisy terms to watch in audit: "fire" (firearms, fire drills), "stress" (oxidative/material
  stress), "depression" (economic/geological/weather depression = a low-pressure system), "storm"
  (brainstorm, cytokine storm), "heat" (body heat, heat of reaction). These drive false INCLUDE/MAYBE
  and should be checked.
- Calibration link: the protocol specifies a 100-record human calibration with Cohen's κ ≥ 0.80 before
  formal screening. The SOP's 100-record Haiku pilot (Part 3) should be reconciled with that calibration
  set so the AI screen and the human dual-screen are measured against the same yardstick.

---

## Open questions for project review (resolve before approval)

1. **Conference abstracts.** Embase contributed many. Treat data-bearing conference abstracts as
   INCLUDE/MAYBE (current draft) or EXCLUDE `non_original` up front? This materially changes volume.
2. **Preprints.** Protocol allows medRxiv/SSRN preprints. Confirm Haiku should not down-rank preprints.
3. **Air-pollution boundary.** Confirm that PM2.5/air-pollution studies without explicit fire attribution
   route to MAYBE (current draft) rather than EXCLUDE.
4. **Cold extremes.** Protocol explicitly includes cold. Confirm reviewers want cold-only studies kept
   (current draft keeps them).
5. **Heat + suicide/violence/aggression** without an explicit psychiatric label — INCLUDE or MAYBE?
6. **Relationship to human dual-screening.** Is Haiku's output (a) a pre-filter that drops clear EXCLUDEs
   before the two human reviewers see the rest, or (b) a non-binding third opinion alongside the humans?
   This governs how conservative the EXCLUDE gate should be.
