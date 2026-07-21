# Statistical Plan for LLM Proxy Validation of Title/Abstract Screening

Climate Change and Mental Health Evidence Review

This document describes how to validate a lower-cost screening model, such as DeepSeek Flash,
against a higher-capability comparator model, such as Claude Opus or another advanced LLM. The
goal is to estimate how many records may be incorrectly included or incorrectly excluded when the
full deduplicated corpus is screened by the lower-cost model.

## 1. Statistical Context

The screening task is a binary classification problem:

- `screen positive`: include or route to human review
- `screen negative`: exclude

For a systematic review, the most important error is a false negative:

- `false negative`: a truly eligible paper is excluded
- `false include`: an ineligible paper is included or routed to review

Because eligible studies are expected to be rare, a small false-negative rate among excluded
records can still imply many missed eligible papers. For example, if 125,000 records are excluded
and the false-negative rate is 0.2%, the expected number of missed eligible records is:

```text
125,000 * 0.002 = 250 missed records
```

Therefore, validation should focus especially on the records excluded by the production model.

## 2. What Opus Can and Cannot Estimate

If Claude Opus or another advanced LLM replaces human checking, the validation estimates:

```text
DeepSeek error relative to Opus
```

It does not directly estimate:

```text
DeepSeek error relative to the true eligibility criteria
```

This distinction matters because Opus can also make mistakes. It may over-include, under-include,
or share blind spots with DeepSeek. However, using an advanced model is still useful when the
project needs a scalable proxy validation before deciding whether a larger human audit is needed.

Recommended interpretation:

- Treat Opus as a `proxy reference`, not as a true gold standard.
- Report results as `DeepSeek vs Opus`, not as final human-verified accuracy.
- Use Opus disagreements to identify likely prompt weaknesses and high-risk records.
- If possible, later human-check a subset of Opus/DeepSeek disagreements and agreements.

## 3. Core Workflow

### Step 1. Run DeepSeek on all records

For every deduplicated record, save:

```text
dedup_id
title
abstract
candidate_topics
DeepSeek final decision
DeepSeek topic-level decisions
DeepSeek reason
model_name
prompt_version
screened_at
```

For statistical estimation, collapse the final decision into two groups:

```text
DeepSeek positive = INCLUDE or HUMAN_REVIEW
DeepSeek negative = EXCLUDE
```

Let:

```text
N_pos = number of DeepSeek-positive records
N_neg = number of DeepSeek-negative records
N_total = N_pos + N_neg
```

### Step 2. Run Opus on a validation sample

Do not use a simple random sample from the whole corpus only. Since most records are likely easy
excludes, a simple random sample will be inefficient for finding possible missed eligible papers.

Instead, use stratified sampling. Recommended strata:

```text
A. DeepSeek positive
B. DeepSeek negative with candidate_topics present
C. DeepSeek negative with no candidate_topics
D. Known borderline or pilot-disagreement records
```

Suggested minimum sample:

```text
300-500 DeepSeek-positive records
600-1,000 DeepSeek-negative records with candidate_topics
300-600 DeepSeek-negative records with no candidate_topics
all known borderline or pilot-disagreement records
```

If budget allows, oversample DeepSeek-negative records because missed eligible papers are the
highest-risk error.

### Step 3. Create the DeepSeek x Opus table

After Opus screens the validation sample, collapse Opus decisions the same way:

```text
Opus positive = INCLUDE or HUMAN_REVIEW
Opus negative = EXCLUDE
```

Then create this table:

| | Opus positive | Opus negative |
|---|---:|---:|
| DeepSeek positive | A | B |
| DeepSeek negative | C | D |

Interpretation:

- `A`: both models screen positive
- `B`: DeepSeek-only positive; possible false includes by DeepSeek relative to Opus
- `C`: Opus-only positive; possible missed papers by DeepSeek relative to Opus
- `D`: both models screen negative

The most important cell is `C`, because those are papers DeepSeek would exclude but Opus would
keep for screening or review.

### Step 4. Estimate DeepSeek false includes relative to Opus

Among DeepSeek-positive records, the proxy false-include rate is:

```text
p_false_include_proxy = B / (A + B)
```

Estimated number of false includes in the full corpus:

```text
estimated_false_includes = N_pos * p_false_include_proxy
```

Example:

```text
N_pos = 5,000
A = 450
B = 50

p_false_include_proxy = 50 / (450 + 50) = 0.10
estimated_false_includes = 5,000 * 0.10 = 500
```

Interpretation: relative to Opus, about 500 of the DeepSeek-positive records may be unnecessary
includes or human-review records.

### Step 5. Estimate missed papers relative to Opus

Among DeepSeek-negative records, the proxy false-negative rate is:

```text
p_missed_proxy = C / (C + D)
```

Estimated number of missed records in the full corpus:

```text
estimated_missed_records = N_neg * p_missed_proxy
```

Example:

```text
N_neg = 126,000
C = 4
D = 996

p_missed_proxy = 4 / (4 + 996) = 0.004
estimated_missed_records = 126,000 * 0.004 = 504
```

Interpretation: relative to Opus, DeepSeek may miss about 504 records.

## 4. Confidence Intervals: General Case

Each rate above is a binomial proportion. For a simple random sample within a stratum:

```text
p_hat = x / n
```

where:

```text
x = number of proxy errors
n = number checked in that group
```

Use a binomial confidence interval for `p_hat`, then multiply the lower and upper bounds by the
size of the corresponding full-corpus group.

For example, for DeepSeek-negative records:

```text
95% CI for missed records =
N_neg * 95% CI for p_missed_proxy
```

Recommended interval methods:

- Wilson interval for routine reporting, including nonzero error counts
- exact binomial interval, also called Clopper-Pearson, for conservative reporting
- one-sided exact upper bound when zero errors are found and the main question is "how bad could
  the rate still be?"

The `3/n` rule is not the general method. It is only a shortcut for the special case where
`x = 0`. In the general case, use `x/n` as the point estimate and calculate a binomial interval.

### General Wilson interval

The Wilson interval works well for rare events and small counts. For a 95% interval:

```text
z = 1.96
p_hat = x / n
denominator = 1 + z^2 / n
center = (p_hat + z^2 / (2n)) / denominator
half_width = z * sqrt((p_hat * (1 - p_hat) / n) + (z^2 / (4n^2))) / denominator

lower = center - half_width
upper = center + half_width
```

Then project the interval to the full corpus:

```text
estimated count = N * p_hat
95% lower count = N * lower
95% upper count = N * upper
```

Example for missed records:

```text
N_neg = 126,000
x = 4 Opus-positive records
n = 1,000 DeepSeek-negative records checked by Opus

p_missed_proxy = 4 / 1000 = 0.004
estimated_missed_records = 126,000 * 0.004 = 504
```

The Wilson 95% interval for the miss rate is approximately:

```text
0.16% to 1.02%
```

Projected to the full DeepSeek-negative pool:

```text
126,000 * 0.0016 = 202
126,000 * 0.0102 = 1,285
```

So the proxy-estimated missed-paper count would be approximately:

```text
504, with a rough 95% interval of 202 to 1,285
```

Additional examples for `n = 1,000`:

| Errors found | Point estimate | Wilson 95% interval | If `N = 126,000`, projected count |
|---:|---:|---:|---:|
| 0 | 0.00% | 0.00% to 0.38% | 0 to 482 |
| 1 | 0.10% | 0.02% to 0.56% | 22 to 711 |
| 4 | 0.40% | 0.16% to 1.02% | 196 to 1,290 |
| 10 | 1.00% | 0.54% to 1.83% | 686 to 2,307 |
| 20 | 2.00% | 1.30% to 3.07% | 1,636 to 3,867 |

### Zero-error case as a special case

If `0` errors are found in `n` checked records, the maximum likelihood estimate is zero, but the
true error rate is not proven to be zero.

If the goal is a one-sided safety statement, the exact 95% upper bound is:

```text
p_upper = 1 - 0.05^(1/n)
```

A close approximation is:

```text
p_upper approximately 3 / n
```

Examples:

| Checked records | Errors found | One-sided 95% upper bound |
|---:|---:|---:|
| 100 | 0 | 2.95% |
| 300 | 0 | 1.00% |
| 600 | 0 | 0.50% |
| 1,000 | 0 | 0.30% |
| 3,000 | 0 | 0.10% |

If DeepSeek excludes 126,000 records and Opus finds zero misses in a random sample of 1,000
DeepSeek-negative records:

```text
p_upper approximately 3 / 1000 = 0.003
upper bound on missed records approximately 126,000 * 0.003 = 378
```

So even a clean 1,000-record audit does not prove that almost no records were missed. It supports
the weaker claim that the proxy-missed count is likely below roughly 378 records at the one-sided
95% level, assuming the sample was random within the target population.

This one-sided zero-error bound is slightly different from the two-sided Wilson interval. For
routine reporting, use one interval method consistently and state which one was used.

## 5. Stratified Estimation

If the validation sample is stratified, do not calculate one pooled error rate unless the sample
was drawn in the same proportions as the full corpus. Oversampling high-risk groups is useful,
but the final estimate must be weighted by stratum size.

For each stratum `s`:

```text
N_s = number of full-corpus records in stratum s
n_s = number of sampled records in stratum s
x_s = number of proxy errors found in stratum s
p_s = x_s / n_s
```

Estimated errors in stratum `s`:

```text
E_s = N_s * p_s
```

Total estimated errors:

```text
E_total = sum(E_s)
```

Suggested excluded-record strata:

```text
1. DeepSeek negative, candidate_topics present
2. DeepSeek negative, no candidate_topics
3. DeepSeek negative, no abstract
4. DeepSeek negative, known borderline hazard language
```

Suggested positive-record strata:

```text
1. DeepSeek INCLUDE
2. DeepSeek HUMAN_REVIEW
3. DeepSeek positive with multiple topics
4. DeepSeek positive with weak mental-health signal
```

The purpose of stratification is to avoid letting easy excludes dominate the validation estimate.

## 6. Power and Sample Size

Power here means the probability of detecting at least one error if the true error rate is `p`.

```text
power = 1 - (1 - p)^n
```

Solving for sample size:

```text
n = log(1 - power) / log(1 - p)
```

Approximate sample sizes:

| True error rate | 80% power | 90% power | 95% power |
|---:|---:|---:|---:|
| 1.0% | 161 | 230 | 299 |
| 0.5% | 322 | 459 | 598 |
| 0.2% | 804 | 1,151 | 1,497 |
| 0.1% | 1,609 | 2,302 | 2,995 |

Interpretation:

- To have 95% probability of seeing at least one miss if the true proxy-miss rate is 1.0%, check
  about 300 DeepSeek-negative records.
- To have 95% probability of seeing at least one miss if the true proxy-miss rate is 0.5%, check
  about 600 DeepSeek-negative records.
- To detect a very small proxy-miss rate such as 0.1%, check about 3,000 DeepSeek-negative
  records.

## 7. Recommended Project Design

For this project, a practical Opus-proxy validation design is:

```text
1. Run DeepSeek Flash on all 131,468 deduplicated records.
2. Collapse DeepSeek output into positive and negative groups.
3. Draw a stratified Opus validation sample:
   - 300-500 DeepSeek-positive records
   - 600-1,000 DeepSeek-negative records with candidate_topics
   - 300-600 DeepSeek-negative records with no candidate_topics
   - all known borderline / pilot-disagreement records
4. Run Opus on that validation sample using the same prompt set.
5. Build the DeepSeek x Opus table.
6. Estimate:
   - DeepSeek false includes relative to Opus
   - DeepSeek missed records relative to Opus
   - topic-specific disagreement rates
   - 95% intervals for projected counts
7. Inspect all Opus-positive / DeepSeek-negative records manually if feasible.
```

If no human review is possible, report conclusions carefully:

```text
Based on Claude Opus as a proxy reference, DeepSeek Flash is estimated to miss X records
(95% CI: L to U) and falsely include Y records (95% CI: L to U).
These are model-disagreement estimates rather than human-adjudicated accuracy estimates.
```

## 8. Suggested Reporting Table

| Quantity | Estimate | 95% interval | Interpretation |
|---|---:|---:|---|
| DeepSeek-positive records | `N_pos` | not applicable | Records sent forward by DeepSeek |
| DeepSeek-negative records | `N_neg` | not applicable | Records excluded by DeepSeek |
| Proxy false-include rate | `B / (A + B)` | binomial CI | Among DeepSeek positives, share Opus would exclude |
| Estimated false includes | `N_pos * B/(A+B)` | projected CI | Count of DeepSeek positives Opus would exclude |
| Proxy miss rate | `C / (C + D)` | binomial CI | Among DeepSeek negatives, share Opus would include |
| Estimated missed records | `N_neg * C/(C+D)` | projected CI | Count of DeepSeek negatives Opus would include |
| Recall vs Opus | `A / (A + C)` | binomial CI | How many Opus positives DeepSeek also keeps |
| Precision vs Opus | `A / (A + B)` | binomial CI | How many DeepSeek positives Opus also keeps |

## 9. Recommended Language for Methods Section

The following wording is appropriate if Opus is used without human adjudication:

```text
We conducted a proxy validation study comparing the production screening model with a
higher-capability LLM comparator. The comparator model was treated as a proxy reference rather
than a human gold standard. We estimated disagreement-based false-include and false-negative
rates using stratified sampling, with records grouped by production-model decision and topic
routing status. Binomial confidence intervals were calculated within strata and projected to the
full corpus using stratum weights. Because the comparator model may share systematic errors with
the production model, these estimates should be interpreted as model-disagreement rates rather
than definitive human-adjudicated screening accuracy.
```

If a subset receives human adjudication, add:

```text
All production-negative / comparator-positive disagreements and a random sample of model-agreement
records were manually adjudicated. Human-adjudicated labels were used to estimate final
false-negative and false-include rates.
```

## 10. Bottom Line

Using Opus or another advanced model can make the validation much more informative than checking
only a small random sample manually. It is especially useful for finding possible missed papers
inside the large DeepSeek-excluded pool.

However, Opus should be described as a proxy comparator unless humans adjudicate at least a subset.
The strongest defensible design is:

```text
DeepSeek full screening
+ Opus stratified proxy validation
+ human adjudication of disagreements and a sample of agreements
```

If human adjudication is impossible, the next-best approach is:

```text
DeepSeek full screening
+ Opus stratified proxy validation
+ explicit reporting that all accuracy estimates are relative to Opus
```
