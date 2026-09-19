---
title: "A/B testing guide"
description: "A practical guide to running reliable experiments, from core statistics to decision-making patterns"
---

# A/B testing guide

> A practical guide to running reliable experiments, from core statistics to decision-making patterns

This guide covers the statistical concepts behind experiments and best practices for designing reliable tests. You don't need to be a statistician — but understanding these fundamentals will help you design better experiments and interpret results correctly.

<Info>
  For hands-on instructions on creating and running experiments in the platform, see [Creating experiments](02-Creating-experiments.md).
</Info>

## What is an experiment?

An experiment answers one question: **is version B truly better than version A, or is the difference just noise?**

* **Control** is your baseline
* **Treatment** is the change you want to test
* Each run is assigned to exactly one variant

Without a controlled experiment, differences can come from traffic mix, seasonality, or random variation rather than your change.

## Hypothesis testing

Every experiment starts with the **null hypothesis**: there is no true difference between control and treatment.

You use data to either:

* **Reject the null** — evidence supports a real difference
* **Fail to reject** — not enough evidence yet

<Note>
  Failing to detect a difference does not prove both versions are equal. It only means the current data is not enough to confidently detect a difference.
</Note>

## P-values and confidence

A **p-value** tells you how likely your observed result would be if there were truly no effect.

* Small p-value → stronger evidence of a real effect
* Large p-value → result could easily be noise

| p-value | Confidence | Interpretation                            |
| ------- | ---------- | ----------------------------------------- |
| 0.05    | 95%        | Common decision threshold                 |
| 0.01    | 99%        | Strong evidence                           |
| 0.20    | 80%        | Weak evidence, usually wait for more data |

## Confidence intervals

A confidence interval gives you a plausible range for the true effect size.

**Example:**

> +4.0% lift, 95% CI \[+0.8%, +7.2%]

This means:

* Your best estimate is that treatment improved the metric by about **4.0%**
* Based on current data, the true effect is plausibly between **+0.8% and +7.2%**
* Because the full interval is above zero, the evidence points to a real positive effect

How to read intervals quickly:

| Interval position       | Interpretation             |
| ----------------------- | -------------------------- |
| Entire interval above 0 | Treatment is likely better |
| Entire interval below 0 | Treatment is likely worse  |
| Interval crosses 0      | Inconclusive               |

## Designing good experiments

* **Start from one clear question.** What specifically are you trying to learn?
* **Choose one primary metric and direction.** This is the metric you use to make your decision.
* **Keep variants unchanged during the run.** Editing a variant mid-experiment invalidates results.
* **Prefer balanced traffic splits.** 50/50 splits maximize statistical power.
* **Decide in advance when you will evaluate.** Pick a target sample size or date before starting.

## Common mistakes to avoid

* **Running with too little traffic** — small sample sizes produce wide confidence intervals and unreliable results
* **Stopping early after a temporary spike** — short-term fluctuations can look significant before enough data accumulates
* **Editing variants mid-run** — changes to either variant during an experiment break the comparison
* **Treating many metrics as co-primary** — the more metrics you test, the higher the chance of a false positive; designate one primary metric
* **Interpreting "inconclusive" as "no difference"** — inconclusive means insufficient data, not that the variants are equivalent

## Metrics on subsets

Be careful with metrics that are only defined for a **subset of runs**.

**Example scenario:**

* You randomize per run
* Your workflow has multiple steps
* Your metric is only defined if a run reaches a later step

**Why this is a problem:**

Randomization makes variants comparable at assignment. But conditioning on a later step introduces **selection bias** — if a variant changes who reaches that step, you end up comparing different populations. This can make a variant look better simply because it reshapes the population, not because it actually performs better.

**What to do instead:**

* Use **primary metrics defined on all runs**: completion rate, success rate, value per run
* Treat subset-based metrics as **diagnostic only**
* If needed, define a **single run-level metric** that combines progression and quality

**Example:**

Instead of:

* ❌ "Price among runs that produced an offer"

Use:

* ✅ "Value per run" — captures both how often an offer happens and how good those offers are

<Note>
  Rule of thumb: if treatment affects whether a metric is observed, that metric alone is not safe as a primary metric.
</Note>

## Power, MDE, and sample size

These concepts help you plan how long to run an experiment:

* **Power** — the probability that your experiment detects a real improvement when one truly exists. 80% power means a 20% chance you miss a real effect (false negative).
* **MDE (minimum detectable effect)** — the smallest improvement you consider meaningful. If your MDE is 5%, you're designing the experiment to reliably detect lifts of 5% or larger.
* **Sample size** — the number of runs required (per variant) to reach your statistical target.

How they relate:

* Lower MDE → larger required sample size
* Higher power → larger required sample size
* Higher metric noise → larger required sample size

Once you estimate sample size, you can translate it into expected experiment duration using your average daily run volume.

### Smaller effects need more data

Detecting a large lift (e.g., 20%) needs far fewer runs than detecting a small lift (e.g., 2-5%). If you care about small gains, expect longer experiments and more inconclusive runs before enough data accumulates.

### Noisy metrics need more data

Some metrics naturally vary a lot (e.g., duration-based metrics). High variance widens confidence intervals and increases the required sample size. Stable outcome metrics often reach clarity faster than noisy continuous metrics.

## The peeking problem

If you check results constantly and stop as soon as they look significant, your false positive rate increases — you're more likely to declare a winner that isn't real.

Use predefined decision points instead of checking daily until something looks significant. Decide before the experiment starts when you will evaluate results (e.g., after N runs, or after 2 weeks).

---

Fuente original: https://docs.happyrobot.ai/experiments/ab-testing-guide
