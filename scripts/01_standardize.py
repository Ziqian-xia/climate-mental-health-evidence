#!/usr/bin/env python3
"""
SOP Part 1, Step 1: Standardize all records from PubMed, Scopus, Embase, PsycINFO
into one row per raw record with the SOP-defined columns.

Output: all_records_standardized.csv
Columns: record_id, source, source_id, doi, title, title_norm, abstract,
         year, authors, first_author, journal
"""
import csv, gzip, re, sys, unicodedata, json
from pathlib import Path

# Usage: python3 01_standardize.py [DATA_DIR] [OUT_DIR]
#   DATA_DIR  folder containing pubmed/ scopus/ embase/ psycinfo/  (default: ./data)
#   OUT_DIR   where outputs are written                            (default: ./out)
BASE = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("data")
OUT  = Path(sys.argv[2]) if len(sys.argv) > 2 else Path("out")
OUT.mkdir(parents=True, exist_ok=True)

csv.field_size_limit(sys.maxsize)

# ---------- normalization helpers ----------
def norm_doi(raw):
    if not raw:
        return ""
    d = raw.strip().lower()
    d = re.sub(r'^https?://(dx\.)?doi\.org/', '', d)
    d = re.sub(r'^doi:\s*', '', d)
    d = d.rstrip(' .,;')
    return d

def strip_accents(s):
    return ''.join(c for c in unicodedata.normalize('NFKD', s)
                   if not unicodedata.combining(c))

def norm_title(raw):
    if not raw:
        return ""
    t = strip_accents(raw.lower())
    # keep alphanumeric words only; collapse whitespace
    t = re.sub(r'[^a-z0-9\s]', ' ', t)
    t = re.sub(r'\s+', ' ', t).strip()
    return t

def year_only(raw):
    if not raw:
        return ""
    m = re.search(r'(19|20)\d{2}', str(raw))
    return m.group(0) if m else ""

def first_author_surname(authors_str, delim_semicolon=True):
    """Return surname of the first author. Author strings are 'Surname, Initials'."""
    if not authors_str:
        return ""
    # take first author chunk
    first = authors_str.split(';')[0].strip() if ';' in authors_str else authors_str.split('|')[0].strip()
    # surname is text before first comma
    surname = first.split(',')[0].strip()
    return surname

rows = []
rid = 0

def add_row(source, source_id, doi, title, abstract, year, authors, journal):
    global rid
    rid += 1
    rows.append({
        "record_id": f"r{rid:07d}",
        "source": source,
        "source_id": source_id or "",
        "doi": norm_doi(doi),
        "title": (title or "").strip(),
        "title_norm": norm_title(title),
        "abstract": (abstract or "").strip(),
        "year": year_only(year),
        "authors": (authors or "").strip(),
        "first_author": first_author_surname(authors or ""),
        "journal": (journal or "").strip(),
    })

# ---------- PubMed ----------
def load_pubmed():
    p = BASE / "pubmed" / "works_summary.csv"
    n = 0
    with open(p, newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            add_row("PubMed", row.get("pmid"), row.get("doi"),
                    row.get("title"), row.get("abstract"),
                    row.get("year"), row.get("authors"), row.get("journal"))
            n += 1
    return n

# ---------- Scopus ----------
def load_scopus():
    p = BASE / "scopus" / "works_summary.csv.gz"
    n = 0
    with gzip.open(p, 'rt', newline='', encoding='utf-8') as f:
        for row in csv.DictReader(f):
            add_row("Scopus", row.get("eid"), row.get("doi"),
                    row.get("title"), row.get("abstract"),
                    row.get("cover_date"), row.get("creator"),
                    row.get("publication_name"))
            n += 1
    return n

# ---------- RIS parser ----------
def parse_ris(path):
    """Yield dicts of {tag: [values]} per record. Records end at 'ER  -'."""
    rec = {}
    with open(path, encoding='utf-8', errors='replace') as f:
        for line in f:
            m = re.match(r'^([A-Z][A-Z0-9])  - (.*)$', line.rstrip('\n').rstrip('\r'))
            if m:
                tag, val = m.group(1), m.group(2)
                if tag == 'ER':
                    if rec:
                        yield rec
                    rec = {}
                else:
                    rec.setdefault(tag, []).append(val)
            # continuation / blank lines ignored
    if rec:
        yield rec

def proquest_id_from_url(url):
    m = re.search(r'docview/(\d+)', url or "")
    return m.group(1) if m else ""

# ---------- Embase ----------
def load_embase():
    n = 0
    files = sorted((BASE / "embase").glob("*.ris"))
    for fp in files:
        for rec in parse_ris(fp):
            doi = (rec.get("DO") or [""])[0]
            title = (rec.get("T1") or [""])[0]
            abstract = (rec.get("N2") or [""])[0]   # Embase abstract = N2
            year = (rec.get("Y1") or [""])[0]
            authors = "; ".join(rec.get("A1") or [])  # Embase authors = A1
            journal = (rec.get("JF") or rec.get("JO") or [""])[0]
            sid = (rec.get("U2") or [""])[0]          # Embase id = U2 (L-number)
            add_row("Embase", sid, doi, title, abstract, year, authors, journal)
            n += 1
    return n

# ---------- PsycINFO ----------
def load_psycinfo():
    n = 0
    fp = BASE / "psycinfo" / "PSYCINFO_QUERY_RESULTS.RIS"
    for rec in parse_ris(fp):
        doi = (rec.get("DO") or [""])[0]
        title = (rec.get("T1") or [""])[0]
        abstract = (rec.get("AB") or [""])[0]       # PsycINFO abstract = AB
        year = (rec.get("Y1") or rec.get("DA") or [""])[0]
        authors = "; ".join(rec.get("AU") or [])    # PsycINFO authors = AU
        journal = (rec.get("JF") or [""])[0]
        sid = proquest_id_from_url((rec.get("UR") or [""])[0])  # ProQuest docview id
        add_row("PsycINFO", sid, doi, title, abstract, year, authors, journal)
        n += 1
    return n

counts = {}
counts["PubMed"]   = load_pubmed();   print(f"PubMed:   {counts['PubMed']}")
counts["Scopus"]   = load_scopus();   print(f"Scopus:   {counts['Scopus']}")
counts["Embase"]   = load_embase();   print(f"Embase:   {counts['Embase']}")
counts["PsycINFO"] = load_psycinfo(); print(f"PsycINFO: {counts['PsycINFO']}")
print(f"TOTAL raw records: {len(rows)}")

# ---------- write ----------
cols = ["record_id","source","source_id","doi","title","title_norm",
        "abstract","year","authors","first_author","journal"]
outpath = OUT / "all_records_standardized.csv"
with open(outpath, "w", newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=cols)
    w.writeheader()
    w.writerows(rows)
print(f"Wrote {outpath}")

# quick QC
with_doi = sum(1 for r in rows if r["doi"])
with_abs = sum(1 for r in rows if r["abstract"])
with_year = sum(1 for r in rows if r["year"])
print(f"with DOI: {with_doi}  with abstract: {with_abs}  with year: {with_year}")
json.dump({"counts": counts, "total": len(rows),
           "with_doi": with_doi, "with_abstract": with_abs, "with_year": with_year},
          open(OUT/"standardize_qc.json","w"), indent=2)
