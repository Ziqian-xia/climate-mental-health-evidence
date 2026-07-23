# Yin & Rust (2026) — "Tracking claim changes from preprint to publication across 72,644 biomedical studies using large language models"

> **Type:** Primary research (bioRxiv preprint; **not yet peer reviewed**)
> **Authors:** Hao Yin¹, Ruslan Rust²,³
> **Affiliations:** ¹ Robarts Research Institute, Schulich School of Medicine and Dentistry, Western University, London, Ontario, Canada; ² Dept. of Physiology and Neuroscience, University of Southern California (USC), Los Angeles; ³ Zilkha Neurogenetic Institute, Keck School of Medicine, USC, Los Angeles.
> **Corresponding author:** Ruslan Rust (rrust@usc.edu), ORCID 0000-0003-3376-3453. Hao Yin ORCID 0000-0002-0018-3228.
> **Posted:** 1 July 2026 (version 1)
> **DOI:** [10.64898/2026.06.30.735556](https://doi.org/10.64898/2026.06.30.735556)
> **License:** CC-BY 4.0
> **Pre-registration:** researchhub.com/proposal/32332
> **Data / code:** GitHub https://github.com/rustlab1/PreprintPaperTracker · searchable site https://rustlab1.github.io/PreprintPaperTracker/
> **Funding:** ResearchHub Foundation. **Competing interests:** none declared.
> **Covered by:** Nature News, 10 July 2026 (see `Nature_News_2026_Preprints_Reliability_summary.md`)

---

## TL;DR

The largest claim-level study to date of how biomedical preprints change on the way to peer-reviewed publication. Using an LLM (**Claude Sonnet 4.6**) to parse and compare **72,644** bioRxiv preprint–publication **abstract pairs (2018–2025)**, the authors find that peer review **leaves the central claim of most abstracts intact** (39.9% unchanged, 50.0% minor, only 10.2% major). When wording shifts, it shifts toward **caution** about twice as often as toward confidence (8.4% vs 4.2%). Major revision is **more common with longer review and higher-impact journals**, and has **declined over time** (17.0% in 2019 → 5.7% in 2024). Preprinted papers are retracted at **~half** the rate of never-preprinted ones (8.1 vs 18.7 per 10,000; rate ratio 2.31). Conclusion: **bioRxiv preprints are a reliable early source of biomedical knowledge.**

---

## Research question and gap addressed

- Preprints disseminate a large share of biomedical research **before** peer review; some scientists regard preprint claims as **unverified / potentially unreliable**.
- Prior evidence is **mixed and limited**: earlier work found abstract conclusions change in only ~7.2% of preprints (more for pandemic-era work), results shift in ~one-fifth of cases in another analysis, yet effect estimates are largely consistent and reporting quality improves only modestly after peer review.
- Prior claim-level studies are **small or COVID-19–specific**, with **heterogeneous measures**; large-scale studies often measure **textual similarity** rather than the **content of the scientific claim** (which cannot reveal whether a claim was strengthened, weakened, or overturned).
- **This study's contribution:** a **large-scale, claim-level** assessment of the preprint → peer-reviewed-publication transition across the full bioRxiv corpus.

---

## Data and sample

- Source: **bioRxiv API** + **PubMed metadata up to April 2026**.
- Inclusion: bioRxiv records posted **2018–2025** with a DOI matching a **peer-reviewed original research article**; both abstracts in **English** and **≥100 characters**; for multiple preprint versions, **only the first version** used.
- Final corpus: **72,644** matched preprint–publication abstract pairs, covering **3,442 journals** and **25 bioRxiv subject categories** (the **17** categories with ≥1,500 pairs are shown in field analyses).
- Label completeness: of **74,098** pairs passing the abstract-length filter, **72,644 (98.0%)** received complete Sonnet labels; the remainder failed on transient API limits and were excluded.
- Retraction analysis comparison group: preprinted papers vs **non-preprinted articles from the same journals and fields over the same period**.

---

## Methods — LLM claim extraction and classification

- **Model:** Claude **Sonnet 4.6** (Anthropic; identifier `claude-sonnet-4-6`), temperature **0**, 1,200-token output limit, returning **structured JSON** under a **locked v7.1 codebook** (locked 25 April 2026).
- For each abstract pair the model extracted **one primary claim + up to two secondary claims**, plus:
  - **Claim type** — one of **6**: mechanistic, associative, descriptive, methodological, therapeutic, null result.
  - **Hedging level** — tier of language certainty.
- A second prompt compared each preprint claim to its published counterpart, yielding two axes:
  - **(1) Content change — 3 levels:**
    - *Unchanged* = identical or trivial paraphrase, no hedging shift.
    - *Minor revision* = wording-only paraphrase or within-tier hedging shift.
    - *Major revision* = direction flips, scope changes (entity, population, species, setting), magnitude shifts **≥20%** on a comparable estimator, effect-type transitions (associative/predictive/explanatory/causal-regulation/causal-necessity), or **outright claim replacement**. (Categorization adapted from Silagy et al. to fit the LLM prompt.)
  - **(2) Hedging shift — 3 levels:** more cautious, unchanged, more confident. Entirely replaced claims → certainty comparison marked **non-applicable** and excluded downstream.
- **Validation / reliability:**
  - Calibrated against a **five-call panel of LLMs** (Sonnet ×3, Haiku, Opus) **+ two independent domain experts (HY, RR)** on a **stratified subsample of 120 abstract pairs**.
  - **Model–expert agreement matched expert–expert agreement:** Cohen's **κ 0.63–0.66** (model vs experts) vs **0.60** (expert vs expert).
  - **Within-Sonnet reproducibility:** three replicate runs agreed at **κ = 0.75**, confirming the majority-vote label was stable → the single Sonnet scheme was applied to the full corpus.

### Statistical analyses (brief)
- Prevalence of unchanged/minor/major with **95% Wilson CIs**, stratified by field, claim type, journal impact (2-yr mean citedness), calendar year, and **review-duration tertiles** (medians **110 / 218 / 416 days**).
- **Multinomial logistic regression** for cross-field differences (adjusting for field and journal impact).
- Journal impact = **2-year mean citedness from OpenAlex** (matched by journal name; 908 journals, 59,012 pairs), **not** the Journal Impact Factor.
- Hedging: **Wilcoxon signed-rank** + **sign test** on paired hedging scores; strengthened-to-weakened ratios across fields/claim types.
- Claim-type transitions visualized with an **alluvial diagram**.
- Drivers of revision: logistic regression with **restricted cubic splines** (content change vs review-duration tertiles); **weighted linear regression** (revision rate vs log journal impact).
- Retraction: **Poisson rate ratio** with **one-sided Fisher's exact test**; restricted to **47 journals** with unambiguous ISSN matches in the Crossref-hosted **Retraction Watch** database (downloaded April 2026); 95% CI via log-normal (Katz) approximation with exact Poisson per-group intervals.

---

## Key results

### 1. Peer review rarely changes primary claims; wording becomes more cautious
- **Content change of the primary claim (n = 72,644; Fig. 1a):**
  - **Unchanged 39.9%**
  - **Minor 50.0%**
  - **Major 10.2%** (text also states 10.1% in the donut label — treat as ~10%)
  - → Nearly **90%** unchanged or only minorly revised.
- **Hedging shift (Fig. 1b):** unchanged in **85.6%**; among shifts, **more cautious 8.4% vs more confident 4.2%** → a **~2:1 cautious/confident ratio**.
- Shift toward caution **scales with extent of revision (Fig. 1c):** among **major** content changes, hedging became more cautious in **38.5%** vs more confident **19.8%**; unchanged-content abstracts rarely shifted certainty.
- The cautious-over-confident excess was **statistically significant** (two-sided sign test on the **9,150** pairs with any hedging shift, **P < 0.001**).

### 2. Variation by field and claim type
- **Major revision of the primary claim by field (Fig. 1d):** ranges from **7.2% (bioinformatics)** to **17.5% (microbiology)**.
- Shift toward caution present in **every** field; strengthened/weakened ratio **below 1** throughout (Fig. 1e). **Weakened claims outnumbered strengthened claims in all 17 fields** with ≥1,500 pairs (sign test, P < 0.001).
- **Claim type is stable:** preserved in **96.5%** of pairs; among the **3.5% (n = 2,520)** that changed type, transitions ran mostly between **adjacent** categories (e.g., mechanistic → associative/descriptive), rarely to a null result (Fig. 1f). Mechanistic claims were most likely to be reclassified (usually to descriptive/associative), so **descriptive claims showed the largest net gain**.

### 3. Primary and secondary claims are revised together
- Secondary-claim revision **tracks** the primary: first secondary claim changed in **90%** of pairs when the primary was substantively revised vs only **34%** when the primary was unchanged (χ² test, P < 0.001) — revision moves an abstract's claims **together**, not in isolation (Fig. 2a).
- Stability depends on claim type: primary claim substantively revised in only **5.4% of method claims** vs **11.4%–11.9%** for descriptive/association/mechanistic claims (Fig. 2b). Within the same papers, **secondary** claims were revised more often than primary for every type; largest gap for method claims (**5.4% vs 11.7%**).

### 4. Larger revisions track longer review and higher-impact journals
- **Temporal decline:** major revision fell from **17.0% (2019)** to **5.7% (2024)** (Fig. 2c). Monotonic decline across the full series (**19.6% in 2018**, n = 341; 2025 excluded as incomplete, n = 53). Held even among preprints with similar review times → consistent with a **real reduction in the need for revision**, not just shorter recent review. Remained significant after adjusting for review duration (logistic regression: **adjusted odds ratio 0.85 per year, P < 0.001**).
- **Review duration:** revision rose with length of review — **7.0%** (fastest tertile, median 110 days) → **14.1%** (slowest, median 416 days) (Fig. 2d). Major revision rose monotonically across review-time tertiles (**7.0%, 9.5%, 14.1%**; χ² test, P < 0.001).
- **Journal impact:** revision rose ~**23 percentage points per tenfold increase** in 2-year mean citedness (**R² = 0.77** across journal impact; Fig. 2e).

### 5. Preprinting is NOT associated with higher retraction
- Never-preprinted papers were retracted **~2× as often** as preprinted papers: **18.7 vs 8.1 per 10,000** (Fig. 2f).
- **Rate ratio 2.31**, 95% CI **1.20–4.45**, **P = 0.003**.
- Raw counts: preprinted **9 / 11,114**; non-preprinted **813 / 435,159**.

---

## Discussion / interpretation (authors)

- The preprint → publication transition **leaves the central claims of most biomedical abstracts intact**; substantial revision is uncommon. Where claims change, wording shifts toward **caution** more than confidence.
- Consistent with smaller prior studies and a recent scoping review; this work **extends** them to the full bioRxiv corpus and to the level of the **scientific claim** rather than textual similarity.
- The cautious-wording shift, though rarely altering the central claim, **matters for interpretation** when it reflects weaker/more uncertain evidence. This signal currently only becomes available **on publication — a median ~7 months after posting**. Future work should test whether LLMs can provide an **equivalent calibration of claim strength at posting time**, removing the delay.
- Because the corpus largely **predates routine LLM use** in scientific writing, the 2018–2024 trend also serves as a **reference point** for how preprint-to-publication revision may change as these tools spread.
- Retraction analysis **provides no support** for the view that preprints are less reliable.
- The revision–review-duration correlation is **not causal** (authors can deposit a preprint before **or** after peer review).

---

## Limitations (as stated by the authors)

1. **Abstracts only, not full texts** — changes confined to methods, figures, or results would not be captured.
2. **First-preprint vs published comparison** conflates author revision + peer review + journal production ("peer review" used loosely for the whole transition).
3. **Single-LLM labeling** — automated extraction remains imperfect; labels not separately validated within individual fields or for secondary claims → possible field-/claim-specific measurement error.
4. **Published-pairs-only sampling** — recent posting years have incomplete follow-up; slower-to-publish papers may be underrepresented, possibly **accentuating the apparent decline** in major revision over time.
5. **Retraction comparison is observational**, based on **few events**, not adjusted for differential time-at-risk (retractions accrue over time; publication-recency differences could bias it).
6. **Unpublished preprints excluded** — may skew the conclusion toward preprint credibility.
7. **Preprints are not a representative sample** of biomedical research; the decision to post (and which manuscript to post) depends on author and completeness → estimates describe the **preprinted literature**, not all submitted manuscripts.
8. **Version status uncertainty** — cannot confirm every bioRxiv record is genuinely pre–peer-review; some authors deposit a revised (post-feedback) version, occasionally as the first posted version → would **underestimate** changes introduced by peer review. Using the first posted version reduces but does not remove this risk.
9. **bioRxiv-only** — may not generalize to clinical or other literatures.

---

## Conclusion (verbatim sense)

The study provides support for the **reliability of biomedical preprints** as a source of scientific claims. Peer review **refines the wording** of abstracts and revises a **minority** of claims, but rarely overturns their central message. The authors note that **claim stability between versions is a necessary but not sufficient condition for scientific correctness**, which they did not assess directly.

---

## Key references from the paper (selected, for our literature map)

- Abdill & Blekhman, *eLife* 8, e45133 (2019) — popularity/outcomes of bioRxiv preprints (~two-thirds eventually published).
- Krumholz et al., *JAMA* 324, 1903–1905 (2020) — medRxiv submissions/downloads.
- Fraser et al., *PLOS Biology* 19, e3000959 (2021) — evolving role of preprints in COVID-19.
- Brierley et al., *PLOS Biology* 20, e3001285 (2022) — tracking preprint→publication changes during a pandemic.
- Oikonomidi et al., *BMC Med* 18, 402 (2020) — changes in evidence for COVID-19 intervention studies.
- Davidson et al., *BMC Med Res Methodol* 24, 9 (2024) — effect-estimate comparison, preprints vs peer-reviewed COVID-19 trials.
- Carneiro et al., *Res Integr Peer Rev* 5, 16 (2020) — reporting quality comparison.
- Zoghbi et al., *Res Integr Peer Rev* 11, 3 (2026) — scoping review, preprints vs peer-reviewed in health.
- Klein et al., *Int J Digit Libr* 20, 335–350 (2019) & Nicholson et al., *PLOS Biology* 20, e3001470 (2022) — **textual-similarity / linguistic-shift** approaches (the "at scale but not claim-level" prior work this study improves on).
- Nelson et al., *Lancet Glob Health* 10, e1684–e1687 (2022) — robustness of preprint evidence through peer review.
- Lazarus et al., *J Clin Epidemiol* 77, 44–51 (2016) — reviewers constrain overstatement/spin in abstracts.
- Avissar-Whiting, *PLOS ONE* 17, e0267971 (2022) — downstream retraction of preprinted research.
- Kobak et al., *Science Advances* 11, eadt3813 (2025) & Kusumegi et al., *Science* 390, 1240–1243 (2025) — **LLM-assisted writing / scientific production in the LLM era** (context for the pre-LLM baseline argument).
- Gartlehner et al., *Cochrane Evid Synth Methods* 3, e70063 (2025) — responsible AI integration in rapid reviews.
- Gallifant et al., *Nat Med* 31, 60–69 (2025) — **TRIPOD-LLM reporting guideline** for LLM studies (relevant reporting standard for our own methods).
- Jefferson et al., *Cochrane Database Syst Rev* MR000016 (2007) — editorial peer review effects on report quality.
- Silagy et al., *JAMA* 287, 2831–2834 (2002) — protocol-vs-final comparison framework (basis for the content-change categories).

---

## Why this is relevant to our own meta-analysis × LLM work (notes for writing our paper)

- **Template methodology:** This is a near-ideal template for an *at-scale, claim-level, LLM-adjudicated* comparison design. Reusable design choices: temperature 0, locked/versioned codebook, structured-JSON output, primary+secondary claim decomposition, dual axes (content change × hedging), 6-type claim taxonomy, and 3-level ordinal change scale adapted from Silagy et al.
- **Reliability blueprint to copy:** validate against a **multi-model panel + human experts on a stratified subsample**, report **model–human vs human–human κ side by side**, and quantify **within-model replicate κ** for label stability. Cite **TRIPOD-LLM** (Gallifant 2025) for reporting. This is exactly what reviewers will demand of us.
- **Confounders/limitations to pre-empt** (mirrors the Nature News critiques): published-only sampling, first-version vs post-feedback deposit ambiguity, LLM matching/labeling error, non-representative preprint population, observational retraction comparison with few events and time-at-risk imbalance. Build robustness checks for each.
- **Metric ideas:** magnitude threshold (**≥20%** on comparable estimator) as an objective "major change" trigger; strengthened/weakened ratio as a directional summary; review-duration tertiles and journal-impact (OpenAlex 2-yr mean citedness, not JIF) as covariates.
- **External datasets to leverage:** PreprintToPaper (Badalova, Sienkiewicz & Mayr 2026) for validating preprint↔paper linkage; Retraction Watch (Crossref) for retraction outcomes; OpenAlex for impact.
- **Open-science asset:** their code + full LLM-derived dataset are public (github.com/rustlab1/PreprintPaperTracker) — a concrete reproducibility baseline and possible data source/comparator for us.
- **Framing hooks:** "necessary but not sufficient" caveat on claim stability vs correctness; the pre-LLM-era corpus as a baseline for measuring how LLM-assisted writing changes revision patterns going forward.

---

*Notes captured for internal research reference (meta-analysis × LLM literature). Primary source is a non-peer-reviewed preprint — figures are from version 1 (posted 1 July 2026) and may change; re-verify before citing.*
