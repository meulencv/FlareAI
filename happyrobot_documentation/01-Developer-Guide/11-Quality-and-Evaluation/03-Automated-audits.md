---
title: "Automated audits"
description: "Every run is automatically evaluated against your northstars"
---

# Automated audits

> Every run is automatically evaluated against your northstars

Automated audits evaluate every workflow run against your [northstars](02-Northstars.md) using an LLM judge. The system reads the conversation transcript, checks each northstar, and produces a grade — **passed**, **failed**, or **not applicable**. This gives you a continuous, automated view of agent quality without manual review.

## How audits work

When a run completes, the audit system:

1. Retrieves the conversation transcript and any tool call data
2. Evaluates the run against each enabled northstar for the relevant prompt node
3. Produces an **audit remark** for each northstar with a grade, correction (if failed), and reasoning
4. Aggregates results into pass rates and trends

Audits run automatically. You can configure the **sampling rate** to control what percentage of runs are audited — from 0% (disabled) to 100% (every run).

## Audit remarks

Each audit produces one remark per northstar. A remark includes:

| Field                 | Description                                                                  |
| --------------------- | ---------------------------------------------------------------------------- |
| **Grade**             | `passed`, `failed`, or `not_applicable`                                      |
| **Correction**        | What the agent should have done differently (only for failures)              |
| **Correction reason** | Why the agent's behavior was incorrect (only for failures)                   |
| **Message IDs**       | The specific messages in the transcript that were relevant to the evaluation |

Audit remarks are also available programmatically. Fetch a single remark by ID or list a workflow's remarks (filtered by northstar, grade, or status) through the [Platform API](https://docs.happyrobot.ai/api-reference/overview) or the `manage_audits` tool on the [Workflows MCP server](../../02-Developer-Tools/01-MCP/03-Workflows-MCP.md).

You can also ask [Frontal](../02-Workflows/03-Frontal-AI-assistant.md) about them directly — "why is this northstar failing?" — and it reads the remarks alongside the run transcript, tool calls, workflow version, and prompt. See [Investigate northstar audit results](../02-Workflows/03-Frontal-AI-assistant.md#investigate-northstar-audit-results).

## Viewing audit results

Navigate to the **Audits** tab in the workflow editor to see audit results. The page has several sections:

<Note>
  A workflow's Audits page covers everything that happened in or beneath its own runs, however those runs started. A workflow invoked by a [Call Workflow](../03-Core-Nodes/12-Call-Workflow.md) node therefore reports its own remarks on its own page, and the calling workflow also sees them under the run it started — so the same remark can appear on both pages. Organization-level metrics still count each run once.
</Note>

### Stats cards

Two summary cards at the top show:

* **24h northstar pass rate** — Percentage of audit remarks that passed in the last 24 hours
* **24h average run score** — Average score across all audited runs

### Northstar audit table

The main table lists every northstar with its aggregate audit metrics. You can:

* **Search** by northstar name
* **Filter** by version, enabled status, or category
* **Click a row** to open the detail sidebar

### Detail sidebar

When you select a northstar, the sidebar shows:

* The northstar's description and configuration
* A list of individual audit remarks (scrollable with infinite loading)
* Each remark shows the grade, correction, and a link to the source run
* Feedback buttons for each remark

### Time-series view

Track pass rates over time to spot trends and regressions. The chart shows passed vs. failed audit counts bucketed by time period, so you can see how quality changes after prompt updates or version deployments.

### Version comparison

Filter audit results by workflow version to compare quality across versions. This is useful for validating that a new version maintains or improves quality before setting it live.

### What the page covers

A workflow's audit page reports on everything that happened in or under its own runs — including runs it was handed as a callee of a [Call Workflow](../03-Core-Nodes/12-Call-Workflow.md) node, and any runs those spawned in turn. It doesn't matter how the run was started: if the run belongs to this workflow, its remarks show up here.

That means a single remark can appear on more than one workflow's page — once on the workflow that executed it, and once on the caller whose run it ran under. Org-level metrics and pass rates are still counted once per run, so nothing is double-counted in the aggregates.

## Quality flags

Quality flags are automated checks that analyze conversation metrics and flag runs that fall outside healthy thresholds. Unlike northstar audits (which evaluate behavioral quality using an LLM judge), quality flags are metric-based and fire automatically without any configuration required.

Flagged runs appear in the **Flags** subtab of the Audits page.

### Latency flags

| Flag                     | Condition                                                    |
| ------------------------ | ------------------------------------------------------------ |
| **High average latency** | Average combined assistant response latency exceeds 3,000 ms |

### Conversation flow flags

| Flag                   | Condition                                                                                          |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| **High interruptions** | The assistant interrupted the user in more than 40% of turns (requires at least 3 turns each side) |
| **High natural cuts**  | The user cut off the assistant in more than 40% of turns (requires at least 3 turns each side)     |

### Audio quality flags

Audio quality flags analyze the raw audio and transcription of a session to detect technical problems:

* **Poor or low audio quality** — Audio clarity is degraded
* **Echo detected** — Echo is present in user audio
* **High word error rate** — Transcription accuracy for user speech is poor
* **Background speaker** — Background speech or noise interferes with transcription
* **Very quiet audio** — Audio volume is too low
* **Number transcription errors** — Numbers may be transcribed incorrectly
* **Empty session** — No speech was detected

Quality flags generate [issues](05-Issues.md) that appear in the Flags subtab alongside manually created issues.

For a full analytics dashboard covering transcription accuracy, conversational dynamics, latency, and acoustic quality — including the **Top Semantic Mismatches** panel — see [Audio audits](04-Audio-audits.md).

## Node errors

The **Node Errors** subtab tracks execution failures at the node level — distinct from behavioral audit failures. Node errors occur when a workflow node throws an error during execution (e.g., an integration timeout, a malformed API response, or a code node exception).

Each error entry shows:

* The error message and affected node
* How many times the error occurred
* When it first and last appeared
* Links to sample runs with the error

## Audit feedback

The audit feedback mechanism creates a data flywheel that improves audit accuracy over time.

When reviewing an audit remark, you can mark it as:

* **Accurate** (thumbs up) — The audit correctly identified a pass or failure
* **Inaccurate** (thumbs down) — The audit got the result wrong

When marking a result as inaccurate, you're asked to attribute the error, and can add an optional comment:

* **Auditor issue** — The LLM judge made a mistake (the northstar definition is fine, but the judge misapplied it)
* **Northstar issue** — The rule is unclear or should be refined

Confirming a remark as accurate turns the conversation excerpt into an example on the northstar — a **positive** example if the remark passed, a **negative** one if it failed — so future grading has a concrete reference. Marking a remark inaccurate, or removing your feedback, takes that example back out again unless a teammate has also confirmed it.

Feedback can be given from two places:

* The **detail sidebar** on the Audits page, next to each remark
* Directly in a **run's transcript** — open the audit badge on the message and rate the remark inline. See [audit remarks](../09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#audit-remarks).

<Note>
  Rating audit remarks requires permission to view northstar audits for the workflow.
</Note>

Feedback is accepted on every audit remark, including remarks produced by northstar-graded [custom tests](06-Custom-tests.md). Reviewing scenario results is a fast way to correct a judge before it grades live traffic.

<Tip>
  Regularly reviewing audit results and providing feedback is the fastest way to improve audit accuracy. Even 10-15 minutes of feedback per week can significantly reduce false positives and false negatives.
</Tip>

Feedback can also be submitted from the API with either a user-level or an org-level [API key](../16-Account-and-Settings/06-API-Keys.md), so an external review tool can feed grades back without a key tied to a person. See [Audit remarks](../../02-Developer-Tools/02-TypeScript-SDK/11-Quality-and-testing.md#audit-remarks).

## Configuring audits

Click the **Configure** button in the audits page header to adjust settings:

* **Enable/disable** automated audits for this workflow
* **Sampling rate** — Set the percentage of runs that are audited (0-100%). Higher sampling gives more complete coverage but uses more evaluation credits.

<Note>
  Audit configuration can be updated by **workspace owners**. Other roles see the audit settings in read-only mode.
</Note>

## Next steps

<CardGroup cols={2}>
  <Card title="Issues" icon="flag" href="05-Issues.md">
    See how failed audits generate issues for tracking and resolution.
  </Card>

  <Card title="Northstars" icon="star" href="02-Northstars.md">
    Refine your northstars based on audit feedback.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/evaluate/audits
