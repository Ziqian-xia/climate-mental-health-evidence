# Cross-database deduplication analysis

Computed 2026-06-03 from `data/pubmed/works_summary.csv` and
`data/scopus/works_summary.csv` using `scripts/dedup_analysis.py`.

## Per-database counts

| Database | Total records | With DOI | Without DOI |
|---|---|---|---|
| PubMed | 27,731 | 24,882 | 2,845 |
| Scopus | 59,721 | 52,731 | 6,912 |
| Raw sum (with cross-database duplicates) | 87,452 | — | — |

The "without DOI" rows are mostly older records (pre-2000) where DOIs were
not yet assigned, plus some non-journal items (conference abstracts, books).

## DOI-based dedup (across PubMed × Scopus)

| Quantity | Value |
|---|---|
| DOI overlap | 15,020 |
| PubMed-only DOIs | 9,862 |
| Scopus-only DOIs | 37,711 |
| **DOI union** | **62,593** |
| + PubMed no-DOI records | + 2,845 |
| + Scopus no-DOI records | + 6,912 |
| **Final pool (DOI-deduped, no-DOI kept)** | **72,350** |

## Coverage statistics

| Direction | Value |
|---|---|
| PubMed records (DOI) also in Scopus | 60.4% |
| Scopus records (DOI) also in PubMed | 28.5% |

PubMed coverage by Scopus is lower than the ~89% figure reported by
[Bramer et al. 2018](https://doi.org/10.1186/s13643-018-0738-1) for
typical systematic-review searches. The gap is explained by what our raw
pull retains:

- PubMed indexes a large body of letters, comments, editorials, and
  conference abstracts that Scopus filters out or indexes selectively.
- Some PubMed records have no DOI (especially older ones), so they are
  counted as no-DOI rather than as overlap.
- Both effects diminish after document-type screening (which is applied
  in the screening stage, not retrieval).

## Remaining duplicates not caught by DOI

The "no-DOI" records (2,845 PubMed + 6,912 Scopus) may include
cross-database duplicates that DOI alone cannot detect. A second-pass
dedup using fuzzy title + first-author + publication-year matching is
recommended before final screening; this typically removes another
~1,500–2,000 duplicates in our experience.

The dedup against the eventual Embase + PsycINFO + OpenAlex pulls is
performed once those datasets arrive.
