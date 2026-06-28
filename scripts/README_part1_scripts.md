# Part 1 Scripts — Deduplication & Standardization

Two scripts reproduce all five Part 1 output files from the raw database exports.
OpenAlex is excluded by project decision; the pipeline uses PubMed, Scopus,
Embase, and PsycINFO.

## Requirements
- Python 3 (standard library only — no pip installs needed)

## Input layout expected
A data directory containing one subfolder per database:

    data/
      pubmed/works_summary.csv
      scopus/works_summary.csv.gz
      embase/*.ris                       (11 year-bucketed RIS files)
      psycinfo/PSYCINFO_QUERY_RESULTS.RIS

(This matches the layout in the climate-mental-health-evidence repo.)

## Step 1 — Standardize

    python3 01_standardize.py [DATA_DIR] [OUT_DIR]
    # defaults: DATA_DIR=./data  OUT_DIR=./out

Reads all four databases (CSV for PubMed/Scopus, a RIS parser for
Embase/PsycINFO), normalizes DOI and title, and writes one row per raw record.

Produces:
  - all_records_standardized.csv      <-- FILE 1
  - standardize_qc.json               (field-completeness QC, not a SOP deliverable)

Per-database field mapping handled inside the script:
  - PubMed:   pmid -> source_id; CSV columns map directly
  - Scopus:   eid -> source_id; cover_date->year, creator->authors,
              publication_name->journal
  - Embase:   RIS; U2 (L-number)->source_id, N2->abstract, A1->authors, DO->doi
  - PsycINFO: RIS; ProQuest docview id from UR->source_id, AB->abstract,
              AU->authors, DO (a full URL)->doi (normalized to bare DOI)

## Step 2 — Deduplicate (SOP Steps 2–5)

    python3 02_deduplicate.py [STANDARDIZED_CSV] [OUT_DIR]
    # defaults: STANDARDIZED_CSV=./out/all_records_standardized.csv  OUT_DIR=./out

DOI dedup (exact normalized-DOI match), then title-metadata dedup with SOP
guard rails (identical normalized title >= 4 words and not generic, years
within 1, no first-author conflict). Records tripping a guard rail are kept
in the pool but flagged for manual review rather than auto-merged.

Produces:
  - merged_deduplicated_records.csv    <-- FILE 2
  - duplicate_groups.csv               <-- FILE 3
  - doi_conflict_title_groups.csv      <-- FILE 4
  - dedup_summary.md                   <-- FILE 5

## End-to-end

    python3 01_standardize.py data out
    python3 02_deduplicate.py out/all_records_standardized.csv out

## Reproduced numbers (4 databases, OpenAlex excluded)
  Raw total:            180,852
  Final screening pool: 131,468
  Duplicates removed:    49,384
  Duplicate groups:      31,454  (31,171 by DOI, 283 by title)
  Manual-review groups:   2,999  (7,154 records; mostly first-author conflicts)

## Tunable parameters (top of 02_deduplicate.py)
  - MIN_TITLE_WORDS = 4        minimum words for a title to be merge-eligible
  - GENERIC_TITLES  = {...}    titles never auto-merged (editorial, erratum, ...)
  Representative-record choice: longest abstract, then most complete title.
