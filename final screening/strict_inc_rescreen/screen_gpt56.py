#!/usr/bin/env python3
"""Independently reassess each broad-screen INCLUDE record with GPT-5.6."""

import argparse
import csv
import hashlib
import json
import os
import sys
import threading
import time
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

MODEL = "gpt-5.6"
CRITERIA_VERSION = "strict-inc-v1.0"
EXPECTED_RECORDS = 802

DECISIONS = ["META_ELIGIBLE", "FULLTEXT_REVIEW", "NARRATIVE_ONLY", "EXCLUDE"]
TOPICS = ["temperature", "wildfire", "flood", "cyclone", "drought", "multiple", "unclear"]
EXPOSURE = ["objective_or_verifiable", "self_report_only", "unclear", "ineligible"]
DESIGNS = [
    "time_series",
    "case_crossover",
    "longitudinal_with_prebaseline",
    "panel_fixed_effects",
    "quasi_experimental",
    "cross_sectional",
    "post_event_only",
    "qualitative",
    "descriptive",
    "other_eligible",
    "unclear",
]
COUNTERFACTUAL = ["yes", "no", "unclear"]
EXTRACTABILITY = [
    "reported_with_uncertainty",
    "likely_extractable",
    "not_extractable",
    "unclear",
]
OUTCOME = ["eligible", "ineligible", "unclear"]
REASON_CODES = [
    "eligible",
    "unclear_exposure_measurement",
    "unclear_design",
    "unclear_effect_extractability",
    "cross_sectional",
    "no_pre_event_baseline",
    "no_hazard_variation",
    "self_report_exposure_only",
    "descriptive_or_predictor_only",
    "qualitative_only",
    "wrong_exposure",
    "wrong_outcome",
    "non_original",
    "not_human_empirical",
    "projection_only",
    "multiple_issues",
]
CONFIDENCE = ["high", "medium", "low"]
OVERLAP = ["none_identified", "potential_overlap", "unclear"]

SCHEMA = {
    "type": "object",
    "additionalProperties": False,
    "properties": {
        "dedup_id": {"type": "string"},
        "strict_decision": {"type": "string", "enum": DECISIONS},
        "primary_topic": {"type": "string", "enum": TOPICS},
        "exposure_measurement": {"type": "string", "enum": EXPOSURE},
        "design_class": {"type": "string", "enum": DESIGNS},
        "counterfactual_status": {"type": "string", "enum": COUNTERFACTUAL},
        "effect_extractability": {"type": "string", "enum": EXTRACTABILITY},
        "outcome_status": {"type": "string", "enum": OUTCOME},
        "primary_reason_code": {"type": "string", "enum": REASON_CODES},
        "confidence": {"type": "string", "enum": CONFIDENCE},
        "reason": {"type": "string", "maxLength": 500},
        "full_text_checks": {
            "type": "array",
            "items": {"type": "string", "maxLength": 200},
            "maxItems": 5,
        },
        "overlap_flag": {"type": "string", "enum": OVERLAP},
    },
    "required": [
        "dedup_id",
        "strict_decision",
        "primary_topic",
        "exposure_measurement",
        "design_class",
        "counterfactual_status",
        "effect_extractability",
        "outcome_status",
        "primary_reason_code",
        "confidence",
        "reason",
        "full_text_checks",
        "overlap_flag",
    ],
}

RESULT_FIELDS = [
    "dedup_id",
    "title",
    "year",
    "journal",
    "candidate_topics",
    "strict_decision",
    "primary_topic",
    "exposure_measurement",
    "design_class",
    "counterfactual_status",
    "effect_extractability",
    "outcome_status",
    "primary_reason_code",
    "confidence",
    "reason",
    "full_text_checks",
    "overlap_flag",
    "model_requested",
    "model_returned",
    "response_id",
    "input_tokens",
    "output_tokens",
    "total_tokens",
    "screened_at",
    "criteria_version",
]


def sha256(path):
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def utc_now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/input_802.csv")
    parser.add_argument("--prompt", default="strict_inc_prompt.md")
    parser.add_argument("--jsonl", default="results/strict_inc_gpt56.jsonl")
    parser.add_argument("--output", default="results/strict_inc_gpt56.csv")
    parser.add_argument("--summary", default="results/summary.json")
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-retries", type=int, default=3)
    parser.add_argument(
        "--validate-only",
        action="store_true",
        help="Validate the frozen input and prompt without calling the API.",
    )
    return parser.parse_args()


def read_input(path):
    csv.field_size_limit(sys.maxsize)
    with open(path, newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def read_completed(path, run_id):
    completed = {}
    if not os.path.exists(path):
        return completed
    with open(path, encoding="utf-8") as handle:
        for line in handle:
            try:
                item = json.loads(line)
            except json.JSONDecodeError:
                continue
            if item.get("run_id") != run_id:
                raise SystemExit(
                    "Checkpoint does not match the current input, prompt, model, and criteria. "
                    "Use a new --jsonl path."
                )
            if item.get("status") == "complete" and item.get("dedup_id"):
                completed[item["dedup_id"]] = item
    return completed


def usage_value(usage, name):
    value = getattr(usage, name, None)
    return int(value or 0)


def screen_one(client, prompt, record, max_retries, run_id):
    payload = {
        "dedup_id": record["dedup_id"],
        "title": record["title"],
        "abstract": record["abstract"],
        "year": record.get("year", ""),
        "journal": record.get("journal", ""),
        "previous_candidate_topics": record.get("candidate_topics", ""),
    }
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = client.responses.create(
                model=MODEL,
                reasoning={"effort": "high"},
                store=False,
                instructions=prompt,
                input=json.dumps(payload, ensure_ascii=False),
                max_output_tokens=3000,
                text={
                    "verbosity": "low",
                    "format": {
                        "type": "json_schema",
                        "name": "strict_inc_decision",
                        "strict": True,
                        "schema": SCHEMA,
                    },
                },
            )
            parsed = json.loads(response.output_text)
            if parsed["dedup_id"] != record["dedup_id"]:
                raise ValueError(
                    "Returned dedup_id {} does not match input {}".format(
                        parsed["dedup_id"], record["dedup_id"]
                    )
                )
            usage = response.usage
            return {
                "status": "complete",
                "run_id": run_id,
                "dedup_id": record["dedup_id"],
                "result": parsed,
                "model_requested": MODEL,
                "model_returned": response.model,
                "response_id": response.id,
                "input_tokens": usage_value(usage, "input_tokens"),
                "output_tokens": usage_value(usage, "output_tokens"),
                "total_tokens": usage_value(usage, "total_tokens"),
                "screened_at": utc_now(),
                "criteria_version": CRITERIA_VERSION,
            }
        except Exception as error:
            last_error = "{}: {}".format(type(error).__name__, str(error))
            if attempt < max_retries:
                time.sleep(min(30, 2 ** attempt))
    return {
        "status": "error",
        "run_id": run_id,
        "dedup_id": record["dedup_id"],
        "error": last_error,
        "attempts": max_retries,
        "screened_at": utc_now(),
        "criteria_version": CRITERIA_VERSION,
    }


def append_jsonl(path, item, lock):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with lock:
        with open(path, "a", encoding="utf-8") as handle:
            handle.write(json.dumps(item, ensure_ascii=False) + "\n")
            handle.flush()
            os.fsync(handle.fileno())


def export_csv(path, records, completed):
    temporary = path + ".tmp"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(temporary, "w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=RESULT_FIELDS)
        writer.writeheader()
        for record in records:
            item = completed.get(record["dedup_id"])
            if not item:
                continue
            result = item["result"]
            writer.writerow(
                {
                    "dedup_id": record["dedup_id"],
                    "title": record["title"],
                    "year": record.get("year", ""),
                    "journal": record.get("journal", ""),
                    "candidate_topics": record.get("candidate_topics", ""),
                    **{key: result[key] for key in result if key != "full_text_checks"},
                    "full_text_checks": " | ".join(result["full_text_checks"]),
                    "model_requested": item["model_requested"],
                    "model_returned": item["model_returned"],
                    "response_id": item["response_id"],
                    "input_tokens": item["input_tokens"],
                    "output_tokens": item["output_tokens"],
                    "total_tokens": item["total_tokens"],
                    "screened_at": item["screened_at"],
                    "criteria_version": item["criteria_version"],
                }
            )
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temporary, path)


def write_summary(path, args, prompt_path, records, completed, errors, run_id):
    decisions = Counter(
        item["result"]["strict_decision"] for item in completed.values()
    )
    summary = {
        "criteria_version": CRITERIA_VERSION,
        "model_requested": MODEL,
        "run_id": run_id,
        "input_records": len(records),
        "completed_records": len(completed),
        "error_records": len(errors),
        "decision_counts": dict(sorted(decisions.items())),
        "input_sha256": sha256(args.input),
        "prompt_sha256": sha256(prompt_path),
        "jsonl_sha256": sha256(args.jsonl) if os.path.exists(args.jsonl) else None,
        "output_sha256": sha256(args.output) if os.path.exists(args.output) else None,
        "input_tokens": sum(item["input_tokens"] for item in completed.values()),
        "output_tokens": sum(item["output_tokens"] for item in completed.values()),
        "total_tokens": sum(item["total_tokens"] for item in completed.values()),
        "generated_at": utc_now(),
    }
    temporary = path + ".tmp"
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(summary, handle, ensure_ascii=False, indent=2)
        handle.write("\n")
    os.replace(temporary, path)
    return summary


def main():
    args = parse_args()
    if args.workers < 1:
        raise SystemExit("--workers must be at least 1")

    script_dir = os.path.dirname(os.path.abspath(__file__))
    prompt_path = (
        args.prompt if os.path.isabs(args.prompt) else os.path.join(script_dir, args.prompt)
    )
    with open(prompt_path, encoding="utf-8") as handle:
        prompt = handle.read()

    records = read_input(args.input)
    if not args.limit and len(records) != EXPECTED_RECORDS:
        raise SystemExit(
            "Expected {} records, found {}.".format(EXPECTED_RECORDS, len(records))
        )
    required_fields = {"dedup_id", "title", "abstract"}
    if records and not required_fields.issubset(records[0]):
        missing = sorted(required_fields - set(records[0]))
        raise SystemExit("Input is missing required fields: " + ", ".join(missing))
    duplicate_ids = [
        dedup_id
        for dedup_id, count in Counter(row["dedup_id"] for row in records).items()
        if count > 1
    ]
    if duplicate_ids:
        raise SystemExit("Duplicate dedup_id values: " + ", ".join(duplicate_ids[:20]))
    empty_abstracts = [row["dedup_id"] for row in records if not row["abstract"].strip()]
    if empty_abstracts:
        raise SystemExit("Records without abstracts: " + ", ".join(empty_abstracts[:20]))
    if args.validate_only:
        print(
            json.dumps(
                {
                    "status": "valid",
                    "criteria_version": CRITERIA_VERSION,
                    "model": MODEL,
                    "records": len(records),
                    "input_sha256": sha256(args.input),
                    "prompt_sha256": sha256(prompt_path),
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return

    if not os.environ.get("OPENAI_API_KEY"):
        raise SystemExit("OPENAI_API_KEY is not set.")
    try:
        from openai import OpenAI
    except ImportError as error:
        raise SystemExit(
            "The openai package is not installed. Run: pip install -r requirements.txt"
        ) from error

    run_identity = "\n".join(
        [sha256(args.input), sha256(prompt_path), MODEL, CRITERIA_VERSION]
    ).encode("utf-8")
    run_id = hashlib.sha256(run_identity).hexdigest()
    completed = read_completed(args.jsonl, run_id)
    unexpected_completed = sorted(set(completed) - {row["dedup_id"] for row in records})
    if unexpected_completed:
        raise SystemExit(
            "Checkpoint contains records outside the current input: "
            + ", ".join(unexpected_completed[:20])
        )
    selected = records[: args.limit] if args.limit else records
    pending = [record for record in selected if record["dedup_id"] not in completed]
    client = OpenAI()
    lock = threading.Lock()
    errors = []

    print(
        "Starting {} pending records with {} workers; {} already complete.".format(
            len(pending), args.workers, len(completed)
        ),
        flush=True,
    )
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(
                screen_one, client, prompt, record, args.max_retries, run_id
            ): record
            for record in pending
        }
        total = len(futures)
        for index, future in enumerate(as_completed(futures), 1):
            item = future.result()
            append_jsonl(args.jsonl, item, lock)
            if item["status"] == "complete":
                completed[item["dedup_id"]] = item
            else:
                errors.append(item)
            if index % 10 == 0 or index == total:
                print(
                    "{}/{} finished; {} complete, {} errors.".format(
                        index, total, len(completed), len(errors)
                    ),
                    flush=True,
                )

    export_csv(args.output, records, completed)
    summary = write_summary(
        args.summary, args, prompt_path, records, completed, errors, run_id
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
