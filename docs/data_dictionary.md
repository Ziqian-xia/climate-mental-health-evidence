# Data dictionary

## `data/pubmed/works_summary.csv`

| Column | Type | Description |
|---|---|---|
| `pmid` | string | PubMed identifier |
| `doi` | string | Digital Object Identifier (may be empty for older records) |
| `title` | string | Article title; truncated to 500 chars for CSV; full string in JSONL |
| `abstract` | string | Concatenated `AbstractText` content; truncated to 1500 chars for CSV; full string in JSONL |
| `journal` | string | `Journal/Title`, falling back to `Journal/ISOAbbreviation` |
| `year` | string | First 4 chars of `PubDate/Year` or `PubDate/MedlineDate` |
| `authors` | string | First 10 authors as `LastName Initials`, joined by `; ` |

## `data/pubmed/works_full.jsonl`

One JSON object per line. Each object has the same fields as the CSV but
without truncation, and with `authors` as a JSON array of strings.

## `data/scopus/works_summary.csv.gz`

(gzip-compressed; decompress with `gunzip -k`.)

| Column | Type | Description |
|---|---|---|
| `eid` | string | Scopus electronic identifier |
| `doi` | string | DOI (often empty for non-journal items) |
| `title` | string | `dc:title`; truncated to 500 chars |
| `abstract` | string | `dc:description`; truncated to 1500 chars |
| `creator` | string | First-author surname + initials (`dc:creator`) |
| `publication_name` | string | Journal or proceedings name (`prism:publicationName`) |
| `cover_date` | string | Cover date `YYYY-MM-DD` (`prism:coverDate`) |
| `citedby_count` | string | Scopus-counted citations as of retrieval date |
| `bucket` | string | Year/doctype bucket the record was retrieved in (provenance) |

## `data/scopus/works_full.jsonl.gz`

One Scopus `search-results.entry` JSON object per line. Schema follows
the [Elsevier Scopus Search API documentation](https://dev.elsevier.com/scopus_search_views.html);
fields commonly present include:

- `eid`, `prism:doi`, `prism:url`
- `dc:title`, `dc:description`, `dc:creator`
- `prism:publicationName`, `prism:issn`, `prism:eIssn`, `prism:volume`,
  `prism:issueIdentifier`, `prism:pageRange`
- `prism:coverDate`, `prism:coverDisplayDate`
- `subtype`, `subtypeDescription`
- `affiliation` (array)
- `author` (often, but depends on view)
- `openaccess`, `openaccessFlag`, `freetoread`

## `data/deduplication_summary.json`

Output of `scripts/dedup_analysis.py`, summarising DOI overlap between
the two pulls.

## `data/{pubmed,scopus}/run_summary.json`

Per-database run metadata: per-slice / per-bucket counts, API call counts,
total elapsed time. Use these as audit logs to confirm the pull was
complete.
