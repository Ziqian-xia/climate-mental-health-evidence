# Usage terms

## PubMed records

PubMed metadata is produced by the US National Library of Medicine and is in
the **public domain** under US copyright law. The PubMed CSV and JSONL files
in `data/pubmed/` may be used, modified, and redistributed without
restriction.

Reference: <https://www.nlm.nih.gov/databases/download/pubmed_medline.html>

## Scopus records

Scopus is a proprietary database owned by Elsevier. The records in
`data/scopus/` were retrieved on 2026-06-03 using an authorised institutional
API key, and are shared here for the purpose of **systematic-review
reproducibility** under research fair-use provisions.

If you intend to:

- Redistribute the Scopus subset as part of a derivative dataset,
- Use these records in a commercial product, or
- Process more than a few thousand records for purposes other than
  reproducing or extending this systematic review,

please consult Elsevier's [API Service Agreement](https://dev.elsevier.com/api_service_agreement.html)
and [Text and Data Mining Policy](https://www.elsevier.com/about/policies/text-and-data-mining)
or contact your institutional Elsevier representative before doing so.

## Code

All code in `scripts/` is released under the MIT licence (see `LICENSE`).

## Derived datasets

`data/deduplication_summary.json` and any aggregate counts derived from this
repository are released under **CC BY 4.0** (see `LICENSE-DATA`). Attribute
to the citation listed in the main `README.md`.
