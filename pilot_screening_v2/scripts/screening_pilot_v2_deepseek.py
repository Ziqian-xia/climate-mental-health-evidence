#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Climate hazards x Mental health -- Title/Abstract screening: OpenAI (GPT) pilot test
====================================================================================
FIXED VERSION. Two changes vs the previous script:
  (A) Aggregation now follows the repo workflow exactly: the router's
      `needs_human_topic_review` flag only sends a record to human review when
      NO candidate topic was found. When topics ARE found, the final decision
      comes from the topic-specific prompts (INCLUDE / EXCLUDE / review_flag).
      -> This fixes the inflated HUMAN_REVIEW count.
  (B) You can now point it at your LOCAL prompt files (see LOCAL_PROMPT_DIR),
      and it prints the size of every loaded prompt so you can confirm it used them.

Workflow (unchanged, per LLM_AGENT_README):
  1. router -> candidate_topics
  2. run each matched topic prompt
  3. if candidate_topics empty AND needs_human_topic_review -> HUMAN_REVIEW (no topic)
     if candidate_topics empty AND not flagged            -> EXCLUDE (no eligible topic)
  4. any topic prompt INCLUDE            -> INCLUDE
  5. else any topic review_flag == true  -> HUMAN_REVIEW (topic uncertain)
  6. else all topic prompts EXCLUDE      -> EXCLUDE

====================================================================================
"""

import os
import sys
import re
import json
import time
import urllib.request

# ------------------------- Editable configuration -------------------------
SAMPLE_SIZE = 100            # How many records to test.
RANDOM_SEED = 42             # Same seed -> same sample (so results are comparable).
VERSION_TAG = "v2_deepseek"   # version tag; written into the output filenames (v2 prompts on DeepSeek)

# v3: instead of random sampling, screen the SAME fixed record set as Jacob's pilot
# (pilot_screening_v1/sampled_dedup_ids.csv on GitHub main). This makes v1/v2/v3 directly
# comparable at n=1000. Set USE_FIXED_SAMPLE = False to fall back to random sampling.
USE_FIXED_SAMPLE = True
SAMPLED_IDS_URL = "https://raw.githubusercontent.com/Ziqian-xia/climate-mental-health-evidence/main/pilot_screening_v1/sampled_dedup_ids.csv"

# provenance recorded into every output row (mirrors Jacob's results columns)
CRITERIA_VERSION = "per-topic prompt set 00-05 v2 (outcome discipline)"

# DeepSeek uses an OpenAI-compatible endpoint; only the base_url and key differ.
BASE_URL = "https://api.deepseek.com"
MODEL = "deepseek-v4-flash"  # DeepSeek model (same model Jacob used), via OpenAI-compatible API.
MAX_TOKENS = 800
PAUSE_SEC = 0.2

# Leave empty ("") to auto-download prompts from GitHub (recommended, always current).
# To use YOUR OWN local copies instead, set this to the folder that contains
# 00_candidate_topics_prompt.md ... 05_drought_prompt.md, e.g.:
#   LOCAL_PROMPT_DIR = "/Users/huangziqian/Desktop/title_abstract_screening"
LOCAL_PROMPT_DIR = ""

# How to handle records where the router found NO hazard topic.
#   "exclude_unless_ambiguous" (RECOMMENDED): exclude them, UNLESS the title/abstract
#        contains an unnamed-disaster cue (e.g. "natural disaster"), then send to human.
#        -> This stops the router's over-eager "needs_human" flag from dumping every
#           clearly-irrelevant record into human review.
#   "trust_model": original behavior -- do whatever the router's needs_human flag says.
#   "always_exclude": exclude ALL no-topic records, no human-review carve-out.
# NOTE: this changes what the AI auto-drops, so confirm the choice with your advisor.
NO_TOPIC_POLICY = "exclude_unless_ambiguous"

# LAYER 1: for no-topic records, only send to human review if the router also detected
# a mental-health signal. A record with NO hazard AND NO mental-health signal cannot be
# a hazard x mental-health study, so excluding it carries zero recall risk. This removes
# pure noise (tree-ring/forestry, urban-energy engineering, etc.) from the review pile.
REQUIRE_MH_FOR_REVIEW = True

# Unnamed / generic disaster cues: a no-topic record that mentions one of these is
# genuinely ambiguous (the specific hazard is resolvable at full text), so keep it for
# human review instead of excluding. Matches screening_criteria_v1.md boundary rules.
AMBIGUITY_CUES = [
    "natural disaster", "natural hazard", "extreme weather", "weather extreme",
    "climate change", "climate event", "climate disaster", "climate-related disaster",
    "weather disaster", "weather-related disaster", "disaster-affected", "disaster exposure",
    "multiple hazards", "compound disaster", "compound hazard", "environmental disaster",
]
# Prepend docs/screening_criteria_v1.md to every prompt as shared REFERENCE context
# (full X/Y vocabulary, the G1-G4 gates, and all the boundary cases). This grounds the
# terse per-topic prompts in the authoritative criteria. Set to False to compare without it.
USE_SHARED_CRITERIA = False
CRITERIA_FILE = "docs/screening_criteria_v1.md"
# --------------------------------------------------------------------------

# Prices (USD per million tokens) for gpt-4o-mini. Update if you change MODEL.
PRICE_INPUT_PER_M = 0.28
PRICE_OUTPUT_PER_M = 0.42

REPO_RAW = "https://raw.githubusercontent.com/Ziqian-xia/climate-mental-health-evidence/main"
DATA_URL = f"{REPO_RAW}/data/merged_deduplicated_records.csv.gz"
DATA_LOCAL = "merged_deduplicated_records.csv.gz"

PROMPT_FILES = {
    "router":      "prompts_v2/title_abstract_screening/00_candidate_topics_prompt.md",
    "temperature": "prompts_v2/title_abstract_screening/01_temperature_prompt.md",
    "wildfire":    "prompts_v2/title_abstract_screening/02_wildfire_prompt.md",
    "flood":       "prompts_v2/title_abstract_screening/03_flood_prompt.md",
    "cyclone":     "prompts_v2/title_abstract_screening/04_cyclone_prompt.md",
    "drought":     "prompts_v2/title_abstract_screening/05_drought_prompt.md",
}


def log(msg):
    print(msg, flush=True)


def die(msg):
    print("\n[ERROR] " + msg + "\n", flush=True)
    sys.exit(1)


try:
    import pandas as pd
except ImportError:
    die("Missing pandas. Run: pip3 install pandas openai")

try:
    from openai import OpenAI
except ImportError:
    die("Missing openai. Run: pip3 install pandas openai")


def get_api_key():
    import getpass
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    log("\nNo DEEPSEEK_API_KEY detected.")
    log("Paste your DeepSeek API key (from platform.deepseek.com; starts with sk-; it will NOT be shown as you type):")
    key = getpass.getpass("API key: ").strip()
    if not key:
        die("No API key entered; cannot continue.")
    return key


def download_if_needed(url, local_path, label):
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        log(f"  Already present, skipping download: {local_path}")
        return
    log(f"  Downloading {label} ... (first time is slow, please wait)")
    try:
        urllib.request.urlretrieve(url, local_path)
    except Exception as e:
        die(f"Download failed: {url}\nReason: {e}")
    log(f"  Download complete: {local_path}")


def fetch_text(url):
    try:
        with urllib.request.urlopen(url) as r:
            return r.read().decode("utf-8")
    except Exception as e:
        die(f"Failed to read: {url}\nReason: {e}")


def load_prompts():
    prompts = {}
    if LOCAL_PROMPT_DIR:
        log(f"      Using LOCAL prompts from: {LOCAL_PROMPT_DIR}")
        for name, path in PROMPT_FILES.items():
            fpath = os.path.join(LOCAL_PROMPT_DIR, os.path.basename(path))
            if not os.path.exists(fpath):
                die(f"Local prompt not found: {fpath}")
            with open(fpath, encoding="utf-8") as fh:
                prompts[name] = fh.read()
    else:
        log("      Downloading prompts from GitHub (main branch) ...")
        for name, path in PROMPT_FILES.items():
            prompts[name] = fetch_text(f"{REPO_RAW}/{path}")

    # Optionally prepend the shared screening_criteria_v1.md as reference context.
    if USE_SHARED_CRITERIA:
        if LOCAL_PROMPT_DIR:
            cpath = os.path.join(LOCAL_PROMPT_DIR, os.path.basename(CRITERIA_FILE))
            criteria = open(cpath, encoding="utf-8").read() if os.path.exists(cpath) \
                else fetch_text(f"{REPO_RAW}/{CRITERIA_FILE}")
        else:
            criteria = fetch_text(f"{REPO_RAW}/{CRITERIA_FILE}")
        log(f"        loaded shared criteria {len(criteria)} chars (screening_criteria_v1.md)")
        header = (
            "=== REFERENCE SCREENING CRITERIA (background: definitions, X/Y vocabulary, "
            "gates, and boundary cases) ===\n"
            + criteria
            + "\n=== END REFERENCE CRITERIA ===\n\n"
            "The section below is YOUR SPECIFIC TASK for THIS record. Follow its instructions "
            "and its output JSON schema EXACTLY. Where the output format below differs from the "
            "reference criteria above, the format below governs (use INCLUDE/EXCLUDE + review_flag, "
            "not MAYBE).\n\n"
        )
        for name in prompts:
            prompts[name] = header + prompts[name]

    # Print sizes so you can confirm real content was loaded.
    for name in PROMPT_FILES:
        log(f"        loaded {name:<12} {len(prompts[name])} chars")
    return prompts


def extract_json(text):
    if text is None:
        raise ValueError("empty reply")
    t = text.strip()
    m = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", t, re.S)
    if m:
        t = m.group(1)
    else:
        start, end = t.find("{"), t.rfind("}")
        if start != -1 and end != -1 and end > start:
            t = t[start:end + 1]
    return json.loads(t)


def call_model(client, system_prompt, record):
    user_text = (
        "Here is one record to screen. Use ONLY its title and abstract.\n\n"
        + json.dumps(record, ensure_ascii=False)
        + "\n\nReturn exactly one JSON object as specified in the instructions. "
        "Output JSON only, with no extra text."
    )
    last_err = None
    for attempt in range(3):
        try:
            resp = client.chat.completions.create(
                model=MODEL,
                max_tokens=MAX_TOKENS,
                temperature=0,
                response_format={"type": "json_object"},
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_text},
                ],
            )
            text = resp.choices[0].message.content
            data = extract_json(text)
            usage = resp.usage
            return data, usage.prompt_tokens, usage.completion_tokens
        except Exception as e:
            last_err = e
            time.sleep(1.5 * (attempt + 1))
    return {"_error": str(last_err)}, 0, 0


def screen_one(client, prompts, record, usage_counter):
    dedup_id = record.get("dedup_id", "")

    # Step 1: router
    router_out, ti, to = call_model(client, prompts["router"], record)
    usage_counter["in"] += ti
    usage_counter["out"] += to

    if "_error" in router_out:
        return {
            "dedup_id": dedup_id, "candidate_topics": "", "mental_health_signal": "",
            "per_topic": "{}", "final_decision": "ERROR",
            "one_line_reason": "router call failed: " + router_out["_error"][:120],
        }

    topics = router_out.get("candidate_topics", []) or []
    mh_signal = router_out.get("mental_health_signal", "")
    needs_human = bool(router_out.get("needs_human_topic_review", False))

    # No candidate topic -> decide by NO_TOPIC_POLICY instead of blindly trusting
    # the router's (unreliable on weak models) needs_human flag.
    if not topics:
        text = (record.get("title", "") + " " + record.get("abstract", "")).lower()
        has_cue = any(cue in text for cue in AMBIGUITY_CUES)
        # LAYER 1 tightening: a no-topic record with NO mental-health signal at all
        # cannot be a hazard x mental-health study, so never send it to human review.
        # (mh_signal is "yes" | "no" | "unclear" from the router.)
        mh_present = str(mh_signal).strip().lower() != "no"   # True for yes/unclear/empty
        if NO_TOPIC_POLICY == "always_exclude":
            route_human = False
        elif NO_TOPIC_POLICY == "trust_model":
            route_human = needs_human and (mh_present if REQUIRE_MH_FOR_REVIEW else True)
        else:  # "exclude_unless_ambiguous" (recommended)
            route_human = has_cue and (mh_present if REQUIRE_MH_FOR_REVIEW else True)
        if route_human:
            final = "HUMAN_REVIEW (no topic)"
            reason = router_out.get("one_line_reason", "unnamed/generic hazard cue + MH signal; human review")
        else:
            final = "EXCLUDE (no eligible topic)"
            reason = router_out.get("one_line_reason", "no eligible hazard topic")
        return {
            "dedup_id": dedup_id, "candidate_topics": "", "mental_health_signal": mh_signal,
            "per_topic": "{}", "final_decision": final, "one_line_reason": reason,
        }

    # Step 2: run each matched topic prompt
    per_topic = {}
    any_include = False
    include_needs_review = False
    any_topic_review = False
    for tp in topics:
        if tp not in prompts:
            continue
        out, ti, to = call_model(client, prompts[tp], record)
        usage_counter["in"] += ti
        usage_counter["out"] += to
        if "_error" in out:
            per_topic[tp] = {"decision": "ERROR"}
            any_topic_review = True
            continue
        decision = str(out.get("decision", "")).upper()
        review_flag = bool(out.get("review_flag", False))
        per_topic[tp] = {"decision": decision, "review_flag": review_flag,
                         "reason": out.get("one_line_reason", "")}
        if decision == "INCLUDE":
            any_include = True
            if review_flag:
                include_needs_review = True
        elif decision == "MAYBE":
            # criteria_v1 uses MAYBE; treat it as "route to human review"
            any_topic_review = True
        if review_flag:
            any_topic_review = True

    # Step 3: aggregate  (router needs_human is intentionally NOT used here)
    if any_include:
        final = "INCLUDE (needs review)" if include_needs_review else "INCLUDE"
    elif any_topic_review:
        final = "HUMAN_REVIEW (topic uncertain)"
    else:
        final = "EXCLUDE"

    reasons = [f"{k}:{v.get('decision', '')}" for k, v in per_topic.items()]
    return {
        "dedup_id": dedup_id, "candidate_topics": "; ".join(topics),
        "mental_health_signal": mh_signal,
        "per_topic": json.dumps(per_topic, ensure_ascii=False),
        "final_decision": final, "one_line_reason": " | ".join(reasons),
    }



def verify_api_key(client):
    """Verify the API key with a minimal request before doing any work; exit immediately if it is invalid, so no time is wasted on downloading/screening."""
    log("  Verifying API key ...")
    try:
        client.chat.completions.create(
            model=MODEL,
            max_tokens=1,
            messages=[{"role": "user", "content": "ping"}],
        )
        log("  API key is valid.\n")
    except Exception as e:
        msg = str(e)
        if "401" in msg or "invalid_api_key" in msg or "Incorrect API key" in msg or "Unauthorized" in msg:
            die("API key is invalid or unauthorized. Check that the sk-... you pasted is correct and has credit.\nOriginal error: " + msg[:200])
        elif "429" in msg or "insufficient_quota" in msg or "quota" in msg:
            die("The API key works but has insufficient quota/credit. Add credit at platform.deepseek.com -> Billing.\nOriginal error: " + msg[:200])
        else:
            die("API call failed (possibly a network or model-name issue): " + msg[:200])


def main():
    log("=" * 64)
    log(" Climate hazards x Mental health -- T/A screening: GPT pilot (v3 = v2 prompts on Jacob's fixed 1000-record sample)")
    log("=" * 64)

    api_key = get_api_key()
    client = OpenAI(api_key=api_key, base_url=BASE_URL)
    verify_api_key(client)

    log("\n[1/4] Preparing the deduplicated records file ...")
    download_if_needed(DATA_URL, DATA_LOCAL, "deduplicated records (~80MB)")
    log("      Reading and sampling ...")
    try:
        df = pd.read_csv(DATA_LOCAL, compression="gzip")
    except Exception as e:
        die(f"Failed to read CSV: {e}")
    total = len(df)
    if USE_FIXED_SAMPLE:
        log("      Loading fixed sample id list (Jacob's pilot) ...")
        ids = pd.read_csv(SAMPLED_IDS_URL)["dedup_id"].astype(str).tolist()
        sample = df[df["dedup_id"].astype(str).isin(ids)].copy()
        # keep the same order as the id list
        order = {d: i for i, d in enumerate(ids)}
        sample = sample.sort_values(by="dedup_id", key=lambda c: c.astype(str).map(order)).reset_index(drop=True)
        n = len(sample)
        missing = len(ids) - n
        log(f"      {total} records total; using FIXED sample of {n} ids"
            + (f" ({missing} ids not found in corpus)" if missing else "") + ".")
    else:
        n = min(SAMPLE_SIZE, total)
        sample = df.sample(n=n, random_state=RANDOM_SEED).reset_index(drop=True)
        log(f"      {total} records total; randomly sampled {n} (seed={RANDOM_SEED}).")

    log("\n[2/4] Loading the 6 prompts (router + 5 hazard topics) ...")
    prompts = load_prompts()

    log(f"\n[3/4] Screening {n} records (each calls the model several times) ...")
    usage_counter = {"in": 0, "out": 0}
    results = []
    t0 = time.time()
    for i, row in sample.iterrows():
        record = {
            "dedup_id": str(row.get("dedup_id", "")),
            "title": "" if pd.isna(row.get("title")) else str(row.get("title")),
            "abstract": "" if pd.isna(row.get("abstract")) else str(row.get("abstract")),
            "year": "" if pd.isna(row.get("year")) else str(row.get("year")),
            "journal": "" if pd.isna(row.get("journal")) else str(row.get("journal")),
        }
        res = screen_one(client, prompts, record, usage_counter)
        res["title"] = record["title"][:160]
        res["model_name"] = MODEL
        res["criteria_version"] = CRITERIA_VERSION
        res["screened_at"] = time.strftime("%Y-%m-%dT%H:%M:%S", time.gmtime())
        results.append(res)
        if (i + 1) % 5 == 0 or (i + 1) == n:
            log(f"      Done {i + 1}/{n} ...")
        time.sleep(PAUSE_SEC)
    elapsed = time.time() - t0

    log("\n[4/4] Saving results and summarizing ...")
    out_df = pd.DataFrame(results)[[
        "dedup_id", "title", "candidate_topics", "mental_health_signal",
        "final_decision", "one_line_reason", "per_topic",
        "model_name", "criteria_version", "screened_at",
    ]]
    tag = (f"fixed{n}" if USE_FIXED_SAMPLE else f"seed{RANDOM_SEED}")
    out_df.to_csv(f"screening_pilot_results_{tag}_{VERSION_TAG}.csv", index=False, encoding="utf-8-sig")
    review_mask = out_df["final_decision"].str.contains("REVIEW|INCLUDE|ERROR", case=False, na=False)
    out_df[review_mask].to_csv(f"screening_pilot_to_review_{tag}_{VERSION_TAG}.csv", index=False, encoding="utf-8-sig")

    cost = (usage_counter["in"] / 1e6) * PRICE_INPUT_PER_M + \
           (usage_counter["out"] / 1e6) * PRICE_OUTPUT_PER_M

    def bucket(d):
        d = d.upper()
        if d.startswith("INCLUDE"):
            return "INCLUDE (keep)"
        if "REVIEW" in d:
            return "HUMAN_REVIEW (to human)"
        if d.startswith("EXCLUDE"):
            return "EXCLUDE (drop)"
        return "ERROR (failed)"

    out_df["bucket"] = out_df["final_decision"].map(bucket)

    topic_counts = {t: 0 for t in ["temperature", "wildfire", "flood", "cyclone", "drought"]}
    for ct in out_df["candidate_topics"].fillna(""):
        for t in topic_counts:
            if t in ct:
                topic_counts[t] += 1

    log("\n" + "=" * 64)
    log(" Summary")
    log("=" * 64)
    log(f"  Model: {MODEL}   |   No-topic policy: {NO_TOPIC_POLICY}")
    log(f"  Records tested: {n}   |   Time: {elapsed:.0f} s")
    log(f"  Estimated cost: ~${cost:.3f}  "
        f"(input {usage_counter['in']:,} / output {usage_counter['out']:,} tokens)")

    log("\n  Coarse buckets:")
    for k, v in out_df["bucket"].value_counts().items():
        log(f"    {k:<24} {v}")

    log("\n  Detailed reasons (this reveals WHAT drives human review):")
    for k, v in out_df["final_decision"].value_counts().items():
        log(f"    {k:<30} {v}")

    log("\n  Records matching each hazard topic (a record can match several):")
    for t, c in topic_counts.items():
        log(f"    {t:<14} {c}")

    log(f"\n  Output files: screening_pilot_results_{tag}_{VERSION_TAG}.csv , screening_pilot_to_review_{tag}_{VERSION_TAG}.csv")
    log("=" * 64 + "\n")


if __name__ == "__main__":
    main()
