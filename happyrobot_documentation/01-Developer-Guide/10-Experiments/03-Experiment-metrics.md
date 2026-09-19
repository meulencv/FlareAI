---
title: "Experiment metrics"
description: "Default and custom metrics available for measuring experiment outcomes"
---

# Experiment metrics

> Default and custom metrics available for measuring experiment outcomes

Metrics define what you measure to determine which variant performs better. Every experiment needs at least one metric, and one must be designated as the **primary metric** — the single metric you use to make your final decision.

Each metric has a **direction** (`higher is better` or `lower is better`) that tells the analysis system which direction represents an improvement.

## Default metrics

Default metrics are predefined by the platform. Use these when a built-in metric already matches your experiment goal.

### Voice metrics

| Metric                       | Description                                                                |
| ---------------------------- | -------------------------------------------------------------------------- |
| Interruption rate            | Ratio of interrupted assistant messages to total assistant messages        |
| Cut rate                     | Ratio of naturally cut assistant messages to total assistant messages      |
| Interruption or cut rate     | Ratio of interrupted or cut assistant messages to total assistant messages |
| Early hangup rate            | Rate of sessions where the user hung up within 4 turns                     |
| LLM time to first token (ms) | Median LLM time-to-first-token across assistant messages                   |
| Median message latency (ms)  | Median total latency across all latency breakdown components               |
| Session duration (seconds)   | Average voice session duration across all sessions in the run              |
| Transfer rate                | Whether a call transfer was detected from sessions or node outputs         |

### Billing metrics

Billing metrics sum the credits a run consumed, so you can check what a variant costs alongside how well it performs. Every billing metric is numeric and treats **lower as better**.

| Metric                      | Description                                      |
| --------------------------- | ------------------------------------------------ |
| Total credits               | All credits consumed by the run                  |
| Voice credits               | Credits consumed by voice                        |
| Voice LLM credits           | The LLM portion of voice credits                 |
| Voice orchestration credits | The voice orchestration portion of voice credits |
| Telephony credits           | Credits consumed by telephony                    |
| Run credits                 | Credits consumed by run execution                |
| Run orchestration credits   | The orchestration portion of run credits         |
| Run LLM credits             | The LLM portion of run credits                   |
| Texting credits             | Credits consumed by texting                      |

These use the same category taxonomy as the credits shown in **Settings > Usage**, so a billing metric on an experiment reconciles with the per-run breakdown described in [Credits for a single run](../16-Account-and-Settings/09-Usage-and-Billing.md#credits-for-a-single-run).

<Tip>
  Pair a cost metric with a quality metric before shipping a cheaper variant. A treatment that halves credits but drops the northstar pass rate is not a win — set the quality metric as primary and keep the cost metric as a guardrail.
</Tip>

### Auditing metrics

| Metric                              | Description                                                    |
| ----------------------------------- | -------------------------------------------------------------- |
| Northstar pass rate                 | Overall pass rate across all northstar evaluations for the run |
| Northstar pass rate (notes)         | Pass rate for northstars in the notes category                 |
| Northstar pass rate (style)         | Pass rate for northstars in the style category                 |
| Northstar pass rate (contradiction) | Pass rate for northstars in the contradiction category         |
| Northstar pass rate (sequential)    | Pass rate for northstars in the sequential category            |

## Custom metrics

Custom metrics let you measure anything specific to your workflow by extracting values from **node outputs**.

### How custom metrics work

1. **Choose source node outputs** — select which node outputs to use, mapped per variant (since control and treatment may have different node configurations)
2. **Define the computation** — specify how the metric value is calculated from those outputs
3. **Choose a value type**:
   * **Binary** — pass/fail metric using condition logic (e.g., "did the agent extract the correct phone number?")
   * **Numeric** — number-valued metric from node output values (e.g., "response time in seconds")
4. **Set direction** — `higher is better` or `lower is better`

### Choosing your primary metric

Your primary metric is the one you use to make the final call on which variant wins. Choose it carefully:

<Tip>
  Use a metric that is defined on **all runs**, not just a subset. Metrics that are only observed for some runs (e.g., "price among runs that produced an offer") introduce selection bias if treatment changes who reaches that step. Prefer run-level metrics like completion rate, success rate, or value per run. See [metrics on subsets](05-A-B-testing-guide.md#metrics-on-subsets) in the A/B testing guide for details.
</Tip>

---

Fuente original: https://docs.happyrobot.ai/experiments/experiment-metrics
