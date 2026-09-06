# Final screening

This directory documents two passes of automated title/abstract screening for
the climate-hazard and mental-health review. Both passes use DeepSeek V4 Flash.
This is not a title/abstract-then-full-text screening sequence, and pass 2 is
not an independent duplicate assessment of the entire corpus.

## Procedure

1. **Pass 1: full-corpus screening.** Screen all 131,468 deduplicated records
   with the original router and eligibility prompts in [round1_full](round1_full/README.md).
2. **Router clarification after pass 1.** Inspect REVIEW triggers and clarify
   unresolved hazard identity and routing coverage in the 00 router prompt.
   Retain the scientific eligibility criteria, hazard definitions, and screening
   engine. The changes are described below.
3. **Pass 2: REVIEW-only reassessment.** Select exactly the 7,217 original REVIEW
   records from the frozen first-pass JSON and reassess them through the
   [second-pass entry point](round2_review/START_REVIEW.md).
4. **Merge.** Replace those selected records with their completed new decisions.
   Retain all 124,251 original INCLUDE/EXCLUDE records unchanged and preserve
   corpus order. The final output again contains 131,468 records.

## Counts

| Snapshot | Records | EXCLUDE | INCLUDE | REVIEW |
| --- | ---: | ---: | ---: | ---: |
| Pass 1: full corpus | 131,468 | 123,543 | 708 | 7,217 |
| Pass 2: selected REVIEW set only | 7,217 | 5,625 | 94 | 1,498 |
| Final merged full corpus | 131,468 | 129,168 | 802 | 1,498 |

All 7,217 reassessments are complete. There are no unfinished reassessments in
the published final snapshot. INCLUDE denotes an automated title/abstract
decision; it does not establish final full-text eligibility. REVIEW remains
a queue for further assessment.

## Two preserved router versions

- [Original 00: pass 1](round1_full/prompts_v4/00_candidate_topics_prompt.md)
- [Revised 00: pass 2](round2_review/prompts_v4/00_candidate_topics_prompt.md)

The original router could set needs_human_topic_review=true for ambiguous
named topics as well as unidentified hazards. The unchanged engine gives
that flag priority over module decisions.

The revised router limits that flag to a text-supported, potentially eligible
exposure whose identity cannot be resolved or covered by assigned modules.
It distinguishes an unidentified hazard from an absent hazard. Low confidence,
manufactured-versus-natural exposure questions, and design or outcome eligibility
questions are routed to the relevant modules rather than independently triggering
human topic review. Genuine unresolved hazard identity still permits REVIEW.

This clarification was made after inspecting the first-pass results. No
eligibility standard was relaxed to force a lower REVIEW count. The five hazard
definitions, master criteria, shared rules, both original scripts, and dependency
file are identical between passes. The second pass adds a wrapper for selection,
resumption, and merging.

Selected records with abstracts rerun the router and newly selected modules.
Records without abstracts rerun the unchanged title-only path and do not use 00.
Six records with neither title nor abstract remain REVIEW without an API call.
Remaining REVIEW decisions are not repeatedly sent again on resume.

## Find the results

- [First-pass results and frozen baseline](round1_full/results/README.md)
- [Final merged results](round2_review/results/README.md)
- [Large result attachments](https://github.com/Ziqian-xia/climate-mental-health-evidence/releases/tag/final-screening-v1)

The repository contains one REVIEW CSV per pass. Full CSVs and compressed full
JSONs are distributed as Release attachments:

~~~text
round1-result.csv
round1-result.json.gz
final-result.csv
final-result.json.gz
~~~

The Release links are configured for tag final-screening-v1; they become live after
the maintainer uploads the accompanying assets and publishes that Release.

## Reproduction

Each round has a complete local source and prompt snapshot. No code fetches
prompts from GitHub. Python 3.11+ is required; install the pinned requirements
and provide your own API key. New API execution incurs charges.

To reproduce the first pass, follow [round1_full/README.md](round1_full/README.md).
The input data remain in the existing repository data directory; download the
compressed file into the local data location documented there.

To reproduce the published second-pass selection, use the exact archived
round1-result.json.gz and follow [round2_review/START_REVIEW.md](round2_review/START_REVIEW.md).
A REVIEW CSV alone is insufficient. The baseline JSON contains the full text
fields, previous decisions, and retained responses required by the wrapper.
Its uncompressed content hash is checked before execution:

~~~text
5e17a7006d6c0f96e64809d230a6119209cccdfce4cfc8a2f069129d90a3c023
~~~

A newly generated first-pass JSON is not interchangeable with the frozen
published baseline. Online API re-execution may differ, so the archived first-pass
JSON fixes the exact 7,217-record reassessment set. This archive reproduces the
record selection, prompts, parameters, and procedure; it does not promise
bit-for-bit identical future model responses.

Keep each run's .work/ directory locally for resumption. The archived output
JSON preserves execution provenance, while the checkpoint directories are not
part of this upload. The final merged JSON distinguishes baseline and second-pass
records instead of attributing every record to the revised router.

## Publication packaging

Scripts, dependencies, prompts, and result contents were copied without changes
from the completed local runs. Only documentation paths and documentation-related
package checksums were updated for this layout. The archived JSON metadata was
not rewritten. [publication_manifest.json](publication_manifest.json) records
source and asset hashes and the two execution fingerprints.

The two prompts_v4 directories inside this folder are the authoritative snapshots
for these two passes. Other prompt and pilot folders elsewhere in the repository
are historical materials. No virtual environments, caches, API keys, test files,
or downloaded input dataset are included here.
