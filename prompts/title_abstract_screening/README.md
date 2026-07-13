# Per-Topic Prompt Set

Use these prompts after deduplication on `repos/climate-mental-health-evidence/data/merged_deduplicated_records.csv.gz`.

Recommended order:

1. Run `00_candidate_topics_prompt.md` on each deduplicated record to generate `candidate_topics`.
2. Run the corresponding topic prompt for every topic in `candidate_topics`.
3. If `candidate_topics` is empty but `needs_human_topic_review = true`, send the record to human topic review rather than automatically excluding it.
4. Keep a record if any topic prompt returns `INCLUDE`.
5. Human-review every record with `review_flag = true`.
6. Audit excludes separately by topic.

The candidate-topic prompt is not an inclusion/exclusion prompt. It only decides which topic-specific prompt(s) should see the record.

The prompts are designed for title/abstract screening only and are aligned to the final PROSPERO registration plus `SM-search formula.pdf`. They intentionally do not make final full-text decisions about objective exposure data, within-unit temporal identification, or extractable effect estimates unless the title/abstract clearly makes the record ineligible.

Heavy precipitation, heavy rainfall, extreme rainfall, rainstorm, downpour, and pluvial rainfall are not standalone registered hazard modules. They should not be assigned as a separate topic. They are relevant to the flood prompt only when flooding/inundation/storm surge/river overflow or documented flood attribution is also present.

Suggested input object:

```json
{
  "dedup_id": "D0000001",
  "title": "...",
  "abstract": "...",
  "year": "2024",
  "journal": "..."
}
```

When a record has no abstract, pass an empty string in `abstract` and let the prompt decide from title only. Missing abstracts should generally set `review_flag = true` if the title contains an eligible hazard and mental-health signal.
