# Pilot title/abstract screening — v3

LLM-assisted title/abstract screening for the climate-hazards × mental-health systematic review.
A router prompt assigns candidate hazard topics, then one prompt per registered hazard decides
INCLUDE / EXCLUDE / review. The LLM is a **first-pass, high-recall sieve**; humans remain the
final arbiter.

The v3 prompts themselves live in [`prompts_v3/`](../prompts_v3) (root level, no
`title_abstract_screening/` subfolder — unlike v1 and v2). This folder holds the v3 **runs** and
their analysis.

## What v3 adds

v3 adds **Design discipline** on top of the v2 *Outcome discipline*. An eligible study must
identify the hazard effect by comparing the **same unit across time** — it must exploit
**within-unit variation** in exposure.

- **Eligible designs:** longitudinal panel / repeated measures where the hazard falls between
  waves, time-series and interrupted time-series, case-crossover, difference-in-differences,
  event-study and fixed-effects panels. Self-reported outcomes are fine **provided measurement is
  repeated** on the same person before and after the shock.
- **Ineligible designs** (new exclusion code `wrong_design`): cross-sectional or single-wave
  surveys, qualitative / interview studies, case reports and case series, ecological correlations
  with no within-unit time variation, and intervention or treatment-efficacy trials.
- **Design gating is explicit-only.** Design is screened **only when the abstract states it**. If
  the design is unstated or ambiguous, route to **human review, never exclude** — abstracts
  frequently omit the design and excluding on silence would cost recall.
- **Open boundary case:** repeated post-hazard follow-ups with **no pre-hazard baseline** (e.g.
  6 months / 2 years / 7 years after an event) contain within-person repeated measures but no
  pre-exposure comparison. These route to human review pending a project decision.

Full rules: [`prompts_v3/screening_criteria_v3.md`](../prompts_v3/screening_criteria_v3.md)
(gate **G5**; supersedes v2.1).

## Contents

```
pilot_screening_v3/
  README.md                                        <- this file
  screening_criteria_v3.md                         <- copy of the rules (canonical: prompts_v3/)
  scripts/
    analyze_packet150_v3.py                        <- regenerates everything in results/
  results/
    comparison_ai_v3_vs_human_packet150.md         <- the write-up
    packet150_v3_deepseek_decisions.csv            <- one row per record, raters anonymised
    packet150_v3_deepseek_anonymised.xlsx          <- full packet, rater sheets renamed A/B/C
```

**Naming convention** (unchanged): the prompt version is always `v1`/`v2`/`v3`; the suffix
describes the run — `seed{N}` for a random sample, `fixed1000_{model}` for the 1000-record
comparison set, `packet150_{model}` for the reviewer packet.

**Rater anonymity.** Everything published here uses Rater A / B / C. The mapping to real names is
not in this repository and is not written by any script.

## Status

| Item | State |
|---|---|
| `screening_criteria_v3.md` (rules, gate G5) | done |
| `prompts_v3/` (router + five hazard prompts with Design discipline) | done, six files, each carrying a `**Version: v3**` marker |
| `prompts_v3/screen_excel_v3_deepseek.py` (reviewer-packet screening) | done |
| **v3 run on the 150-record reviewer packet** | **done — see `results/`** |
| v3 run on the fixed 1000-record sample | **not started** |
| v2-vs-v3 comparison on the fixed 1000-record sample | **blocked on the run above** |
| Boundary case: post-hazard follow-ups with no baseline | **unresolved — needs a project decision** |

## Headline result

On the 150-record reviewer packet, v3 on `deepseek-v4-flash` **did not drop a single record that
any rater marked INCLUDE** (12/12 kept), and there is **no record that both of its raters kept and
the model excluded**. This is the project's first direct recall measurement.

Final decision split: **112 EXCLUDE / 20 REVIEW / 18 INCLUDE**, no errors.

Two findings from the reverse direction are worth acting on. Of the 18 records the model marked
INCLUDE, **three were eligible studies that no rater caught** — in each the qualifying evidence (a
named difference-in-difference design, an explicit pre/post-Katrina comparison, survey waves with
the outcome measured in each) sits late in the abstract behind an off-topic opening. And **two
were false positives sharing one cause**: cold exposure in a climate chamber and in an Arctic
ultra-marathon, i.e. thermal settings a participant entered deliberately rather than hazard events.
Excluding controlled and self-selected thermal exposure in `01_temperature_prompt.md` is the
highest-value edit for a v3.1.

Read [`results/comparison_ai_v3_vs_human_packet150.md`](results/comparison_ai_v3_vs_human_packet150.md)
for the decision distribution, every disagreement adjudicated against its abstract, inter-rater
agreement, and what the result does and does not establish.

Two caveats stated up front: the packet is a purposively stratified sample rather than a random
draw, so this is not a corpus-wide recall estimate; and the denominators are small (12 records
carried an INCLUDE), so the interval around 100% is wide.

## Reproducing the run

Screening (prompts are fetched from GitHub at run time — see
[`prompts_v3/README.md`](../prompts_v3/README.md) for the step-by-step version, including the API
key and the smoke test):

```
cd prompts_v3
python screen_excel_v3_deepseek.py
```

Analysis (regenerates every file in `results/` from the screened workbook):

```
python pilot_screening_v3/scripts/analyze_packet150_v3.py \
    --in review_packet_pairwise_v3_ai.xlsx
```

Requirements: Python 3.9+, `pip install openpyxl openai`, and a `DEEPSEEK_API_KEY`. API usage is
billed separately from any chat subscription; a 150-record run costs well under US$1.

## Comparisons (how to read results)

Each run fixes a model and a prompt version, so the meaningful comparisons are:

| Comparison | Held constant | Isolates |
|---|---|---|
| v3 vs v2, same model, same records | **model** | the **pure effect of the design gate** |
| v3 on gpt-4o-mini vs v3 on DeepSeek | prompt | the model effect |
| v2 vs v1, same model, same records | model | the effect of Outcome discipline |

**Hold either the model or the prompt fixed, never both.** Established empirically: `D0020934`
(hurricane × adolescent mental health) was dropped when v2 prompts ran on gpt-4o-mini but retained
on DeepSeek — a model effect, not a prompt effect.

Prior prompt-effect result, v1 → v2 with the model held constant on DeepSeek, n = 1000
([`pilot_screening_v2/results/comparison_v1_vs_v2_deepseek_1000.md`](../pilot_screening_v2/results/comparison_v1_vs_v2_deepseek_1000.md)):

| Decision | v1 | v2 |
|---|---|---|
| INCLUDE | 34 | 29 |
| REVIEW | 31 | 6 |
| EXCLUDE | 935 | 965 |

v2 changed 42 of 1000 decisions, mostly by clearing a noisy human-review pile (28 REVIEW →
EXCLUDE: engineering, animal-lab and methods papers, commentaries, non-registered hazards, and
records where "flooding" or "cold" meant a *therapy* rather than a hazard).

**The equivalent v2 → v3 comparison on those same 1000 records has not been run.** The packet
result above measures v3 against *humans*, which is a different question from measuring v3
against *v2*. Both are needed.

## Notes

- Runtime is dominated by sequential API calls (one router call plus one per candidate hazard
  topic). 150 records take 20–40 minutes on DeepSeek; a 1000-record run takes a few hours.
- Keep the terminal open and stop the machine from sleeping during long runs. Progress is
  checkpointed after every record, so an interrupted run resumes without re-spending API calls.
- **11 of the 150 packet records carry no usable abstract.** Gate G5 cannot operate on those at
  all — see §7 of the comparison document. They need abstracts retrieved before any decision on
  them is final.
- **A failed hazard-module call used to be indistinguishable from genuine uncertainty**, because
  the failure is recorded inside the reason string while the record keeps a normal-looking
  decision. In the first pass of this run, 19 of 38 REVIEW decisions were nothing but failed
  calls. `--retry-errors` now re-runs module-level failures too and the run summary warns when any
  remain; any earlier v3 figure with a REVIEW count near 38 predates that fix.
