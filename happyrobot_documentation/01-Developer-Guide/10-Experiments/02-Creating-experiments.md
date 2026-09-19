---
title: "Creating experiments"
description: "Set up an A/B test with variants, traffic split, and metrics"
---

# Creating experiments

> Set up an A/B test with variants, traffic split, and metrics

Experiments are configured at the workflow level. You create an experiment, define what you want to compare, choose how to measure success, and start the test.

## Create a new experiment

<Steps>
  <Step title="Open the experiments panel">
    Navigate to your workflow and open the **Experiments** area. You'll see a left panel with your experiment list (searchable, filterable by status and environment) and a right panel for details.
  </Step>

  <Step title="Create the experiment">
    Click **New experiment** and fill in:

    * **Name** (required) — a descriptive name for your test
    * **Description** (optional) — context about what you're testing and why
    * **Environment** — `production`, `staging`, or `development`
  </Step>

  <Step title="Configure in draft mode">
    After creation, the experiment opens in draft mode where you set up variants and metrics.
  </Step>
</Steps>

## Configure variants

Every experiment has one **control** variant (your baseline) and one or more **treatment** variants (the changes you want to test). The **Variants** table in the draft editor lists them with a column each for the variant name, its version, status, traffic percentage, and actions.

Click **Add Treatment** to add another treatment. A new treatment is named **Treatment 1**, **Treatment 2**, and so on, and each one is configured independently — its own version or config overrides, and its own traffic share.

### Configuration override (same version)

A treatment uses the **same workflow version** as control, but applies **config overrides** to selected nodes.\
Use this to test targeted changes, like a different LLM, voice, or setting, without creating a new version.

To enable this, select the same version for the treatment as control. The **Config Overrides** section will appear.
Then you can select overridable nodes from your workflow and override supported settings on those nodes.

### Version comparison (different version)

A treatment points to a **different workflow version** than control.\
Use this when you want to compare two distinct workflow versions. If you want to test structural changes (different nodes, order, etc.), this is the only option.

Treatments in the same experiment can mix the two approaches — one treatment can override config on the control version while another points at a separate version.

### Traffic split

Each variant, including control, has its own traffic percentage. Percentages must be whole numbers, at least 1% per variant, and must sum to 100% before the experiment can start. The traffic bar above the table shows the current allocation.

<Tip>
  Prefer balanced splits (50/50 for two variants, 33/33/34 for three) when possible. Uneven splits reduce statistical power and require more runs to reach confident results.
</Tip>

### Renaming and removing variants

Open a variant's actions menu (the `…` icon at the end of its row) to:

* **Rename Control…** or **Rename Treatment…** — give the variant a name that describes what it tests. Names must be unique within the experiment.
* **Lock Version** — lock the variant's workflow version so it can't be edited while the experiment runs.
* **Remove** — available on treatments only. A confirmation dialog names the treatment and the traffic percentage that returns to control; the treatment's version selection and config overrides are lost.

An experiment always keeps its control and at least one treatment, so the last treatment can't be removed.

## Configure metrics

Metrics determine how you measure the difference between variants. Configure them in draft mode — they auto-save as you go.

* At least **one metric** is required to start an experiment
* One metric must be marked as the **primary metric** (the first one is primary by default)
* Each metric has a **direction**: `higher is better` or `lower is better`

There are two metric types:

* **Default metrics** — predefined metrics from the platform catalog (voice quality, northstar pass rates, latency). See the [metrics reference](03-Experiment-metrics.md) for the full list.
* **Custom metrics** — user-defined metrics built from node outputs. See [custom metrics](03-Experiment-metrics.md#custom-metrics) for details.

A custom metric's source nodes are mapped for every variant in the experiment. When all variants run the same version, one mapping is shared across them; when versions differ, each variant gets its own node and output selection. Adding, removing, or repointing a variant preserves the mappings you already made for the others.

## Start the experiment

Once variants and at least one metric are configured, click **Start** to activate traffic splitting.

<Warning>
  Workflow versions participating in an active experiment are **locked** — you cannot unpublish or edit them. To make changes, finish or stop the experiment first.
</Warning>

After starting, the experiment moves to active mode and the draft editor becomes read-only. You can monitor results in the [analysis dashboard](04-Analyzing-results.md).

---

Fuente original: https://docs.happyrobot.ai/experiments/creating-experiments
