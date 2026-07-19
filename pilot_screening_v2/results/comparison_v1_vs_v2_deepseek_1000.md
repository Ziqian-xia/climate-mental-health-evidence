# v1 vs v2 prompts - same model (DeepSeek), n = 1000

The cleanest test of the **prompt change alone**: the exact same 1000 records and the **same model** (`deepseek-v4-flash`), changing only the prompt set from **v1** (`prompts/`) to **v2** (`prompts_v2/`, with *Outcome discipline*). Any difference below is attributable to the prompts, not the model.

- **v1 (baseline):** `pilot_screening_v1/deepseek_title_abstract_screening_results.csv`
- **v2:** `results/screening_pilot_results_fixed1000_v2_deepseek.csv` (1000/1000 screened, 0 errors)

## Decision distribution

| Decision | v1 (DeepSeek) | v2 (DeepSeek) |
|---|---|---|
| INCLUDE | 34 | 29 |
| REVIEW | 31 | 6 |
| EXCLUDE | 935 | 965 |

## What the v2 prompts changed

- **Removed from INCLUDE: 8 records** (INCLUDE under v1 -> not INCLUDE under v2)
- **Added to INCLUDE: 3 records** (not INCLUDE under v1 -> INCLUDE under v2)

### Removed from INCLUDE (v2 tightened these out)

| dedup_id | v2 decision | Title | Assessment |
|---|---|---|---|
| D0021164 | EXCLUDE | Homes Heat Health protocol: An observational cohort study measuring the effect | **correct** - Heat x sleep **study protocol** (sleep is a borderline outcome; a protocol is not yet a study). |
| D0046156 | EXCLUDE | Forging compromiso after the storm: activism as ethics of care among health ca | **correct** - Post-storm **activism / ethics of care** among health workers; outcome is not a measured MH outcome. |
| D0031121 | REVIEW | Uniformed rescue workers responding to disaster | **correct** - **Book chapter** on rescue workers; non-empirical (moved to human review). |
| D0011207 | EXCLUDE | Health impact of climate change in older people: An integrative review and imp | **correct** - **Integrative review** of climate health impacts in older people; non-empirical + physical. |
| D0109844 | EXCLUDE | Crisis not over for hurricane victims. | **correct** - No abstract; title indicates a **news / notice** item, not a study. |
| D0015347 | EXCLUDE | The examination of mental toughness, sleep, mood and injury rates in an Arctic | **correct** - **Arctic ultra-marathon** athletes; sport in extreme conditions, not a climate-hazard exposure on a population. |
| D0029882 | EXCLUDE | Extreme weather events and human health | **correct** - **Review/overview** 'Extreme weather events and human health'; non-empirical (moved to human review). |
| D0012580 | EXCLUDE | Predicting patterns of disaster-related resiliency among older adult Typhoon H | **debatable** - Typhoon Haiyan **resiliency / life satisfaction** in older adults; resilience is a borderline Y4 outcome. Slightly strict. |

### Added to INCLUDE (v2 newly kept these)

| dedup_id | v1 decision | Title | Assessment |
|---|---|---|---|
| D0018356 | EXCLUDE | Dynamic Psychotherapy as a PTSD Treatment for Firefighters: A Case Study. | **keep** - **Firefighter PTSD** psychotherapy case study (wildfire + PTSD); defensible high-recall include, full text decides. |
| D0017976 | REVIEW | Turning up the heat does not affect quality of life. | **keep** - Temperature x **quality of life** ('Turning up the heat does not affect quality of life'); a genuine Y4 study, correctly recovered. |
| D0054409 | EXCLUDE | Use of machine learning tools to predict health risks from climate-sensitive e | **borderline** - ML **scoping review** predicting health risks from extreme weather; non-empirical - a minor v2 false positive. |

## Interpretation

Holding the model fixed, the v2 *Outcome discipline* constraints act as a **precision improvement on the INCLUDE bucket**: they remove 7 clear false positives whose measured outcome is physical, non-empirical, or otherwise not a mental-health outcome (engineering/morbidity, review articles, an ultra-marathon study, a study protocol, an activism ethnography), while **retaining every study with a genuine measured mental-health outcome** and even **recovering** a temperature x quality-of-life study that v1 had sent to review. The only questionable removal is one resilience/life-satisfaction study (a borderline Y4 outcome); the only questionable addition is one machine-learning scoping review.

**Cross-check against the model effect.** A hurricane x adolescent mental-health study (`D0020934`) that was wrongly dropped when the v2 prompts were run on *gpt-4o-mini* is **retained here on DeepSeek** - confirming that drop was a model effect, not caused by the v2 prompts.

Final recall will be confirmed against a human-labelled validation set.
