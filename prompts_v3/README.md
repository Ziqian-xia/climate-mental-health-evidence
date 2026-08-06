# Title/abstract screening prompts — v3

Prompt set for the LLM-assisted title/abstract pre-screen of the climate-hazards × mental-health
systematic review. A router prompt assigns candidate hazard topics; one prompt per registered
hazard then decides INCLUDE / EXCLUDE / review. The LLM is a **first-pass, high-recall sieve** —
humans remain the final arbiter.

## Contents of this folder

| File | Purpose |
|---|---|
| `00_candidate_topics_prompt.md` | Router: assigns candidate hazard topics. Topic assignment only — no design or outcome gate |
| `01_temperature_prompt.md` | Temperature / heat / cold module |
| `02_wildfire_prompt.md` | Wildfire / bushfire / smoke module |
| `03_flood_prompt.md` | Flood / inundation module |
| `04_cyclone_prompt.md` | Tropical cyclone / hurricane / typhoon module |
| `05_drought_prompt.md` | Drought / water scarcity module |
| `screening_criteria_v3.md` | Full eligibility rules, including gate **G5** (supersedes v2.1) |
| `screen_excel_v3_deepseek.py` | Screens the reviewer packet (Excel) with these prompts on DeepSeek |
| `README.md` | This file |

**Note on the folder layout.** v1 and v2 prompts live in a `title_abstract_screening/` subfolder;
**v3 prompts sit directly in `prompts_v3/`** with no subfolder. Any script pointing at
`prompts_v3/title_abstract_screening/...` will fail with a 404.

| Version | Path in this repo | What it adds |
|---|---|---|
| v1 | `prompts/title_abstract_screening/` | Baseline: hazard (X) and outcome (Y) gates, deliberately over-inclusive |
| v2 / v2.1 | `prompts_v2/title_abstract_screening/` | **Outcome discipline**: the measured outcome must be mental health / wellbeing. v2.1 adds non-original / evidence-synthesis discipline |
| v3 | `prompts_v3/` (this folder) | **Design discipline** (gate G5): the study must exploit within-unit variation. New exclusion code `wrong_design` |

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

Every file in this folder carries a `**Version: v3**` marker on line 3. The screening script
refuses to run if any prompt is missing it, so a v2 file can never be screened with and reported
as v3.

---

# Screening the reviewer packet: `screen_excel_v3_deepseek.py`

Screens `review_packet_pairwise.xlsx` — the three-way pairwise human-labelling packet (sheets
`Ziqian`, `Jacob`, `Tony`; 100 rows each, 300 rows, **150 unique records**, each record assigned
to exactly two raters) — with the v3 prompts on `deepseek-v4-flash`.

The six prompts are **fetched from GitHub at runtime**, so a collaborator can clone the repo (or
download just this one script) and run it without editing any path. If the network is
unavailable, the script falls back to a local `prompts_v3/` folder and prints which source it
used — it never falls back silently.

Title and abstract are read straight from the Excel file, so **no corpus download is needed**.

**What it will not touch.** Results are written to a **new** file as two new columns per sheet,
`AI Suggestion (v3)` and `AI Reason (v3)`. The `Human Decision` and `Audit Notes` columns are
never modified. The packet exists to produce *independent* human labels for validating the AI
pipeline and to measure inter-rater agreement; writing model output into the human columns would
make that validation circular and destroy the agreement statistics.

Records that appear on two sheets are screened once, and the same result is written to both rows.

## Requirements

- Python 3.9 or newer
- `pip install openpyxl openai`
- A DeepSeek API key from `platform.deepseek.com`, in the environment variable
  `DEEPSEEK_API_KEY` (or paste it when the script asks — it is not echoed as you type)
- API usage is billed by DeepSeek and is **separate from any chat subscription**. A 150-record
  run costs well under US$1. The `openai` package name does not mean OpenAI is being called —
  DeepSeek exposes an OpenAI-compatible endpoint at `https://api.deepseek.com`.

## How to run

Run these one line at a time. After each step, the "you should see" line tells you whether it
worked before you move on.

**1. Install the two packages** (once per machine):

```
pip install openpyxl openai
```

You should see `Successfully installed ...`, or `Requirement already satisfied` if they are
already there. Both outcomes are fine.

**2. Go to this folder.**

Windows (PowerShell):

```
cd C:\path\to\climate-mental-health-evidence\prompts_v3
```

macOS / Linux:

```
cd /path/to/climate-mental-health-evidence/prompts_v3
```

**3. Set your API key** for this terminal window.

Windows (PowerShell):

```
$env:DEEPSEEK_API_KEY="sk-your-key-here"
```

macOS / Linux:

```
export DEEPSEEK_API_KEY="sk-your-key-here"
```

There is no output — that is correct. The key is not saved to disk and is forgotten when you
close the window. If you skip this step the script will prompt you for the key instead.

**4. Smoke-test on three records first.** Do not skip this — it catches a wrong path, a bad key,
or a network problem in thirty seconds instead of thirty minutes.

```
python screen_excel_v3_deepseek.py --limit 3
```

You should see, in order:

```
      300 rows across 3 sheet(s); 150 unique records.
      Prompt source: GitHub Ziqian-xia/climate-mental-health-evidence@main/prompts_v3
      Loaded 6 prompts; temperature prompt = 8829 chars (v3 ~8829, v2 ~5900, v1 ~2600).
      API key is valid.
```

Those four lines confirm the packet was found, GitHub was reachable, the prompts really are v3,
and the key works. The run then finishes in under a minute and writes a summary.

**5. Run the full set.**

```
python screen_excel_v3_deepseek.py
```

150 records take roughly **20–40 minutes** on DeepSeek (one router call plus one call per
candidate hazard topic, sent sequentially). Progress prints every five records with an estimated
time remaining.

Every record is checkpointed to `screen_v3_progress.json` immediately, so if the network drops or
the window closes, **just run the same command again** — it resumes where it stopped and re-screens
nothing. Keep the terminal open and stop the machine from sleeping during the run.

**6. Collect the output.**

`review_packet_pairwise_v3_ai.xlsx`, written next to the input file. Delete
`screen_v3_progress.json` once you are happy with the result — leaving it in place will make the
next run think the work is already done.

## Options

All optional; the defaults are what step 5 uses.

| Flag | Default | Use it when |
|---|---|---|
| `--in <path.xlsx>` | `review_packet_pairwise.xlsx`, searched next to the script, in the parent folder, then the current folder | The packet is somewhere else |
| `--out <path.xlsx>` | `<input>_v3_ai.xlsx` | You want a different output name |
| `--limit N` | 0 (all) | Smoke test, or screening in batches |
| `--prompts-dir <folder>` | (unset — fetch from GitHub) | Force local prompts, e.g. to test an unpushed edit |
| `--ref <branch-or-sha>` | `main` | Pin an exact prompt revision for a reproducible run |
| `--model <name>` | `deepseek-v4-flash` | Compare models (see the caveat below) |
| `--sheets A,B,C` | `Ziqian,Jacob,Tony` | The packet has different sheet names |
| `--checkpoint <path.json>` | `screen_v3_progress.json` next to the output | Two runs must not share a resume file |

## How a decision is reached

1. The router (`00`) returns candidate hazard topics. **No topics → EXCLUDE** ("no eligible
   registered hazard identified").
2. Each candidate topic's prompt (`01`–`05`) returns `decision`, `review_flag`, `exclusion_code`
   and `one_line_reason`.
3. Aggregated across topics: any INCLUDE → **INCLUDE** (or **REVIEW** if that topic also set
   `review_flag`); otherwise any MAYBE or any `review_flag` → **REVIEW**; otherwise **EXCLUDE**.

`AI Reason (v3)` records every topic's verdict, exclusion code and one-line reason, so a REVIEW or
EXCLUDE can be traced to the gate that produced it.

## Troubleshooting

| Message | What to do |
|---|---|
| `Could not reach GitHub` then `Falling back to the local copy` | Nothing — the run continues on the identical local prompts. A phone hotspot usually restores the GitHub path |
| `GitHub is unreachable and no local copy ... was found` | Get on a network, or pass `--prompts-dir` pointing at a folder holding all six `00_`–`05_` prompt files |
| `These prompt files do not look like v3` | The folder passed to `--prompts-dir` holds v1/v2 prompts. Correct it rather than removing the check |
| `Could not find review_packet_pairwise.xlsx` | Pass the path: `--in "C:\full\path\review_packet_pairwise.xlsx"` |
| `API key is invalid or unauthorized` | Re-copy the key from `platform.deepseek.com`; check for a stray space |
| `The API key works but has insufficient credit` | Top up the DeepSeek balance |
| `Missing openpyxl` / `Missing openai` | Re-run step 1. If you have several Pythons installed, use `python -m pip install openpyxl openai` |
| Run interrupted | Re-run the same command; it resumes from the checkpoint |

## Provenance and comparisons

Every run records the model, the criteria version, and the prompt source (GitHub ref or local
folder) in the closing summary. Quote those when reporting results.

**Hold either the model or the prompt version fixed, never both.** This was established
empirically: record `D0020934` (hurricane × adolescent mental health) was dropped when v2 prompts
ran on gpt-4o-mini but retained on DeepSeek — a **model** effect, not a prompt effect. Use `--ref`
to pin the prompt revision when a comparison has to be reproducible.

Prior prompt-effect result for context (v1 → v2, model held constant on DeepSeek, n = 1000,
identical records; see `pilot_screening_v2/results/comparison_v1_vs_v2_deepseek_1000.md`):

| Decision | v1 | v2 |
|---|---|---|
| INCLUDE | 34 | 29 |
| REVIEW | 31 | 6 |
| EXCLUDE | 935 | 965 |

v2 changed 42 of 1000 decisions, mostly by clearing a noisy human-review pile (28 REVIEW →
EXCLUDE: engineering, animal-lab and methods papers, commentaries, non-registered hazards, and
records where "flooding" or "cold" meant a *therapy* rather than a hazard).

**Expected direction for v3.** The design gate should cut INCLUDE further, because many on-topic
disaster studies are cross-sectional or qualitative. In a manual pass over one 100-record reviewer
sheet, applying the design rule moved 33 of 100 decisions and left only designs with genuine
within-unit variation (panel pre/post, case-crossover, time-series). The risk to watch is
**recall**: abstracts often omit the design, so the explicit-only rule and the review route for
unstated designs are what keep eligible studies from being dropped. Final recall will be confirmed
against the completed human labels from this packet.
