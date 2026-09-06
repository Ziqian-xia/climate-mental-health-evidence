# Reassess the original REVIEW records

Use **rerun_review.py** for this workflow. The original run.py is retained as
an unchanged dependency/source snapshot. Do not start this pass with run.py.

## Scope and unchanged files

| Original decision | Records | Treatment |
| --- | ---: | --- |
| EXCLUDE | 123,543 | Retain the original record unchanged |
| INCLUDE | 708 | Retain the original record unchanged |
| REVIEW | 7,217 | Reassess using the unchanged screening engine |
| Total | 131,468 | Export the complete corpus |

Among the screening prompts, only prompts_v4/00_candidate_topics_prompt.md changed.
Its v4.2 revision clarifies unresolved hazard identity, empty topic lists, and
the human topic review flag. The original hazard definitions remain unchanged.

Both original Python scripts, requirements.txt, and all seven other prompt files
are byte-for-byte identical to the baseline package. The workflow adds
rerun_review.py, these instructions, and package_manifest.json. Documentation
paths and checksums were updated for this publication layout. The entry point
checks the released file hashes before proceeding.

## Required baseline

[Download the frozen baseline](https://github.com/Ziqian-xia/climate-mental-health-evidence/releases/download/final-screening-v1/round1-result.json.gz).
This link becomes available when the accompanying Release is published.

Provide the **original full result.json**, or the separately supplied compressed
copy, round1-result.json.gz. A REVIEW CSV alone lacks the full
input text, responses, and unselected records needed for this workflow.

Expected SHA256 of the uncompressed JSON content:

~~~text
5e17a7006d6c0f96e64809d230a6119209cccdfce4cfc8a2f069129d90a3c023
~~~

The entry point reads .json.gz directly and verifies its decompressed content.
Do not modify the baseline or replace it with a later merged result. The REVIEW
selection stays fixed across interruptions and restarts.

The compressed baseline is distributed separately to keep the source ZIP small.
When publishing, provide it as a separate downloadable asset, for example a
GitHub Release attachment, and link it alongside this source package.
Collaborators require both. No download URL is assumed or fetched by the code.

The original data CSV is not needed here: the baseline JSON already contains all
titles and abstracts. To reproduce the earlier full screening from scratch,
download merged_deduplicated_records.csv.gz from the repository's
[data directory](https://github.com/Ziqian-xia/climate-mental-health-evidence/tree/main/data)
and follow ../round1_full/README.md in this archive.

## Install

Python 3.11 or newer is required. Open PowerShell in this package directory:

~~~powershell
py -3 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
~~~

An existing environment installed from the unchanged requirements also works.
On macOS/Linux, use python3 -m venv .venv and .venv/bin/python.

## Run

Download round1-result.json.gz from the Release linked above and save it in
round1_full/results/. From round2_review/:

~~~powershell
.\.venv\Scripts\python.exe rerun_review.py --baseline "..\round1_full\results\round1-result.json.gz" --output reproduced_results
~~~

Alternatively, point directly to the original full-screening result:

~~~powershell
.\.venv\Scripts\python.exe rerun_review.py --baseline "..\round1_full\results\result.json" --output reproduced_results
~~~

Use ONE command. They identify the same frozen baseline. The documented
--output reproduced_results option separates new results from the published
results/ snapshot. Preserve this option when resuming.

The entry point uses DEEPSEEK_API_KEY if set; otherwise it requests the key
through hidden terminal input. No key is included in this package.
Screening incurs API charges on the supplied account.

The model, endpoint, thinking level, token limits, and seed come from the
original run metadata: deepseek-v4-flash, high thinking, 4,096 initial output
tokens, and a 16,384-token ceiling. Concurrency defaults to 32; add
--concurrency 16 to reduce it. The original three retries and 660-second timeout
are retained. There is no sampling or record limit. Prompts and text are local.

## What is reassessed

For selected records with abstracts, the router is called again with the new 00
prompt. Every hazard module selected by that router is then called using the
unchanged module prompts and criteria. Old router or module responses are not
imported into the new run's checkpoints.

Selected records without abstracts rerun the original title-only path; the new
00 prompt is not used on that path. The six records without either title or
abstract remain REVIEW without an API call. Reassessing all 7,217 records does
not imply that every one uses the router or that every REVIEW will change.

The engine's aggregation rules remain unchanged. This workflow does not
mechanically convert old REVIEW records to EXCLUDE or relax eligibility criteria.

## Preparation and progress export without API calls

Validate the baseline and construct the frozen REVIEW input only:

~~~powershell
.\.venv\Scripts\python.exe rerun_review.py --baseline "..\round1_full\results\round1-result.json.gz" --prepare-only --output reproduced_results
~~~

Export current checkpoints into a full-corpus snapshot without API calls:

~~~powershell
.\.venv\Scripts\python.exe rerun_review.py --baseline "..\round1_full\results\round1-result.json.gz" --export-only --output reproduced_results
~~~

Exports always contain all 131,468 records. An unfinished reassessment retains
the old REVIEW decision, with status in_progress or retryable_error and
decision_basis=review_rerun_pending. The JSON retains the original reason and
any partial new response. It is never counted as a completed new decision.

## Resume and retry

After interruption, execute the identical run command again. Preserve the entire
.work/review_reassessment/ directory and the frozen source files.

- review_input.csv: only the original 7,217 REVIEW records.
- baseline.jsonl: verified local cache of the full original results.
- preparation.json: frozen baseline, input hashes, and selection rule.
- rerun/records/: one atomic JSON checkpoint per reassessed record.
- rerun/manifest.json and rerun/prompt_snapshot/: identity of the new run.

The unchanged engine skips completed new checkpoints even if they still say
REVIEW. It reuses valid completed stages and retries unfinished stages.
The original 124,251 INCLUDE/EXCLUDE records are never sent for reassessment.
The console reused count refers to saved records in the NEW run, not those
124,251 preserved baseline records.

Exit code 0 means all selected reassessments are complete. Exit code 2 means
some remain unfinished. API/runtime errors can return 1; interruption can
return 130. Resolve the cause, then use the same command to resume.

A response not committed before interruption may require another API request.
Exactly-once API execution or billing cannot be guaranteed.

## Full-corpus outputs

A new execution writes the following three files to the requested output directory:

- result.csv: all 131,468 records in original corpus order.
- review.csv: currently retained REVIEW records, including unfinished
  reassessments explicitly marked as pending.
- result.json: all records, retained raw responses, baseline and new-run
  provenance, progress, and hashes of the two matching CSV files.

The CSVs retain the original 12 columns, without token, cost, or attempt-count
columns. Original non-REVIEW JSON records are retained unchanged.
Selected records carry a review_reassessment audit field linking them to their
baseline document. Completed new records retain their original full-corpus
source_row; the subset row is recorded separately in the audit field.

The merged JSON has two distinct provenance histories. Do not describe all
merged records as screened with the new router. Inspect:

~~~text
metadata.summary.review_rerun_complete
metadata.summary.unfinished_review_records
metadata.summary.review_transitions
metadata.baseline_metadata
metadata.rerun_manifest
~~~

CSV/JSON exports are regenerated snapshots, not checkpoints. Exports write
temporary files first, then replace completed files, publishing JSON last.
If stopped between replacements, use --export-only to rebuild the matching set.
The CSV hashes in JSON identify matching files. Manual edits to exports will
be overwritten; keep human annotations separately.

The archived first-pass results are not modified. The entry
point rejects an output directory containing another workflow's result.json.

## Sharing and reproducibility

Publish the source package and the exact baseline download. After reassessment,
publish the three new results separately. Do not publish API keys, environments,
or .work/. Keep .work/ locally for resumption. Only the two published REVIEW CSV snapshots are bundled; no test data,
checkpoints, or full-result files are included in the repository upload.

This preserves the exact selection, source files, parameters, baseline decisions,
and new responses. Online API re-execution may differ because model generation
and the serving model are not guaranteed deterministic. A sampling seed does not
guarantee identical model responses.

## macOS / Linux

From round2_review, after creating the environment and installing requirements:

~~~bash
.venv/bin/python rerun_review.py --baseline "../round1_full/results/round1-result.json.gz" --output reproduced_results
~~~
