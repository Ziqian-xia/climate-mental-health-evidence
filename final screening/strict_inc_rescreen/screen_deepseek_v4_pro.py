#!/usr/bin/env python3
"""Independently reassess the frozen 802 INC records with DeepSeek V4 Pro."""

import argparse
import csv
import hashlib
import json
import os
import random
import sys
import threading
import time
import urllib.error
import urllib.request
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone

from screen_gpt56 import (
    CONFIDENCE,
    COUNTERFACTUAL,
    CRITERIA_VERSION,
    DECISIONS,
    DESIGNS,
    EXPECTED_RECORDS,
    EXPOSURE,
    EXTRACTABILITY,
    OUTCOME,
    OVERLAP,
    REASON_CODES,
    RESULT_FIELDS,
    TOPICS,
    read_input,
    sha256,
    utc_now,
)

MODEL = "deepseek-v4-pro"
API_URL = "https://api.deepseek.com/chat/completions"

ENUM_FIELDS = {
    "strict_decision": DECISIONS,
    "primary_topic": TOPICS,
    "exposure_measurement": EXPOSURE,
    "design_class": DESIGNS,
    "counterfactual_status": COUNTERFACTUAL,
    "effect_extractability": EXTRACTABILITY,
    "outcome_status": OUTCOME,
    "primary_reason_code": REASON_CODES,
    "confidence": CONFIDENCE,
    "overlap_flag": OVERLAP,
}
REQUIRED_RESULT_FIELDS = [
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
]

OUTPUT_INSTRUCTIONS = """

Return one JSON object and nothing else. Use exactly these keys:
{
  "dedup_id": "copy the supplied value exactly",
  "strict_decision": "META_ELIGIBLE | FULLTEXT_REVIEW | NARRATIVE_ONLY | EXCLUDE",
  "primary_topic": "temperature | wildfire | flood | cyclone | drought | multiple | unclear",
  "exposure_measurement": "objective_or_verifiable | self_report_only | unclear | ineligible",
  "design_class": "time_series | case_crossover | longitudinal_with_prebaseline | panel_fixed_effects | quasi_experimental | cross_sectional | post_event_only | qualitative | descriptive | other_eligible | unclear",
  "counterfactual_status": "yes | no | unclear",
  "effect_extractability": "reported_with_uncertainty | likely_extractable | not_extractable | unclear",
  "outcome_status": "eligible | ineligible | unclear",
  "primary_reason_code": "eligible | unclear_exposure_measurement | unclear_design | unclear_effect_extractability | cross_sectional | no_pre_event_baseline | no_hazard_variation | self_report_exposure_only | descriptive_or_predictor_only | qualitative_only | wrong_exposure | wrong_outcome | non_original | not_human_empirical | projection_only | multiple_issues",
  "confidence": "high | medium | low",
  "reason": "concise record-specific justification based only on title and abstract",
  "full_text_checks": ["zero to five exact facts to verify"],
  "overlap_flag": "none_identified | potential_overlap | unclear"
}
Do not add keys. Use valid JSON, not Markdown. Keep reason under 500 characters and each
full_text_checks item under 200 characters.
"""


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="results/input_802.csv")
    parser.add_argument("--prompt", default="strict_inc_prompt.md")
    parser.add_argument("--jsonl", default="results/strict_inc_deepseek_v4_pro.jsonl")
    parser.add_argument("--output", default="results/strict_inc_deepseek_v4_pro.csv")
    parser.add_argument("--summary", default="results/deepseek_v4_pro_summary.json")
    parser.add_argument("--workers", type=int, default=16)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--max-retries", type=int, default=5)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--validate-only", action="store_true")
    return parser.parse_args()


def validate_result(result, expected_id):
    if not isinstance(result, dict):
        raise ValueError("response is not a JSON object")
    if set(result) != set(REQUIRED_RESULT_FIELDS):
        missing = sorted(set(REQUIRED_RESULT_FIELDS) - set(result))
        extra = sorted(set(result) - set(REQUIRED_RESULT_FIELDS))
        raise ValueError("wrong keys; missing={} extra={}".format(missing, extra))
    if result["dedup_id"] != expected_id:
        raise ValueError("returned dedup_id does not match input")
    for field, allowed in ENUM_FIELDS.items():
        if result[field] not in allowed:
            raise ValueError("invalid {}: {}".format(field, result[field]))
    if not isinstance(result["reason"], str) or not result["reason"].strip():
        raise ValueError("reason must be a non-empty string")
    if len(result["reason"]) > 500:
        raise ValueError("reason exceeds 500 characters")
    checks = result["full_text_checks"]
    if not isinstance(checks, list) or len(checks) > 5:
        raise ValueError("full_text_checks must be an array of at most five strings")
    if any(not isinstance(item, str) or len(item) > 200 for item in checks):
        raise ValueError("invalid full_text_checks item")


def api_request(api_key, prompt, record, timeout):
    user_payload = {
        "dedup_id": record["dedup_id"],
        "title": record["title"],
        "abstract": record["abstract"],
        "year": record.get("year", ""),
        "journal": record.get("journal", ""),
        "previous_candidate_topics": record.get("candidate_topics", ""),
    }
    body = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": prompt + OUTPUT_INSTRUCTIONS},
            {
                "role": "user",
                "content": "Assess this record and return JSON:\n"
                + json.dumps(user_payload, ensure_ascii=False),
            },
        ],
        "thinking": {"type": "enabled"},
        "reasoning_effort": "high",
        "response_format": {"type": "json_object"},
        # DeepSeek counts hidden reasoning and visible JSON against this limit.
        "max_tokens": 8000,
        "stream": False,
    }
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": "Bearer " + api_key,
            "Content-Type": "application/json",
            "User-Agent": "climate-mental-health-strict-screen/1.0",
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


def screen_one(api_key, prompt, record, max_retries, timeout, run_id):
    last_error = None
    for attempt in range(1, max_retries + 1):
        try:
            response = api_request(api_key, prompt, record, timeout)
            choice = response["choices"][0]
            if choice.get("finish_reason") != "stop":
                raise ValueError("finish_reason={}".format(choice.get("finish_reason")))
            content = choice["message"].get("content")
            if not content:
                raise ValueError("empty response content")
            result = json.loads(content)
            validate_result(result, record["dedup_id"])
            usage = response.get("usage") or {}
            return {
                "status": "complete",
                "run_id": run_id,
                "dedup_id": record["dedup_id"],
                "result": result,
                "model_requested": MODEL,
                "model_returned": response.get("model", ""),
                "response_id": response.get("id", ""),
                "input_tokens": int(usage.get("prompt_tokens") or 0),
                "output_tokens": int(usage.get("completion_tokens") or 0),
                "total_tokens": int(usage.get("total_tokens") or 0),
                "screened_at": utc_now(),
                "criteria_version": CRITERIA_VERSION,
            }
        except urllib.error.HTTPError as error:
            detail = error.read().decode("utf-8", errors="replace")[:1000]
            last_error = "HTTPError {}: {}".format(error.code, detail)
            if error.code in {400, 401, 402, 403}:
                break
        except Exception as error:
            last_error = "{}: {}".format(type(error).__name__, str(error))
        if attempt < max_retries:
            time.sleep(min(60, (2 ** attempt) + random.random()))
    return {
        "status": "error",
        "run_id": run_id,
        "dedup_id": record["dedup_id"],
        "error": last_error,
        "attempts": max_retries,
        "screened_at": utc_now(),
        "criteria_version": CRITERIA_VERSION,
    }


def read_checkpoint(path, run_id):
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
                raise SystemExit("Checkpoint run identity mismatch; use a new --jsonl path.")
            if item.get("status") == "complete":
                completed[item["dedup_id"]] = item
    return completed


def append_checkpoint(path, item, lock):
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
                    **{key: value for key, value in result.items() if key != "full_text_checks"},
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
    decisions = Counter(item["result"]["strict_decision"] for item in completed.values())
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
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    temporary = path + ".tmp"
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
    prompt_path = args.prompt if os.path.isabs(args.prompt) else os.path.join(script_dir, args.prompt)
    with open(prompt_path, encoding="utf-8") as handle:
        prompt = handle.read()
    records = read_input(args.input)
    if not args.limit and len(records) != EXPECTED_RECORDS:
        raise SystemExit("Expected {} records, found {}.".format(EXPECTED_RECORDS, len(records)))
    if len({row["dedup_id"] for row in records}) != len(records):
        raise SystemExit("Input contains duplicate dedup_id values.")
    if any(not row["abstract"].strip() for row in records):
        raise SystemExit("Input contains a blank abstract.")
    identity = "\n".join([sha256(args.input), sha256(prompt_path), MODEL, CRITERIA_VERSION])
    run_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()
    if args.validate_only:
        print(json.dumps({"status": "valid", "records": len(records), "model": MODEL, "run_id": run_id}, indent=2))
        return
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise SystemExit("DEEPSEEK_API_KEY is not set.")
    completed = read_checkpoint(args.jsonl, run_id)
    selected = records[: args.limit] if args.limit else records
    pending = [row for row in selected if row["dedup_id"] not in completed]
    errors = []
    lock = threading.Lock()
    print("Starting {} pending records; {} already complete.".format(len(pending), len(completed)), flush=True)
    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = {
            executor.submit(screen_one, api_key, prompt, row, args.max_retries, args.timeout, run_id): row
            for row in pending
        }
        for index, future in enumerate(as_completed(futures), 1):
            item = future.result()
            append_checkpoint(args.jsonl, item, lock)
            if item["status"] == "complete":
                completed[item["dedup_id"]] = item
            else:
                errors.append(item)
            if index % 10 == 0 or index == len(futures):
                print("{}/{} finished; {} complete, {} errors.".format(index, len(futures), len(completed), len(errors)), flush=True)
    export_csv(args.output, records, completed)
    summary = write_summary(args.summary, args, prompt_path, records, completed, errors, run_id)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
