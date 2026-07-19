# Pilot title/abstract screening

LLM-assisted title/abstract screening for the climate-hazards × mental-health systematic
review. These scripts run deduplicated records through the per-topic screening prompts
(a router + five hazard modules) via an LLM, then report the decision distribution,
per-topic counts, runtime, and cost.

This is a **pilot / pipeline test**: it characterises how the prompts behave and what they
cost. It is not the final screening run. The LLM acts as a first-pass, high-recall sieve;
humans remain the final arbiter.

## Two things vary across runs

Every run is defined by **two** independent choices, both recorded in the output:

- **Prompt version** — `v1` (`prompts/title_abstract_screening/`) or `v2`
  (`prompts_v2/title_abstract_screening/`, which adds the *Outcome discipline* constraints).
- **Model** — `gpt-4o-mini` (OpenAI) or `deepseek-v4-flash` (DeepSeek).

Holding one fixed while changing the other is how a difference is attributed to the prompt
vs. the model (see *Comparisons*).

## Files

```
pilot_screening_v2/
  README.md                          <- this file
  scripts/
    screening_pilot_v1.py            <- v1 prompts, gpt-4o-mini (random sample by seed)
    screening_pilot_v2.py            <- v2 prompts, gpt-4o-mini (random sample by seed)
    screening_pilot_v2_gpt.py        <- v2 prompts, gpt-4o-mini (fixed 1000-record sample)
    screening_pilot_v2_deepseek.py   <- v2 prompts, deepseek-v4-flash (fixed 1000-record sample)
    fix_errors_deepseek.py           <- re-runs only ERROR rows and patches them back in place
  results/
    screening_pilot_results_seed{N}_v1.csv / _v2.csv    <- gpt-4o-mini, random seed
    screening_pilot_results_fixed1000_v2_gpt.csv        <- v2 prompts, gpt-4o-mini, 1000 recs
    screening_pilot_results_fixed1000_v2_deepseek.csv   <- v2 prompts, DeepSeek, 1000 recs
    comparison_v1_vs_v2.md                 <- v1 vs v2 on gpt-4o-mini, 3 seeds x 100 (quick look)
    comparison_v1_vs_v2_deepseek_1000.md   <- v1 vs v2 on DeepSeek, n=1000 (MAIN RESULT, read this)
```

| Script | Prompts | Model | Sample |
|---|---|---|---|
| `screening_pilot_v1.py` | v1 | gpt-4o-mini | random (`RANDOM_SEED`) |
| `screening_pilot_v2.py` | v2 | gpt-4o-mini | random (`RANDOM_SEED`) |
| `screening_pilot_v2_gpt.py` | v2 | gpt-4o-mini | fixed 1000 (`pilot_screening_v1/sampled_dedup_ids.csv`) |
| `screening_pilot_v2_deepseek.py` | v2 | deepseek-v4-flash | fixed 1000 (`pilot_screening_v1/sampled_dedup_ids.csv`) |

Naming convention: the prompt version is always `v1`/`v2`; the suffix describes the run —
`seed{N}` for a random sample, or `fixed1000_{model}` for the 1000-record comparison set.
The two `fixed1000` scripts screen the **same 1000 records** as the earlier DeepSeek/v1 pilot
in `pilot_screening_v1/`, so results are directly comparable.

Prompts are fetched **at runtime from the `main` branch on GitHub**, so editing a prompt in the
repo changes screening behaviour without editing a script.

## What each script does

1. Loads records: fixed-sample scripts read `pilot_screening_v1/sampled_dedup_ids.csv`; seed
   scripts draw a reproducible random sample (`SAMPLE_SIZE`, `RANDOM_SEED`).
2. Fetches the six prompts (`00_candidate_topics` router + `01`-`05` hazard modules).
3. For each record: runs the router for candidate hazard topics, then the matching topic
   prompt(s). Kept if any topic returns INCLUDE; sent to human review if a topic is uncertain,
   or (for no-topic records) an unnamed-disaster cue plus a mental-health signal is present;
   otherwise excluded.
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
python scripts/screening_pilot_v2_deepseek.py
```

On first run it prompts you to paste the API key (not echoed as you type; can also be set via
the environment variable). The script verifies the key with a minimal request and exits
immediately with a clear message if it is invalid or has no credit. Editable settings live in
a configuration block at the top of each script (`SAMPLE_SIZE`, `RANDOM_SEED`, `MODEL`,
`USE_FIXED_SAMPLE`). Runs work on Windows, macOS, and Linux.

If a few records fail (e.g. a transient network drop) they are marked `ERROR`; run
`python scripts/fix_errors_deepseek.py` to re-screen only those rows and patch them back into
the CSV.

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
`screening_pilot_results_fixed1000_v2_deepseek.csv`.

## Comparisons (how to read the results)

Each run fixes a model and a prompt version, so the meaningful comparisons are:

| Comparison | Held constant | Isolates |
|---|---|---|
| `v2_deepseek` **vs** `pilot_screening_v1` (v1/DeepSeek) | **model** | the **pure prompt effect** (v1 -> v2) |
| `v2_gpt` vs `v2_deepseek` | prompt | the model effect (gpt-4o-mini vs DeepSeek) |
| `v1` vs `v2` (both gpt-4o-mini, same seed) | model | the prompt effect on gpt-4o-mini |

**Main result — model held constant (DeepSeek), v1 -> v2 prompts, n = 1000**
(`comparison_v1_vs_v2_deepseek_1000.md`):

| Decision | v1 | v2 |
|---|---|---|
| INCLUDE | 34 | 29 |
| REVIEW | 31 | 6 |
| EXCLUDE | 935 | 965 |

The v2 *Outcome discipline* constraints act as a precision improvement on the INCLUDE bucket:
they remove ~7 clear false positives whose measured outcome is physical, infectious,
agricultural/economic, or non-empirical (flood-control engineering -> morbidity, a
hospital-climatisation study, review articles, an ultra-marathon study, a study protocol, an
activism ethnography), while retaining every study with a genuine measured mental-health
outcome (suicide, PTSD, depression, quality of life) and recovering a temperature x
quality-of-life study. No genuine measured-mental-health study is dropped by the prompt change.
A false negative seen earlier under gpt-4o-mini (a hurricane x adolescent mental-health study)
is retained under DeepSeek, showing that drop was a model effect, not a prompt effect.

## Notes

- Runtime is dominated by sequential API calls (~2-3 per record); a 1000-record run takes tens
  of minutes to a couple of hours depending on provider. Reduce `SAMPLE_SIZE` while iterating.
- Keep the terminal open and prevent the machine from sleeping during long runs.
- Final recall will be confirmed against a human-labelled validation set.
