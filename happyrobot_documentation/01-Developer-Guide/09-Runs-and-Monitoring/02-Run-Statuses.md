---
title: "Run Statuses"
description: "Understanding run lifecycle and status codes"
---

# Run Statuses

> Understanding run lifecycle and status codes

Every run moves through a series of statuses as it executes. Understanding these statuses helps you monitor workflows, debug failures, and build automation around run outcomes.

## Status lifecycle

A run progresses through statuses in a predictable order. Most runs follow the path: **scheduled** → **running** → **completed**, but failures, cancellations, and special conditions create alternate paths.

```
scheduled → running → completed
                   → failed
                   → canceled
```

## Status reference

| Status        | Badge color | Description                                                                                                           |
| ------------- | ----------- | --------------------------------------------------------------------------------------------------------------------- |
| **Scheduled** | Purple      | The run has been created but execution hasn't started yet. Common for outbound call campaigns where calls are queued. |
| **Running**   | Blue        | The run is actively executing nodes. For voice calls, this means the conversation is in progress.                     |
| **Completed** | Green       | All nodes executed successfully and the workflow finished normally.                                                   |
| **Failed**    | Red         | One or more nodes encountered an error that prevented the workflow from completing.                                   |
| **Canceled**  | Yellow      | The run was manually canceled by a user or programmatically via the API.                                              |

## Status details

### Scheduled

A run enters `scheduled` status when the trigger fires but execution is deferred. This happens in several scenarios:

* **Outbound calls** are queued and wait for the batcher to process them (typically within 1 second)
* **Business hours** are enabled and the current time is outside the configured window
* **Concurrency limits** are reached and the run is waiting for capacity

Scheduled runs can be **canceled** before they start executing. Once a scheduled run begins processing, it transitions to `running`.

### Running

The `running` status indicates active execution. For voice calls, this means the agent is on the line. For non-voice workflows, nodes are being processed in sequence.

Running runs can be **canceled** from the run details panel or via the API. Canceling a running run immediately terminates all in-progress activity.

### Completed

A `completed` run finished all nodes successfully. This is the expected outcome for most runs. The run details panel shows full execution data including:

* All node outputs and data
* Complete transcripts and recordings (for voice runs)
* Credit usage and performance metrics
* Duration from trigger to completion

### Failed

A run enters `failed` status when an unrecoverable error occurs during execution. Common failure causes include:

* An integration action returns an error (e.g., API timeout, authentication failure)
* A voice call fails to connect (e.g., invalid phone number, carrier rejection)
* A node encounters a runtime error (e.g., missing required variable, invalid data format)

Failed runs show error details in the run details panel — look for red error indicators on individual nodes to identify exactly where the failure occurred.

<Tip>
  When a voice agent node fails, the platform supports **retrying failed activities** internally. Check the node output in the run details to see if a retry was attempted and its outcome.
</Tip>

#### Voice session failure reasons

When a voice session ends in a failure, the run timeline names the reason. Use it to tell a telephony problem apart from an agent problem before you start digging through the transcript.

| Reason                       | What it means                                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `sip_call_never_connected`   | The call never connected — the carrier rejected the dial or no answer was received.                               |
| `sip_user_unavailable`       | The recipient was unavailable (line busy, out of service).                                                        |
| `sip_user_rejected`          | The recipient rejected the call.                                                                                  |
| `sip_trunk_failure`          | The SIP trunk reported a failure delivering the call.                                                             |
| `sip_call_error`             | The SIP call ended with an error status.                                                                          |
| `connection_timeout`         | The call timed out before connecting.                                                                             |
| `media_failure`              | A media (audio) failure ended the call.                                                                           |
| `join_failure`               | The participant failed to join the call.                                                                          |
| `transport_failure`          | An unrecoverable transport failure ended the call.                                                                |
| `agent_loop_error`           | The agent hit an internal error during the call.                                                                  |
| `start_agent_error`          | The agent failed to start.                                                                                        |
| `prompt_too_large`           | The agent's assembled prompt exceeded what the model provider accepts, so the session failed before it could run. |
| `agent_config_failed`        | The agent's configuration could not be loaded.                                                                    |
| `voice_bootstrap_failed`     | The voice agent failed to start up.                                                                               |
| `room_join_failed`           | The agent failed to join the call.                                                                                |
| `outbound_sip_create_failed` | The outbound call could not be placed.                                                                            |

<Tip>
  `prompt_too_large` almost always means something oversized was interpolated into the prompt — an unfiltered API or webhook response, or a knowledge base result with no cap. Check the resolved prompt on the prompt node's row in the **Details** tab, then trim the offending variable at its source. For tool results, hide the fields the agent doesn't need in the tool's [Tool Call Result](../04-Tools/03-Tool-Call-Result.md) panel.
</Tip>

### Canceled

Runs are canceled when a user or API call explicitly stops execution. A run can only be canceled when its status is `scheduled` or `running`.

When a run is canceled:

* Active voice calls are terminated
* Pending node executions are skipped
* The run status changes to `canceled` immediately
* No further workflow logic executes

## Node-level statuses

Individual nodes within a run track their own statuses independently from the run itself. When reviewing run details, you may see node outputs with these additional statuses:

* **Not started** — The node hasn't begun execution yet
* **Skipped** — The node was bypassed (e.g., a condition branch that wasn't taken)
* **Succeeded** — The node completed successfully

These statuses appear on individual step outputs in the run details panel, not on the run as a whole.

## Filtering by status

### In the platform

Use the **Status** filter in the runs table to view runs in specific states. You can select multiple statuses simultaneously — for example, showing all `failed` and `canceled` runs to review issues.

### Via the API

Pass the `status` query parameter when listing runs:

<CodeGroup>
  ```bash cURL theme={null}
  # List only failed runs
  curl -X GET "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&status=failed" \
    -H "Authorization: Bearer hr_live_abc123def456"
  ```

  ```python Python theme={null}
  import requests

  # List only failed runs
  response = requests.get(
      "https://platform.happyrobot.ai/runs/",
      headers={"Authorization": "Bearer hr_live_abc123def456"},
      params={
          "use_case_id": "YOUR_USE_CASE_ID",
          "status": "failed",
      },
  )

  failed_runs = response.json()
  ```

  ```javascript Node.js theme={null}
  // List only failed runs
  const response = await fetch(
    "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&status=failed",
    {
      headers: {
        Authorization: "Bearer hr_live_abc123def456",
      },
    }
  );

  const failedRuns = await response.json();
  ```
</CodeGroup>

## Canceling runs via API

Cancel a running or scheduled run programmatically:

<CodeGroup>
  ```bash cURL theme={null}
  curl -X POST "https://platform.happyrobot.ai/runs/RUN_ID/cancel" \
    -H "Authorization: Bearer hr_live_abc123def456"
  ```

  ```python Python theme={null}
  import requests

  response = requests.post(
      "https://platform.happyrobot.ai/runs/RUN_ID/cancel",
      headers={"Authorization": "Bearer hr_live_abc123def456"},
  )

  print(response.json())  # {"status": "canceled"}
  ```

  ```javascript Node.js theme={null}
  const response = await fetch(
    "https://platform.happyrobot.ai/runs/RUN_ID/cancel",
    {
      method: "POST",
      headers: {
        Authorization: "Bearer hr_live_abc123def456",
      },
    }
  );

  const result = await response.json();
  console.log(result);  // { status: "canceled" }
  ```
</CodeGroup>

<Warning>
  Canceling a run is immediate and irreversible. Active voice calls will be disconnected and downstream nodes will not execute. Only cancel runs when you're certain you want to stop execution.
</Warning>

## Business hours and status

When a workflow has business hours enabled, the run's behavior depends on the call type:

* **Outbound calls** outside business hours are queued with `scheduled` status until business hours resume
* **Inbound calls** are always processed immediately regardless of business hours (unless explicitly configured otherwise)

Runs that were started outside business hours are tracked with a special indicator in the run details, and you can filter for them using the **Business Hours** filter in the runs table.

## Next steps

<CardGroup cols={3}>
  <Card title="Runs overview" icon="list-check" href="01-Runs-Overview.md">
    Learn about the runs table, filtering, and export.
  </Card>

  <Card title="Transcripts" icon="message" href="03-Transcripts-and-Messages.md">
    Read conversation transcripts and execution timelines.
  </Card>

  <Card title="Annotations" icon="tags" href="05-Annotations.md">
    Mark runs as correct, incorrect, or critical for quality tracking.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/runs/run-statuses
