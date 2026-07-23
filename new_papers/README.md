# new_paper — Reference Library: Meta-analysis × LLM

A working collection of papers and structured notes on **preprints, peer review, and LLM-based literature analysis**, assembled to support writing our own **meta-analysis × LLM** paper. Each source paper is paired with a full-English, key-point Markdown summary that ends with a **"Why this is relevant to our own work"** section.

_Last updated: 2026-07-23_

---

## Folder structure

```
new_paper/
├── README.md          ← this index
├── papers/            ← source articles (PDF)
└── md_files/          ← key-point summaries (Markdown), one per paper
```

- **`papers/`** — the original/rebuilt source documents (PDFs).
- **`md_files/`** — one summary per paper; same filename stem as the paper it covers (`_summary.md`).

---

## Catalogue

| # | Paper (in `papers/`) | Summary (in `md_files/`) | Type | Year | One-line takeaway |
|---|---|---|---|---|---|
| 1 | `Yin_Rust_2026_Preprint_bioRxiv_full.pdf` | `Yin_Rust_2026_Preprint_to_Publication_summary.md` | Primary research (bioRxiv preprint, **not peer reviewed**) | 2026 | LLM (Claude Sonnet 4.6) comparison of **72,644** bioRxiv preprint→publication abstract pairs: peer review leaves the central claim intact in ~90% of cases (39.9% unchanged / 50.0% minor / 10.2% major), wording shifts toward caution ~2:1, and preprinted papers are retracted at ~half the rate of never-preprinted ones. |
| 2 | `Nature_News_2026_Preprints_Reliability.pdf` | `Nature_News_2026_Preprints_Reliability_summary.md` | News / secondary commentary (*Nature*) | 2026 | *Nature* news write-up of paper #1; relays the headline reliability finding **and** independent-expert caveats (selection bias, LLM preprint↔paper matching error, reviewer-overload as an alternative explanation for the temporal trend). |

> Papers #1 and #2 are linked: #2 is journalism reporting on #1. Read the preprint summary for the evidence; read the news summary for the public framing and the critique surface.

---

## Key reusable takeaways for our paper

- **Design template (from #1):** at-scale, *claim-level* (not textual-similarity) LLM adjudication — temperature 0, locked/versioned codebook, structured-JSON output, primary + up to two secondary claims, dual axes (content change × hedging), 6 claim types, 3-level ordinal change scale (with a ≥20% magnitude threshold for "major").
- **Reliability blueprint:** validate against a **multi-model panel + human experts** on a stratified subsample; report **model–human vs human–human κ side by side**; quantify **within-model replicate κ**; cite **TRIPOD-LLM** (Gallifant et al., *Nat Med* 2025) for reporting standards.
- **Confounders to pre-empt** (both #1's Limitations and #2's critiques): published-preprints-only sampling, first-version vs post-feedback deposit ambiguity, LLM matching/labeling error, non-representative preprint population, observational retraction comparison (few events, time-at-risk imbalance).
- **External datasets:** PreprintToPaper (Badalova, Sienkiewicz & Mayr 2026) for preprint↔paper linkage; Retraction Watch (via Crossref) for retractions; OpenAlex 2-yr mean citedness for journal impact (not JIF).
- **Reproducibility asset:** #1's code + full LLM-derived dataset are public — https://github.com/rustlab1/PreprintPaperTracker (searchable: https://rustlab1.github.io/PreprintPaperTracker/).

---

## Convention for adding new articles

To keep this library consistent and comparable as it grows:

1. Put the source document in **`papers/`** (PDF preferred). Filename: `FirstAuthor_Year_ShortTitle.pdf`.
2. Put its summary in **`md_files/`** with the **same stem** + `_summary.md`.
3. Follow the summary template used by the existing files:
   **metadata header → TL;DR → key facts/figures → methods → results → limitations → references → "Why this is relevant to our own work."**
4. Add a row to the **Catalogue** table above and, if it introduces a new methodological idea, note it under **Key reusable takeaways**.
5. Flag non-peer-reviewed sources explicitly and re-verify their numbers before citing.

---

_Internal research reference only. Summaries are aids, not substitutes for the primary sources — verify figures against the original papers before citing._
