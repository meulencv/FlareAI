---
title: "Analyzing results"
description: "Read your experiment dashboard and make data-driven decisions"
---

# Analyzing results

> Read your experiment dashboard and make data-driven decisions

Once an experiment is active, the details panel switches from the draft editor to a read-only analysis view. This page explains what you see and how to interpret it.

## Experiment lifecycle

| Action               | What happens                                            |
| -------------------- | ------------------------------------------------------- |
| **Start**            | Traffic splitting begins, runs are assigned to variants |
| **Refresh analysis** | Recalculates statistics with the latest run data        |
| **Finish**           | Ends the experiment, moves it to `completed` status     |

<Note>
  Results may auto-refresh when stale, but use Refresh analysis to force the latest computation.
</Note>

## Dashboard elements

### KPI header

The top of the analysis view shows high-level numbers:

* **Total runs** — how many runs have been collected across all variants
* **Duration** — how long the experiment has been active
* **Metric count** — number of configured metrics
* **Per-variant runs** — run counts for control and each treatment, listed control first. With more than four variants the header shows the variant count and points you to the per-variant breakdown instead of listing every number inline

### Metric cards

Each metric gets a card showing the current analysis. Cards include the observed values for each variant, the estimated effect, and the statistical confidence. Every treatment is compared against control, so a card in a multi-treatment experiment reports one relative lift, absolute lift, and confidence figure per treatment.

### Daily estimates chart

Shows the metric value for each variant on a day-by-day basis. Use this to spot trends or anomalies — for example, if one treatment's performance dropped on a specific day, there may be an external factor worth investigating.

### Cumulative effect chart

Shows the estimated effect of each treatment over time as data accumulates. Early in the experiment the estimate will be noisy and the confidence interval wide. As more runs come in, the estimate stabilizes and the interval narrows.

## Interpreting results

### Confidence intervals

A confidence interval gives you a plausible range for the true effect size. For example:

> **+4.0% lift, 95% CI \[+0.8%, +7.2%]**

This means your best estimate is a 4.0% improvement, and the true effect is plausibly between +0.8% and +7.2%.

How to read intervals quickly:

| Interval position       | Interpretation                         |
| ----------------------- | -------------------------------------- |
| Entire interval above 0 | Treatment is likely better             |
| Entire interval below 0 | Treatment is likely worse              |
| Interval crosses 0      | Inconclusive — not enough evidence yet |

### P-values

A p-value tells you how likely your observed result would be if there were truly no difference between variants.

| p-value | Confidence | Interpretation                            |
| ------- | ---------- | ----------------------------------------- |
| 0.05    | 95%        | Common decision threshold                 |
| 0.01    | 99%        | Strong evidence                           |
| 0.20    | 80%        | Weak evidence, usually wait for more data |

A small p-value means stronger evidence of a real effect. A large p-value means the result could easily be noise.

## Making decisions

When reviewing results, keep these principles in mind:

* **Focus on the primary metric.** Secondary metrics provide context but should not override the primary metric's signal.
* **"Inconclusive" does not mean "no difference."** It means you don't have enough data to confidently detect a difference. If the experiment is inconclusive, consider running it longer.
* **Check the confidence interval width.** A wide interval means high uncertainty — even if the point estimate looks good, the true effect could be much smaller (or negative).
* **Don't stop early on a temporary spike.** Short-term fluctuations can look significant before enough data accumulates. Decide in advance when you will evaluate results.
* **Discount significance when you have several treatments.** Each treatment is tested against control separately, so the more arms you run, the more likely one of them clears the threshold by chance. Treat a single significant arm among many as weaker evidence than the same result from a two-variant test.

<Warning>
  Finished experiments move to **completed** status and cannot be restarted. Make sure you're ready to make a decision before clicking Finish.
</Warning>

For a deeper dive into experimental design and common pitfalls, see the [A/B testing guide](05-A-B-testing-guide.md).

---

Fuente original: https://docs.happyrobot.ai/experiments/analyzing-results
