"""
Title/abstract screening pilot -- v3 criteria, 300-record random sample, concurrent.

Applies screening_criteria_v3.md (INCLUDE / MAYBE / EXCLUDE, with the v3 design
gate G5 and its `wrong_design` exclusion code) to a random 300-record sample of
merged_deduplicated_records.parquet, using deepseek-v4-flash via DeepSeek's
OpenAI-compatible API, with requests sent concurrently.

Output: screening_v3_pilot_300_results.xlsx
"""

import os
import json
import time
import random
import re
import asyncio
import datetime
from pathlib import Path

import pandas as pd
from openai import AsyncOpenAI
from tqdm.auto import tqdm

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
RECORDS_FILE = "merged_deduplicated_records.parquet"
CRITERIA_MD = "screening_criteria_v3.md"

SAMPLE_SIZE = 300
RANDOM_SEED = 42

MODEL = "deepseek-v4-flash"
TEMPERATURE = 0
MAX_RETRIES = 3
RETRY_BACKOFF_SECONDS = 5
MAX_CONCURRENCY = 15

OUTPUT_XLSX = "screening_v3_pilot_300_results.xlsx"
PROMPT_LOG_TXT = "screening_v3_pilot_300_prompt.txt"

DEEPSEEK_API_KEY = os.environ["DEEPSEEK_API_KEY"]
DEEPSEEK_BASE_URL = "https://api.deepseek.com"

client = AsyncOpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_BASE_URL)

# ---------------------------------------------------------------------------
# Load records and criteria
# ---------------------------------------------------------------------------
records_path = Path(RECORDS_FILE)
df = pd.read_parquet(records_path)
df = df.astype(str)
print(f"Loaded {len(df):,} deduplicated records")
assert len(df) > 0

required_cols = ["dedup_id", "title", "abstract", "year", "journal", "sources"]
missing = [c for c in required_cols if c not in df.columns]
assert not missing, f"Missing required columns: {missing}"

criteria_text = Path(CRITERIA_MD).read_text(encoding="utf-8")
print(f"Criteria document loaded: {len(criteria_text):,} characters")

# ---------------------------------------------------------------------------
# Draw the 300-record sample
# ---------------------------------------------------------------------------
random.seed(RANDOM_SEED)
n = min(SAMPLE_SIZE, len(df))
sample_idx = random.sample(range(len(df)), n)
pilot_df = df.iloc[sample_idx].reset_index(drop=True)
print(f"Pilot sample size: {len(pilot_df)} (seed={RANDOM_SEED})")

# ---------------------------------------------------------------------------
# Prompt template -- v3 schema (INCLUDE / MAYBE / EXCLUDE)
# ---------------------------------------------------------------------------
SYSTEM_PROMPT = (
    "You are conducting title/abstract screening for a systematic literature review. "
    "Apply the supplied criteria's gate sequence, vocabulary, and MAYBE-routing rules "
    "exactly as written. This is a recall-first screen: when the criteria says to route "
    "a case to MAYBE, you must return MAYBE -- do not resolve ambiguity yourself by "
    "picking INCLUDE or EXCLUDE. Return only valid JSON."
)

USER_PROMPT_TEMPLATE = """You are conducting title/abstract screening for a literature review.
Apply the APPROVED SCREENING CRITERIA below exactly as written, including its gate sequence
(G1-G5), vocabulary (X hazards, Y outcomes, Z design cues), and its MAYBE-routing rules.
This is a recall-first screen -- MAYBE is a legitimate and expected outcome for a large
share of records, not a fallback to avoid. Follow the criteria's own instructions for when
to EXCLUDE (only when clearly true, with the matching exclusion_code) versus when to route
to MAYBE (whenever there is genuine ambiguity on hazard, outcome, empirical-study status, or
design). Do not invent information not present in the title or abstract.

APPROVED CRITERIA:
{criteria}

RECORD:
dedup_id: {dedup_id}
title: {title}
abstract: {abstract}
year: {year}
journal: {journal}
sources: {sources}

Return exactly one JSON object with these fields and nothing else:
{{
  "dedup_id": "...",
  "decision": "INCLUDE|MAYBE|EXCLUDE",
  "confidence": 0.0,
  "exposure_or_intervention_tag": "temperature|wildfire|flood|cyclone|drought|multiple|unclear|none",
  "outcome_tag": "common_mental_disorder|severe_outcome|service_utilisation|subjective_wellbeing|climate_psychological|multiple|unclear|none",
  "human_empirical_signal": "yes|no|unclear",
  "one_line_reason": "...",
  "exclusion_code": "NA|not_human_empirical|wrong_exposure|wrong_outcome|non_original|animal_or_lab_only|wrong_design",
  "notes_for_human_review": "..."
}}"""


def build_user_prompt(row) -> str:
    return USER_PROMPT_TEMPLATE.format(
        criteria=criteria_text,
        dedup_id=row["dedup_id"],
        title=row["title"],
        abstract=row["abstract"] if row["abstract"] else "[no abstract available]",
        year=row["year"],
        journal=row["journal"],
        sources=row["sources"],
    )


example_prompt = build_user_prompt(pilot_df.iloc[0])
Path(PROMPT_LOG_TXT).write_text(
    "SYSTEM PROMPT:\n" + SYSTEM_PROMPT + "\n\n---\n\nEXAMPLE USER PROMPT (first pilot record):\n\n" + example_prompt,
    encoding="utf-8",
)
print(f"Saved example prompt to {PROMPT_LOG_TXT}")
print(f"Approx. prompt length for one call: {len(example_prompt):,} characters (~{len(example_prompt)//4:,} tokens)")

# ---------------------------------------------------------------------------
# Concurrent screening
# ---------------------------------------------------------------------------
REQUIRED_FIELDS = [
    "dedup_id", "decision", "confidence", "exposure_or_intervention_tag",
    "outcome_tag", "human_empirical_signal", "one_line_reason",
    "exclusion_code", "notes_for_human_review",
]
VALID_DECISIONS = {"INCLUDE", "MAYBE", "EXCLUDE"}
VALID_EXCLUSION_CODES = {
    "NA", "not_human_empirical", "wrong_exposure", "wrong_outcome",
    "non_original", "animal_or_lab_only", "wrong_design",
}


def extract_json(raw_text: str):
    raw_text = raw_text.strip()
    raw_text = re.sub(r"^```(?:json)?\s*", "", raw_text)
    raw_text = re.sub(r"\s*```$", "", raw_text)
    match = re.search(r"\{.*\}", raw_text, re.DOTALL)
    if not match:
        raise ValueError("No JSON object found in response")
    return json.loads(match.group(0))


def validate_decision(d: dict) -> list:
    problems = []
    for f in REQUIRED_FIELDS:
        if f not in d:
            problems.append(f"missing field: {f}")
    if d.get("decision") not in VALID_DECISIONS:
        problems.append(f"invalid decision: {d.get('decision')!r}")
    if d.get("exclusion_code") not in VALID_EXCLUSION_CODES:
        problems.append(f"invalid exclusion_code: {d.get('exclusion_code')!r}")
    if d.get("decision") in ("INCLUDE", "MAYBE") and d.get("exclusion_code") != "NA":
        problems.append("exclusion_code must be NA when decision is INCLUDE or MAYBE")
    conf = d.get("confidence")
    if not isinstance(conf, (int, float)) or not (0.0 <= float(conf) <= 1.0):
        problems.append(f"invalid confidence: {conf!r}")
    return problems


sem = asyncio.Semaphore(MAX_CONCURRENCY)


async def screen_one_async(row) -> dict:
    user_prompt = build_user_prompt(row)
    last_error = None

    async with sem:
        for attempt in range(1, MAX_RETRIES + 1):
            try:
                response = await client.chat.completions.create(
                    model=MODEL,
                    temperature=TEMPERATURE,
                    messages=[
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": user_prompt},
                    ],
                )
                raw_text = response.choices[0].message.content
                parsed = extract_json(raw_text)
                problems = validate_decision(parsed)

                if problems:
                    last_error = "; ".join(problems)
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)
                    continue

                parsed["dedup_id"] = row["dedup_id"]
                parsed["_status"] = "ok"
                parsed["_attempts"] = attempt
                parsed["_raw_response"] = raw_text
                return parsed

            except Exception as e:
                last_error = str(e)
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(RETRY_BACKOFF_SECONDS * attempt)
                continue

    return {
        "dedup_id": row["dedup_id"],
        "decision": "MALFORMED",
        "confidence": None,
        "exposure_or_intervention_tag": None,
        "outcome_tag": None,
        "human_empirical_signal": None,
        "one_line_reason": None,
        "exclusion_code": None,
        "notes_for_human_review": f"AUTO-FLAG: failed after {MAX_RETRIES} attempts. Last error: {last_error}",
        "_status": "failed",
        "_attempts": MAX_RETRIES,
        "_raw_response": None,
    }


async def run_pilot():
    tasks = [screen_one_async(row) for _, row in pilot_df.iterrows()]
    results = []
    for coro in tqdm(asyncio.as_completed(tasks), total=len(tasks), desc="Screening (concurrent)"):
        result = await coro
        results.append(result)
    return results


start_time = time.time()
results = asyncio.run(run_pilot())
elapsed = time.time() - start_time

n_ok = sum(1 for r in results if r["_status"] == "ok")
n_failed = sum(1 for r in results if r["_status"] == "failed")
n_needed_retry = sum(1 for r in results if r["_status"] == "ok" and r["_attempts"] > 1)

print(f"Completed {len(results)} records in {elapsed:.1f}s ({elapsed/len(results):.2f}s/record average)")
print(f"OK: {n_ok}, failed/malformed after {MAX_RETRIES} retries: {n_failed}")
print(f"Needed at least one retry: {n_needed_retry} ({n_needed_retry/len(results)*100:.0f}%)")

# ---------------------------------------------------------------------------
# Assemble results sheet
# ---------------------------------------------------------------------------
CRITERIA_VERSION = Path(CRITERIA_MD).name
SCREENED_AT = datetime.datetime.utcnow().isoformat(timespec="seconds") + "Z"

records_by_id = pilot_df.set_index("dedup_id")

rows_out = []
for r in results:
    did = r["dedup_id"]
    row = records_by_id.loc[did] if did in records_by_id.index else None
    rows_out.append({
        "dedup_id": did,
        "title": row["title"] if row is not None else None,
        "year": row["year"] if row is not None else None,
        "journal": row["journal"] if row is not None else None,
        "sources": row["sources"] if row is not None else None,
        "abstract": row["abstract"] if row is not None else None,
        "decision": r["decision"],
        "confidence": r["confidence"],
        "exposure_or_intervention_tag": r["exposure_or_intervention_tag"],
        "outcome_tag": r["outcome_tag"],
        "human_empirical_signal": r["human_empirical_signal"],
        "one_line_reason": r["one_line_reason"],
        "exclusion_code": r["exclusion_code"],
        "notes_for_human_review": r["notes_for_human_review"],
        "attempts_needed": r.get("_attempts"),
        "co_investigator_agree_y_n": "",
        "co_investigator_comments": "",
    })

results_df = pd.DataFrame(rows_out)

decision_counts = results_df["decision"].value_counts()
summary_lines = [
    ("Criteria version", CRITERIA_VERSION),
    ("Model", MODEL),
    ("Sample size", len(results_df)),
    ("Random seed", RANDOM_SEED),
    ("Records file", RECORDS_FILE),
    ("Screened at (UTC)", SCREENED_AT),
    ("", ""),
    ("INCLUDE", int(decision_counts.get("INCLUDE", 0))),
    ("MAYBE", int(decision_counts.get("MAYBE", 0))),
    ("EXCLUDE", int(decision_counts.get("EXCLUDE", 0))),
    ("MALFORMED", int(decision_counts.get("MALFORMED", 0))),
]
summary_df = pd.DataFrame(summary_lines, columns=["Field", "Value"])

with pd.ExcelWriter(OUTPUT_XLSX, engine="openpyxl") as writer:
    results_df.to_excel(writer, sheet_name="screening_results", index=False)
    summary_df.to_excel(writer, sheet_name="run_info", index=False)

    ws = writer.sheets["screening_results"]
    widths = {
        "A": 12, "B": 60, "C": 8, "D": 30, "E": 14, "F": 60,
        "G": 12, "H": 12, "I": 26, "J": 20, "K": 16, "L": 55,
        "M": 20, "N": 55, "O": 14, "P": 22, "Q": 30,
    }
    for col, w in widths.items():
        ws.column_dimensions[col].width = w
    ws.freeze_panes = "A2"

print(f"\nSaved {len(results_df)} rows to {OUTPUT_XLSX}")
print(decision_counts)
