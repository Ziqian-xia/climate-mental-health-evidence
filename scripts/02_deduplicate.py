#!/usr/bin/env python3
"""
SOP Part 1, Steps 2-5: Deduplicate standardized records.

Step 2: DOI dedup (exact normalized-DOI match).
Step 3: Title-metadata dedup on remaining records, with SOP guard rails.
        Conflicts -> doi_conflict_title_groups.csv for manual review.
Step 4: Build merged_deduplicated_records.csv.
Step 5: Write dedup_summary.md.
Also writes duplicate_groups.csv.
"""
import csv, sys, re, json
from collections import defaultdict, Counter

csv.field_size_limit(sys.maxsize)
# Usage: python3 02_deduplicate.py [STANDARDIZED_CSV] [OUT_DIR]
#   STANDARDIZED_CSV  output of 01_standardize.py  (default: ./out/all_records_standardized.csv)
#   OUT_DIR           where outputs are written     (default: ./out)
import os
IN  = sys.argv[1] if len(sys.argv) > 1 else "out/all_records_standardized.csv"
OUT = sys.argv[2] if len(sys.argv) > 2 else "out"
os.makedirs(OUT, exist_ok=True)

# ---------- load ----------
records = list(csv.DictReader(open(IN, encoding="utf-8")))
for r in records:
    r["_used"] = False  # track whether record has been absorbed into a group

raw_counts = Counter(r["source"] for r in records)
total_raw = len(records)

# ---------- representative selection ----------
def richness(r):
    # SOP: richest metadata = longest abstract + most complete title
    return (len(r["abstract"]), len(r["title"]),
            1 if r["doi"] else 0, 1 if r["year"] else 0)

def pick_rep(group):
    return max(group, key=richness)

def merge_group(group, dedup_id):
    rep = pick_rep(group)
    sources = sorted({r["source"] for r in group})
    all_dois = sorted({r["doi"] for r in group if r["doi"]})
    all_ids = sorted({f'{r["source"]}:{r["source_id"]}' for r in group if r["source_id"]})
    return {
        "dedup_id": dedup_id,
        "duplicate_count": len(group),
        "sources": "; ".join(sources),
        "all_dois": "; ".join(all_dois),
        "all_source_ids": "; ".join(all_ids),
        "title": rep["title"],
        "abstract": rep["abstract"],
        "year": rep["year"],
        "journal": rep["journal"],
        "authors": rep["authors"],
    }

merged = []
dup_group_log = []   # for duplicate_groups.csv: dedup_id, method, member record_ids+sources
dedup_n = 0

def new_id():
    global dedup_n
    dedup_n += 1
    return f"D{dedup_n:07d}"

# ---------- Step 2: DOI dedup ----------
doi_groups = defaultdict(list)
for r in records:
    if r["doi"]:
        doi_groups[r["doi"]].append(r)

doi_merged_records = 0
doi_groups_count = 0
for doi, group in doi_groups.items():
    did = new_id()
    for r in group:
        r["_used"] = True
    merged.append(merge_group(group, did))
    if len(group) > 1:
        doi_groups_count += 1
        doi_merged_records += len(group)
    dup_group_log.append({
        "dedup_id": did, "method": "doi", "n": len(group),
        "members": "; ".join(f'{r["source"]}:{r["source_id"]}' for r in group),
        "key": doi,
    })

# ---------- Step 3: title-metadata dedup on remaining (no-DOI) records ----------
GENERIC_TITLES = {
    "", "editorial", "introduction", "abstracts", "abstract", "preface",
    "erratum", "correction", "corrigendum", "obituary", "in memoriam",
    "letter to the editor", "reply", "response", "comment", "book review",
    "news", "announcements", "contents", "index", "review",
}
MIN_TITLE_WORDS = 4   # "not extremely short or generic"

def too_short_or_generic(tn):
    if tn in GENERIC_TITLES:
        return True
    return len(tn.split()) < MIN_TITLE_WORDS

remaining = [r for r in records if not r["_used"]]

# bucket remaining by normalized title
title_buckets = defaultdict(list)
for r in remaining:
    title_buckets[r["title_norm"]].append(r)

def years_close(a, b):
    try:
        return abs(int(a) - int(b)) <= 1
    except ValueError:
        return False  # can't verify -> treat as not-close (conservative)

def first_authors_conflict(group):
    fa = {r["first_author"].lower() for r in group if r["first_author"].strip()}
    return len(fa) > 1

def years_span_ok(group):
    yrs = [r["year"] for r in group if r["year"]]
    if len(yrs) < 2:
        return True
    yrs_int = sorted(int(y) for y in yrs)
    return (yrs_int[-1] - yrs_int[0]) <= 1

title_merged_records = 0
title_groups_count = 0
conflict_rows = []

for tn, group in title_buckets.items():
    if len(group) == 1:
        # singleton -> its own dedup record
        r = group[0]
        did = new_id()
        r["_used"] = True
        merged.append(merge_group([r], did))
        continue

    # multi-member title bucket: decide auto-merge vs manual review
    if too_short_or_generic(tn):
        reason = "title_short_or_generic"
        action = "review"
    elif not years_span_ok(group):
        reason = "year_gap_gt_1"
        action = "review"
    elif first_authors_conflict(group):
        reason = "first_author_conflict"
        action = "review"
    else:
        # check the SOP "same title different DOI" guard: members here have no DOI
        # (DOI records already removed in Step 2), so this guard rarely triggers;
        # but a member could have a DOI that simply didn't group (it would have).
        dois = {r["doi"] for r in group if r["doi"]}
        if len(dois) > 1:
            reason = "same_title_diff_doi"
            action = "review"
        else:
            action = "merge"
            reason = "title+year+author_match"

    if action == "merge":
        did = new_id()
        for r in group:
            r["_used"] = True
        merged.append(merge_group(group, did))
        title_groups_count += 1
        title_merged_records += len(group)
        dup_group_log.append({
            "dedup_id": did, "method": "title", "n": len(group),
            "members": "; ".join(f'{r["source"]}:{r["source_id"]}' for r in group),
            "key": tn[:120],
        })
    else:
        # route to manual review; each member kept as its own dedup record so
        # nothing is lost from the screening pool, but flagged for audit
        gid = f"C{len(conflict_rows)//1+1:06d}"
        cgid = new_id  # not used; keep members as singletons
        for r in group:
            did = new_id()
            r["_used"] = True
            merged.append(merge_group([r], did))
            conflict_rows.append({
                "conflict_group": tn[:120],
                "reason": reason,
                "dedup_id": did,
                "source": r["source"],
                "source_id": r["source_id"],
                "doi": r["doi"],
                "title": r["title"],
                "year": r["year"],
                "first_author": r["first_author"],
            })

# ---------- sanity: every record used exactly once ----------
used = sum(1 for r in records if r["_used"])
assert used == total_raw, f"used {used} != total {total_raw}"

# ---------- Step 4: write merged_deduplicated_records.csv ----------
mcols = ["dedup_id","duplicate_count","sources","all_dois","all_source_ids",
         "title","abstract","year","journal","authors"]
with open(f"{OUT}/merged_deduplicated_records.csv","w",newline='',encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=mcols); w.writeheader(); w.writerows(merged)

# duplicate_groups.csv (only groups with >1 member)
with open(f"{OUT}/duplicate_groups.csv","w",newline='',encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=["dedup_id","method","n","key","members"])
    w.writeheader()
    for g in dup_group_log:
        if g["n"] > 1:
            w.writerow(g)

# doi_conflict_title_groups.csv
ccols = ["conflict_group","reason","dedup_id","source","source_id","doi",
         "title","year","first_author"]
with open(f"{OUT}/doi_conflict_title_groups.csv","w",newline='',encoding="utf-8") as f:
    w = csv.DictWriter(f, fieldnames=ccols); w.writeheader(); w.writerows(conflict_rows)

# ---------- Step 5: dedup_summary.md ----------
final_pool = len(merged)
dups_removed = total_raw - final_pool
total_dup_groups = sum(1 for g in dup_group_log if g["n"] > 1)
conflict_groups_n = len({c["conflict_group"] for c in conflict_rows})

src_contrib = Counter()
for m in merged:
    for s in m["sources"].split("; "):
        src_contrib[s] += 1

md = f"""# Deduplication Summary

Climate Change and Mental Health Evidence Review
Generated by SOP Part 1 (Steps 2-5). OpenAlex excluded by project decision.

## Raw records
- PubMed: n = {raw_counts['PubMed']:,}
- Scopus: n = {raw_counts['Scopus']:,}
- Embase: n = {raw_counts['Embase']:,}
- PsycINFO: n = {raw_counts['PsycINFO']:,}
- **Raw total: n = {total_raw:,}**

## Deduplicated records
- **Final merged screening pool: n = {final_pool:,}**
- Duplicates removed: n = {dups_removed:,}
- Duplicate groups (>1 member): n = {total_dup_groups:,}
  - via DOI match: {doi_groups_count:,} groups
  - via title metadata: {title_groups_count:,} groups
- DOI-conflict / title groups routed to manual review: {conflict_groups_n:,} groups ({len(conflict_rows):,} records)

## Records contributed to final pool by source
(a deduplicated record can list more than one source)
- PubMed: {src_contrib['PubMed']:,}
- Scopus: {src_contrib['Scopus']:,}
- Embase: {src_contrib['Embase']:,}
- PsycINFO: {src_contrib['PsycINFO']:,}

## Method notes
- Step 2: exact normalized-DOI match. Representative = longest abstract + most complete title.
- Step 3: title merged only when normalized title identical, >= {MIN_TITLE_WORDS} words and not generic,
  publication years within 1 year, and first authors do not conflict.
- Records tripping any guard rail (short/generic title, year gap > 1, first-author conflict,
  same title with different DOIs) were NOT auto-merged; they are kept in the pool and
  flagged in doi_conflict_title_groups.csv for manual review.

## Files produced
- merged_deduplicated_records.csv
- duplicate_groups.csv
- doi_conflict_title_groups.csv
- dedup_summary.md
"""
open(f"{OUT}/dedup_summary.md","w",encoding="utf-8").write(md)

print(f"Raw total:        {total_raw:,}")
print(f"DOI groups (>1):  {doi_groups_count:,}  (records merged: {doi_merged_records:,})")
print(f"Title groups:     {title_groups_count:,}  (records merged: {title_merged_records:,})")
print(f"Conflict records: {len(conflict_rows):,}  in {conflict_groups_n:,} groups")
print(f"FINAL POOL:       {final_pool:,}")
print(f"Dups removed:     {dups_removed:,}")
