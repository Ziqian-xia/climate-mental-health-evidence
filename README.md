# climate-mental-health-evidence

Retrieved literature for a systematic review and meta-analysis of the causal impacts of diverse climate hazards on global mental health and wellbeing (PROSPERO registration in progress).

This repository archives:

- The bibliographic records pulled from **PubMed** (n = 27,731) and **Scopus** (n = 59,721) on 2026-06-03 using the registered Boolean search formula.
- The exact queries used.
- The retrieval scripts, with credentials externalised to environment variables.
- A cross-database deduplication summary (DOI overlap, union, final pool).

Embase, APA PsycINFO, and OpenAlex retrievals are performed separately and will be added when complete.

---

## Contents

```
.
├── data/
│   ├── pubmed/
│   │   ├── query.txt                # exact Boolean used (PubMed/MeSH syntax)
│   │   ├── works_summary.csv        # 27,731 rows: pmid, doi, title, abstract, journal, year, authors
│   │   ├── works_full.jsonl         # 27,731 records, one JSON per line
│   │   └── run_summary.json         # per-year slice counts + API call count
│   ├── scopus/
│   │   ├── query.txt                # exact Boolean used (Scopus TITLE-ABS-KEY syntax)
│   │   ├── works_summary.csv.gz     # 59,721 rows, gzip-compressed
│   │   ├── works_full.jsonl.gz      # 59,721 records, gzip-compressed
│   │   └── run_summary.json         # per-bucket cursor pagination log
│   └── deduplication_summary.json   # DOI overlap stats across PubMed × Scopus
├── docs/
│   ├── retrieval_method.md
│   ├── deduplication_analysis.md
│   ├── data_dictionary.md
│   └── usage_terms.md
├── scripts/
│   ├── pubmed_pull.py
│   ├── scopus_pull.py
│   └── dedup_analysis.py
├── LICENSE                          # MIT for code
├── LICENSE-DATA                     # CC BY 4.0 for derived datasets
└── README.md
```

---

## Key numbers

| Database | Date retrieved | Records | With DOI | Without DOI |
|---|---|---|---|---|
| PubMed | 2026-06-03 | 27,731 | 24,882 | 2,845 |
| Scopus | 2026-06-03 | 59,721 | 52,731 | 6,912 |
| Raw sum | — | 87,452 | — | — |
| DOI-deduped union | — | 62,593 | — | — |
| Final pool (DOI-deduped + no-DOI kept) | — | 72,350 | — | — |

PubMed records contained in Scopus by DOI: 60.4%
Scopus records contained in PubMed by DOI: 28.5%

See [`docs/deduplication_analysis.md`](docs/deduplication_analysis.md) for full details.

---

## Quick start

### Read the PubMed CSV

```python
import pandas as pd
df = pd.read_csv("data/pubmed/works_summary.csv")
print(df.shape, df.columns.tolist())
```

### Read the Scopus JSONL (compressed)

```python
import gzip, json
with gzip.open("data/scopus/works_full.jsonl.gz", "rt") as f:
    records = [json.loads(line) for line in f]
print(len(records), records[0].keys())
```

### Re-run the deduplication

```bash
# Decompress Scopus first
gunzip -k data/scopus/works_summary.csv.gz
python3 scripts/dedup_analysis.py \
    data/pubmed/works_summary.csv \
    data/scopus/works_summary.csv \
    data/deduplication_summary.json
```

### Re-pull the data (with your own API keys)

```bash
export PUBMED_API_KEY="your_ncbi_api_key"
export ELSEVIER_API_KEY="your_elsevier_key"
export ELSEVIER_INST_TOKEN="your_institutional_token"  # optional
export CONTACT_EMAIL="your.email@institution.edu"

python3 scripts/pubmed_pull.py output_pubmed data/pubmed/query.txt
python3 scripts/scopus_pull.py output_scopus data/scopus/query.txt year_counts.json
```

---

## How to cite

If you use these data in derivative work, please cite this archive (DOI to be assigned via Zenodo once the snapshot is final):

> Xia, Z. (2026). climate-mental-health-evidence: PubMed + Scopus retrieval for a systematic review of climate hazards and mental health [Dataset]. GitHub. https://github.com/Ziqian-xia/climate-mental-health-evidence

---

## Licence

- **Code** (`scripts/`): MIT (see `LICENSE`)
- **Data** (`data/`): see [`docs/usage_terms.md`](docs/usage_terms.md) for source-specific terms. PubMed metadata is in the US public domain; Scopus metadata is shared here under fair-use research provisions but downstream users should consult Elsevier's API Terms of Use before significant redistribution.

---

## Reproducibility note

The two retrieval scripts deliberately avoid two well-known E-utilities and Scopus API pitfalls that silently truncate large pulls:

- **PubMed**: WebEnv + EFetch with `retstart/retmax` can drop records; we use `id=PMID,...` lists instead.
- **Scopus**: start+count pagination is hard-capped at 5,000; we use year-bucket cursor pagination instead.

Details are documented in [`docs/retrieval_method.md`](docs/retrieval_method.md).
