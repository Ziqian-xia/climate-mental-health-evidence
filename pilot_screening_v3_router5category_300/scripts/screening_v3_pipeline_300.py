"""
Title/abstract screening pilot -- v3 pipeline (router + 5 hazard modules), 300-record
random sample, concurrent across records.

This mirrors the router+module screening logic in prompts_v3/screen_excel_v3_deepseek.py
(same prompts, same aggregation rule: any topic INCLUDE -> INCLUDE, any MAYBE/review_flag
-> REVIEW, else EXCLUDE), but instead of reading the fixed reviewer packet, it draws a fresh
random 300-record sample from merged_deduplicated_records.parquet, the same way the earlier
single-prompt pilot did.

Output: screening_v3_pipeline_300_results.xlsx
"""

import os
import json
import time
import random
import re
import asyncio
import datetime
from pathlib import Path
from collections import Counter

import pandas as pd
from openai import AsyncOpenAI
from tqdm.auto import tqdm

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RECORDS_FILE = "merged_deduplicated_records.parquet"
PROMPTS_DIR = "/Users/jacobchen/climate-mental-health-evidence/prompts_v3"

SAMPLE_SIZE = 300
RANDOM_SEED = 42   # same 300 records as the earlier single-prompt pilot -- only the pipeline changes

MODEL = "deepseek-v4-flash"
MAX_CONCURRENCY = 10   # each record makes 1 (router) + up to 5 (topic) sequential calls
PAUSE_SEC = 0.0

OUTPUT_XLSX = "screening_v3_pipeline_300_results.xlsx"
CRITERIA_VERSION = "per-topic prompt set 00-05 v3 (outcome + design discipline)"

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

PROMPT_FILES = {
    "router":      "00_candidate_topics_prompt.md",
    "temperature": "01_temperature_prompt.md",
    "wildfire":    "02_wildfire_prompt.md",
    "flood":       "03_flood_prompt.md",
    "cyclone":     "04_cyclone_prompt.md",
    "drought":     "05_drought_prompt.md",
}
VERSION_MARKER = "**Version: v3**"

# ---------------------------------------------------------------------------
# Load prompts
# ---------------------------------------------------------------------------
prompts_dir = Path(PROMPTS_DIR)
prompts = {}
for name, filename in PROMPT_FILES.items():
    text = (prompts_dir / filename).read_text(encoding="utf-8")
    prompts[name] = text
bad = [n for n, t in prompts.items() if VERSION_MARKER not in t]
assert not bad, f"These prompt files do not look like v3 (missing '{VERSION_MARKER}'): {bad}"
print(f"Loaded {len(prompts)} v3 prompts from {prompts_dir.resolve()}")

# ---------------------------------------------------------------------------
# Load records and draw the sample
# ---------------------------------------------------------------------------
df = pd.read_parquet(RECORDS_FILE)
df = df.astype(str)
print(f"Loaded {len(df):,} deduplicated records")

required_cols = ["dedup_id", "title", "abstract", "year", "journal", "sources"]
missing = [c for c in required_cols if c not in df.columns]
assert not missing, f"Missing required columns: {missing}"

random.seed(RANDOM_SEED)
n = min(SAMPLE_SIZE, len(df))
sample_idx = random.sample(range(len(df)), n)
pilot_df = df.iloc[sample_idx].reset_index(drop=True)
print(f"Pilot sample size: {len(pilot_df)} (seed={RANDOM_SEED})")

# ---------------------------------------------------------------------------
# Model calls -- router then per-topic modules, same logic as screen_excel_v3_deepseek.py
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


async def call_model_async(system_prompt, record):
    # deepseek-v4-flash spends part of max_tokens on internal reasoning before writing the
    # JSON; 800 was too tight and produced empty/truncated content on ~15% of calls.
    user_text = ("Here is one record to screen. Use ONLY its title and abstract.\n\n"
                 + json.dumps(record, ensure_ascii=False)
                 + "\n\nReturn exactly one JSON object as specified. Output JSON only.")
    last = None
    for attempt in range(4):
        try:
            resp = await client.chat.completions.create(
                model=MODEL, max_tokens=3000, temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_text}])
            content = resp.choices[0].message.content
            if not content:
                raise ValueError(f"empty content (finish_reason={resp.choices[0].finish_reason})")
            return extract_json(content)
        except Exception as e:
            last = e
            await asyncio.sleep(2 * (attempt + 1))
    return {"_error": str(last)}


sem = asyncio.Semaphore(MAX_CONCURRENCY)


async def screen_one_async(row):
    record = {"dedup_id": row["dedup_id"], "title": row["title"], "abstract": row["abstract"]}

    async with sem:
        router = await call_model_async(prompts["router"], record)
        if "_error" in router:
            return {"dedup_id": row["dedup_id"], "decision": "ERROR",
                    "reason": "router failed: " + str(router["_error"])[:150], "topics": ""}

        topics = router.get("candidate_topics", []) or []
        if not topics:
            return {"dedup_id": row["dedup_id"], "decision": "EXCLUDE",
                    "reason": "No eligible registered hazard identified.", "topics": ""}

        per, any_inc, inc_rev, any_rev = [], False, False, False
        for tp in topics:
            if tp not in prompts:
                continue
            out = await call_model_async(prompts[tp], record)
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

        return {"dedup_id": row["dedup_id"], "decision": decision, "reason": reason,
                "topics": ", ".join(topics)}


async def run_pilot():
    tasks = [screen_one_async(row) for _, row in pilot_df.iterrows()]
    results = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Screening (router+modules)"):
        result = await coro
        results.append(result)
    return results


start_time = time.time()
results = asyncio.run(run_pilot())
elapsed = time.time() - start_time
print(f"Completed {len(results)} records in {elapsed:.1f}s ({elapsed/len(results):.2f}s/record average)")

# ---------------------------------------------------------------------------
# Assemble results sheet
# ---------------------------------------------------------------------------
SCREENED_AT = datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds")

records_by_id = pilot_df.set_index("dedup_id")
results_by_id = {r["dedup_id"]: r for r in results}

rows_out = []
for did, r in results_by_id.items():
    row = records_by_id.loc[did]
    rows_out.append({
        "dedup_id": did,
        "title": row["title"],
        "year": row["year"],
        "journal": row["journal"],
        "sources": row["sources"],
        "abstract": row["abstract"],
        "candidate_topics": r["topics"],
        "decision": r["decision"],
        "reason": r["reason"],
        "criteria_version": CRITERIA_VERSION,
        "model_name": MODEL,
        "screened_at": SCREENED_AT,
        "co_investigator_agree_y_n": "",
        "co_investigator_comments": "",
    })

results_df = pd.DataFrame(rows_out)
decision_counts = Counter(results_df["decision"])

summary_lines = [
    ("Criteria version", CRITERIA_VERSION),
    ("Model", MODEL),
    ("Sample size", len(results_df)),
    ("Random seed", RANDOM_SEED),
    ("Records file", RECORDS_FILE),
    ("Screened at (UTC)", SCREENED_AT),
    ("", ""),
    ("INCLUDE", decision_counts.get("INCLUDE", 0)),
    ("REVIEW", decision_counts.get("REVIEW", 0)),
    ("EXCLUDE", decision_counts.get("EXCLUDE", 0)),
    ("ERROR", decision_counts.get("ERROR", 0)),
]
summary_df = pd.DataFrame(summary_lines, columns=["Field", "Value"])

with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
    results_df.to_excel(writer, sheet_name="screening_results", index=False)
    summary_df.to_excel(writer, sheet_name="run_info", index=False)

    ws = writer.sheets["screening_results"]
    widths = {
        "A": 12, "B": 60, "C": 8, "D": 30, "E": 14, "F": 60,
        "G": 20, "H": 12, "I": 80, "J": 40, "K": 20, "L": 22,
        "M": 22, "N": 30,
    }
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"

print(f"\nSaved {len(results_df)} rows to {OUTPUT_XLSX}")
print(decision_counts)
