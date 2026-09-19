---
title: "Annotations"
description: "Add annotations and notes to runs"
---

# Annotations

> Add annotations and notes to runs

Annotations let you mark runs with quality labels — **correct**, **incorrect**, or **critical** — to track how well your agents are performing. Use them to flag issues, build training datasets, and measure accuracy across your workflow volume.

## Annotation types

Each annotation type signals a different quality level:

| Annotation    | Icon        | Color  | When to use                                                                                                                                |
| ------------- | ----------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Correct**   | Checkmark   | Green  | The agent handled the run as expected — correct data extraction, appropriate responses, successful outcome                                 |
| **Incorrect** | Alert       | Orange | The agent made a mistake — wrong data extracted, inappropriate response, or missed information — but the error wasn't severe               |
| **Critical**  | Exclamation | Red    | A serious failure — the agent gave dangerous advice, lost a customer, provided completely wrong information, or violated a compliance rule |

## Adding annotations

### From the run details panel

1. Open a run and click the **actions menu** (three-dot icon) in the panel header.
2. Select **Mark as Correct**, **Mark as Incorrect**, or **Mark as Critical**.
3. Optionally, add an explanation in the text field describing what went right or wrong.
4. Click **Submit Annotation**.

The annotation appears as a colored indicator on the run — visible both in the run details header and in the runs table row.

### Updating an annotation

To change an existing annotation, open the actions menu and select a different annotation type. The previous annotation is replaced with the new one.

### Removing an annotation

To remove an annotation entirely, open the actions menu and select **Remove Annotation**. The run returns to an unannotated state.

## Annotation indicators

Annotated runs are visually marked throughout the platform:

* **Runs table** — Annotated runs show a colored icon next to the status badge, making them easy to spot when scanning the list
* **Run details header** — The run icon changes to the annotation icon with the corresponding color
* **Filtering** — Use the `annotation` query parameter in the API to retrieve runs with a specific annotation type

## Filtering by annotation via the API

Pass the `annotation` query parameter when listing runs to filter by annotation type:

<CodeGroup>
  ```bash cURL theme={null}
  # List runs marked as incorrect
  curl -X GET "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&annotation=incorrect" \
    -H "Authorization: Bearer hr_live_abc123def456"
  ```

  ```python Python theme={null}
  import requests

  # List runs marked as incorrect
  response = requests.get(
      "https://platform.happyrobot.ai/runs/",
      headers={"Authorization": "Bearer hr_live_abc123def456"},
      params={
          "use_case_id": "YOUR_USE_CASE_ID",
          "annotation": "incorrect",
      },
  )

  incorrect_runs = response.json()
  print(f"Incorrect runs: {incorrect_runs['pagination']['totalRecords']}")
  ```

  ```javascript Node.js theme={null}
  // List runs marked as incorrect
  const response = await fetch(
    "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&annotation=incorrect",
    {
      headers: {
        Authorization: "Bearer hr_live_abc123def456",
      },
    }
  );

  const incorrectRuns = await response.json();
  console.log(`Incorrect runs: ${incorrectRuns.pagination.totalRecords}`);
  ```
</CodeGroup>

## Best practices

<CardGroup cols={2}>
  <Card title="Establish review workflows" icon="list-check">
    Set a routine — daily or weekly — to review a sample of runs. Focus on failed runs and edge cases first, then spot-check completed runs to catch subtle issues the agent handled "successfully" but incorrectly.
  </Card>

  <Card title="Use corrections for training" icon="wand-magic-sparkles">
    When marking a run as incorrect, always include an explanation describing what the agent should have done differently. These correction notes become valuable for refining prompts and improving agent behavior.
  </Card>

  <Card title="Reserve critical for real impact" icon="shield-check">
    Use the **critical** annotation sparingly — reserve it for runs where the agent's behavior could cause real harm: compliance violations, lost revenue, dangerous advice, or severe customer impact. This keeps the critical label meaningful in aggregate reporting.
  </Card>

  <Card title="Track trends over time" icon="chart-line">
    Monitor annotation ratios across your run volume. A rising incorrect rate after a prompt change signals a regression. A declining critical rate after a fix confirms the improvement.
  </Card>
</CardGroup>

<Tip>
  Annotations are visible to your entire team. When reviewing runs collaboratively, annotations create a shared understanding of what "good" and "bad" agent behavior looks like — which helps align prompt engineering efforts across team members.
</Tip>

## Annotations and the quality system

Annotations feed into the broader [quality and evaluation system](../11-Quality-and-Evaluation/01-Quality-and-evaluation-overview.md). When you annotate runs, you're contributing to a data flywheel that improves automated quality checks:

* **Incorrect and critical annotations** highlight runs that the automated audit system should catch. If a run is annotated as incorrect but passed all northstar audits, that signals a gap in your northstar coverage.
* **Correct annotations** on runs that failed audits indicate false positives — the audit flagged a problem that wasn't actually there. Use the [audit feedback mechanism](../11-Quality-and-Evaluation/03-Automated-audits.md#audit-feedback) to correct these and improve future accuracy.
* **Annotation trends** complement audit pass rates. Together, they give you both a human and automated view of agent quality over time.

<Tip>
  Combine manual annotations with automated audits for the most complete quality picture. Annotations catch nuances that automated checks miss, while audits provide consistent, scalable coverage across your full run volume.
</Tip>

## Next steps

<CardGroup cols={3}>
  <Card title="Runs overview" icon="list-check" href="01-Runs-Overview.md">
    Navigate and filter your run history.
  </Card>

  <Card title="Transcripts" icon="message" href="03-Transcripts-and-Messages.md">
    Read transcripts to understand agent behavior before annotating.
  </Card>

  <Card title="Recordings" icon="circle-dot" href="04-Recordings.md">
    Listen to call recordings for audio quality review.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/runs/annotations
