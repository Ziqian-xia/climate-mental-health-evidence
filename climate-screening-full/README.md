# Climate and Mental Health: Full-Corpus Screening

Screen all **131,468 records** using DeepSeek V4 Flash and the current screening criteria.
This package contains only the current code, prompts, dependencies, and instructions. The dataset must be downloaded separately; no results, pilot runs, historical versions, or test files are included.

## Download the input data

The dataset is not included in this package.

1. Open the [data folder in the GitHub repository](https://github.com/Ziqian-xia/climate-mental-health-evidence/tree/main/data).
2. Download **merged_deduplicated_records.csv.gz** using GitHub's raw-file download option.
3. Create a folder named **data** beside **run.py** and save the downloaded file there.

The required local layout is:

~~~text
run.py
screen_fast.py
prompts_v4/
data/
    merged_deduplicated_records.csv.gz
~~~

Keep the file compressed: do not unzip it or change its filename. The script reads the .csv.gz file directly.
If you already have the same file locally, copy it to this location instead of downloading it again.
The expected record count and SHA256 are listed under Screening rules and reproducibility below.
The script does not download data automatically.

## Install

Requires Python 3.11 or newer. Open a terminal in this directory.

Windows PowerShell:

```powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

macOS / Linux:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
```

## Run the entire corpus

Windows PowerShell:

```powershell
.\.venv\Scripts\python.exe run.py
```

macOS / Linux:

```bash
.venv/bin/python run.py
```

The script uses DEEPSEEK_API_KEY from the environment, or asks for your key using hidden input.
Model requests use your DeepSeek account and incur API charges. No API key is included in this package.

The default configuration is deepseek-v4-flash, high thinking, 32 concurrent requests, and no sampling or record limit.
To change concurrency, add --concurrency 16, for example.

All input data and prompts are read locally. The script does not fetch files from GitHub.
Screening requests are sent to https://api.deepseek.com/chat/completions.

## Resume or export progress

After an interruption, run the same command again. Completed stages are reused from .work/full/.
Do not delete this directory until you no longer need to resume the run.

To export saved progress without making API requests:

```powershell
.\.venv\Scripts\python.exe run.py --export-only
```

Use .venv/bin/python instead on macOS/Linux.
Changing the input, prompts, model settings, or engine code makes existing checkpoints incompatible; keep those files fixed during a run.

## Results to upload after screening

The results/ directory is created when results are exported and contains exactly:

- result.csv: one row per processed record, with 12 screening columns.
- review.csv: records whose current decision is REVIEW, using the same 12 columns.
- result.json: all detailed record responses plus input, prompt and code hashes, parameters, completion counts, and recorded usage.

CSV columns:
dedup_id, title, status, decision, decision_basis, candidate_topics, reason, module_decisions, module_exclusion_codes, screening_mode, title_only_decision, title_only_exclusion_code.

Check metadata.summary.complete_corpus in result.json before publishing final results. It must be true for a completed full-corpus run.
An interrupted or partially failed run may contain pending REVIEW placeholders; use status and decision_basis to distinguish them.
Exit code 2 indicates unresolved retryable errors; rerun the same command to retry saved unfinished stages.

Internal per-record JSON checkpoints and intermediate exports stay under .work/. They are excluded by .gitignore and do not need to be uploaded.

## Screening rules and reproducibility

The script reads the eight files in prompts_v4/. The overall criteria are in screening_criteria_v4.md, version v4.2.

- With an abstract: route the record to the relevant hazard modules.
- With a title but no abstract: EXCLUDE only when the title clearly establishes ineligibility; otherwise REVIEW. Never INCLUDE from a title alone.
- With neither title nor abstract: REVIEW.
- Semantic inconsistencies are retained as audit notes. Unusable JSON, invalid core routing/identity fields, and network errors remain technical errors.

There is no separate title_only_policy.md.
The engine is screen_fast.py, version 1.0.5. Use run.py as the entry point.
Fixed inputs and parameters support reproducibility, but online model outputs are not guaranteed to be identical across repeated runs.
The original bibliographic data are preserved without translation or other changes.

Input: data/merged_deduplicated_records.csv.gz
Records: 131,468
SHA256: 1bd5b4b7917174907173a9fb59c82e8ec6fe060b1367255c7d4b7ad553fafddb
Source repository: https://github.com/Ziqian-xia/climate-mental-health-evidence
Original data commit: d7770bfef837610d8ead6109985970612f931ebc

## Uploading this package

Extract the package and place its contents in the repository, preserving the directory structure.
The dataset is not included in this archive. Keep the existing repository data file in place; collaborators should download it using the instructions above.
Merge README.md and .gitignore with existing repository files if necessary.

Upload the three results/ files after the full run finishes.
Do not upload .venv/, .env, .work/, or any API key.
