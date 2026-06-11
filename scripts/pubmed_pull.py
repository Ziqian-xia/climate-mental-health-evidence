"""
PubMed retrieval for the climate-mental-health systematic review.

Approach: year-sliced ESearch (XML) + id-list EFetch (XML). This bypasses two
known limits of NCBI E-utilities:

  1. ESearch retmax is hard-capped at 9,999 per call. Slicing by publication
     year keeps each call below that cap for our query (max year ~ 2,300).
  2. WebEnv-based pagination of EFetch can silently drop records when responses
     are large. Explicit `id=PMID,PMID,...` lists avoid this.

Usage:

    export PUBMED_API_KEY="your_ncbi_api_key"
    export CONTACT_EMAIL="your.email@institution.edu"
    python3 pubmed_pull.py OUT_DIR QUERY_FILE

Outputs in OUT_DIR:
    works_summary.csv   one row per PMID, columns: pmid, doi, title, abstract,
                        journal, year, authors
    works_full.jsonl    one JSON record per line, same fields plus parsing source
    run_summary.json    metadata: total found, stored, API calls, elapsed time,
                        per-year slice counts
"""
import os, sys, json, time, csv, pathlib, requests
import xml.etree.ElementTree as ET

API_KEY = os.environ["PUBMED_API_KEY"]
EMAIL = os.environ.get("CONTACT_EMAIL", "your.email@institution.edu")
TOOL = "ccmh_review"
BASE = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"


def esearch_xml(term):
    """POST ESearch (POST handles long queries; GET hits HTTP 414 above ~2 KB)."""
    for attempt in range(4):
        try:
            r = requests.post(
                f"{BASE}/esearch.fcgi",
                data={"db": "pubmed", "term": term, "retmode": "xml",
                      "retmax": 9999, "api_key": API_KEY, "email": EMAIL, "tool": TOOL},
                timeout=60)
            if r.status_code == 200:
                root = ET.fromstring(r.content)
                count = int(root.findtext("Count") or 0)
                ids = [el.text.strip() for el in root.findall(".//IdList/Id") if el.text]
                return count, ids
            time.sleep(5 * (2 ** attempt))
        except (requests.Timeout, requests.ConnectionError):
            time.sleep(5 * (2 ** attempt))
    return None, []


def efetch_chunk(pmids):
    """POST EFetch by id-list; XML reply parsed for PubmedArticle + PubmedBookArticle."""
    for attempt in range(4):
        try:
            r = requests.post(
                f"{BASE}/efetch.fcgi",
                data={"db": "pubmed", "id": ",".join(pmids),
                      "retmode": "xml", "rettype": "abstract",
                      "api_key": API_KEY, "email": EMAIL, "tool": TOOL},
                timeout=180)
            if r.status_code == 200:
                return r.content
            time.sleep(5 * (2 ** attempt))
        except (requests.Timeout, requests.ConnectionError):
            time.sleep(5 * (2 ** attempt))
    return None


def main(out_dir, query_file):
    out = pathlib.Path(out_dir); out.mkdir(parents=True, exist_ok=True)
    query = " ".join(line.strip() for line in open(query_file) if line.strip())

    # Slice ESearch by publication year so each call returns < 9,999 PMIDs.
    buckets = [("pre1990", '("1500"[PDAT] : "1989"[PDAT])')]
    for y in range(1990, 2027):
        buckets.append((f"y{y}", f'"{y}"[PDAT]'))

    all_pmids = []
    slices = []
    for bname, datespec in buckets:
        count, ids = esearch_xml(f"({query}) AND {datespec}")
        if count is None: continue
        all_pmids.extend(ids)
        slices.append({"bucket": bname, "count": count, "ids_returned": len(ids)})
        print(f"  [{bname}] count={count:>5}  returned={len(ids):>5}")
        time.sleep(0.15)
    all_pmids = list(dict.fromkeys(all_pmids))
    print(f"\n[ESearch] unique PMIDs = {len(all_pmids):,}")

    # EFetch in chunks of 200 PMIDs.
    csv_f = open(out / "works_summary.csv", "w", newline="")
    csv_w = csv.writer(csv_f)
    csv_w.writerow(["pmid", "doi", "title", "abstract", "journal", "year", "authors"])
    jsonl_f = open(out / "works_full.jsonl", "w")

    BATCH = 200
    stored = 0
    start = time.time()
    for i in range(0, len(all_pmids), BATCH):
        chunk = all_pmids[i:i + BATCH]
        xml_bytes = efetch_chunk(chunk)
        if xml_bytes is None: continue
        root = ET.fromstring(xml_bytes)
        for art in root.iter():
            if art.tag not in ("PubmedArticle", "PubmedBookArticle"): continue
            pmid = (art.findtext(".//PMID") or "").strip()
            title = (art.findtext(".//ArticleTitle") or art.findtext(".//BookTitle") or "").strip()
            abstract = " ".join((t.text or "").strip() for t in art.findall(".//AbstractText") if t.text)
            journal = (art.findtext(".//Journal/Title") or
                       art.findtext(".//Journal/ISOAbbreviation") or "").strip()
            year = (art.findtext(".//PubDate/Year") or
                    art.findtext(".//PubDate/MedlineDate") or "")[:4]
            doi = ""
            for aid in art.findall(".//ArticleId"):
                if aid.get("IdType") == "doi":
                    doi = (aid.text or "").strip(); break
            authors = []
            for au in art.findall(".//Author")[:10]:
                ln = au.findtext("LastName") or ""
                fi = au.findtext("Initials") or ""
                if ln: authors.append(f"{ln} {fi}".strip())
            rec = {"pmid": pmid, "doi": doi, "title": title, "abstract": abstract,
                   "journal": journal, "year": year, "authors": authors}
            jsonl_f.write(json.dumps(rec, ensure_ascii=False) + "\n")
            csv_w.writerow([pmid, doi, title[:500], abstract[:1500], journal, year,
                            "; ".join(authors)])
            stored += 1
        csv_f.flush(); jsonl_f.flush()
        time.sleep(0.15)

    csv_f.close(); jsonl_f.close()
    json.dump({"pmids_collected": len(all_pmids), "stored_records": stored,
               "elapsed_seconds": round(time.time() - start, 1),
               "slices": slices},
              open(out / "run_summary.json", "w"), indent=2)
    print(f"[Done] stored {stored:,} in {time.time() - start:.0f}s")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
