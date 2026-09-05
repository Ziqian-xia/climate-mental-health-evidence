"""Screen the entire local corpus and export result.csv, review.csv, and result.json."""
from __future__ import annotations
import argparse
import csv
import getpass
import json
import os
from pathlib import Path
import platform
import sys

import screen_fast as engine

ROOT = Path(__file__).resolve().parent
INPUT = ROOT / "data/merged_deduplicated_records.csv.gz"
FIELDS = ["dedup_id", "title", "status", "decision", "decision_basis", "candidate_topics",
          "reason", "module_decisions", "module_exclusion_codes", "screening_mode",
          "title_only_decision", "title_only_exclusion_code"]

def write_public_results(work, output):
    """Export a frozen run as exactly two CSV files and one self-contained JSON."""
    engine_path = ROOT / "screen_fast.py"
    prompt_dir = ROOT / "prompts_v4"
    manifest = json.loads((work / "manifest.json").read_text(encoding="utf-8"))
    config = manifest["config"]
    if config["engine_sha256"] != engine.file_sha(engine_path):
        raise ValueError("Selected code version does not match the saved results.")
    if config["input_sha256"] != engine.file_sha(INPUT):
        raise ValueError("Input data differ from the saved results.")
    raw, _ = engine.prompts(prompt_dir)
    if {k: engine.digest(v) for k, v in raw.items()} != config["prompt_sha256"]:
        raise ValueError("Selected prompts differ from the saved results.")
    output.mkdir(parents=True, exist_ok=True)
    row_counts = {}
    for source, target in [("screening_results.csv", "result.csv"), ("human_review.csv", "review.csv")]:
        with (work/source).open(encoding="utf-8-sig", newline="") as src, \
             (output/(target+".tmp")).open("w", encoding="utf-8-sig", newline="") as dst:
            reader = csv.DictReader(src)
            if not set(FIELDS).issubset(reader.fieldnames or []):
                raise ValueError("Saved CSV lacks required screening columns.")
            writer = csv.DictWriter(dst, fieldnames=FIELDS)
            writer.writeheader()
            count = 0
            for row in reader:
                writer.writerow({k: row[k] for k in FIELDS})
                count += 1
            row_counts[target] = count

    portable_manifest = {k:v for k,v in manifest.items() if k != "input_path"}
    portable_manifest["input_path"] = "data/merged_deduplicated_records.csv.gz"
    sessions = [json.loads(p.read_text(encoding="utf-8")) for p in sorted((work/"sessions").glob("*.json"))]
    source_files = [engine_path, ROOT/"run.py", ROOT/"requirements.txt"] + [prompt_dir/n for n in engine.FILES.values()]
    metadata = {
        "schema_version": 1,
        "engine_version": engine.VERSION,
        "scope": "Full input corpus; no sampling.",
        "manifest": portable_manifest,
        "summary": json.loads((work/"summary.json").read_text(encoding="utf-8")),
        "recorded_sessions": sessions,
        "source_file_sha256": {p.relative_to(ROOT).as_posix():engine.file_sha(p) for p in source_files},
        "csv_rows": row_counts,
        "csv_sha256": {name:engine.file_sha(output/(name+".tmp")) for name in row_counts},
        "export_runtime": {"python":platform.python_version()},
        "reproducibility_note": "Inputs, prompts, parameters, and responses are retained for reproducibility. Online API re-execution can differ because model generation is not guaranteed deterministic."
    }
    tmp = output/"result.json.tmp"
    ids = set()
    with tmp.open("w",encoding="utf-8",newline="\n") as dst, (work/"screening_results.jsonl").open(encoding="utf-8") as src:
        dst.write('{"metadata":'+engine.dumps(metadata)+',"records":[')
        first = True
        for line in src:
            if not line.strip():
                continue
            doc = json.loads(line)
            did = doc["record"]["dedup_id"]
            if did in ids:
                raise ValueError("Duplicate record in JSONL.")
            if doc["run_fingerprint"] != manifest["fingerprint"]:
                raise ValueError("Record fingerprint differs from run.")
            ids.add(did)
            if not first:
                dst.write(",")
            dst.write(engine.dumps(doc))
            first = False
        dst.write("]}\n")
    if len(ids) != row_counts["result.csv"]:
        raise ValueError("CSV and JSON record counts disagree.")
    # Publish the matching JSON last; its CSV hashes allow cross-file consistency checks.
    for name in ["result.csv", "review.csv", "result.json"]:
        engine.replace_with_retry(output/(name+".tmp"), output/name)
    print(f"Saved {row_counts['result.csv']} records and {row_counts['review.csv']} REVIEW records to {output}")

def main(argv=None):
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--concurrency", type=int, default=32, help="Maximum simultaneous API requests")
    p.add_argument("--export-only", action="store_true", help="Export local checkpoints without any API call")
    args = p.parse_args(argv)
    if not 1 <= args.concurrency <= 2500:
        p.error("concurrency must be between 1 and 2500")
    prompt_dir = ROOT / "prompts_v4"
    work, output = ROOT / ".work/full", ROOT / "results"
    cli = ["run", "--input", str(INPUT), "--prompts", str(prompt_dir), "--out", str(work),
           "--sample-size", "0", "--limit", "0", "--concurrency", str(args.concurrency),
           "--thinking", "high", "--max-tokens", "4096", "--max-tokens-ceiling", "16384",
           "--retries", "3", "--timeout", "660", "--no-export"]
    prior = os.environ.get("DEEPSEEK_API_KEY")
    try:
        if not args.export_only:
            if not prior:
                os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("DeepSeek API key (hidden): ").strip()
            code = engine.main(cli)
            if code:
                return code
        with engine.run_lock(work):
            summary = engine.export(engine.parse_args(["export", "--input", str(INPUT), "--out", str(work)]))
            write_public_results(work, output)
            return 2 if summary["counts"].get("retryable_error", 0) else 0
    finally:
        if prior is None:
            os.environ.pop("DEEPSEEK_API_KEY", None)
        else:
            os.environ["DEEPSEEK_API_KEY"] = prior

if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted. Re-run the identical command to resume, or use --export-only to export saved progress.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(engine.error_text(exc), file=sys.stderr)
        raise SystemExit(1)
