---
title: "Experiments"
description: "Run controlled A/B tests to compare workflow versions and configuration changes with statistical rigor"
---

# Experiments

> Run controlled A/B tests to compare workflow versions and configuration changes with statistical rigor

<Note>
  Experiments are generally available to all users with workflow access — no internal access required. Experiments run on the V3 workflow engine.
</Note>

Experiments let you answer one question with confidence: **is version B truly better than version A, or is the difference just noise?**

Without a controlled experiment, differences in agent performance can come from traffic mix, seasonality, or random variation rather than your change. Experiments eliminate this ambiguity by splitting traffic between variants and measuring the impact with statistical analysis.

<Info>
  New to experimentation concepts? Start with the [A/B testing guide](05-A-B-testing-guide.md) for a primer on the statistics behind experiments.
</Info>

## Key concepts

* **Control variant** — your baseline behavior, typically the current production version
* **Treatment variant** — a change you want to test against control. An experiment can have several
* **Traffic split** — the percentage of runs assigned to each variant, summing to 100%
* **Metrics** — what you measure to determine which variant performs better
* **Primary metric** — the single metric you use to make your final decision

## How experiments work

Each experiment follows a simple lifecycle:

1. **Draft** — configure your variants, traffic split, and metrics
2. **Active** — traffic is split between variants and results accumulate
3. **Completed** — you finish the experiment and apply your decision

You can have multiple drafts, but currently only one active experiment per workflow at a time (regardless of environment).

## Current limits

* An experiment has exactly one control variant and at least one treatment. Because traffic percentages are whole numbers with a 1% minimum per variant, 100 variants is the ceiling — in practice, keep the count low enough that each variant collects a usable number of runs
* There is no built-in recommended duration — in general, longer experiments produce more precise estimates

<Warning>
  Every additional treatment splits the same traffic further, so each variant reaches statistical significance more slowly. Adding arms also increases the chance that one of them looks significant by luck. Add a treatment because you need to compare it, not because there's room for it.
</Warning>

## Get started

<CardGroup cols={2}>
  <Card title="Create an experiment" icon="plus" href="02-Creating-experiments.md">
    Set up variants, traffic split, and metrics for your test.
  </Card>

  <Card title="Metrics reference" icon="chart-bar" href="03-Experiment-metrics.md">
    Explore default and custom metrics available for experiments.
  </Card>

  <Card title="Analyze results" icon="chart-line" href="04-Analyzing-results.md">
    Read your experiment dashboard and make data-driven decisions.
  </Card>

  <Card title="A/B testing guide" icon="graduation-cap" href="05-A-B-testing-guide.md">
    Learn the statistics behind experiments and best practices.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/experiments/overview
