#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Screen the reviewer packet (Ziqian / Jacob / Tony sheets) with the v3 prompts on DeepSeek.

Reads title + abstract directly from the Excel file, so no corpus download is needed.
Writes two new columns per sheet - "AI Suggestion (v3)" and "AI Reason (v3)" - into a NEW
Excel file. The existing "Human Decision" and "Audit Notes" columns are never modified.

Records that appear on more than one sheet (pairwise assignment) are screened once and the
same result is written to every row with that dedup_id.

Progress is checkpointed to a JSON file after every record, so if the run is interrupted
(network drop, closed window) you can simply run the script again and it resumes.
"""

import os, sys, re, json, time, getpass

# ------------------------- configuration -------------------------
EXCEL_IN  = r"C:\Users\32367\Desktop\stanford\review_packet_pairwise.xlsx"
EXCEL_OUT = r"C:\Users\32367\Desktop\stanford\review_packet_pairwise_v3_ai.xlsx"
CHECKPOINT = "screen_v3_progress.json"      # resume file, created next to this script

SHEETS = ["Ziqian", "Jacob", "Tony"]        # sheets to screen

# Local folder holding the six v3 prompt files (00-05). Leave "" to fetch from GitHub instead.
LOCAL_PROMPT_DIR = r"C:\Users\32367\Desktop\stanford\prompts_v3\title_abstract_screening"

REPO_RAW = "https://raw.githubusercontent.com/Ziqian-xia/climate-mental-health-evidence/main"
PROMPT_FILES = {
    "router":      "prompts_v3/title_abstract_screening/00_candidate_topics_prompt.md",
    "temperature": "prompts_v3/title_abstract_screening/01_temperature_prompt.md",
    "wildfire":    "prompts_v3/title_abstract_screening/02_wildfire_prompt.md",
    "flood":       "prompts_v3/title_abstract_screening/03_flood_prompt.md",
    "cyclone":     "prompts_v3/title_abstract_screening/04_cyclone_prompt.md",
    "drought":     "prompts_v3/title_abstract_screening/05_drought_prompt.md",
}

MODEL = "deepseek-v4-flash"
BASE_URL = "https://api.deepseek.com"
MAX_TOKENS = 800
PAUSE_SEC = 0.2
CRITERIA_VERSION = "per-topic prompt set 00-05 v3 (outcome + design discipline)"
# -----------------------------------------------------------------


def log(m): print(m, flush=True)
def die(m): print("\n[ERROR] " + m + "\n", flush=True); sys.exit(1)

try:
    import openpyxl
except ImportError:
    die("Missing openpyxl. Run: pip install openpyxl openai")
try:
    from openai import OpenAI
except ImportError:
    die("Missing openai. Run: pip install openpyxl openai")


def get_api_key():
    key = os.environ.get("DEEPSEEK_API_KEY", "").strip()
    if key:
        return key
    log("\nNo DEEPSEEK_API_KEY detected.")
    log("Paste your DeepSeek API key (from platform.deepseek.com; it will NOT be shown as you type):")
    key = getpass.getpass("API key: ").strip()
    if not key:
        die("No API key entered.")
    return key


def verify_api_key(client):
    log("  Verifying API key ...")
    try:
        client.chat.completions.create(model=MODEL, max_tokens=1,
                                       messages=[{"role": "user", "content": "ping"}])
        log("  API key is valid.\n")
    except Exception as e:
        msg = str(e)
        if any(t in msg for t in ("401", "invalid_api_key", "Unauthorized")):
            die("API key is invalid or unauthorized.\nOriginal error: " + msg[:200])
        if any(t in msg for t in ("429", "insufficient", "quota")):
            die("The API key works but has insufficient credit.\nOriginal error: " + msg[:200])
        die("API call failed (network or model-name issue): " + msg[:200])


def load_prompts():
    prompts = {}
    if LOCAL_PROMPT_DIR:
        for name, path in PROMPT_FILES.items():
            fp = os.path.join(LOCAL_PROMPT_DIR, os.path.basename(path))
            if not os.path.exists(fp):
                die(f"Prompt file not found: {fp}\nFix LOCAL_PROMPT_DIR at the top of this script, "
                    f"or set it to \"\" to fetch prompts from GitHub.")
            prompts[name] = open(fp, encoding="utf-8").read()
        log(f"  Loaded {len(prompts)} prompts from disk.")
    else:
        import urllib.request
        for name, path in PROMPT_FILES.items():
            try:
                with urllib.request.urlopen(f"{REPO_RAW}/{path}") as r:
                    prompts[name] = r.read().decode("utf-8")
            except Exception as e:
                die(f"Failed to fetch {path}\nReason: {e}")
        log(f"  Loaded {len(prompts)} prompts from GitHub.")
    log(f"  (temperature prompt = {len(prompts['temperature'])} chars; v3 should be ~8800)")
    return prompts


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


def call_model(client, system_prompt, record):
    user_text = ("Here is one record to screen. Use ONLY its title and abstract.\n\n"
                 + json.dumps(record, ensure_ascii=False)
                 + "\n\nReturn exactly one JSON object as specified. Output JSON only.")
    last = None
    for attempt in range(4):
        try:
            resp = client.chat.completions.create(
                model=MODEL, max_tokens=MAX_TOKENS, temperature=0,
                response_format={"type": "json_object"},
                messages=[{"role": "system", "content": system_prompt},
                          {"role": "user", "content": user_text}])
            return extract_json(resp.choices[0].message.content)
        except Exception as e:
            last = e
            time.sleep(2 * (attempt + 1))
    return {"_error": str(last)}


def screen_one(client, prompts, record):
    """Returns (decision, reason)."""
    router = call_model(client, prompts["router"], record)
    if "_error" in router:
        return "ERROR", "router failed: " + str(router["_error"])[:150]

    topics = router.get("candidate_topics", []) or []
    if not topics:
        return "EXCLUDE", "No eligible registered hazard identified."

    per, any_inc, inc_rev, any_rev = [], False, False, False
    for tp in topics:
        if tp not in prompts:
            continue
        out = call_model(client, prompts[tp], record)
        if "_error" in out:
            per.append(f"{tp}: ERROR")
            any_rev = True
            continue
        dec = str(out.get("decision", "")).upper()
        rf = bool(out.get("review_flag", False))
        code = out.get("exclusion_code", "")
        why = str(out.get("one_line_reason", ""))[:150]
        per.append(f"{tp}: {dec}" + (f" [{code}]" if code and code != "NA" else "") + f" - {why}")
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
        return ("REVIEW" if inc_rev else "INCLUDE"), reason
    if any_rev:
        return "REVIEW", reason
    return "EXCLUDE", reason


def main():
    log("=" * 72)
    log("  Reviewer packet screening - v3 prompts on DeepSeek")
    log("=" * 72)

    if not os.path.exists(EXCEL_IN):
        die(f"Excel file not found:\n  {EXCEL_IN}\nFix EXCEL_IN at the top of this script.")

    log("\n[1/5] Reading the Excel file ...")
    wb = openpyxl.load_workbook(EXCEL_IN)
    missing = [s for s in SHEETS if s not in wb.sheetnames]
    if missing:
        die(f"Sheet(s) not found: {missing}\nSheets present: {wb.sheetnames}")

    # collect unique records across the three sheets
    records, locations = {}, {}
    for sheet in SHEETS:
        ws = wb[sheet]
        H = {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1)}
        for col in ("Dedup Id", "Title", "Abstract"):
            if col not in H:
                die(f"Sheet '{sheet}' has no column named '{col}'. Columns: {list(H)}")
        for r in range(2, ws.max_row + 1):
            did = ws.cell(r, H["Dedup Id"]).value
            if not did:
                continue
            did = str(did)
            title = ws.cell(r, H["Title"]).value or ""
            abstract = ws.cell(r, H["Abstract"]).value or ""
            records.setdefault(did, {"dedup_id": did, "title": str(title), "abstract": str(abstract)})
            locations.setdefault(did, []).append((sheet, r))
    total_rows = sum(len(v) for v in locations.values())
    log(f"      {total_rows} rows across {len(SHEETS)} sheets; {len(records)} unique records to screen.")

    log("\n[2/5] Loading v3 prompts ...")
    prompts = load_prompts()

    log("\n[3/5] Connecting to DeepSeek ...")
    client = OpenAI(api_key=get_api_key(), base_url=BASE_URL)
    verify_api_key(client)

    # resume from checkpoint
    done = {}
    if os.path.exists(CHECKPOINT):
        try:
            done = json.load(open(CHECKPOINT, encoding="utf-8"))
            log(f"      Resuming: {len(done)} record(s) already screened (from {CHECKPOINT}).")
        except Exception:
            done = {}

    log(f"\n[4/5] Screening {len(records) - len(done)} remaining record(s) ...")
    t0 = time.time()
    todo = [d for d in records if d not in done]
    for i, did in enumerate(todo, 1):
        dec, reason = screen_one(client, prompts, records[did])
        done[did] = {"decision": dec, "reason": reason}
        json.dump(done, open(CHECKPOINT, "w", encoding="utf-8"), ensure_ascii=False)
        if i % 5 == 0 or i == len(todo):
            el = time.time() - t0
            rate = el / i
            log(f"      {i}/{len(todo)} done  ({el/60:.1f} min elapsed, ~{rate*(len(todo)-i)/60:.1f} min left)")
        time.sleep(PAUSE_SEC)

    log("\n[5/5] Writing results into a new Excel file ...")
    for sheet in SHEETS:
        ws = wb[sheet]
        H = {ws.cell(1, c).value: c for c in range(1, ws.max_column + 1)}
        c_dec = H.get("AI Suggestion (v3)") or ws.max_column + 1
        ws.cell(1, c_dec, "AI Suggestion (v3)")
        c_rea = H.get("AI Reason (v3)") or c_dec + 1
        ws.cell(1, c_rea, "AI Reason (v3)")
        for r in range(2, ws.max_row + 1):
            did = ws.cell(r, H["Dedup Id"]).value
            if did and str(did) in done:
                ws.cell(r, c_dec, done[str(did)]["decision"])
                ws.cell(r, c_rea, done[str(did)]["reason"][:900])
    wb.save(EXCEL_OUT)

    from collections import Counter
    cnt = Counter(v["decision"] for v in done.values())
    log("\n" + "=" * 72)
    log("  SUMMARY")
    log("=" * 72)
    log(f"  Unique records screened : {len(done)}")
    for k, v in cnt.most_common():
        log(f"    {k:<10} {v}")
    log(f"  Model                   : {MODEL}")
    log(f"  Criteria                : {CRITERIA_VERSION}")
    log(f"  Runtime                 : {(time.time()-t0)/60:.1f} min")
    log(f"\n  Saved: {EXCEL_OUT}")
    log(f"  ('Human Decision' and 'Audit Notes' columns were not modified.)")
    log(f"  You can delete {CHECKPOINT} once you are happy with the output.")


if __name__ == "__main__":
    main()
