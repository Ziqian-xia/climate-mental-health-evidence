"""
Cross-database deduplication summary by DOI.

Usage:

    python3 dedup_analysis.py PUBMED_CSV SCOPUS_CSV [OUT_JSON]

Reports the size of the PubMed × Scopus DOI overlap, the union, and the
final pool size when no-DOI records are kept (since they may include
non-overlapping unique records).
"""
import csv, json, sys, pathlib


def load_dois(path):
    dois, no_doi = set(), 0
    with open(path) as f:
        for row in csv.DictReader(f):
            d = (row.get("doi") or "").strip().lower()
            if d: dois.add(d)
            else: no_doi += 1
    return dois, no_doi


def main(pubmed_csv, scopus_csv, out_json=None):
    pm_dois, pm_no = load_dois(pubmed_csv)
    sc_dois, sc_no = load_dois(scopus_csv)

    overlap = pm_dois & sc_dois
    union = pm_dois | sc_dois
    pool = len(union) + pm_no + sc_no

    summary = {
        "pubmed_with_doi": len(pm_dois), "pubmed_no_doi": pm_no,
        "scopus_with_doi": len(sc_dois), "scopus_no_doi": sc_no,
        "doi_overlap": len(overlap),
        "pubmed_only_doi": len(pm_dois - sc_dois),
        "scopus_only_doi": len(sc_dois - pm_dois),
        "doi_union": len(union),
        "final_pool_keeping_no_doi": pool,
        "scopus_in_pubmed_pct": round(len(overlap) / len(sc_dois) * 100, 1),
        "pubmed_in_scopus_pct": round(len(overlap) / len(pm_dois) * 100, 1),
    }
    print(json.dumps(summary, indent=2))
    if out_json:
        pathlib.Path(out_json).write_text(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main(*sys.argv[1:])
