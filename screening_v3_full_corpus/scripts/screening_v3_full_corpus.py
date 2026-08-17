"""
Full-corpus title/abstract screening -- v3 pipeline (router + 5 hazard modules), ALL records
in data/merged_deduplicated_records.csv.gz (~131,468 records as of 2026-08-17).

This is the full-scale version of pilot_screening_v3_router5category_300/scripts/
screening_v3_pipeline_300.py: same prompts, same router-then-module architecture, same
aggregation rule (any topic INCLUDE -> INCLUDE, or REVIEW if that topic also set review_flag;
otherwise any MAYBE/review_flag -> REVIEW; else EXCLUDE). It is NOT the single-prompt
methodology (that approach was tried and reverted -- see git history, commit cd962fc).

Settings are pinned to match the CONFIGURATION THAT WAS ACTUALLY VALIDATED against human
labels (pilot_screening_v3/pilot_screening_v3/results/comparison_ai_v3_vs_human_packet150.md:
100% recall on any-rater-INCLUDE, 72% on INCLUDE-or-REVIEW, n=150) and re-confirmed by a
head-to-head low-vs-high reasoning effort test on the 300-record pilot sample
(pilot_screening_v3_router5category_300/results/highvlow_effort_comparison_300.csv):
low effort measurably degraded decisions on exactly the two mechanisms v3 depends on (the
design gate G5, and the "explicit-only, never exclude on silence" rule for ambiguous/no-abstract
records) -- 2 of the pilot's 4 non-EXCLUDE records flipped from REVIEW to EXCLUDE under low
effort, which is the wrong direction for a high-recall first-pass sieve. Cohen's kappa between
the two effort settings fell accordingly. Decision: run the full corpus on reasoning_effort=
"high" (DeepSeek's default for deepseek-v4-flash), matching what was validated, not the cheaper
setting.

WHY THIS SCRIPT EXISTS SEPARATELY FROM THE PILOT SCRIPTS: at ~131k records this run is expected
to take on the order of a day of wall-clock time. Neither prior pipeline script
(screening_v3_pipeline_300.py, screening_v3_pipeline_300_lowreasoning.py) checkpoints
incrementally -- they hold all results in memory and write the Excel file once at the very end,
so any interruption (network blip, API outage, machine sleep, process kill) loses 100% of
progress. This script checkpoints every completed record to an append-only JSONL file
immediately, and skips already-checkpointed dedup_ids on restart, so an interrupted run resumes
cleanly and re-screens nothing already done.

Usage
-----
    python screening_v3_full_corpus.py                  # run (or resume) the full corpus
    python screening_v3_full_corpus.py --limit 500       # smoke-test on the first 500 unscreened
    python screening_v3_full_corpus.py --finalize-only   # skip screening; just rebuild the xlsx
                                                          # from whatever the checkpoint has so far

Requires: DEEPSEEK_API_KEY in the environment. pip install pandas openai tqdm openpyxl
"""

import os
import sys
import json
import time
import re
import argparse
import asyncio
import datetime
from pathlib import Path
from collections import Counter

import pandas as pd
from openai import AsyncOpenAI
from tqdm.auto import tqdm

# ---------------------------------------------------------------------------
# Configuration -- pinned to the validated pilot settings. Do not change any of
# MODEL / REASONING_EFFORT / MAX_TOKENS / TEMPERATURE without re-running the
# validation comparisons this script's docstring describes.
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
RECORDS_FILE = REPO_ROOT / "data" / "merged_deduplicated_records.csv.gz"
PROMPTS_DIR = REPO_ROOT / "prompts_v3"
OUT_DIR = Path(__file__).resolve().parents[1] / "results"

MODEL = "deepseek-v4-flash"
REASONING_EFFORT = "high"     # matches the validated packet150 + 300-pilot runs; see docstring
MAX_TOKENS = 3000             # starting budget. 800 truncated ~15% of calls in the 300-record
                               # pilot; 3000 fixed all but 1/300 (which needed 6000). Truncated
                               # calls now escalate this budget on retry -- see call_model_async.
MAX_TOKENS_CAP = 9000          # ceiling for the escalation; 3000 -> 6000 -> 9000 -> 9000
TEMPERATURE = 0                # note: DeepSeek's thinking mode ignores temperature/top_p; kept
                               # for parity with the validated scripts, not because it has effect

MAX_CONCURRENCY = 10          # matches the validated 300-record pilot's concurrency. DeepSeek's
                               # published concurrency limit for this model is far higher
                               # (500 peak / 2500 off-peak, account-wide) -- this can be raised
                               # once this script's resumability has been exercised on a real
                               # interruption, but was not itself part of what was validated.

CHECKPOINT_FILE = OUT_DIR / "full_corpus_checkpoint.jsonl"
OUTPUT_XLSX = OUT_DIR / "screening_v3_full_corpus_results.xlsx"
CRITERIA_VERSION = "per-topic prompt set 00-05 v3 (outcome + design discipline)"

DEEPSEEK_BASE_URL = "https://api.deepseek.com"

PROMPT_FILES = {
    "router":      "00_candidate_topics_prompt.md",
    "temperature": "01_temperature_prompt.md",
    "wildfire":    "02_wildfire_prompt.md",
    "flood":       "03_flood_prompt.md",
    "cyclone":     "04_cyclone_prompt.md",
    "drought":     "05_drought_prompt.md",
}
VERSION_MARKER = "**Version: v3**"
HAZARD_TOPICS = set(PROMPT_FILES) - {"router"}   # the 5 modules a topic string may validly name

# Pricing for running-cost display only (deepseek-v4-flash, per 1M tokens; verified against
# https://api-docs.deepseek.com/quick_start/pricing on 2026-08-17). Off-peak = 01:00-04:00 and
# 06:00-10:00 UTC excluded; off-peak rates are exactly half of peak.
PRICE_PEAK = {"cache_hit": 0.014, "cache_miss": 0.44, "output": 1.32}   # USD / 1M tokens
PRICE_OFFPEAK = {"cache_hit": 0.007, "cache_miss": 0.22, "output": 0.66}


def log(msg):
    print(msg, flush=True)


def die(msg):
    print("\n[ERROR] " + msg + "\n", flush=True)
    sys.exit(1)


# ---------------------------------------------------------------------------
def load_prompts():
    prompts = {}
    for name, filename in PROMPT_FILES.items():
        path = PROMPTS_DIR / filename
        if not path.exists():
            die(f"Missing prompt file: {path}")
        prompts[name] = path.read_text(encoding="utf-8")
    bad = [n for n, t in prompts.items() if VERSION_MARKER not in t]
    if bad:
        die(f"These prompt files do not look like v3 (missing '{VERSION_MARKER}'): {bad}\n"
            "Refusing to run -- the output would be mislabelled as v3.")
    log(f"Loaded {len(prompts)} v3 prompts from {PROMPTS_DIR}")
    return prompts


def load_corpus():
    if not RECORDS_FILE.exists():
        die(f"Corpus file not found: {RECORDS_FILE}")
    # Default C engine handles this file's large abstract fields fine (verified directly) and
    # is faster than engine="python" -- no need for the python csv module's field_size_limit.
    df = pd.read_csv(RECORDS_FILE, dtype=str, keep_default_na=False)
    df = df.astype(str)
    required_cols = ["dedup_id", "title", "abstract", "year", "journal", "sources"]
    missing = [c for c in required_cols if c not in df.columns]
    if missing:
        die(f"Missing required columns: {missing}. Columns present: {list(df.columns)}")
    if df["dedup_id"].duplicated().any() or (df["dedup_id"] == "").any():
        die("dedup_id column has duplicates or empty values -- it is used as the unique key "
            "for checkpointing and resume; refusing to run until the corpus file is fixed.")
    log(f"Loaded {len(df):,} records from {RECORDS_FILE.name}")
    return df


def load_checkpoint():
    """Returns dict {dedup_id: result_dict} of everything already screened."""
    done = {}
    if CHECKPOINT_FILE.exists():
        with open(CHECKPOINT_FILE, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    rec = json.loads(line)
                    done[rec["dedup_id"]] = rec
                except json.JSONDecodeError:
                    log(f"      WARNING: skipping unparseable checkpoint line: {line[:120]}")
        log(f"      Resuming: {len(done):,} record(s) already screened "
            f"(from {CHECKPOINT_FILE.name}).")
    return done


_checkpoint_lock = asyncio.Lock()


async def append_checkpoint(result):
    async with _checkpoint_lock:
        with open(CHECKPOINT_FILE, "a", encoding="utf-8") as fh:
            fh.write(json.dumps(result, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------------------
def extract_json(text):
    if not text:
        raise ValueError("empty reply")
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    else:
        a, b = t.find("{"), t.rfind("}")
        if a != -1 and b != -1 and b > a:
            t = t[a:b + 1]
    return json.loads(t)


def usage_to_dict(resp):
    u = resp.usage
    reasoning = 0
    try:
        reasoning = getattr(u.completion_tokens_details, "reasoning_tokens", 0) or 0
    except Exception:
        pass
    cached = 0
    try:
        cached = getattr(u.prompt_tokens_details, "cached_tokens", 0) or 0
    except Exception:
        pass
    return {
        "prompt_tokens": getattr(u, "prompt_tokens", 0) or 0,
        "completion_tokens": getattr(u, "completion_tokens", 0) or 0,
        "reasoning_tokens": reasoning,
        "cached_tokens": cached,
    }


async def call_model_async(client, system_prompt, record):
    # deepseek-v4-flash spends part of max_tokens on hidden reasoning before writing the JSON
    # answer. The 300-record pilot found ~15% of calls truncated at max_tokens=800 and one
    # record needed 6000 even after raising the default to 3000 (see this script's docstring
    # and pilot_screening_v3_router5category_300/README.md). Retrying with the SAME budget on
    # a truncated/empty reply just reproduces the same truncation -- so each retry after the
    # first doubles the budget, capped at MAX_TOKENS_CAP, rather than repeating it unchanged.
    user_text = ("Here is one record to screen. Use ONLY its title and abstract.\n\n"
                 + json.dumps(record, ensure_ascii=False)
                 + "\n\nReturn exactly one JSON object as specified. Output JSON only.")
    last = None
    for attempt in range(4):
        budget = min(MAX_TOKENS_CAP, MAX_TOKENS * (2 ** attempt))
        try:
            resp = await client.chat.completions.create(
                model=MODEL, max_tokens=budget, temperature=TEMPERATURE,
                reasoning_effort=REASONING_EFFORT,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_text}])
            content = resp.choices[0].message.content
            usage = usage_to_dict(resp)
            if not content:
                raise ValueError(f"empty content (finish_reason={resp.choices[0].finish_reason}, "
                                 f"max_tokens={budget})")
            return extract_json(content), usage
        except Exception as e:
            last = e
            await asyncio.sleep(2 * (attempt + 1))
    return {"_error": str(last)}, {"prompt_tokens": 0, "completion_tokens": 0,
                                    "reasoning_tokens": 0, "cached_tokens": 0}


def add_usage(a, b):
    return {k: a.get(k, 0) + b.get(k, 0) for k in
            ("prompt_tokens", "completion_tokens", "reasoning_tokens", "cached_tokens")}


async def screen_one_async(client, prompts, dedup_id, row):
    record = {"dedup_id": dedup_id, "title": row["title"], "abstract": row["abstract"]}
    total_usage = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0,
                   "cached_tokens": 0}
    n_calls = 0

    router, u = await call_model_async(client, prompts["router"], record)
    total_usage = add_usage(total_usage, u)
    n_calls += 1

    if "_error" in router:
        result = {"dedup_id": dedup_id, "decision": "ERROR",
                  "reason": "router failed: " + str(router["_error"])[:150], "topics": ""}
    else:
        topics = router.get("candidate_topics", []) or []
        if not topics:
            result = {"dedup_id": dedup_id, "decision": "EXCLUDE",
                      "reason": "No eligible registered hazard identified.", "topics": ""}
        else:
            per, any_inc, inc_rev, any_rev = [], False, False, False
            for tp in topics:
                if tp not in HAZARD_TOPICS:
                    continue
                out, u2 = await call_model_async(client, prompts[tp], record)
                total_usage = add_usage(total_usage, u2)
                n_calls += 1
                if "_error" in out:
                    per.append(f"{tp}: ERROR")
                    any_rev = True
                    continue
                dec = str(out.get("decision", "")).upper()
                rf = bool(out.get("review_flag", False))
                code = out.get("exclusion_code", "")
                why = str(out.get("one_line_reason", ""))[:150]
                per.append("{}: {}{} - {}".format(
                    tp, dec, " [{}]".format(code) if code and code != "NA" else "", why))
                if dec == "INCLUDE":
                    any_inc = True
                    if rf:
                        inc_rev = True
                elif dec == "MAYBE":
                    any_rev = True
                if rf:
                    any_rev = True

            reason = " | ".join(per)
            if any_inc:
                decision = "REVIEW" if inc_rev else "INCLUDE"
            elif any_rev:
                decision = "REVIEW"
            else:
                decision = "EXCLUDE"

            result = {"dedup_id": dedup_id, "decision": decision, "reason": reason,
                      "topics": ", ".join(topics)}

    result.update({
        "title": row["title"], "year": row["year"], "journal": row["journal"],
        "sources": row["sources"], "abstract": row["abstract"],
        "criteria_version": CRITERIA_VERSION, "model_name": MODEL,
        "reasoning_effort": REASONING_EFFORT,
        "screened_at": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
        "n_calls": n_calls, "usage": total_usage,
    })
    await append_checkpoint(result)
    return result


# ---------------------------------------------------------------------------
def estimate_cost(usage_totals):
    """Rough running-cost display; actual billing depends on the real peak/off-peak split
    of when each call landed, which this function does not track. Reports both bounds."""
    cache_hit = usage_totals["cached_tokens"]
    cache_miss = usage_totals["prompt_tokens"] - usage_totals["cached_tokens"]
    output = usage_totals["completion_tokens"]

    def cost(price):
        return (cache_hit / 1e6 * price["cache_hit"]
                + cache_miss / 1e6 * price["cache_miss"]
                + output / 1e6 * price["output"])

    return cost(PRICE_OFFPEAK), cost(PRICE_PEAK)


async def run_screening(df, prompts, todo_ids, limit):
    api_key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if not api_key:
        die("DEEPSEEK_API_KEY is not set in the environment.")
    client = AsyncOpenAI(api_key=api_key, base_url=DEEPSEEK_BASE_URL)

    by_id = df.set_index("dedup_id")
    todo_ids = [d for d in todo_ids if d in by_id.index]
    if limit:
        todo_ids = todo_ids[:limit]
        log(f"      --limit {limit} -> screening only {len(todo_ids)} record(s) this run.")

    if not todo_ids:
        log("      Nothing left to screen.")
        await client.close()
        return

    # Bounded worker pool over a queue, rather than materializing all ~131k tasks (and their
    # row lookups) up front: memory now scales with MAX_CONCURRENCY, not with corpus size.
    queue = asyncio.Queue()
    for d in todo_ids:
        queue.put_nowait(d)

    total = len(todo_ids)
    running_usage = {"prompt_tokens": 0, "completion_tokens": 0, "reasoning_tokens": 0,
                      "cached_tokens": 0}
    t0 = time.time()
    n_done = 0
    pbar = tqdm(total=total, desc="Screening full corpus")

    async def worker():
        nonlocal n_done, running_usage
        while True:
            try:
                dedup_id = queue.get_nowait()
            except asyncio.QueueEmpty:
                return
            row = by_id.loc[dedup_id]
            result = await screen_one_async(client, prompts, dedup_id, row)
            running_usage = add_usage(running_usage, result["usage"])
            n_done += 1
            pbar.update(1)
            if n_done % 200 == 0 or n_done == total:
                elapsed = time.time() - t0
                rate = elapsed / n_done
                remaining = rate * (total - n_done)
                off, peak = estimate_cost(running_usage)
                log(f"      {n_done:,}/{total:,} done  "
                    f"({elapsed/60:.1f} min elapsed, ~{remaining/60:.1f} min left)  "
                    f"running cost est: ${off:.2f}-${peak:.2f}")

    try:
        await asyncio.gather(*(worker() for _ in range(MAX_CONCURRENCY)))
    finally:
        pbar.close()
        await client.close()


# ---------------------------------------------------------------------------
def finalize(df):
    """Rebuild the xlsx report from whatever the checkpoint has, at any point -- complete
    or partial."""
    done = load_checkpoint()
    if not done:
        log("      Checkpoint is empty; nothing to write.")
        return

    by_id = df.set_index("dedup_id")
    rows_out, usage_rows = [], []
    for did, r in done.items():
        rows_out.append({
            "dedup_id": did,
            "title": r.get("title", ""), "year": r.get("year", ""),
            "journal": r.get("journal", ""), "sources": r.get("sources", ""),
            "abstract": r.get("abstract", ""),
            "candidate_topics": r.get("topics", ""),
            "decision": r.get("decision", ""), "reason": r.get("reason", ""),
            "criteria_version": r.get("criteria_version", CRITERIA_VERSION),
            "model_name": r.get("model_name", MODEL),
            "reasoning_effort": r.get("reasoning_effort", REASONING_EFFORT),
            "screened_at": r.get("screened_at", ""),
            "n_calls": r.get("n_calls", ""),
        })
        u = r.get("usage", {})
        usage_rows.append({"dedup_id": did, **u})

    results_df = pd.DataFrame(rows_out)
    usage_df = pd.DataFrame(usage_rows)
    decision_counts = Counter(results_df["decision"])

    totals = {k: usage_df[k].sum() if k in usage_df else 0 for k in
              ("prompt_tokens", "completion_tokens", "reasoning_tokens", "cached_tokens")}
    off, peak = estimate_cost(totals)

    n_total_corpus = len(df)
    summary_lines = [
        ("Criteria version", CRITERIA_VERSION),
        ("Model", MODEL),
        ("Reasoning effort", REASONING_EFFORT),
        ("Records screened this checkpoint", len(results_df)),
        ("Total records in corpus", n_total_corpus),
        ("Complete", "YES" if len(results_df) >= n_total_corpus else
         f"NO -- {n_total_corpus - len(results_df):,} remaining"),
        ("Records file", str(RECORDS_FILE)),
        ("Finalized at (UTC)", datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")),
        ("", ""),
        ("INCLUDE", decision_counts.get("INCLUDE", 0)),
        ("REVIEW", decision_counts.get("REVIEW", 0)),
        ("EXCLUDE", decision_counts.get("EXCLUDE", 0)),
        ("ERROR", decision_counts.get("ERROR", 0)),
        ("", ""),
        ("Total prompt_tokens", totals["prompt_tokens"]),
        ("Total completion_tokens", totals["completion_tokens"]),
        ("Total reasoning_tokens", totals["reasoning_tokens"]),
        ("Total cached_tokens", totals["cached_tokens"]),
        ("Estimated cost (off-peak)", f"${off:.2f}"),
        ("Estimated cost (peak)", f"${peak:.2f}"),
    ]
    summary_df = pd.DataFrame(summary_lines, columns=["Field", "Value"])

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    # Cheap fallback alongside the xlsx: a plain CSV of just the decisions, in case the xlsx
    # write is slow/fails at full scale or someone just wants to script against the labels.
    csv_path = OUTPUT_XLSX.with_suffix(".csv")
    results_df[["dedup_id", "decision", "candidate_topics", "reason"]].to_csv(csv_path, index=False)

    with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
        results_df.to_excel(writer, sheet_name="screening_results", index=False)
        summary_df.to_excel(writer, sheet_name="run_info", index=False)
        usage_df.to_excel(writer, sheet_name="usage_log", index=False)

        ws = writer.sheets["screening_results"]
        widths = {"A": 12, "B": 60, "C": 8, "D": 30, "E": 14, "F": 60,
                  "G": 20, "H": 12, "I": 80, "J": 40, "K": 16, "L": 22}
        for col, w in widths.items():
            ws.column_dimensions[col].width = w
        ws.freeze_panes = "A2"

    log(f"\n  Wrote {len(results_df):,}/{n_total_corpus:,} screened records to {OUTPUT_XLSX}")
    log(f"  {decision_counts}")
    log(f"  Estimated cost so far: ${off:.2f} (off-peak) - ${peak:.2f} (peak)")


# ---------------------------------------------------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Full-corpus v3 screening (router + 5 modules).")
    p.add_argument("--limit", type=int, default=0,
                   help="screen at most N unscreened records this run (0 = all remaining)")
    p.add_argument("--finalize-only", action="store_true",
                   help="skip screening; just rebuild the xlsx from the current checkpoint")
    return p.parse_args()


def main():
    args = parse_args()
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    log("=" * 72)
    log("  Full-corpus screening -- v3 router + 5-module pipeline on deepseek-v4-flash")
    log("=" * 72)

    df = load_corpus()

    if args.finalize_only:
        finalize(df)
        return

    prompts = load_prompts()
    done = load_checkpoint()
    # ERROR results (router/module calls that exhausted all retries -- e.g. a sustained API
    # outage across the whole in-flight batch) do NOT count as "done": they're excluded here so
    # they're automatically re-screened on the next invocation, rather than silently stranded as
    # unreviewable rows forever. Since append_checkpoint() only ever appends, a later successful
    # re-screen writes a new line for the same dedup_id, and load_checkpoint()'s
    # last-line-wins dict construction picks that up -- the stale ERROR line is superseded, not
    # deleted, so the checkpoint file stays a true append log.
    n_errors = sum(1 for r in done.values() if r.get("decision") == "ERROR")
    resolved = {d for d, r in done.items() if r.get("decision") != "ERROR"}
    todo_ids = [d for d in df["dedup_id"] if d not in resolved]
    log(f"      {len(resolved):,} already screened, {n_errors:,} previously ERRORed "
        f"(will be retried), {len(todo_ids):,} remaining of {len(df):,} total records.")

    asyncio.run(run_screening(df, prompts, todo_ids, args.limit))

    log("\n  Screening pass complete (or --limit reached). Writing/refreshing xlsx report ...")
    finalize(df)


if __name__ == "__main__":
    main()
