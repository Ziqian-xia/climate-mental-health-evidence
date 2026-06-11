"""
Scopus retrieval for the climate-mental-health systematic review.

Approach: year-bucketed COMPLETE-view cursor pagination. This handles two
practical issues with the Elsevier Scopus Search API:

  1. start+count pagination has a hard cap of 5,000 records per query. Splitting
     by publication year keeps almost every bucket under that cap (we additionally
     split 2025 by doctype to stay under).
  2. Long-running cursor sessions sometimes drop with read timeouts. Per-bucket
     independence + HTTPAdapter retries + per-call manual retry on Timeout /
     ConnectionError makes the pull resumable in practice.

Usage:

    export ELSEVIER_API_KEY="your_elsevier_key"
    export ELSEVIER_INST_TOKEN="your_institutional_token"   # optional
    python3 scopus_pull.py OUT_DIR QUERY_FILE YEAR_COUNTS_JSON

YEAR_COUNTS_JSON is a JSON object {"1990": int, ..., "<1990": int} produced by
probing single-year counts before the main pull. Buckets exceeding 5,000 are
split by doctype.

Outputs in OUT_DIR:
    works_summary.csv   columns: eid, doi, title, abstract, creator,
                        publication_name, cover_date, citedby_count, bucket
    works_full.jsonl    one Scopus entry per line (Elsevier JSON schema)
    run_summary.json    metadata: per-bucket counts, calls, elapsed time
"""
import os, sys, json, time, csv, pathlib, requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

API = os.environ["ELSEVIER_API_KEY"]
TOKEN = os.environ.get("ELSEVIER_INST_TOKEN", "")
URL = "https://api.elsevier.com/content/search/scopus"


def make_session():
    s = requests.Session()
    retry = Retry(total=5, backoff_factor=2,
                  status_forcelist=[429, 500, 502, 503, 504],
                  allowed_methods=["GET"])
    s.mount("https://", HTTPAdapter(max_retries=retry))
    headers = {"X-ELS-APIKey": API, "Accept": "application/json"}
    if TOKEN: headers["X-ELS-Insttoken"] = TOKEN
    s.headers.update(headers)
    return s


def fetch_one(sess, params):
    """Per-call retry on Timeout / ConnectionError beyond what HTTPAdapter handles."""
    for attempt in range(4):
        try:
            return sess.get(URL, params=params, timeout=180)
        except (requests.Timeout, requests.ConnectionError):
            time.sleep(5 * (2 ** attempt))
    return None


def pull_bucket(sess, query, csv_w, jsonl_f, seen, bname):
    """Cursor through one bucket's results."""
    cursor, stored, calls, total = "*", 0, 0, None
    while True:
        r = fetch_one(sess, {"query": query, "count": 25, "cursor": cursor,
                             "view": "COMPLETE"})
        if r is None or r.status_code != 200:
            break
        calls += 1
        sr = r.json().get("search-results", {})
        if total is None:
            total = int(sr.get("opensearch:totalResults", -1))
        entries = sr.get("entry", []) or []
        for e in entries:
            if "error" in e and len(e) <= 3: continue
            eid = e.get("eid", "")
            if not eid or eid in seen: continue
            seen.add(eid)
            jsonl_f.write(json.dumps(e, ensure_ascii=False) + "\n")
            csv_w.writerow([eid, e.get("prism:doi", ""),
                            (e.get("dc:title") or "")[:500],
                            (e.get("dc:description") or "")[:1500],
                            e.get("dc:creator", ""),
                            e.get("prism:publicationName", ""),
                            e.get("prism:coverDate", ""),
                            e.get("citedby-count", ""),
                            bname])
            stored += 1
        cur = sr.get("cursor", {})
        nxt = cur.get("@next") if isinstance(cur, dict) else None
        if not entries or not nxt or nxt == cursor: break
        cursor = nxt
    return total, stored, calls


def main(out_dir, query_file, year_counts_json):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    base = " ".join(line.strip() for line in open(query_file) if line.strip())
    year_counts = json.load(open(year_counts_json))

    # Build per-year buckets; split 2025 by doctype to stay under 5,000.
    buckets = []
    for k, v in year_counts.items():
        if not isinstance(v, int) or v == 0: continue
        if k == "<1990":
            buckets.append(("pre1990", f"{base} AND PUBYEAR < 1990"))
        elif k == "2025" and v > 5000:
            buckets.append(("2025_ar_re",
                            f"{base} AND PUBYEAR = 2025 AND (DOCTYPE(ar) OR DOCTYPE(re))"))
            buckets.append(("2025_other",
                            f"{base} AND PUBYEAR = 2025 AND NOT (DOCTYPE(ar) OR DOCTYPE(re))"))
        else:
            buckets.append((f"y{k}", f"{base} AND PUBYEAR = {k}"))

    sess = make_session()
    csv_f = open(out / "works_summary.csv", "w", newline="")
    csv_w = csv.writer(csv_f)
    csv_w.writerow(["eid", "doi", "title", "abstract", "creator", "publication_name",
                    "cover_date", "citedby_count", "bucket"])
    jsonl_f = open(out / "works_full.jsonl", "w")

    seen, log, grand_start = set(), [], time.time()
    for bname, bquery in buckets:
        total, stored, calls = pull_bucket(sess, bquery, csv_w, jsonl_f, seen, bname)
        log.append({"bucket": bname, "scopus_count": total, "stored": stored,
                    "api_calls": calls})
        print(f"  [{bname}] stored={stored} scopus_total={total} calls={calls}")
        csv_f.flush(); jsonl_f.flush()

    csv_f.close(); jsonl_f.close()
    json.dump({"total_stored": sum(b["stored"] for b in log),
               "unique_eids": len(seen),
               "buckets": log,
               "grand_elapsed_s": round(time.time() - grand_start, 1)},
              open(out / "run_summary.json", "w"), indent=2)
    print(f"[Done] {len(seen):,} records")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2], sys.argv[3])
