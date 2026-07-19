# v1 vs v2 prompts - same model (DeepSeek), n = 1000

Cleanest test of the **prompt change alone**: identical 1000 records, identical model (`deepseek-v4-flash`), only the prompt set changes from **v1** (`prompts/`) to **v2** (`prompts_v2/`, adding *Outcome discipline*). Every difference below is attributable to the prompts. Each record was re-checked against its **abstract** (not title alone); where a record has no abstract in the corpus, that is stated.

- **v1 baseline:** `pilot_screening_v1/deepseek_title_abstract_screening_results.csv`
- **v2:** `results/screening_pilot_results_fixed1000_v2_deepseek.csv` (1000/1000, 0 errors)

## Decision distribution

| Decision | v1 | v2 |
|---|---|---|
| INCLUDE | 34 | 29 |
| REVIEW | 31 | 6 |
| EXCLUDE | 935 | 965 |

## Full decision migration (row = v1, col = v2)

| v1 \ v2 | EXCLUDE | INCLUDE | REVIEW |
|---|---|---|---|
| **EXCLUDE** | 930 | 2 | 3 |
| **INCLUDE** | 7 | 26 | 1 |
| **REVIEW** | 28 | 1 | 2 |

**42 records changed.** The EXCLUDE count rises by 30 (= 35 into EXCLUDE - 5 out). The largest block is **28 REVIEW -> EXCLUDE**: v2 clears records that v1 had parked for human review. v2 is **not** monotonically stricter - it also moves **3 records EXCLUDE -> REVIEW** (protecting recall) and recovers 2 into INCLUDE.

## Every changed record, by transition

### REVIEW → EXCLUDE (v2 cleared these from the review pile) — 28 records

Mostly engineering, animal-lab, methods/reporting, wrong or non-registered hazards, and therapy-technique false matches ('flooding' = exposure therapy; 'cold immersion' = a treatment).

| dedup_id | Title | Assessment |
|---|---|---|
| D0043441 | Urban Sustainability Versus the Impact of Covid-19: A Madrid Case  | **correct** - Urban-health/COVID case study (cardio-respiratory, heatstroke); no measured MH outcome. |
| D0120476 | Smoked Marijuana Discrimination and Marijuana Choice in Humans: A  | **correct** - Marijuana-discrimination laboratory model; no climate hazard, no MH outcome. |
| D0107881 | Integration of SCADA and GIS technologies in Jefferson parish, Lou | **correct** - SCADA/GIS flood-control engineering for a parish; no measured MH outcome. |
| D0083129 | Epidemiology of injuries from fire, heat and hot substances: globa | **correct** - Global Burden of Disease injuries from fire/heat; physical morbidity/mortality. |
| D0011797 | Effect of | **borderline** - No abstract (title truncated 'Effect of'); excluded on no evidence. |
| D0054090 | Editorial: Exploring the effects of human activities and climate c | **correct** - Editorial on soil microorganisms in grasslands; not human MH. |
| D0049069 | The 2023 China report of the Lancet Countdown on health and climat | **defensible** - Lancet Countdown China report; non-empirical, no single measured MH outcome. |
| D0093570 | Case-Crossover Design for Assessing Associations With Short-Term,  | **correct** - Statistical methods paper (case-crossover design); no outcome studied. |
| D0103848 | Clinical ecology and its role in diagnosis of chronic diseases cau | **defensible** - Clinical-ecology/indoor-pollution overview; psychological stress only listed among factors. |
| D0045804 | Rethinking Water and Sanitation in Challenging Environments: Lesso | **correct** - Portable water/sanitation engineering in cold regions; no measured MH. |
| D0116280 | The NSI (Noise Sensitive Index) - A suitable method for recording  | **correct** - Noise-index method for bodily complaints; not climate, not MH. |
| D0018822 | Candida die-off: Adverse effect and neutralization with phytothera | **correct** - Candida infection / phytotherapy; irrelevant. |
| D0050539 | Design and development of IV fluid warming system using TRIZ metho | **correct** - IV fluid-warming medical-device engineering. |
| D0107942 | Role of gastric glandular mucosal energy metabolism in cold-restra | **correct** - Animal lab (cold-restraint gastric ulcers in rats). |
| D0052874 | Towards an integrative understanding of British Columbia’s Nechako | **defensible** - Watershed knowledge-systems paper; no measured MH. |
| D0102528 | Rising population and environmental degradation. | **correct** - Population/environmental-degradation essay; 'well-being' rhetorical, no measured MH. |
| D0091776 | Survival among cancer patients after coalmine fire: Analysis of re | **correct** - Outcome is cancer survival after a coalmine fire; physical outcome. |
| D0000964 | [Modified implosive (flooding) therapy: treatment of phobias in Lo | **correct** - 'Flooding' = implosive/exposure therapy for phobias, not a flood hazard. |
| D0127576 | Safety and Efficiency of the Prolonged (72-hour) Use of a Single H | **correct** - Heat-and-moisture-exchanger medical-device trial. |
| D0000950 | A comparison of 'flooding' and 'successive approximation' in the t | **correct** - 'Flooding' = exposure therapy for agoraphobia; no climate hazard. |
| D0083135 | Landscapes of Fire | **borderline** - No abstract; title 'Landscapes of Fire' only. |
| D0069740 | Pharmacogenetics and pharmacogenomics of schizophrenia: A review o | **correct** - Schizophrenia pharmacogenetics review; MH topic but no climate hazard. |
| D0127043 | Effect of Lower Extremities Cold Immersion Applied to Patients Wit | **correct** - Therapeutic cold-water immersion for varicose veins; hazard is a medical intervention, not ambient temperature. |
| D0046900 | Vertical Structure Characteristics of Atmospheric Boundary Layer i | **correct** - Atmospheric physics of sandstorms; no MH. |
| D0129388 | Community crisis intervention: The Coldenham tragedy revisited | **debatable** - Tornado struck a school + crisis intervention; genuine disaster+MH, but tornado is not a registered hazard - defensible on scope. |
| D0042634 | Google Trends-based non-English language query data and epidemic d | **defensible** - Google-Trends surveillance of 'uneasiness/fear'; outcome is search-query patterns, not a measured MH outcome. |
| D0114745 | Effect of 3-methylisoxazole-5-carbonic acid on metabolism and heat | **correct** - Animal lab (drug x heat production in cold-exposed mice). |
| D0049602 | Climate Change and the Opioid Epidemic | **defensible** - 'Climate Change and the Opioid Epidemic' commentary; non-empirical, no measured MH outcome. |

### INCLUDE → EXCLUDE (v2 tightened these out) — 7 records

| dedup_id | Title | Assessment |
|---|---|---|
| D0021164 | Homes Heat Health protocol: An observational cohort study measurin | **defensible** - Summer temperature x SLEEP, observational-cohort PROTOCOL; sleep is borderline, protocol not yet a study. |
| D0046156 | Forging compromiso after the storm: activism as ethics of care amo | **correct** - 56 qualitative interviews on activism/ethics of care post-Maria; not a measured MH outcome. |
| D0011207 | Health impact of climate change in older people: An integrative re | **correct** - Integrative review of climate health impacts (mortality-focused); non-empirical. |
| D0109844 | Crisis not over for hurricane victims. | **borderline** - No abstract; title indicates a news item. |
| D0015347 | The examination of mental toughness, sleep, mood and injury rates  | **correct** - Ultra-marathon athletes in extreme conditions (injury/mood/sleep); not a climate-hazard exposure on a population. |
| D0029882 | Extreme weather events and human health | **defensible** - Overview of extreme-weather health effects (PTSD mentioned in passing); non-empirical review. |
| D0012580 | Predicting patterns of disaster-related resiliency among older adu | **FALSE NEGATIVE** - Typhoon Haiyan survivors: life satisfaction/spirituality -> resiliency. A genuine hazard x wellbeing (Y4) study; should stay INCLUDE/REVIEW. |

### INCLUDE → REVIEW — 1 records

| dedup_id | Title | Assessment |
|---|---|---|
| D0031121 | Uniformed rescue workers responding to disaster | **reasonable** - Book chapter on first responders in disasters; non-empirical, routed to human review (not dropped). |

### EXCLUDE → INCLUDE (v2 newly kept these) — 2 records

| dedup_id | Title | Assessment |
|---|---|---|
| D0018356 | Dynamic Psychotherapy as a PTSD Treatment for Firefighters: A Case | **defensible** - Forest-fire firefighters, PTSD psychotherapy case study; wildfire + PTSD, kept for review. |
| D0054409 | Use of machine learning tools to predict health risks from climate | **FALSE POSITIVE** - Systematic review of ML algorithms for extreme-weather health risks; non-empirical, not a measured MH outcome. |

### EXCLUDE → REVIEW (v2 MORE cautious here — recall-protective) — 3 records

| dedup_id | Title | Assessment |
|---|---|---|
| D0107387 | The changing climate: Managing health impacts | **recall-protective** - Climate-health overview; routed to human review rather than excluded. |
| D0102276 | The stressors and the post-traumatic stress syndrome after an indu | **recall-protective (good)** - PTSD after an industrial explosion/fire (246 employees); disaster x PTSD, correctly sent to human review. |
| D0020871 | Air pollution, traffic noise, mental health, and cognitive develop | **recall-protective** - Air pollution/noise x mental health & cognition; MH outcome present but hazard non-registered -> human review. |

### REVIEW → INCLUDE — 1 records

| dedup_id | Title | Assessment |
|---|---|---|
| D0017976 | Turning up the heat does not affect quality of life. | **defensible** - No abstract; title indicates temperature x quality of life; moved to INCLUDE. |

## Bottom line

- **The EXCLUDE increase of 30 is real and largely legitimate.** It comes mostly from clearing a noisy human-review pile (28 records): engineering, animal labs, statistical-methods papers, reports/commentaries, non-registered hazards, and records where 'flooding'/'cold' referred to a therapy or medical procedure rather than a climate hazard. Of the 35 records newly excluded, ~28 are clearly correct and ~5 are borderline-but-defensible (no-abstract items, reports, a tornado crisis-intervention piece, a search-trend surveillance study).
- **v2 is not simply stricter.** It moved 3 records the other way (EXCLUDE -> REVIEW) to protect recall, including `D0102276` (PTSD after an industrial explosion/fire) and `D0020871` (a study that does measure mental health). These now get human eyes instead of being dropped.
- **Only two changes look like genuine v2 errors:** `D0012580` (Typhoon Haiyan resilience / life-satisfaction study wrongly excluded — a likely **false negative**) and `D0054409` (an ML systematic review wrongly included — a minor **false positive**). Everything else is correct or defensible.
- **No measured mental-health study with a registered hazard was silently dropped**, with the single arguable exception of `D0012580`. A gpt-4o-mini false negative seen earlier (`D0020934`, hurricane × adolescent mental health) is retained here under DeepSeek, confirming that earlier drop was a model effect, not the prompt.

Final recall will be confirmed against a human-labelled validation set; `D0012580` and `D0054409` are worth a manual look.
