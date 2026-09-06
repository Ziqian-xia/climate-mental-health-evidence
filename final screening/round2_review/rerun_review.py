"""Re-screen the frozen baseline REVIEW set and merge into the full corpus.

The original screening engine and its decision rules are used without changes.
Preparation and export-only operations never make API requests.
"""
from __future__ import annotations

import argparse
from collections import Counter
import csv
import getpass
import gzip
import hashlib
import json
import os
from pathlib import Path
import sys

import screen_fast as engine
from run import FIELDS

ROOT = Path(__file__).resolve().parent


class JSONStream:
    """Incrementally decode the original public JSON without loading the corpus."""

    def __init__(self, stream):
        self.stream, self.buffer, self.eof = stream, "", False
        self.decoder = json.JSONDecoder()

    def fill(self):
        chunk = self.stream.read(1024 * 1024)
        self.eof = not chunk
        self.buffer += chunk

    def peek(self):
        while True:
            self.buffer = self.buffer.lstrip()
            if self.buffer or self.eof:
                return self.buffer[:1]
            self.fill()

    def take(self, expected):
        if self.peek() != expected:
            raise ValueError(f"Malformed baseline JSON: expected {expected!r}.")
        self.buffer = self.buffer[1:]

    def value(self):
        self.peek()
        while True:
            try:
                value, end = self.decoder.raw_decode(self.buffer)
            except json.JSONDecodeError:
                if self.eof or len(self.buffer) > 128 * 1024 * 1024:
                    raise ValueError("Truncated or malformed baseline JSON.") from None
                self.fill()
            else:
                self.buffer = self.buffer[end:]
                return value


def baseline_items(path):
    """Read the metadata-then-records layout produced by the unchanged run.py."""
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rt", encoding="utf-8-sig") as handle:
        reader = JSONStream(handle)
        reader.take("{")
        if reader.value() != "metadata":
            raise ValueError("Expected the original public result.json, with metadata first.")
        reader.take(":")
        yield "metadata", reader.value()
        reader.take(",")
        if reader.value() != "records":
            raise ValueError("Baseline JSON has no records array.")
        reader.take(":")
        reader.take("[")
        if reader.peek() != "]":
            while True:
                yield "record", reader.value()
                if reader.peek() == "]":
                    break
                reader.take(",")
        reader.take("]")
        reader.take("}")
        if reader.peek():
            raise ValueError("Unexpected content after baseline JSON.")


def content_sha(path):
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def check_package():
    package = json.loads((ROOT / "package_manifest.json").read_text(encoding="utf-8"))
    for name, expected in package["package_file_sha256"].items():
        if engine.file_sha(ROOT / name) != expected:
            raise ValueError(f"Package file changed: {name}. Use the frozen release files.")
    return package


def baseline_docs(work):
    with (work / "baseline.jsonl").open(encoding="utf-8") as handle:
        for line in handle:
            yield json.loads(line)


def prepare(baseline, work, package):
    """Freeze membership once from the original completed REVIEW decisions."""
    if content_sha(baseline) != package["baseline_result_json_sha256"]:
        raise ValueError("Baseline hash mismatch. Supply the exact original full result.json (or its gzip copy).")
    contract = engine.digest(package)
    prepared_path = work / "preparation.json"
    if prepared_path.exists():
        prepared = json.loads(prepared_path.read_text(encoding="utf-8"))
        if prepared["package_digest"] != contract:
            raise ValueError("Package changed since preparation. Use a new work directory.")
        for name, checksum in prepared["cache_sha256"].items():
            if engine.file_sha(work / name) != checksum:
                raise ValueError(f"Prepared input changed: {name}. Restore it before resuming.")
        return prepared

    if (work / "rerun" / "manifest.json").exists():
        raise ValueError("Rerun checkpoints exist without preparation metadata; refusing to reconstruct provenance.")
    raw, _ = engine.prompts(ROOT / "prompts_v4")
    ids, counts = set(), Counter()
    baseline_metadata = None
    with (work / "baseline.jsonl.tmp").open("w", encoding="utf-8", newline="\n") as saved, \
         (work / "review_input.csv.tmp").open("w", encoding="utf-8", newline="") as subset:
        writer = csv.DictWriter(subset, fieldnames=["dedup_id", "title", "abstract"], lineterminator="\n")
        writer.writeheader()
        for kind, value in baseline_items(baseline):
            if kind == "metadata":
                baseline_metadata = value
                manifest = value["manifest"]
                if manifest["fingerprint"] != package["baseline_run_fingerprint"]:
                    raise ValueError("Baseline run fingerprint mismatch.")
                config = manifest["config"]
                if config["engine_sha256"] != engine.file_sha(ROOT / "screen_fast.py"):
                    raise ValueError("The baseline used a different screening engine.")
                for key, text in raw.items():
                    if key != "router" and engine.digest(text) != config["prompt_sha256"][key]:
                        raise ValueError(f"Non-router prompt differs from baseline: {key}")
                continue
            doc = value
            rec = doc["record"]
            did = rec["dedup_id"]
            if did in ids:
                raise ValueError(f"Duplicate baseline ID: {did}")
            ids.add(did)
            if doc["status"] != "complete" or doc["decision"] not in {"INCLUDE", "EXCLUDE", "REVIEW"}:
                raise ValueError(f"Baseline record is not a completed screening decision: {did}")
            if doc["run_fingerprint"] != package["baseline_run_fingerprint"] or doc["record_sha256"] != engine.digest(rec):
                raise ValueError(f"Baseline record provenance mismatch: {did}")
            counts[doc["decision"]] += 1
            saved.write(engine.dumps(doc) + "\n")
            if doc["decision"] == "REVIEW":
                writer.writerow(rec)
    if len(ids) != package["baseline_records"] or dict(counts) != package["baseline_decision_counts"]:
        raise ValueError("Baseline record counts do not match the frozen release.")
    for name in ["baseline.jsonl", "review_input.csv"]:
        engine.replace_with_retry(work / (name + ".tmp"), work / name)
    prepared = {
        "created_at": engine.now(), "package_digest": contract,
        "baseline_result_json_sha256": package["baseline_result_json_sha256"],
        "baseline_metadata": baseline_metadata, "baseline_counts": dict(counts),
        "input_records": len(ids), "selected_review_records": counts["REVIEW"],
        "selection_rule": "Original baseline status=complete and decision=REVIEW; frozen before rerun.",
        "cache_sha256": {name: engine.file_sha(work / name) for name in ["baseline.jsonl", "review_input.csv"]},
    }
    engine.atomic_json(prepared_path, prepared)
    return prepared


def engine_args(work, prepared, concurrency):
    config = prepared["baseline_metadata"]["manifest"]["config"]
    args = ["run", "--input", str(work / "review_input.csv"), "--prompts", str(ROOT / "prompts_v4"),
            "--out", str(work / "rerun"), "--concurrency", str(concurrency),
            "--sample-size", "0", "--limit", "0", "--retries", "3", "--timeout", "660", "--no-export"]
    for key in ["model", "base_url", "thinking", "max_tokens", "max_tokens_ceiling", "seed"]:
        args.extend(["--" + key.replace("_", "-"), str(config[key])])
    return args


def csv_row(doc):
    """Keep the existing 12 public columns and the engine's CSV escaping convention."""
    rec, stages = doc["record"], doc["stages"]
    router = stages.get("router", {}).get("result", {})
    modules = {topic: stages[topic]["result"] for topic in engine.TOPICS
               if stages.get(topic, {}).get("status") == "ok"}
    title_only = stages.get("title_only", {}).get("result", {})
    row = dict(dedup_id=rec["dedup_id"], title=rec["title"], status=doc["status"],
               decision=doc["decision"], decision_basis=doc["decision_basis"], reason=doc["reason"],
               candidate_topics="|".join(router.get("candidate_topics", [])),
               module_decisions=engine.dumps({t: r["decision"] for t, r in modules.items()}),
               module_exclusion_codes=engine.dumps({t: r.get("exclusion_code", "") for t, r in modules.items()}),
               screening_mode="title_abstract" if rec["abstract"] else ("title_only" if rec["title"] else "no_text"),
               title_only_decision=title_only.get("decision", ""),
               title_only_exclusion_code=title_only.get("exclusion_code", ""))
    return {k: "'" + v if isinstance(v, str) and v.lstrip().startswith(("=", "+", "-", "@")) else v
            for k, v in row.items()}


def merge_results(work, output, prepared, package, cli):
    run_dir = work / "rerun"
    raw, _ = engine.prompts(ROOT / "prompts_v4")
    parsed = engine.parse_args(cli)
    manifest = engine.manifest(parsed, raw)
    store = engine.Store(run_dir, manifest["fingerprint"])
    output.mkdir(parents=True, exist_ok=True)
    counts, progress, transitions, usage = Counter(), Counter(), Counter(), Counter()
    preserved_digest, merged_preserved_digest = hashlib.sha256(), hashlib.sha256()
    with (output / "result.csv.tmp").open("w", encoding="utf-8-sig", newline="") as all_csv, \
         (output / "review.csv.tmp").open("w", encoding="utf-8-sig", newline="") as review_csv, \
         (work / "merged_records.jsonl.tmp").open("w", encoding="utf-8", newline="\n") as docs:
        writers = [csv.DictWriter(handle, fieldnames=FIELDS) for handle in [all_csv, review_csv]]
        for writer in writers:
            writer.writeheader()
        for original in baseline_docs(work):
            doc = original
            if original["decision"] == "REVIEW":
                updated = store.load(original["record"])
                if updated:
                    usage.update(engine.usage_totals(updated))
                if updated and updated.get("status") == "complete":
                    doc = dict(updated)
                    progress["complete"] += 1
                    transitions["REVIEW_to_" + doc["decision"]] += 1
                    audit = {"rerun_status": "complete", "rerun_source_row": updated["source_row"]}
                    doc["source_row"] = original["source_row"]
                else:
                    # Keep the old REVIEW decision until a new decision is complete.
                    doc = dict(original)
                    state = "not_started" if updated is None else updated.get("status", "in_progress")
                    progress[state] += 1
                    doc["status"] = "retryable_error" if state == "retryable_error" else "in_progress"
                    doc["decision_basis"] = "review_rerun_pending"
                    doc["reason"] = "Review reassessment unfinished; original REVIEW retained. " + original["reason"]
                    audit = {"rerun_status": state, "partial_rerun": updated}
                doc["review_reassessment"] = {
                    **audit, "baseline_decision": "REVIEW", "baseline_decision_basis": original["decision_basis"],
                    "baseline_reason": original["reason"], "baseline_document_sha256": engine.digest(original),
                    "baseline_run_fingerprint": original["run_fingerprint"],
                    "target_run_fingerprint": manifest["fingerprint"],
                }
            else:
                preserved_digest.update(engine.dumps(original).encode("utf-8") + b"\n")
                merged_preserved_digest.update(engine.dumps(doc).encode("utf-8") + b"\n")
                progress["preserved_non_review"] += 1
            counts[doc["decision"]] += 1
            row = csv_row(doc)
            writers[0].writerow(row)
            if doc["decision"] == "REVIEW":
                writers[1].writerow(row)
            docs.write(engine.dumps(doc) + "\n")

    total = sum(counts.values())
    if total != prepared["input_records"]:
        raise ValueError("Merged corpus count mismatch.")
    if progress["preserved_non_review"] != total - prepared["selected_review_records"]:
        raise ValueError("Non-REVIEW preservation count mismatch.")
    if preserved_digest.digest() != merged_preserved_digest.digest():
        raise ValueError("A retained non-REVIEW record changed.")
    finished = progress["complete"] == prepared["selected_review_records"]
    portable_manifest = {**manifest, "input_path": ".work/review_reassessment/review_input.csv"}
    summary = {"input_records": total, "decision_counts": dict(counts), "review_rerun": dict(progress),
               "review_transitions": dict(transitions), "complete_corpus": finished,
               "review_rerun_complete": finished,
               "unfinished_review_records": prepared["selected_review_records"] - progress["complete"]}
    metadata = {
        "schema_version": 2, "created_at": engine.now(),
        "scope": "Full baseline corpus; reassess only its frozen original REVIEW set.",
        "baseline_result_json_sha256": prepared["baseline_result_json_sha256"],
        "baseline_metadata": prepared["baseline_metadata"], "rerun_manifest": portable_manifest,
        "rerun_sessions": [json.loads(p.read_text(encoding="utf-8")) for p in sorted((run_dir / "sessions").glob("*.json"))],
        "selection_rule": prepared["selection_rule"], "selected_review_records": prepared["selected_review_records"],
        "package_manifest": package, "summary": summary, "rerun_usage": dict(usage),
        "csv_rows": {"result.csv": total, "review.csv": counts["REVIEW"]},
        "csv_sha256": {n: engine.file_sha(output / (n + ".tmp")) for n in ["result.csv", "review.csv"]},
        "preserved_non_review_documents_sha256": preserved_digest.hexdigest(),
        "reproducibility_note": "Baseline and rerun have distinct provenance. Original non-REVIEW documents are retained unchanged. Online API re-execution is not guaranteed deterministic.",
    }
    with (output / "result.json.tmp").open("w", encoding="utf-8", newline="\n") as dst, \
         (work / "merged_records.jsonl.tmp").open(encoding="utf-8") as src:
        dst.write('{"metadata":' + engine.dumps(metadata) + ',"records":[')
        for index, line in enumerate(src):
            if index:
                dst.write(",")
            dst.write(line.rstrip("\n"))
        dst.write("]}\n")
        dst.flush()
        os.fsync(dst.fileno())
    # Publish JSON last; its hashes identify the matching CSV generation.
    for name in ["result.csv", "review.csv", "result.json"]:
        engine.replace_with_retry(output / (name + ".tmp"), output / name)
    engine.atomic_json(work / "merged_summary.json", summary)
    print(json.dumps(summary, indent=2))
    print(f"Saved full-corpus result.csv, review.csv, and result.json to {output}")
    return 0 if finished else 2


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True, help="Frozen original full result.json or result.json.gz")
    parser.add_argument("--concurrency", type=int, default=32)
    modes = parser.add_mutually_exclusive_group()
    modes.add_argument("--prepare-only", action="store_true", help="Verify baseline and prepare REVIEW input; no API calls")
    modes.add_argument("--export-only", action="store_true", help="Merge local checkpoints into all records; no API calls")
    parser.add_argument("--work-dir", type=Path, default=ROOT / ".work/review_reassessment")
    parser.add_argument("--output", type=Path, default=ROOT / "results")
    args = parser.parse_args(argv)
    if not 1 <= args.concurrency <= 2500:
        parser.error("concurrency must be between 1 and 2500")
    baseline, work, output = args.baseline.resolve(), args.work_dir.resolve(), args.output.resolve()
    if not baseline.is_file():
        raise ValueError(f"Baseline file not found: {baseline}")
    if baseline.parent == output or baseline.is_relative_to(work) or output == work or output.is_relative_to(work) or work.is_relative_to(output):
        raise ValueError("Keep the baseline, work directory, and output directory separate.")
    package = check_package()
    if (output / "result.json").exists():
        existing = baseline_items(output / "result.json")
        try:
            _, metadata = next(existing)
        finally:
            existing.close()
        if metadata.get("package_manifest") != package or "rerun_manifest" not in metadata:
            raise ValueError("Output directory contains results from another workflow. Choose a new output directory.")
    with engine.run_lock(work):
        prepared = prepare(baseline, work, package)
        print(f"Frozen baseline: {prepared['input_records']} records; original REVIEW set: {prepared['selected_review_records']}.")
        cli = engine_args(work, prepared, args.concurrency)
        if args.prepare_only:
            print("Preparation complete. No API requests made.")
            return 0
        # Check provenance before requesting a key or starting paid work.
        with engine.run_lock(work / "rerun"):
            engine.manifest(engine.parse_args(cli), engine.prompts(ROOT / "prompts_v4")[0])
        code = 0
        if not args.export_only:
            prior = os.environ.get("DEEPSEEK_API_KEY")
            try:
                if not (prior or "").strip():
                    os.environ["DEEPSEEK_API_KEY"] = getpass.getpass("DeepSeek API key (hidden): ").strip()
                code = engine.main(cli)
            except KeyboardInterrupt:
                print("Interrupted. Saved stages retained; exporting current full-corpus progress.", file=sys.stderr)
                code = 130
            except Exception as exc:
                print(engine.error_text(exc), file=sys.stderr)
                code = 1
            finally:
                if prior is None:
                    os.environ.pop("DEEPSEEK_API_KEY", None)
                else:
                    os.environ["DEEPSEEK_API_KEY"] = prior
        with engine.run_lock(work / "rerun"):
            merged_code = merge_results(work, output, prepared, package, cli)
        return code or merged_code


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print("Interrupted. Re-run the identical command to resume; --export-only rebuilds saved progress.", file=sys.stderr)
        raise SystemExit(130)
    except Exception as exc:
        print(engine.error_text(exc), file=sys.stderr)
        raise SystemExit(1)
