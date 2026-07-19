# v1 vs v2 prompt comparison (pilot screening)

Comparison of the baseline prompts (**v1**, `prompts/`) against the tightened prompts (**v2**, `prompts_v2/`, which add the *Outcome discipline* constraints). Each seed draws the **same 100-record sample** for both versions (same `RANDOM_SEED`, same corpus), so every difference below is due to the prompt change alone.

## Summary

| Seed | Sample | v1 excluded | v2 excluded | Records changed | INCLUDE→EXCLUDE | EXCLUDE→INCLUDE |
|---|---|---|---|---|---|---|
| 1 | 100 | 95 | 98 | 3 | 3 | 0 |
| 10 | 100 | 93 | 97 | 4 | 4 | 0 |
| 100 | 100 | 92 | 94 | 4 | 3 | 1 |
| **Total** | 300 | — | — | **11** | **10** | **1** |

Across three independent 100-record samples, v2 changed only **11 of 300** decisions. The changes are almost all INCLUDE→EXCLUDE and, on inspection, remove records whose measured outcome is physical, infectious, agricultural/economic, or non-empirical. One EXCLUDE→INCLUDE change *recovers* a study with a measured mental-health outcome (PTSD) that v1 had wrongly dropped. No record with a genuine measured mental-health outcome was newly excluded.

## Every changed record

| Seed | dedup_id | v1 | v2 | Title | Assessment |
|---|---|---|---|---|---|
| 1 | D0129651 | INCLUDE/review | EXCLUDE | Impact of Hurricane Katrina on epilepsy patients in the Louisiana Medicaid population | Katrina x epilepsy healthcare use -> physical outcome. Correct exclude. |
| 1 | D0099759 | INCLUDE/review | EXCLUDE | Hot temperatures, hostile affect, hostile cognition, and arousal: Tests of a general model of affective aggres | Hot temp x hostile affect/aggression, lab-manipulated -> not an eligible MH outcome. Correct exclude. |
| 1 | D0022577 | INCLUDE/review | EXCLUDE | Assessment of extreme climate trends using temperature, rainfall, and cyclones in the West Bengal coastal regi | Climate-trend analysis for agriculture/water -> agricultural/economic outcome. Correct exclude (flood-agriculture fix). |
| 10 | D0056861 | INCLUDE/review | EXCLUDE | Working together to drive change: weaving caring for Country practices into fire risk management on Djiringanj | Cultural fire-management action-research -> no measured MH outcome. Correct exclude. |
| 10 | D0101575 | INCLUDE/review | EXCLUDE | Effect of insulating existing houses on health inequality: Cluster randomised study in the community | House-insulation RCT -> indoor temperature + general health. Not hazard->MH. Correct exclude. |
| 10 | D0004373 | INCLUDE/review | EXCLUDE | Katrina-related health concerns of Latino survivors and evacuees | Katrina Latino 'health concerns' (hunger/sleep, qualitative) -> not a measured MH outcome. Defensible exclude. |
| 10 | D0050578 | INCLUDE/review | EXCLUDE | Behind climate change: Extreme heat and health cost | Extreme heat x morbidity/hospitalisation/health cost -> physical + economic outcome. Correct exclude. |
| 100 | D0085853 | EXCLUDE | INCLUDE/review | Influence of Avoidant Coping on Posttraumatic Stress Symptoms and Job Burnout Among Firefighters: The Mediatin | Firefighters x measured PTSD (PCL-5) + burnout -> v2 RECOVERS this (v1 wrongly dropped it). Recall-improving. |
| 100 | D0066395 | INCLUDE/review | EXCLUDE | Salutogenesis and culture: Personal and community sense of coherence among adolescents belonging to three diff | Sense of coherence across cultures -> no climate hazard at all. Correct exclude (v1 false positive fixed). |
| 100 | D0023018 | INCLUDE/review | EXCLUDE | The 2024 South America ablaze: health impacts and policy imperatives for protecting population health in an er | 2024 South America wildfires policy commentary -> non-empirical, no measured MH outcome. Defensible exclude. |
| 100 | D0008071 | INCLUDE/review | EXCLUDE | Cold summer weather, constrained restoration, and very low birth weight in Sweden | Cold summer x very-low-birth-weight -> physical birth outcome (stress only a mechanism). Correct exclude. |

## Conclusion

v2 behaves as a **surgical tightening** of v1, not a blunt one: it enforces the criterion that the measured outcome must be a mental-health / wellbeing outcome. It removes physical / infectious / agricultural / economic / non-empirical false positives, recovers at least one measured-PTSD study v1 missed, and does not drop any record with a genuine measured mental-health outcome (including suicide/PTSD/depression). Final recall will be confirmed against the human-labelled validation set.
