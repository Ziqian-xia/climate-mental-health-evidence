# Nature News (2026) — "Think preprints are unreliable? Analysis of 70,000 studies might change your mind"

> **Type:** Journalistic news article (secondary source / commentary on a primary preprint)
> **Author:** Mohana Basu
> **Outlet:** *Nature* — News
> **Published:** 10 July 2026
> **DOI:** [10.1038/d41586-026-02167-3](https://doi.org/10.1038/d41586-026-02167-3)
> **URL:** https://www.nature.com/articles/d41586-026-02167-3
> **Reports on:** Yin, H. & Rust, R. (2026), bioRxiv preprint [10.64898/2026.06.30.735556](https://doi.org/10.64898/2026.06.30.735556) — see companion summary `Yin_Rust_2026_Preprint_to_Publication_summary.md`

---

## TL;DR

A news piece covering a large bioRxiv preprint (Yin & Rust) that used a large language model (LLM) to compare the abstracts of ~72,644 biomedical preprints with their eventual peer-reviewed versions. The headline message: peer review rarely overturns a preprint's central conclusion (only ~10% see major change), and preprinted papers are retracted at about half the rate of never-preprinted papers. The article balances the authors' "preprints are reliable" framing with cautionary notes from an independent expert (Julian Sienkiewicz) about selection bias, LLM matching error, and reviewer overload.

---

## Key facts and figures (as reported in the news piece)

- **Corpus:** Main scientific conclusion extracted (via an LLM) from abstracts of **72,644** biomedical manuscripts first uploaded to **bioRxiv between 2018 and 2025**.
- **Content change of main conclusion (preprint → published):**
  - **39.9%** unchanged
  - **~50%** only minor revisions
  - **>10%** (slightly more than) major changes
- **Direction of change (hedging):** When conclusions changed, they more often became **more cautious** than more confident.
  - **8.4%** adopted more cautious language after peer review
  - **4.2%** used more confident wording
- **Variation by discipline:** Major changes in only **7.2%** of bioinformatics papers vs **17.5%** of microbiology studies.
- **Trend over time:** Frequency of major revisions **declined**, from **17%** (papers posted 2019) to **5.7%** (posted 2024).
- **Retractions:**
  - Preprinted papers retracted at **8.1 per 10,000**
  - Comparable never-preprinted papers retracted at **18.7 per 10,000**
  - i.e., preprinted papers retracted at **roughly half** the rate.

---

## Central argument / interpretation

- **Authors' claim (Ruslan Rust, neuroscientist, USC, Los Angeles):** Peer review does not typically produce major changes in study content; this holds across biomedical fields, so **preprints are a reliable source of information**.
- Rust motivation: he often hears colleagues call preprints unreliable, and wanted to test whether that belief holds across biomedical research.
- On the **declining major-revision trend**, Rust suggests it reflects a **change in how preprints are used**: in the early bioRxiv years (and especially during COVID-19) scientists rushed to post, forcing more major revisions later; more recently, some manuscripts already incorporate reviewer feedback into the first posted version.
- On **lower retractions / data sharing**: Rust argues those who post preprints tend to be "open about sharing data," and sharing raw data is associated with "better and more reproducible science."

---

## Caveats and counter-arguments (raised in the article)

- **Observational retraction comparison:** The authors caution the retraction comparison is **observational**, based on **relatively few retractions**, and does **not prove** that preprinting reduces retraction likelihood.
- **Selection bias (from LinkedIn reactions + Rust's own concession):** Preprints are subject to **strong selection bias** depending on who posts them and which studies are posted. Differences between authors who post vs. don't post preprints could drive the observed pattern.
- **Only published preprints analysed:** The study **included only preprints that were eventually published**, so it does **not** assess the veracity of unpublished preprints. Rust notes a prior estimate that ~**two-thirds** of bioRxiv preprints posted before 2017 are eventually published.
- **LLM matching error (Julian Sienkiewicz, Warsaw University of Technology):** LLMs do **not always accurately match** preprints to their peer-reviewed versions. In a dataset of thousands of papers, even a **small margin of error** could exclude many preprints and possibly skew results. (Sienkiewicz co-created **PreprintToPaper**, a dataset linking bioRxiv preprints to published papers.)
- **Reviewer overload interpretation:** Sienkiewicz suggests the **decline in major revisions over time** could instead indicate reviewers are **overloaded** and may not read papers thoroughly — an alternative to Rust's "better preprints" explanation.
- **Clinical caution:** Rust himself advises **extra caution** when using preprints to inform **clinical decisions**, and stresses that scientists should **read and evaluate papers themselves** rather than judging quality by preprint-vs-published status.

---

## Named people and entities

- **Ruslan Rust** — neuroscientist, University of Southern California (USC), Los Angeles; co-author of the preprint.
- **Hao Yin** — co-author (named in references, not quoted in the news text).
- **Julian Sienkiewicz** — studies AI tools and data exploration, Warsaw University of Technology; independent commentator; co-creator of PreprintToPaper.
- **Mohana Basu** — Nature news author.

## References cited in the news article

1. Yin, H. & Rust, R. Preprint at bioRxiv https://doi.org/10.64898/2026.06.30.735556 (2026). *(the primary study)*
2. Abdill, R. J. & Blekhman, R. *eLife* **8**, e45133 (2019). https://doi.org/10.7554/eLife.45133 *(source of the "~two-thirds of preprints get published" figure)*
3. Badalova, F., Sienkiewicz, J. & Mayr, P. *Sci. Data* **13**, 301 (2026). https://doi.org/10.1038/s41597-026-06867-3 *(PreprintToPaper dataset)*

---

## Why this is relevant to our own meta-analysis × LLM work

- **Framing / motivation source:** Provides a concise, quotable public-facing framing of the "are preprints reliable?" debate — useful for an introduction or significance statement.
- **The critique paragraph is a gift for our Limitations/Discussion:** the article cleanly enumerates the three main attack surfaces of LLM-based, at-scale preprint studies — (1) **selection bias** (who posts, what gets posted, published-only sampling), (2) **LLM preprint↔paper matching error**, and (3) **alternative explanations** for temporal trends (reviewer overload vs. improving preprints). We should pre-empt all three if we run a similar design.
- **Benchmark numbers to cite/compare:** 39.9% unchanged / 50% minor / ~10% major; 8.4% vs 4.2% cautious/confident asymmetry; 7.2%–17.5% field range; 17%→5.7% temporal decline; 8.1 vs 18.7 per 10,000 retraction rates.
- **Methodological signal:** at-scale LLM claim-comparison is now being taken seriously by *Nature* news, and independent datasets (PreprintToPaper) exist for validating preprint→paper linkage — a possible external-validation resource for our pipeline.
- **Norm to emulate:** the piece models balanced reporting — pairing the positive headline with expert skepticism. A strong paper should do the same internally (state the reliability finding, then adversarially stress-test it).

---

*Notes captured for internal research reference (meta-analysis × LLM literature). This is a summary of a journalistic secondary source; verify all figures against the primary preprint before citing.*
