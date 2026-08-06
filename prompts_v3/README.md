# Pilot title/abstract screening — v3

LLM-assisted title/abstract screening for the climate-hazards × mental-health systematic
review. These scripts run deduplicated records through the per-topic screening prompts
(a router + five hazard modules) via an LLM, then report the decision distribution,
per-topic counts, runtime, and cost.

This is a **pilot / pipeline test**: it characterises how the prompts behave and what they
cost. It is not the final screening run. The LLM acts as a first-pass, high-recall sieve;
humans remain the final arbiter.

## What is new in v3

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
- **Design gating is explicit-only.** Design is screened here **only when the abstract states it**.
  If the design is unstated or ambiguous, route to **human review**, never exclude — abstracts
  frequently omit the design and excluding on silence would cost recall.
- **Open boundary case:** repeated post-hazard follow-ups with **no pre-hazard baseline** (e.g.
  6 months / 2 years / 7 years after an event) contain within-person repeated measures but no
  pre-exposure comparison. These route to human review pending a project decision.

Full rules: `prompts_v3/screening_criteria_v3.md` (gate **G5**; supersedes v2.1).

## Three things vary across runs

Every run is defined by choices that are all recorded in the output:

- **Prompt version** — `v1` (`prompts/`), `v2` (`prompts_v2/`, Outcome discipline), or `v3`
  (`prompts_v3/`, Outcome + Design discipline).
- **Model** — `gpt-4o-mini` (OpenAI) or `deepseek-v4-flash` (DeepSeek).

Holding one fixed while changing the other is how a difference is attributed to the prompt
vs. the model (see *Comparisons*).

## Files

```
pilot_screening_v3/
  README.md                          <- this file
  scripts/
    screening_pilot_v3_gpt.py        <- v3 prompts, gpt-4o-mini (fixed 1000-record sample)
    screening_pilot_v3_deepseek.py   <- v3 prompts, deepseek-v4-flash (fixed 1000-record sample)
  results/
    screening_pilot_results_fixed1000_v3_gpt.csv        <- v3 prompts, gpt-4o-mini, 1000 recs
    screening_pilot_results_fixed1000_v3_deepseek.csv   <- v3 prompts, DeepSeek, 1000 recs
    comparison_v2_vs_v3_deepseek_1000.md                <- v2 vs v3, same model, n=1000
```

Naming convention (unchanged): the prompt version is always `v1`/`v2`/`v3`; the suffix describes
the run — `seed{N}` for a random sample, or `fixed1000_{model}` for the 1000-record comparison
set. The `fixed1000` scripts screen the **same 1000 records** as the earlier pilots in
`pilot_screening_v1/` and `pilot_screening_v2/`, so all three prompt versions are directly
comparable on identical records.

Prompts are fetched **at runtime from the `main` branch on GitHub**, so editing a prompt in the
repo changes screening behaviour without editing a script.

## Status

| Item | State |
|---|---|
| `screening_criteria_v3.md` (rules, gate G5) | drafted, pending project review |
| `prompts_v3/` (router + five hazard prompts with Design discipline) | **to be created** |
| v3 scripts | **to be created** (copies of the v2 scripts pointing at `prompts_v3/`) |
| v3 results and the v2-vs-v3 comparison | **pending the first v3 run** |

Until `prompts_v3/` exists, the scripts in `pilot_screening_v2/` remain the runnable pipeline and
screen to v2 rules (no design gate).

## What each script does

1. Loads records: fixed-sample scripts read `pilot_screening_v1/sampled_dedup_ids.csv`; seed
   scripts draw a reproducible random sample (`SAMPLE_SIZE`, `RANDOM_SEED`).
2. Fetches the six prompts (`00_candidate_topics` router + `01`-`05` hazard modules).
3. For each record: runs the router for candidate hazard topics, then the matching topic
   prompt(s). Kept if any topic returns INCLUDE; sent to human review if a topic is uncertain,
   if the design is unstated or ambiguous, or (for no-topic records) an unnamed-disaster cue plus
   a mental-health signal is present; otherwise excluded.
4. Writes per-record results (with provenance: `model_name`, `criteria_version`, `screened_at`)
   plus a summary (counts, per-topic distribution, runtime, cost).

## Requirements

- Python 3.9+
- `pip install openai pandas` (the DeepSeek script uses the `openai` package via DeepSeek's
  OpenAI-compatible endpoint - no extra install)
- An API key for the provider used:
  - OpenAI (`platform.openai.com`) for the gpt-4o-mini scripts - env var `OPENAI_API_KEY`
  - DeepSeek (`platform.deepseek.com`) for the DeepSeek script - env var `DEEPSEEK_API_KEY`
- Billing must be set up with the provider; API usage is billed separately from any chat
  subscription. A 1000-record run costs well under US$1 on either provider.

## How to run

```
pip install openai pandas
python scripts/screening_pilot_v3_deepseek.py
```

On first run it prompts you to paste the API key (not echoed as you type; can also be set via
the environment variable). The script verifies the key with a minimal request and exits
immediately with a clear message if it is invalid or has no credit. Editable settings live in
a configuration block at the top of each script (`SAMPLE_SIZE`, `RANDOM_SEED`, `MODEL`,
`USE_FIXED_SAMPLE`). Runs work on Windows, macOS, and Linux.

## Output columns

| Column | Meaning |
|---|---|
| `dedup_id` | Record ID (join key back to the corpus) |
| `title` | Article title (truncated) |
| `candidate_topics` | Hazard topic(s) the router assigned |
| `mental_health_signal` | Router's read on whether a mental-health signal is present |
| `final_decision` | INCLUDE / EXCLUDE / HUMAN_REVIEW (with reason variant) |
| `one_line_reason` | Short rationale |
| `per_topic` | Per-topic decisions and reasons (JSON) |
| `model_name` | Model used for this run |
| `criteria_version` | Prompt set / version used |
| `screened_at` | UTC timestamp |

Files are named so runs never overwrite each other, e.g.
`screening_pilot_results_fixed1000_v3_deepseek.csv`.

## Comparisons (how to read the results)

Each run fixes a model and a prompt version, so the meaningful comparisons are:

| Comparison | Held constant | Isolates |
|---|---|---|
| `v3_deepseek` **vs** `v2_deepseek` | **model** | the **pure effect of the design gate** (v2 -> v3) |
| `v3_gpt` vs `v3_deepseek` | prompt | the model effect (gpt-4o-mini vs DeepSeek) |
| `v2_deepseek` vs `pilot_screening_v1` | model | the effect of Outcome discipline (v1 -> v2) |

**Previous result for context — v1 -> v2, model held constant (DeepSeek), n = 1000**
(`pilot_screening_v2/results/comparison_v1_vs_v2_deepseek_1000.md`):

| Decision | v1 | v2 |
|---|---|---|
| INCLUDE | 34 | 29 |
| REVIEW | 31 | 6 |
| EXCLUDE | 935 | 965 |

v2 changed 42 of 1000 decisions, mostly by clearing a noisy human-review pile (28 REVIEW ->
EXCLUDE: engineering, animal-lab and methods papers, commentaries, non-registered hazards, and
records where "flooding"/"cold" meant a therapy rather than a hazard). Two changes looked like
genuine errors: one likely false negative (`D0012580`) and one minor false positive (`D0054409`).

**Expected direction for v3.** The design gate should cut INCLUDE further, because many
on-topic disaster studies are cross-sectional or qualitative. In a manual pass over one
100-record reviewer packet, applying the design rule moved roughly a third of decisions and left
only designs with genuine within-unit variation (panel pre/post, time-series, case-crossover).
The risk to watch is **recall**: abstracts often omit the design, so the "explicit-only" rule and
the review route for unstated designs are what keep eligible studies from being dropped. Verify
this on the first v3 run before adopting v3 for the full corpus.

## Notes

- Runtime is dominated by sequential API calls (~2-3 per record); a 1000-record run takes tens
  of minutes to a couple of hours depending on provider. Reduce `SAMPLE_SIZE` while iterating.
- Keep the terminal open and prevent the machine from sleeping during long runs.
- Final recall will be confirmed against a human-labelled validation set.
