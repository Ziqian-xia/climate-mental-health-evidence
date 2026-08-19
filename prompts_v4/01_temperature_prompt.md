# Temperature Title/Abstract Screening Prompt

> **Version: v4** — three changes, all narrow:
> (1) the `exclusion_code` enum in the output schema below now includes **`wrong_design`**, the code
> the v3 *Design discipline* section already instructs you to emit (it was missing from the enum);
> (2) the hazard-gate code is renamed `wrong_hazard` -> **`wrong_exposure`**, matching
> `screening_criteria_v4.md`, which has always used that name;
> (3) `01_temperature_prompt.md` gains an explicit **Setting requirement** section excluding
> laboratory / climate-chamber / engineered-indoor thermal exposure. Everything else is byte-identical
> to v3. See `README.md` for the full changelog.

> **Version: v3** — adds a *Design discipline* section (gate G5: the study must exploit
> within-unit variation in hazard exposure) and aligns this file with `screening_criteria_v4.md`.
> All original v2 content below is unchanged; v3 only inserts additional constraints.


> **Version: v2** — adds an *Outcome discipline* section and aligns this file with `screening_criteria_v4.md`. All original v1 content below is unchanged; v2 only inserts additional constraints.


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

### Setting requirement (v4)

The temperature exposure must arise as a **naturally occurring environmental condition experienced by
the study population**. `EXCLUDE` with `exclusion_code = "wrong_exposure"` when the title/abstract makes
clear that the thermal exposure was **staged by the investigators or produced by an engineered indoor
environment**, including:

- climate chamber, environmental chamber, thermal chamber, controlled-climate room or booth;
- laboratory heat or cold exposure sessions; cold-pressor tests; water-immersion protocols;
  experimentally applied thermal pain stimuli;
- cold-storage depots, freezer rooms, refrigerated warehouses, blast chillers, and other refrigerated
  or artificially heated workplaces where the temperature is machine-generated;
- sauna, cryotherapy, therapeutic heating or cooling, and induced hypothermia.

Apply this **even when the abstract calls the chamber temperature "ambient"** (chamber studies routinely
do), and **even when the study design is otherwise eligible** — a within-subject chamber crossover
identifies its own effect perfectly well; it simply is not a climate hazard. The failure is on the
**hazard gate (G2)**, not the design gate (G5), so the code is `wrong_exposure`, never `wrong_design`.

Worked example — `EXCLUDE`, `wrong_exposure`:
*"12 subjects underwent different cold exposures at -5 C, -10 C, and -15 C in a climate chamber.
Cognitive function was measured with the Neurobehavioral Core Test Battery ... mood effects
(confusion-bewilderment) ..."* — real ambient-temperature wording, clean within-subject design, still
ineligible, because the cold was manufactured for the experiment.

Scope limit — do NOT use this rule to exclude:

- **outdoor workers, farmers, construction and agricultural labourers, or any occupational group exposed
  to naturally occurring outdoor heat or cold.** They are a core exposed population and remain eligible.
  The distinction is machine-generated vs naturally occurring, not occupational vs general population;
- indoor exposure to naturally occurring heat or cold (e.g. housing without air conditioning during a
  heatwave, fuel-poor households during a cold spell) — the temperature there is of outdoor origin;
- records where the abstract does not state the setting. If it is unclear whether the exposure was
  naturally occurring or staged, output `INCLUDE` with `review_flag = true`. Never exclude on silence.


## Eligible outcomes

Eligible outcomes include depression, anxiety, psychological distress/stress, PTSD, suicide, suicidal ideation, self-harm, psychiatric emergency visits/admissions, mental-health service use, subjective wellbeing, life satisfaction, affect, climate anxiety, eco-anxiety, solastalgia, and ecological grief.

## Decision rules

- `INCLUDE` if the title/abstract plausibly reports a human empirical study linking ambient temperature to an eligible mental-health or wellbeing outcome.
- `INCLUDE` with `review_flag = true` if ambient temperature and mental health are both plausible but the abstract is incomplete.
- `EXCLUDE` only when the record clearly fails one gate.
- Do not exclude only because the abstract does not prove objective exposure linkage, within-unit temporal design, or extractable effect estimate.

## v2 additions (apply these when deciding INCLUDE / EXCLUDE above)

These refine the Decision rules above and align this prompt with the shared criteria
(`screening_criteria_v4.md`). Where the shared criteria say MAYBE, output `INCLUDE` with
`review_flag = true` — this prompt uses INCLUDE/EXCLUDE + `review_flag` and does not emit MAYBE.
Study design/identification (time-series, quasi-experimental, cross-sectional, etc.) is NOT a gate
at title/abstract; never exclude on design grounds here.

### Eligible mental-health / wellbeing outcomes (Y1-Y5, for reference)

- Y1 common mental disorders: depression, anxiety, psychological distress/stress;
- Y2 severe outcomes: PTSD/acute stress, suicide, suicidal ideation, self-harm/NSSI;
- Y3 psychiatric service use: psychiatric ED visits, admissions, mental-health service contacts or disruption;
- Y4 subjective wellbeing: life satisfaction, positive/negative affect, self-rated wellbeing/quality of life;
- Y5 climate-related psychological responses: eco-anxiety, climate anxiety, solastalgia, ecological grief;
- Instruments that signal an eligible outcome when named: PHQ-9, GAD-7, K6/K10, PCL-5, IES-R, PSS, CES-D.

### Outcome discipline

The eligible outcome must be a MEASURED mental-health / wellbeing outcome (Y1-Y5) of the study.

`EXCLUDE` as `wrong_outcome` when the study's measured outcome is NOT a mental-health/wellbeing
outcome - even if temperature exposure is present, and even if the title or abstract mentions
"climate change", "mental health", or a psychiatric term in passing. In particular, exclude when
the only measured outcome is:

- physical morbidity or physical/all-cause mortality (e.g. cardiovascular, respiratory, renal,
  musculoskeletal, heat stroke, heat exhaustion, hypothermia, frostbite, physical injury, or death
  from physical causes);
- an infectious-disease outcome (e.g. dengue, malaria, diarrhoeal disease) or hospitalisation /
  mortality for a physical or infectious condition;
- agriculture, crop, livestock, food-security, livelihood, or economic-loss outcomes only;
- purely biophysical, hydrological, climatological, ecological, engineering, modelling, or
  expert-elicitation results with no measured human mental-health outcome.

A mental-health or psychiatric term that appears ONLY as a risk factor, predisposing factor,
comorbidity, covariate, sample-selection criterion, or background/motivation statement is NOT an
eligible outcome. The construct must be something the study MEASURES as an outcome.

Do NOT use this rule to exclude the following - they ARE eligible (keep them):

- suicide, suicidal ideation, or self-harm, including suicide mortality or attempts;
- psychiatric emergency-department visits, psychiatric admissions, or mental-health service use or
  service disruption;
- a record reporting BOTH a physical outcome AND an eligible mental-health outcome - keep it for the
  mental-health component;
- a record where an eligible mental-health outcome is plausibly present but the abstract is
  incomplete - use `INCLUDE` with `review_flag = true`, do not EXCLUDE.

## v3 additions — Design discipline (gate G5)

An eligible study must identify the hazard effect by comparing the **same unit** (person, household,
small area, or facility) **across time** — it must exploit **within-unit variation** in exposure.
Apply this only AFTER the hazard and outcome checks above are satisfied.

### Eligible designs (keep)

- Longitudinal panel or cohort with **repeated measures on the same individuals**, where the hazard
  occurs between waves (pre-post within person);
- Time-series or interrupted time-series on the same unit (daily/weekly counts for a population,
  city, or facility);
- Case-crossover, including time-stratified case-crossover (each case is its own control);
- Difference-in-differences, event-study, fixed-effects panel, regression-discontinuity, or
  instrumental-variable designs built on the same units over time.

**Self-reported outcomes are eligible** provided measurement is repeated: the same person reports
mental health on several occasions and the hazard strikes between measurements.

### Ineligible designs — `EXCLUDE` with `exclusion_code = "wrong_design"`

Exclude when the abstract **explicitly states** a design that cannot identify a within-unit effect:

- **cross-sectional** — a single survey or assessment administered once, however large the sample,
  including post-disaster surveys that measure symptoms only after the event;
- **one-wave** — a single post-hazard assessment compared with a separate unexposed sample or with
  population norms, rather than with the same units before exposure;
- **qualitative / interview-based** — interviews, focus groups, ethnography, phenomenology, or
  thematic analysis with no repeated quantitative measurement;
- **case report or case series** — clinical vignettes or small-N descriptive accounts;
- **ecological correlation with no within-unit time variation** — e.g. season-of-birth or
  cross-country correlations;
- **intervention or treatment-efficacy studies** — trials of therapies, counselling, or digital
  tools after a hazard (these estimate the treatment effect, not the hazard effect).

### When the design is not stated — do NOT exclude

- If the abstract does **not** state the design, or states it ambiguously (e.g. "prospective"
  without the number of waves), output `INCLUDE` with `review_flag = true`. Never EXCLUDE on silence.
- If there is **no abstract**, judge on the title and output `INCLUDE` with `review_flag = true`.
- Repeated post-hazard follow-ups with **no pre-hazard baseline** (e.g. 6 months, 2 years, and
  7 years after the event) are a **boundary case**: output `INCLUDE` with `review_flag = true`.

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
  "exclusion_code": "NA | wrong_exposure | wrong_outcome | not_human_empirical | non_original | animal_or_lab_only | wrong_design",
  "one_line_reason": "string, <=25 words",
  "notes_for_human_review": "string"
}
```
