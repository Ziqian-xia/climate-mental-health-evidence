#!/usr/bin/env python3
"""Build the frozen 802-record strict-rescreen input from published sources."""

import argparse
import csv
import gzip
import hashlib
import json
import os
import sys

EXPECTED_INCLUDE_COUNT = 802
OUTPUT_FIELDS = [
    "dedup_id",
    "title",
    "abstract",
    "year",
    "journal",
    "authors",
    "sources",
    "all_dois",
    "candidate_topics",
    "broad_screen_reason",
    "broad_module_decisions",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--final-result", required=True)
    parser.add_argument("--corpus", required=True)
    parser.add_argument("--out", default="results/input_802.csv")
    return parser.parse_args()


def portable_path(path):
    absolute = os.path.abspath(path)
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    try:
        if os.path.commonpath([absolute, repo_root]) == repo_root:
            return os.path.relpath(absolute, repo_root)
    except ValueError:
        pass
    return os.path.basename(absolute)


def main():
    csv.field_size_limit(sys.maxsize)
    args = parse_args()

    with open(args.final_result, newline="", encoding="utf-8-sig") as handle:
        final_rows = list(csv.DictReader(handle))
    include_rows = [row for row in final_rows if row.get("decision") == "INCLUDE"]
    if len(include_rows) != EXPECTED_INCLUDE_COUNT:
        raise SystemExit(
            "Expected {} INCLUDE records, found {}.".format(
                EXPECTED_INCLUDE_COUNT, len(include_rows)
            )
        )

    wanted = {row["dedup_id"] for row in include_rows}
    corpus_by_id = {}
    with gzip.open(args.corpus, "rt", newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            if row.get("dedup_id") in wanted:
                corpus_by_id[row["dedup_id"]] = row

    missing = sorted(wanted - set(corpus_by_id))
    if missing:
        raise SystemExit("Missing corpus records: " + ", ".join(missing[:20]))

    output_rows = []
    for broad in include_rows:
        source = corpus_by_id[broad["dedup_id"]]
        output_rows.append(
            {
                "dedup_id": broad["dedup_id"],
                "title": source.get("title", ""),
                "abstract": source.get("abstract", ""),
                "year": source.get("year", ""),
                "journal": source.get("journal", ""),
                "authors": source.get("authors", ""),
                "sources": source.get("sources", ""),
                "all_dois": source.get("all_dois", ""),
                "candidate_topics": broad.get("candidate_topics", ""),
                "broad_screen_reason": broad.get("reason", ""),
                "broad_module_decisions": broad.get("module_decisions", ""),
            }
        )

    empty_abstracts = [row["dedup_id"] for row in output_rows if not row["abstract"].strip()]
    if empty_abstracts:
        raise SystemExit(
            "Strict INC input unexpectedly contains records without abstracts: "
            + ", ".join(empty_abstracts[:20])
        )

    os.makedirs(os.path.dirname(os.path.abspath(args.out)), exist_ok=True)
    temporary = args.out + ".tmp"
    with open(temporary, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_FIELDS)
        writer.writeheader()
        writer.writerows(output_rows)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, args.out)

    manifest = {
        "records": len(output_rows),
        "source_final_result": portable_path(args.final_result),
        "source_final_result_sha256": sha256(args.final_result),
        "source_corpus": portable_path(args.corpus),
        "source_corpus_sha256": sha256(args.corpus),
        "output": portable_path(args.out),
        "output_sha256": sha256(args.out),
    }
    manifest_path = os.path.splitext(args.out)[0] + "_manifest.json"
    with open(manifest_path + ".tmp", "w", encoding="utf-8") as handle:
        json.dump(manifest, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(manifest_path + ".tmp", manifest_path)
    print(json.dumps(manifest, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
