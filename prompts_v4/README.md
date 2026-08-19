# Title/abstract screening prompts — v4

Prompt set for the LLM-assisted title/abstract pre-screen of the climate-hazards × mental-health
systematic review. A router prompt assigns candidate hazard topics; one prompt per registered
hazard then decides INCLUDE / EXCLUDE / review. The LLM is a **first-pass, high-recall sieve** —
humans remain the final arbiter.

**v4 is a maintenance release.** It fixes one schema omission, unifies one code name, and adds one
exposure constraint.
It does not introduce a new discipline the way v2 (outcome) and v3 (design) did, and it changes no
other rule. Everything not listed under *What v4 changes* is byte-identical to v3.

## Contents of this folder

| File | Purpose |
|---|---|
| `00_candidate_topics_prompt.md` | Router: assigns candidate hazard topics. Topic assignment only — no design or outcome gate |
| `01_temperature_prompt.md` | Temperature / heat / cold module — **changed in v4** |
| `02_wildfire_prompt.md` | Wildfire / bushfire / smoke module — **changed in v4** |
| `03_flood_prompt.md` | Flood / inundation module — **changed in v4** |
| `04_cyclone_prompt.md` | Tropical cyclone / hurricane / typhoon module — **changed in v4** |
| `05_drought_prompt.md` | Drought / water scarcity module — **changed in v4** |
| `screening_criteria_v4.md` | Full eligibility rules (supersedes v3) |
| `screen_excel_v4_deepseek.py` | Screens the reviewer packet (Excel) with these prompts on DeepSeek |
| `README.md` | This file |

**Note on the folder layout.** v1 and v2 prompts live in a `title_abstract_screening/` subfolder;
**v3 and v4 prompts sit directly in `prompts_v3/` / `prompts_v4/`** with no subfolder. Any script
pointing at `prompts_v4/title_abstract_screening/...` will fail with a 404.

| Version | Path in this repo | What it adds |
|---|---|---|
| v1 | `prompts/title_abstract_screening/` | Baseline: hazard (X) and outcome (Y) gates, deliberately over-inclusive |
| v2 / v2.1 | `prompts_v2/title_abstract_screening/` | **Outcome discipline**: the measured outcome must be mental health / wellbeing. v2.1 adds non-original / evidence-synthesis discipline |
| v3 | `prompts_v3/` | **Design discipline** (gate G5): the study must exploit within-unit variation. New exclusion code `wrong_design` |
| v4 | `prompts_v4/` (this folder) | **Maintenance**: `wrong_design` added to the hazard prompts' output enum; hazard-gate code renamed `wrong_hazard` -> `wrong_exposure`; temperature gains a laboratory / climate-chamber **setting requirement** |

---

## What v4 changes

### 1. `wrong_design` added to the `exclusion_code` enum in `01`–`05`

v3 introduced the *Design discipline* section, which instructs the model to emit
`exclusion_code = "wrong_design"`. The JSON output schema at the bottom of the same five files never
listed that value:

```diff
- "exclusion_code": "NA | wrong_hazard    | wrong_outcome | not_human_empirical | non_original | animal_or_lab_only",
+ "exclusion_code": "NA | wrong_exposure | wrong_outcome | not_human_empirical | non_original | animal_or_lab_only | wrong_design",
```

(The `wrong_hazard` -> `wrong_exposure` half of this line is change 2, below.)

Applied identically to all five hazard prompts. The router (`00`) has no `exclusion_code` field and
is unchanged.

**Practical impact: small but worth doing.** With free-form JSON generation (which is how
`screen_excel_*_deepseek.py` calls the model) the omission did no damage — in the 150-record
`packet150_v3` run the model emitted `wrong_design` 28 times, more than any other code. The enum
only bites if the value is ever enforced as a real JSON schema / structured-output constraint, or
if a downstream consumer validates against the documented enum. This change removes that
landmine and makes the file self-consistent.

### 2. Hazard-gate code renamed `wrong_hazard` -> `wrong_exposure`

The five hazard prompts emitted `wrong_hazard` for a failed hazard gate; `screening_criteria_v4.md`
has always called the same code `wrong_exposure`. v4 standardises on **`wrong_exposure`**, the
criteria document's name, so the two can be tabulated together. Two places change:

- the `exclusion_code` enum in all five hazard prompts (shown in the diff above);
- one prose line in `03_flood_prompt.md`: *"`EXCLUDE` as `wrong_exposure` if the title/abstract
  studies heavy precipitation/rainfall as the exposure without a flood … pathway."*

**No back-migration is needed.** Both v3 result sets in the repo were checked and neither contains a
single `wrong_hazard` value:

| Result file | Codes actually emitted |
|---|---|
| `pilot_screening_v3/.../packet150_v3_deepseek_decisions.csv` | `wrong_design` 28, `wrong_outcome` 12, `non_original` 5, `not_human_empirical` 3, `animal_or_lab_only` 1 |
| `pilot_screening_v3_router5category_300/.../screening_v3_pipeline_300_results.xlsx` | `wrong_outcome` 25, `not_human_empirical` 14, `wrong_design` 8, `animal_or_lab_only` 4, `non_original` 3 |

Hazard-gate failures are almost always resolved earlier, at the router: a record with no eligible
hazard gets an empty `candidate_topics` list and is excluded with *"No eligible registered hazard
identified"* before any module prompt runs, so no module-level code is produced. That is why the
rename is free — but it also means the *hazard* gate is currently invisible in exclusion-code
statistics. Worth knowing before reading those tables as a breakdown of why records were dropped.

### 3. Temperature gains a *Setting requirement* (new section in `01`)

The temperature hazard is defined as ambient temperature "across the full distribution". Nothing in
v3 said the temperature had to occur *naturally*, so a laboratory or climate-chamber exposure
satisfied every gate — including the design gate, since a within-subject chamber crossover
identifies its own effect cleanly.

This is not hypothetical. In the `packet150_v3` run:

> `D0085607` — *Human mood and cognitive function after different extreme cold exposure*
> → AI decision **INCLUDE**, reason: *"Within-subject climate chamber cold exposure; mood measured
> as outcome, so eligible."* A human rater caught it: *"No specific disaster, lab creates cold
> environment."*

The abstract repeatedly uses the words *ambient temperature* to describe the chamber, which is
exactly why the existing wording admitted it. The three pre-existing rules that look like they
should have caught it all miss:

| Existing rule | Why it misses |
|---|---|
| `not_human_empirical` — "in-vitro/laboratory-only … **with no human mental-health outcome**" | Chamber studies have human subjects and a mood outcome |
| `animal_or_lab_only` — "animal or laboratory model … **with no human outcome**" | Same |
| `01`'s "heat shock proteins, cellular heat stress, **animal/lab thermal exposure**" | Reads as being about animal and cell work; also sits under a list prefixed *"unless an eligible ambient temperature exposure is also present"*, and a chamber is described as ambient |

v4 therefore adds a **separate section**, not another bullet in that list, so the "unless ambient"
escape hatch does not defeat it. It excludes with `exclusion_code = "wrong_exposure"` (hazard gate
G2), never `wrong_design` — the design is fine; the exposure is not a climate hazard.

The section carries an explicit **scope limit**, because the obvious over-broad version of this rule
would be wrong:

- **outdoor workers, farmers, construction and agricultural labourers remain eligible.** They are a
  core exposed population in this literature. The distinction drawn is **machine-generated vs
  naturally occurring**, not occupational vs general population.
- indoor exposure to outdoor-origin heat or cold (housing without air conditioning in a heatwave,
  fuel-poor households in a cold spell) remains eligible.
- if the abstract does not state the setting → `INCLUDE` with `review_flag = true`. Never exclude on
  silence, consistent with the v3 design gate.

A matching *Setting requirement* paragraph is added under X1 in `screening_criteria_v4.md`, plus a
cross-reference under `wrong_exposure`, so the criteria document and the prompt cannot drift apart.

### 4. Version markers

Every file in this folder carries a `**Version: v4**` marker near the top. The screening script
refuses to run if any prompt is missing it, so a v3 file can never be screened with and reported as
v4. The historical v3 and v2 banners are kept underneath, as they were in v3.

---

## Verifying this release

```
grep -c "wrong_design" 0[1-5]_*.md          # 2 per file: section heading + enum
grep -n "wrong_hazard" 0[1-5]_*.md          # banner note only, never in the enum
grep -n "Version: v4" *.md                  # 6 files, one marker each
grep -n "Setting requirement" 01_*.md screening_criteria_v4.md
python -c "import ast;ast.parse(open('screen_excel_v4_deepseek.py').read())"
```

A three-record smoke test (below) prints the temperature prompt size: **~11832 chars means v4**
(v3 ~8829, v2 ~5916, v1 ~2616).

---

# Screening the reviewer packet: `screen_excel_v4_deepseek.py`

Screens `review_packet_pairwise.xlsx` — the three-way pairwise human-labelling packet (sheets
`Ziqian`, `Jacob`, `Tony`; 100 rows each, 300 rows, **150 unique records**, each record assigned
to exactly two raters) — with the v4 prompts on `deepseek-v4-flash`.

The six prompts are **fetched from GitHub at runtime**, so a collaborator can clone the repo (or
download just this one script) and run it without editing any path. If the network is
unavailable, the script falls back to a local `prompts_v4/` folder and prints which source it
used — it never falls back silently.

Title and abstract are read straight from the Excel file, so **no corpus download is needed**.

**What it will not touch.** Results are written to a **new** file as two new columns per sheet,
`AI Suggestion (v4)` and `AI Reason (v4)`. The `Human Decision` and `Audit Notes` columns are
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
cd C:\path\to\climate-mental-health-evidence\prompts_v4
```

macOS / Linux:

```
cd /path/to/climate-mental-health-evidence/prompts_v4
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
python screen_excel_v4_deepseek.py --limit 3
```

You should see, in order:

```
      300 rows across 3 sheet(s); 150 unique records.
      Prompt source: GitHub Ziqian-xia/climate-mental-health-evidence@main/prompts_v4
      Loaded 6 prompts; temperature prompt = 11832 chars (v4 ~11832, v3 ~8829, v2 ~5900, v1 ~2600).
      API key is valid.
```

Those four lines confirm the packet was found, GitHub was reachable, the prompts really are v4,
and the key works. The run then finishes in under a minute and writes a summary.

**5. Run the full set.**

```
python screen_excel_v4_deepseek.py
```

150 records take roughly **20–40 minutes** on DeepSeek (one router call plus one call per
candidate hazard topic, sent sequentially). Progress prints every five records with an estimated
time remaining.

Every record is checkpointed to `screen_v4_progress.json` immediately, so if the network drops or
the window closes, **just run the same command again** — it resumes where it stopped and re-screens
nothing. Keep the terminal open and stop the machine from sleeping during the run.

**6. Collect the output.** Two files, written next to the input:

- `review_packet_pairwise_v4_ai.xlsx` — the packet with `AI Suggestion (v4)` / `AI Reason (v4)`
  added. This is what a human reads.
- `review_packet_pairwise_v4_ai_records.jsonl` — **one JSON object per record, written the moment
  that record is screened.** This is the provenance record; see *Per-record output* below. Keep it.

Delete `screen_v4_progress.json` once you are happy with the result — leaving it in place will make
the next run think the work is already done. **Do not delete the `.jsonl`**: it is the only copy of
the raw model output, and it is also what the script resumes from.

## Options

All optional; the defaults are what step 5 uses.

| Flag | Default | Use it when |
|---|---|---|
| `--in <path.xlsx>` | `review_packet_pairwise.xlsx`, searched next to the script, in the parent folder, then the current folder | The packet is somewhere else |
| `--out <path.xlsx>` | `<input>_v4_ai.xlsx` | You want a different output name |
| `--limit N` | 0 (all) | Smoke test, or screening in batches |
| `--prompts-dir <folder>` | (unset — fetch from GitHub) | Force local prompts, e.g. to test an unpushed edit |
| `--ref <branch-or-sha>` | `main` | Pin an exact prompt revision for a reproducible run |
| `--model <name>` | `deepseek-v4-flash` | Compare models (see the caveat below) |
| `--sheets A,B,C` | `Ziqian,Jacob,Tony` | The packet has different sheet names |
| `--checkpoint <path.json>` | `screen_v4_progress.json` next to the output | Two runs must not share a resume file |
| `--jsonl <path.jsonl>` | `<output>_records.jsonl` | You want the per-record log somewhere specific, or two runs must not share one |

## Per-record output (`*_records.jsonl`)

The Excel file keeps only the aggregated decision and a truncated reason string. Everything the
aggregation discards — and it discards a lot — is written to a JSONL log instead, one line per
record, appended and `fsync`ed **before the script moves on to the next record**:

```json
{"dedup_id": "D0085607", "screened_at": "2026-08-18T09:31:22Z", "model": "deepseek-v4-flash",
 "criteria_version": "per-topic prompt set 00-05 v4 ...", "prompt_source": "GitHub ...@main/prompts_v4",
 "decision": "EXCLUDE", "reason": "temperature: EXCLUDE [wrong_exposure] - ...",
 "candidate_topics": ["temperature"],
 "router_raw":  { ... full router reply: topic_confidence, needs_human_topic_review, ... },
 "modules_raw": [{"topic": "temperature", "raw": { ... full module reply: decision, review_flag,
                                                   exclusion_code, confidence, notes_for_human_review }}],
 "title": "...", "abstract_chars": 1042, "elapsed_sec": 3.8}
```

Why this matters:

- **`exclusion_code` becomes countable.** Reading it out of the free-text `reason` column means
  parsing `[wrong_design]` out of a string; here it is a field, per topic.
- **`needs_human_topic_review` and `topic_confidence` are preserved.** Both are produced by the
  router on every record and both were previously dropped on the floor.
- **Failed replies keep their raw text.** A call that could not be parsed is stored as
  `{"_error": ..., "_raw": "...", "_finish_reason": "length", "_hint": "reply was truncated ..."}`,
  so a truncation and a network failure are no longer indistinguishable after the fact.
- **Nothing is lost to a crash.** Records are durable as they are produced; a kill mid-write costs
  at most the final line, which is skipped on the next read.
- **It restores the step-wise provenance of the v1 pilot**, which logged
  `step1_candidate_topics.jsonl` / `step2_topic_screening.jsonl`. v2 and v3 dropped that.

Re-deriving a summary from the log needs no API calls:

```python
import json, collections
rows = [json.loads(l) for l in open("..._records.jsonl", encoding="utf-8")]
print(collections.Counter(r["decision"] for r in rows))
print(collections.Counter(m["raw"].get("exclusion_code")
                          for r in rows for m in r["modules_raw"] if "raw" in m))
```

### Token budget

`MAX_TOKENS` is **3000** (v3 used 800), with the fourth and final retry escalating to 6000. In the
300-record router-pipeline run, 800 produced empty or truncated replies on **46/300 records
(~15%)**: `deepseek-v4-flash` spends part of the budget on internal reasoning before emitting the
JSON, and longer or more ambiguous records ran out mid-reasoning. Truncations are now visible in
the log via `_finish_reason: "length"` rather than surfacing as an unexplained REVIEW.

## How a decision is reached

1. The router (`00`) returns candidate hazard topics. **No topics → EXCLUDE** ("no eligible
   registered hazard identified").
2. Each candidate topic's prompt (`01`–`05`) returns `decision`, `review_flag`, `exclusion_code`
   and `one_line_reason`.
3. Aggregated across topics: any INCLUDE → **INCLUDE** (or **REVIEW** if that topic also set
   `review_flag`); otherwise any MAYBE or any `review_flag` → **REVIEW**; otherwise **EXCLUDE**.

`AI Reason (v4)` records every topic's verdict, exclusion code and one-line reason, so a REVIEW or
EXCLUDE can be traced to the gate that produced it.

## Troubleshooting

| Message | What to do |
|---|---|
| `Could not reach GitHub` then `Falling back to the local copy` | Nothing — the run continues on the identical local prompts. A phone hotspot usually restores the GitHub path |
| `GitHub is unreachable and no local copy ... was found` | Get on a network, or pass `--prompts-dir` pointing at a folder holding all six `00_`–`05_` prompt files |
| `These prompt files do not look like v4` | The folder passed to `--prompts-dir` holds v1/v2 prompts. Correct it rather than removing the check |
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

**Expected direction for v4.** The design gate should cut INCLUDE further, because many on-topic
disaster studies are cross-sectional or qualitative. In a manual pass over one 100-record reviewer
sheet, applying the design rule moved 33 of 100 decisions and left only designs with genuine
within-unit variation (panel pre/post, case-crossover, time-series). The risk to watch is
**recall**: abstracts often omit the design, so the explicit-only rule and the review route for
unstated designs are what keep eligible studies from being dropped. Final recall will be confirmed
against the completed human labels from this packet.

## Completed v4 human-alignment validation

The completed 300-paper validation used `deepseek-v4-flash` with the v4 prompt set and the
pairwise human-review labels. The AI returned **272 EXCLUDE, 20 REVIEW, and 8 INCLUDE** decisions,
with no API or parsing errors. Mapping human `MAYBE` to `REVIEW`, pooled AI–human agreement was
94.3% and **Cohen's κ = 0.673** across 600 label pairs. Per-rater kappas were **0.664 for Jacob**
and **0.683 for Tony**; human–human κ was **0.540** on the same 300 papers.

Full methods, distributions, and reproducibility paths are recorded in
[`results_v4_validation_300.md`](results_v4_validation_300.md).
