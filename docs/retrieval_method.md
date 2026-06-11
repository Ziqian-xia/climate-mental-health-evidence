# Retrieval method

Date of retrieval: **2026-06-03**

This document describes how the PubMed and Scopus snapshots in `data/` were
collected. The goal is to make the pulls fully reproducible by anyone with
their own API credentials.

---

## Common parameters

- **No date restriction.** Both pulls span the full backfile (`pre-1990` bucket
  plus every individual year up to 2026).
- **No language restriction.** No filter on document language was applied at
  retrieval time.
- **No document-type restriction.** Articles, reviews, letters, conference
  abstracts, book chapters, and erratum notices were all retained. Eligibility
  by document type is applied later at the screening stage, per Cochrane
  Handbook guidance.
- **Human filter (PubMed and Embase only).** The PubMed Boolean ends with
  `NOT (animals[mh] NOT humans[mh])` to exclude animal-only studies indexed
  with `animals[mh]` but no `humans[mh]` tag. Scopus, PsycINFO, and OpenAlex
  do not index animal-only studies in the way PubMed does, so no equivalent
  filter is needed for those.

---

## PubMed (`data/pubmed/`)

### API used

NCBI Entrez E-utilities ESearch + EFetch:

- `POST https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi`
- `POST https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi`

With an API key, the rate cap is 10 requests/second.

### Year-slice strategy

Per the registered query, the total result count (27,731) exceeds the
ESearch `retmax` hard cap of 9,999 in a single call. To get a complete PMID
list we slice the search by publication year:

| Slice term | Per-year PMIDs |
|---|---|
| `("1500"[PDAT] : "1989"[PDAT])` | 1,816 |
| `"1990"[PDAT]` through `"2026"[PDAT]` | each <2,500 |

Each slice ESearch returns a complete PMID list (well under 9,999).
PMIDs are concatenated and de-duplicated across slices (in case a citation
straddles two `PDAT` years).

### Why not WebEnv+EFetch?

The "canonical" PubMed pull pattern is:

1. ESearch with `usehistory=y` → returns WebEnv + QueryKey
2. EFetch with WebEnv + QueryKey + `retstart` + `retmax=500` → paginate

We tried this first and discovered that for a single large WebEnv session,
EFetch silently returns fewer records than `retmax` requests once the
cumulative offset is high enough — in our run, 92 EFetch calls returned only
9,953 of 27,731 expected records (~36%). The issue is intermittent and not
documented by NCBI but well-reported by other systematic reviewers.

Explicit `id=PMID1,PMID2,...` EFetch calls (in batches of 200) avoid the
issue entirely because each call is self-contained.

### Output parsing

EFetch returns XML containing `<PubmedArticle>` and `<PubmedBookArticle>`
elements. Both are extracted. Fields:

- `pmid`: `.//PMID`
- `doi`: `.//ArticleId[@IdType="doi"]`
- `title`: `.//ArticleTitle` or `.//BookTitle`
- `abstract`: concatenated `.//AbstractText` (joined by spaces; preserves
  any structured-abstract section labels)
- `journal`: `.//Journal/Title` or `.//Journal/ISOAbbreviation`
- `year`: `.//PubDate/Year` or first 4 chars of `.//PubDate/MedlineDate`
- `authors`: first 10 authors as `LastName Initials`

### Total runtime

ESearch: 38 calls in ~10 s.
EFetch: 139 calls (200 PMIDs each) in ~200 s.
Wall clock: ~3 minutes 37 seconds.

---

## Scopus (`data/scopus/`)

### API used

Elsevier Scopus Search API:

- `GET https://api.elsevier.com/content/search/scopus`
- Authentication: `X-ELS-APIKey` header (plus optional `X-ELS-Insttoken`).
- Rate cap: 9 requests/second; weekly quota tracked via `X-RateLimit-Remaining`.

### Year-bucketed cursor strategy

`start+count` pagination on the Scopus Search API is hard-capped at 5,000
results per query. Cursor pagination can theoretically bypass this, but a
single-cursor pull of 59,721 records is prone to mid-run read-timeouts that
lose the cursor state.

We instead split by publication year so each bucket is independent:

| Bucket | Filter | Count |
|---|---|---|
| `pre1990` | `PUBYEAR < 1990` | 3,779 |
| `y1990` ... `y2024` | `PUBYEAR = YYYY` | 256 ... 4,736 |
| `2025_ar_re` | `PUBYEAR = 2025 AND (DOCTYPE(ar) OR DOCTYPE(re))` | 4,449 |
| `2025_other` | `PUBYEAR = 2025 AND NOT (DOCTYPE(ar) OR DOCTYPE(re))` | 789 |
| `y2026` | `PUBYEAR = 2026` | 2,183 |

2025 had to be split by doctype (article/review vs. other) because the
single-year count (5,238) just exceeded the 5,000 cap. All other years
stayed under.

Within each bucket, cursor pagination is used with `count=25` and
`view=COMPLETE` (the `view=COMPLETE` is required to get the abstract field
`dc:description` filled).

### Robustness

- A `requests.Session` with `urllib3` `Retry` adapter handles HTTP 429 and
  5xx automatically with exponential backoff.
- An additional per-call manual retry handles `Timeout` / `ConnectionError`
  exceptions (which the Retry adapter does not always catch).
- Each bucket is independent — a failure in one bucket loses at most a few
  thousand records, not the whole 60k.
- All records are EID-deduped across buckets (no cross-bucket overlap was
  observed in practice).

### Output parsing

Each Scopus `search-results.entry` JSON object is stored verbatim in
`works_full.jsonl.gz`. The flattened CSV includes:

- `eid`: `eid` (Scopus identifier)
- `doi`: `prism:doi`
- `title`: `dc:title`
- `abstract`: `dc:description`
- `creator`: `dc:creator` (first author last name + initials)
- `publication_name`: `prism:publicationName`
- `cover_date`: `prism:coverDate`
- `citedby_count`: `citedby-count`
- `bucket`: the year/doctype bucket the record came from

### Total runtime

39 buckets, 2,401 API calls, ~98 minutes wall clock. One bucket (`y2023`)
took ~42 minutes due to transient connection drops; all retries succeeded.

---

## Queries

The exact Boolean strings are committed at `data/pubmed/query.txt` and
`data/scopus/query.txt`. They are byte-identical to the canonical search
formula registered with the protocol. Anyone re-running the scripts with
their own API keys against the same dates should obtain the same counts
(small drift is possible if records are added or removed from the index
in the intervening period).
