#!/usr/bin/env python3
"""Validate GPT-5.6 subagent parts, merge them, and compare with DeepSeek."""

import argparse
import csv
import json
import os
from collections import Counter

from screen_deepseek_v4_pro import REQUIRED_RESULT_FIELDS, validate_result

GPT_EXTRA_FIELDS = ["screener_model", "criteria_version", "source_row"]
STRICT_FIELDS = REQUIRED_RESULT_FIELDS


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/input_802.csv")
    parser.add_argument("--parts-dir", default="results/subagents")
    parser.add_argument("--deepseek", default="results/strict_inc_deepseek_v4_pro.csv")
    parser.add_argument("--gpt-output", default="results/strict_inc_gpt56_subagents.csv")
    parser.add_argument("--combined", default="results/two_model_screening.csv")
    parser.add_argument("--disagreements", default="results/model_disagreements.csv")
    parser.add_argument("--summary", default="results/model_comparison_summary.json")
    return parser.parse_args()


def read_jsonl(path):
    with open(path, encoding="utf-8") as handle:
        for line_number, line in enumerate(handle, 1):
            try:
                yield json.loads(line)
            except json.JSONDecodeError as error:
                raise SystemExit("{}:{} invalid JSON: {}".format(path, line_number, error))


def kappa(pairs, labels):
    count = len(pairs)
    observed = sum(left == right for left, right in pairs) / count
    left_counts = Counter(left for left, _ in pairs)
    right_counts = Counter(right for _, right in pairs)
    expected = sum(left_counts[label] * right_counts[label] for label in labels) / (count * count)
    return observed, (observed - expected) / (1 - expected) if expected != 1 else 1.0


def atomic_csv(path, fieldnames, rows):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    temporary = path + ".tmp"
    with open(temporary, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    os.replace(temporary, path)


def main():
    args = parse_args()
    with open(args.input, newline="", encoding="utf-8-sig") as handle:
        input_rows = list(csv.DictReader(handle))
    if len(input_rows) != 802:
        raise SystemExit("Expected 802 input rows, found {}.".format(len(input_rows)))

    part_names = sorted(name for name in os.listdir(args.parts_dir) if name.endswith(".jsonl"))
    if len(part_names) != 8:
        raise SystemExit("Expected 8 GPT part files, found {}.".format(len(part_names)))
    gpt_by_row = {}
    expected_keys = set(STRICT_FIELDS + GPT_EXTRA_FIELDS)
    for name in part_names:
        path = os.path.join(args.parts_dir, name)
        for item in read_jsonl(path):
            if set(item) != expected_keys:
                raise SystemExit("{} contains unexpected keys for {}.".format(name, item.get("dedup_id")))
            try:
                source_row = int(item["source_row"])
            except (TypeError, ValueError):
                raise SystemExit("Invalid source_row in {}.".format(name))
            if source_row in gpt_by_row:
                raise SystemExit("Duplicate GPT source_row {}.".format(source_row))
            if not 1 <= source_row <= len(input_rows):
                raise SystemExit("GPT source_row out of range: {}.".format(source_row))
            source = input_rows[source_row - 1]
            validate_result({field: item[field] for field in STRICT_FIELDS}, source["dedup_id"])
            if item["screener_model"] != "gpt-5.6-sol":
                raise SystemExit("Unexpected GPT model at row {}.".format(source_row))
            if item["criteria_version"] != "strict-inc-v1.0":
                raise SystemExit("Unexpected criteria version at row {}.".format(source_row))
            gpt_by_row[source_row] = item
    if set(gpt_by_row) != set(range(1, 803)):
        missing = sorted(set(range(1, 803)) - set(gpt_by_row))
        raise SystemExit("Missing GPT source rows: {}".format(missing[:20]))

    with open(args.deepseek, newline="", encoding="utf-8-sig") as handle:
        deepseek_rows = list(csv.DictReader(handle))
    if len(deepseek_rows) != 802:
        raise SystemExit("Expected 802 DeepSeek rows, found {}.".format(len(deepseek_rows)))
    deepseek_by_id = {row["dedup_id"]: row for row in deepseek_rows}

    gpt_fields = [
        "source_row", "dedup_id", "title", "year", "journal", "candidate_topics",
        *[field for field in STRICT_FIELDS if field != "dedup_id"],
        "screener_model", "criteria_version",
    ]
    gpt_rows = []
    combined_rows = []
    disagreement_rows = []
    pairs = []
    for source_row, source in enumerate(input_rows, 1):
        gpt = gpt_by_row[source_row]
        deepseek = deepseek_by_id[source["dedup_id"]]
        pairs.append((gpt["strict_decision"], deepseek["strict_decision"]))
        gpt_advances = gpt["strict_decision"] in {"META_ELIGIBLE", "FULLTEXT_REVIEW"}
        deepseek_advances = deepseek["strict_decision"] in {"META_ELIGIBLE", "FULLTEXT_REVIEW"}
        if gpt["strict_decision"] == deepseek["strict_decision"] == "META_ELIGIBLE":
            recommended_action = "PRIORITY_FULLTEXT"
        elif gpt_advances and deepseek_advances:
            recommended_action = "FULLTEXT_REVIEW"
        elif gpt_advances != deepseek_advances:
            recommended_action = "ADJUDICATE_PRIORITY"
        else:
            recommended_action = "DO_NOT_ADVANCE_MAIN_META"
        combined_rows.append(
            {
                "source_row": source_row,
                "dedup_id": source["dedup_id"],
                "title": source["title"],
                "year": source.get("year", ""),
                "journal": source.get("journal", ""),
                "candidate_topics": source.get("candidate_topics", ""),
                "gpt_decision": gpt["strict_decision"],
                "gpt_reason": gpt["reason"],
                "deepseek_decision": deepseek["strict_decision"],
                "deepseek_reason": deepseek["reason"],
                "recommended_action": recommended_action,
            }
        )
        gpt_rows.append(
            {
                "source_row": source_row,
                "dedup_id": source["dedup_id"],
                "title": source["title"],
                "year": source.get("year", ""),
                "journal": source.get("journal", ""),
                "candidate_topics": source.get("candidate_topics", ""),
                **{
                    field: " | ".join(gpt[field]) if field == "full_text_checks" else gpt[field]
                    for field in STRICT_FIELDS
                    if field != "dedup_id"
                },
                "screener_model": gpt["screener_model"],
                "criteria_version": gpt["criteria_version"],
            }
        )
        if gpt["strict_decision"] != deepseek["strict_decision"]:
            disagreement_rows.append(
                {
                    "source_row": source_row,
                    "dedup_id": source["dedup_id"],
                    "title": source["title"],
                    "candidate_topics": source.get("candidate_topics", ""),
                    "gpt_decision": gpt["strict_decision"],
                    "gpt_reason": gpt["reason"],
                    "deepseek_decision": deepseek["strict_decision"],
                    "deepseek_reason": deepseek["reason"],
                    "crosses_fulltext_boundary": "yes" if gpt_advances != deepseek_advances else "no",
                }
            )

    labels = ["META_ELIGIBLE", "FULLTEXT_REVIEW", "NARRATIVE_ONLY", "EXCLUDE"]
    exact_agreement, four_kappa = kappa(pairs, labels)
    advance = {"META_ELIGIBLE", "FULLTEXT_REVIEW"}
    binary_pairs = [(left in advance, right in advance) for left, right in pairs]
    advance_agreement, binary_kappa = kappa(binary_pairs, [True, False])
    confusion = {
        left: {right: sum(a == left and b == right for a, b in pairs) for right in labels}
        for left in labels
    }
    summary = {
        "records": len(pairs),
        "criteria_version": "strict-inc-v1.0",
        "gpt_model": "gpt-5.6-sol",
        "deepseek_model": "deepseek-v4-pro",
        "gpt_decision_counts": dict(sorted(Counter(left for left, _ in pairs).items())),
        "deepseek_decision_counts": dict(sorted(Counter(right for _, right in pairs).items())),
        "exact_four_category_agreement": exact_agreement,
        "cohen_kappa_four_category": four_kappa,
        "advance_to_fulltext_agreement": advance_agreement,
        "cohen_kappa_advance_binary": binary_kappa,
        "disagreements": len(disagreement_rows),
        "cross_boundary_disagreements": sum(
            row["crosses_fulltext_boundary"] == "yes" for row in disagreement_rows
        ),
        "consensus_advance_to_fulltext": sum(left and right for left, right in binary_pairs),
        "consensus_do_not_advance": sum(not left and not right for left, right in binary_pairs),
        "confusion_gpt_rows_deepseek_columns": confusion,
    }

    atomic_csv(args.gpt_output, gpt_fields, gpt_rows)
    atomic_csv(
        args.combined,
        [
            "source_row", "dedup_id", "title", "year", "journal", "candidate_topics",
            "gpt_decision", "gpt_reason", "deepseek_decision", "deepseek_reason",
            "recommended_action",
        ],
        combined_rows,
    )
    atomic_csv(
        args.disagreements,
        [
            "source_row", "dedup_id", "title", "candidate_topics", "gpt_decision",
            "gpt_reason", "deepseek_decision", "deepseek_reason",
            "crosses_fulltext_boundary",
        ],
        disagreement_rows,
    )
    os.makedirs(os.path.dirname(os.path.abspath(args.summary)), exist_ok=True)
    temporary = args.summary + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, args.summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
