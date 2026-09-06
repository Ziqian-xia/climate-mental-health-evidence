# Pass 1: full-corpus title/abstract screening

This directory contains the exact executable source and eight prompt files used
to screen all 131,468 deduplicated records in the first pass. The original router
is prompts_v4/00_candidate_topics_prompt.md (v4.1). Documentation paths were updated
for publication; scripts, dependencies, and prompts were not changed.

See the [complete procedure](../README.md) and [archived results](results/README.md).

## Input

Download merged_deduplicated_records.csv.gz from the repository's
[data directory](https://github.com/Ziqian-xia/climate-mental-health-evidence/tree/main/data).
Save it in round1_full/data/merged_deduplicated_records.csv.gz.
Keep it compressed. This local data directory is not included in the upload.

Expected SHA256:

~~~text
1bd5b4b7917174907173a9fb59c82e8ec6fe060b1367255c7d4b7ad553fafddb
~~~

## Install and run

From the repository root, in PowerShell:

~~~powershell
Set-Location "final screening/round1_full"
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
~~~

On macOS/Linux:

~~~bash
cd "final screening/round1_full"
python3 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python run.py
~~~

The script uses DEEPSEEK_API_KEY or requests it through hidden input.
API execution incurs charges. Inputs and prompts are local.

This uses deepseek-v4-flash, high thinking, 32 concurrent requests, no sampling,
4,096 initial output tokens, a 16,384-token ceiling, three retries per unfinished
stage, and a 660-second request timeout. Add --concurrency 16 to lower concurrency.

Results are written to results/result.csv, results/review.csv, and results/result.json.
A rerun updates the local results/review.csv snapshot, so keep published results
separate from any new execution before committing changes.

## Resume

Preserve .work/full/ and run the identical command again. Valid completed stages
and records are reused. To export saved progress without API calls:

~~~powershell
.\.venv\Scripts\python.exe run.py --export-only
~~~

Exports use temporary files and per-file replacement. They are regenerated
snapshots, while per-record JSON files under .work/full/ provide resumption.

## Interpretation

The first-pass decisions were EXCLUDE 123,543; INCLUDE 708; REVIEW 7,217.
INCLUDE means retained by the automated title/abstract criteria, not final
full-text eligibility. Unresolved REVIEW records were reassessed in pass 2.

The published second pass uses the frozen published first-pass JSON. A newly
executed first pass may produce different answers and cannot silently replace
that baseline, whose exact hash is checked by the second-pass entry point.
