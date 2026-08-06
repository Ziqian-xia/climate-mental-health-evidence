# v3 screening of the 150-record reviewer packet — AI vs. human labels

Model **deepseek-v4-flash**, prompt set **v3** (`prompts_v3/`, router `00` + hazard modules `01`–`05`, outcome discipline + design gate G5), run with `prompts_v3/screen_excel_v3_deepseek.py`.

Source workbook: `review_packet_pairwise_v3_ai.xlsx`. Raters are anonymised as Rater A, Rater B, Rater C; the mapping is not published.

**150 unique records**, each independently labelled by exactly two of the three raters (three-way rotating pairwise design, 300 rows, no triple overlap).


## 1. Headline: the AI missed nothing a human wanted to keep

| Reference set | n | AI kept | AI dropped | AI errored | Recall |
|---|---|---|---|---|---|
| Any rater marked INCLUDE | 12 | 12 | 0 | 0 | **100%** |
| Any rater marked INCLUDE or REVIEW | 36 | 26 | 10 | 0 | **72%** |

`AI kept` means the AI returned INCLUDE **or** REVIEW — both route the record onward to a human, which is what recall means for a first-pass sieve.


Records **both** raters kept and the AI excluded: **0**


## 2. Decision distribution

| AI decision (v3) | n | share |
|---|---|---|
| EXCLUDE | 112 | 75% |
| REVIEW | 20 | 13% |
| INCLUDE | 18 | 12% |

| Rater | records labelled | INCLUDE | REVIEW | EXCLUDE |
|---|---|---|---|---|
| Rater A | 100 | 5 | 2 | 93 |
| Rater B | 100 | 7 | 18 | 75 |
| Rater C | 100 | 5 | 6 | 89 |

## 3. Why records were excluded

| Exclusion code | n (topic verdicts) |
|---|---|
| wrong_design | 28 |
| wrong_outcome | 12 |
| non_original | 7 |
| not_human_empirical | 4 |
| animal_or_lab_only | 1 |

A further **65** records were excluded by the router before any hazard module ran — no eligible registered hazard in the title/abstract. `wrong_design` is the code introduced by v3; its frequency is the direct footprint of gate G5 on this set.


## 4. Every disagreement where the AI excluded and a rater did not

10 record(s). No record was adjudicated from its title alone — each verdict below was formed by reading the record's own abstract.

| Dedup id | Title | Human labels | AI exclusion code | Adjudication |
|---|---|---|---|---|
| `D0008842` | The influence of weather on health-related help-seek | B=REVIEW, C=EXCLUDE | wrong_outcome | Genuinely borderline |
| `D0022405` | Seven Months After Tropical Cyclone Chido in Mayotte | B=REVIEW, C=EXCLUDE | non_original | AI correct |
| `D0022622` | Impacts of extreme temperatures on mood disorders: A | A=REVIEW, B=EXCLUDE | non_original | AI correct |
| `D0024142` | Mental health impacts of climate change on vulnerabl | A=REVIEW, B=EXCLUDE | non_original | AI correct |
| `D0038140` | School based post disaster mental health services: D | A=EXCLUDE, B=REVIEW | wrong_design | AI correct |
| `D0043897` | CRITERION-REFERENCED ASSESSMENT INDEX FOR EVALUATING | A=EXCLUDE, B=REVIEW | wrong_outcome | AI correct |
| `D0059024` | Assessment of multiple predictors to the psychologic | B=REVIEW, C=EXCLUDE | wrong_design | AI correct |
| `D0066623` | Kidney cancer | B=REVIEW, C=EXCLUDE | no topic | AI correct |
| `D0072924` | Prenatal polycyclic aromatic hydrocarbon (PAH) expos | B=REVIEW, C=EXCLUDE | no topic | AI correct |
| `D0127047` | An Efficient Treatment for Posttraumatic Injury for  | A=EXCLUDE, B=REVIEW | no topic | Blocked by missing metadata |

- **`D0008842`** — Genuinely borderline: Design is sound (1.66M emergency-link calls against daily weather - a time-series). It fails on outcome: help-seeking for general health, not a psychiatric or mental-health service-use outcome. The closest call in this set and worth a second human look.
- **`D0022405`** — AI correct: 'Information was collected through informal interviews'; the paper reviews the Chido cyclone and recommends launching a study. Commentary, no measured outcome.
- **`D0022622`** — AI correct: Abstract states 'This systematic review was conducted following the PRISMA guideline'. Non-original evidence synthesis, excluded by v2.1 discipline.
- **`D0024142`** — AI correct: 'This systematic review synthesises evidence...', PRISMA 2020, PROSPERO CRD420250651981. Non-original.
- **`D0038140`** — AI correct: Repeated-measures ANOVA, but the estimand is the efficacy of a school-based treatment, not the effect of the hurricane. Intervention trials are ineligible under G5.
- **`D0043897`** — AI correct: Mixed-review method plus structured interviews; the outcome is a social wellbeing index for relief camps, not an eligible mental-health outcome.
- **`D0059024`** — AI correct: 'Empirical face-to-face survey' of 217 respondents, willingness-to-pay design. Cross-sectional, no within-unit variation over time.
- **`D0066623`** — AI correct: Title is 'Kidney cancer' and the abstract is empty. No registered hazard and no mental-health outcome.
- **`D0072924`** — AI correct: Exposure is prenatal polycyclic aromatic hydrocarbons from fossil-fuel combustion. Not one of the five registered hazards; airborne pollutants are eligible only when fire-attributed.
- **`D0127047`** — Blocked by missing metadata: The abstract field contains only the string 'Brief Summary' - a registry stub. Nothing can be screened. Route to full-text retrieval rather than counting this as a screening decision.

So of the 10 disagreements, **8 are the AI applying the rules correctly against a single over-inclusive rater**, one is unscreenable because the record has no abstract, and one is a real borderline call. None is a missed eligible study.


## 5. The other direction: the AI said INCLUDE and no rater did

Of the 18 records the AI marked INCLUDE, **10 were also marked INCLUDE by at least one rater** and **8 were not**. Those 8 are where a first-pass sieve pays for its recall, so each was read against its abstract.

| Dedup id | Title | Human labels | Adjudication |
|---|---|---|---|
| `D0005795` | Trends in serious emotional disturbance among yout | A=EXCLUDE, B=REVIEW | AI correct, raters missed it |
| `D0015347` | The examination of mental toughness, sleep, mood a | B=REVIEW, C=EXCLUDE | AI wrong |
| `D0018695` | A Difference-In Difference Analysis of the South C | A=EXCLUDE, C=EXCLUDE | AI correct, raters missed it |
| `D0085607` | Human mood and cognitive function after different  | B=EXCLUDE, C=EXCLUDE | AI wrong |
| `D0106423` | Suicide mortality rates in Louisiana, 1999-2010. | A=EXCLUDE, C=EXCLUDE | AI correct, raters missed it |
| `D0106479` | Outpatient evaluation of the immediate and delayed | B=REVIEW, C=EXCLUDE | Genuinely borderline |
| `D0128578` | Internet gaming disorder among disaster-exposed ch | A=EXCLUDE, B=REVIEW | AI over-confident |
| `D0128821` | Cumulative trauma and the long-term health and rec | B=EXCLUDE, C=REVIEW | AI over-confident |

- **`D0005795`** — AI correct, raters missed it: Hurricane Katrina, baseline plus follow-up survey waves, serious emotional disturbance measured across waves. Note that every wave is post-hurricane - this is a live instance of the unresolved boundary case.
- **`D0015347`** — AI wrong: Mood measured repeatedly across a three-day Arctic ultra-marathon at -20 to -6 C. Repeated measures and cold, but the cold is the self-selected setting of an athletic event, not a hazard exposure.
- **`D0018695`** — AI correct, raters missed it: Abstract names a 'difference-in-difference analysis' of the 2015 South Carolina floods and reports outcomes including 'mental disorders of pregnancy, depression, and generalized anxiety'. Eligible design and eligible outcome; the eligibility evidence sits late in the abstract, after a passage about physical maternal morbidity.
- **`D0085607`** — AI wrong: 12 subjects exposed to -5/-10/-15 C in a climate chamber. A laboratory exposure is not a climate hazard. The model's own reason says 'climate chamber' and included it anyway.
- **`D0106423`** — AI correct, raters missed it: Abstract states 'a comparison of suicide rates post-Katrina versus pre-Katrina was done for Orleans Parish'. Explicit pre/post hazard comparison with an eligible outcome, again disclosed late in the abstract.
- **`D0106479`** — Genuinely borderline: 2010 Russian heat wave, HADS anxiety and depression collected for the hot period and at visit - eligible hazard and outcome, but the primary endpoints are cardiovascular and the mental-health comparison is retrospective recall.
- **`D0128578`** — AI over-confident: Typhoon-exposed young adults, but the study is a psychometric validation with network analysis and the abstract never states a longitudinal design. The model's reason asserts 'longitudinal study', which the abstract does not support. Under the explicit-only rule this should be REVIEW.
- **`D0128821`** — AI over-confident: Katrina survivors and PTSD trajectories, but the abstract does not state whether measurement was repeated. Should be REVIEW; one rater said exactly that.

Tally: **3** AI correct, raters missed it; **2** AI wrong; **2** AI over-confident; **1** Genuinely borderline.


The three *raters missed it* cases are the most useful finding here. In all three the eligibility evidence — a named difference-in-difference design, an explicit pre/post Katrina comparison, survey waves with an outcome measured in each — appears **late in the abstract**, after an opening that reads as off-topic or as physical health. A human skimming 100 abstracts misses those; the model does not skim. That is a real complementarity argument for keeping the model in the loop rather than a point against the raters.


**Both outright false positives have the same cause.** `D0085607` (climate chamber) and `D0015347` (Arctic ultra-marathon) are cold *settings* that a participant entered deliberately — a laboratory protocol and a sporting event — not hazard events that befell a population. Both satisfy the letter of gate G5, because measurement really is repeated within person, and both have a genuine mood outcome. The gate they should have failed is the hazard gate. `01_temperature_prompt.md` tells the model not to assign temperature for body temperature or fever, but says nothing about controlled or self-selected thermal exposure. Adding that exclusion is the single highest-value edit for a v3.1.


## 6. Inter-rater agreement

| Pair | n | Raw agreement | Cohen's κ |
|---|---|---|---|
| Rater A vs Rater B | 50 | 76% | 0.28 |
| Rater A vs Rater C | 50 | 94% | 0.39 |
| Rater B vs Rater C | 50 | 70% | 0.09 |

Raw agreement is high while κ is low. That is the base-rate effect: roughly nine in ten records are EXCLUDE, so a rater who excluded everything would still score high raw agreement, and κ discounts exactly that. The substantive disagreement is concentrated in **how readily each rater reaches for REVIEW** rather than in what they include — see the REVIEW column in §2. Reading κ as "the raters disagree about eligibility" would over-state the problem; reading it as "the REVIEW threshold is not yet standardised" is the accurate reading.


### Each rater against the AI

| Rater | n | Same decision | AI kept, rater excluded | AI excluded, rater kept |
|---|---|---|---|---|
| Rater A | 100 | 78 | 19 | 2 |
| Rater B | 100 | 76 | 11 | 8 |
| Rater C | 100 | 86 | 13 | 0 |

The last column is the one that matters for a high-recall sieve, and it is small for every rater. Disagreement is overwhelmingly the AI being *wider* than the human, which is the correct direction of error at the pre-screen stage: an over-inclusive model costs reviewer time, an under-inclusive one costs evidence.


## 7. Records with no abstract — a structural limit on the design gate

**11 of 150 records (7%) carry no usable abstract** — the field is empty or holds a stub such as `Brief Summary`. Gate G5 screens design *only when the abstract states it*, so on these records the design gate cannot operate at all and the decision rests on the title.

| Dedup id | Title | AI (v3) | Human labels |
|---|---|---|---|
| `D0017976` | Turning up the heat does not affect quality of life. | REVIEW | A=EXCLUDE, C=REVIEW |
| `D0032910` | Re: Primary full-gland prostate cryoablation in olde | EXCLUDE | B=EXCLUDE, C=EXCLUDE |
| `D0066623` | Kidney cancer | EXCLUDE | B=REVIEW, C=EXCLUDE |
| `D0089594` | Discrepancy Between Fingertip Glucose Levels and HbA | EXCLUDE | B=EXCLUDE, C=EXCLUDE |
| `D0102464` | Psychotic reactions to a natural disaster: Hurricane | REVIEW | B=REVIEW, C=REVIEW |
| `D0103339` | MEASURING PERFORMANCE CHANGES IN HIGHLY TRANSIENT EX | EXCLUDE | A=EXCLUDE, C=EXCLUDE |
| `D0109844` | Crisis not over for hurricane victims. | REVIEW | A=INCLUDE, B=REVIEW |
| `D0116211` | Caring for the caretakers in times of disaster. The  | REVIEW | A=EXCLUDE, B=REVIEW |
| `D0118717` | Randomized Clinical Trial to Evaluate Guidelines for | EXCLUDE | A=EXCLUDE, C=EXCLUDE |
| `D0122391` | Test-retest Reproducibility of [11C]PHNO PET Using t | EXCLUDE | B=EXCLUDE, C=EXCLUDE |
| `D0127047` | An Efficient Treatment for Posttraumatic Injury for  | EXCLUDE | A=EXCLUDE, B=REVIEW |

The explicit-only rule behaves as designed here: the AI routed **4 of 11** of these to INCLUDE/REVIEW rather than excluding on silence. `D0109844` (*Crisis not over for hurricane victims*) has an empty abstract, was marked INCLUDE by one rater, and the AI still kept it — exactly the recall protection the rule exists for.

**Action this implies:** these records need abstracts retrieved before any screening decision on them can be called final, whether the decision came from a human or the model.


## 8. Errors

No record returned ERROR: every one of the 150 records carries an AI decision.


**Module-level failures are counted separately and matter more than they look.** A record can carry a normal-looking decision while one of its hazard modules never returned a verdict; the failure is visible only inside the reason string. Because a failed module is treated as uncertainty, such records are pushed to REVIEW — so a transport error silently inflates the human-review pile rather than announcing itself.

This run still carries **1**: `D0015366`. Another module returned a substantive verdict, so the final decision does not rest on the failed call.


The first pass of this run had **19 of 38 REVIEW decisions produced by nothing but a failed module call** — half the review pile was an artefact. `--retry-errors` in the screening script now re-runs module-level failures as well as router failures, and the run summary warns when any remain. Any earlier v3 numbers quoting a REVIEW count near 38 predate that fix and should not be used.


## 9. What this does and does not establish

- **Establishes:** on this 150-record set the v3 prompt set did not drop a single record that a human rater wanted to keep. This is the first direct recall measurement in the project; until now recall was the outstanding unvalidated quantity.
- **Does not establish:** recall on the full ~72,000-record corpus. The packet is a purposively stratified sample, not a random draw, so the rate here is not a corpus-wide estimate.
- **Does not establish:** that v3 is better than v2 *on the same records*. No v2 run exists for this packet, so the two cannot be compared here. The registered v2→v3 comparison is still the 1000-record fixed sample, and it has not been run.
- **Small denominators.** 12 records carried an INCLUDE from any rater. A 100% recall figure on 12 records has a wide confidence interval — it is consistent with, but does not demonstrate, high recall at scale.
- **Model and prompt are confounded with nothing here** because only one configuration was run. Any future comparison must hold either the model or the prompt version fixed; `D0020934` earlier changed decision between gpt-4o-mini and DeepSeek under identical v2 prompts, which is a model effect, not a prompt effect.


### Actions this run generates

1. **Edit `01_temperature_prompt.md` for v3.1** to exclude controlled or self-selected thermal exposure (climate chambers, laboratory protocols, cold-weather sporting events). This is the cause of both false positives in §5 and is a one-paragraph fix.
2. **Retrieve abstracts for the 11 records that have none** (§7). No screening decision on them is final until then.
3. **Resolve the boundary case.** `D0005795` is a live instance: Katrina survey waves with an eligible outcome, but every wave is post-hurricane. The project has not decided whether these are eligible, and raters will keep splitting on them until it does.
4. **Standardise the REVIEW threshold** before reading anything into κ (§6). The raters used REVIEW 2, 18 and 6 times on 100 records each; that spread, not disagreement about eligibility, is what the κ values are measuring.
5. **Run v2 on this same packet**, or v3 on the fixed 1000-record sample, to get the prompt-version comparison that this document cannot provide.


## 10. Reproducing this

```
cd prompts_v3
python screen_excel_v3_deepseek.py --ref main
python ../pilot_screening_v3/scripts/analyze_packet150_v3.py \
    --in ../review_packet_pairwise_v3_ai.xlsx
```

The screening script fetches the six v3 prompts from GitHub at run time; pass `--ref <commit-sha>` to pin an exact prompt revision. Every run prints the model, the criteria version and the prompt source in its closing summary — quote those when reporting results.

