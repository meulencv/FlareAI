---
title: "Runs Overview"
description: "Monitor and manage workflow executions"
---

# Runs Overview

> Monitor and manage workflow executions

A run is a single execution of a workflow. Every time a trigger fires — a webhook call, an incoming phone call, a scheduled event — HappyRobot creates a run and processes each node in sequence. The **Runs** tab gives you a complete view of every execution, with real-time status updates, full transcripts, recordings, and node-level outputs.

## The runs table

The runs table is the primary interface for monitoring workflow executions. Select a workflow from the sidebar and click the **Runs** tab to see all runs for that workflow.

Each row in the table shows:

| Column             | Description                                                                                                                                                              |
| ------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Timestamp**      | When the run was triggered                                                                                                                                               |
| **Status**         | Current execution state — completed, failed, running, canceled, or scheduled                                                                                             |
| **Version**        | Which workflow version the run executed on                                                                                                                               |
| **Environment**    | Execution environment (Staging or Production)                                                                                                                            |
| **Parent run**     | For loop [child runs](../03-Core-Nodes/10-Loops.md#child-runs), the short ID of the run that spawned this one (or `—` if none). Hidden by default — enable it from the column menu. |
| **Custom columns** | Node output values configured per workflow (see below)                                                                                                                   |

Click any row to open the run details panel on the right side of the screen.

### Real-time updates

The runs table updates in real time via WebSocket. When a new run starts or a status changes, the table reflects it immediately — no manual refresh needed. A visual indicator appears when new activity arrives while you're viewing the table.

To temporarily freeze the table while reviewing runs, click **Pause Realtime Updates** in the header. While paused, no new runs appear and no status changes are applied to the visible rows. Click **Resume Realtime Updates** to re-enable live updates — the table refreshes immediately to show the latest state.

### Custom columns

You can add custom columns to the runs table to surface specific node output values directly in the list view. This is useful when you want to scan key data points — like a caller's name, extracted order ID, or classification result — without opening each run individually.

To add a custom column:

1. Click the **+** button in the table header.
2. Select a node output field from the dropdown.
3. The column appears in the table, populated with values from each run.

Custom columns are saved per workflow and visible to all team members. Click the column menu in the table header to show or hide any column. Drag column headers to reorder them — the new order is preserved between sessions.

Tool call **parameters** are available as custom columns too, including the parameters of tools exposed by an [MCP server](../04-Tools/05-MCP-Tools.md). Because a tool's parameters are its inputs rather than its outputs, they're read from the node's input when no matching output value exists — so a column on, say, an MCP tool's `load_id` argument populates from the values the agent actually passed.

### Filtering

Use the filter bar above the table to narrow results. Filters can be combined and persist in the URL, so filtered views are shareable.

<AccordionGroup>
  <Accordion title="Run ID filter">
    Narrow the table to one or more specific runs by their run ID. Choose **Equals** to match a single ID, or **In list** to match several. Useful for jumping straight to a run someone shared with you by ID.
  </Accordion>

  <Accordion title="Status filter">
    Filter runs by one or more statuses. Select from: **Completed**, **Failed**, **Running**, **Canceled**, and **Scheduled**. See [Run Statuses](02-Run-Statuses.md) for details on each status.
  </Accordion>

  <Accordion title="Date range filter">
    Restrict runs to a specific time window using **From** and **To** date pickers. Useful for investigating incidents or reviewing a specific day's activity.
  </Accordion>

  <Accordion title="Version filter">
    Show only runs that executed on a specific workflow version. This helps you compare behavior across version changes.
  </Accordion>

  <Accordion title="Business hours filter">
    Filter runs that started during or outside your configured business hours. Helpful for understanding off-hours call patterns.
  </Accordion>

  <Accordion title="Custom column filters">
    Filter by values in any custom column you've added. Choose an operator first, then enter a value:

    | Operator                                                                    | Matches                                                                                                                             |
    | --------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
    | **Equals** / **Not equal**                                                  | Exact value match, e.g. `caller_intent` equals `"billing question"`.                                                                |
    | **Like (case-sensitive)** / **iLike (any case)**                            | Text pattern with `%` wildcards — `%` matches any text, e.g. `%value%`.                                                             |
    | **Is empty** / **Is not empty**                                             | The field has no value, or has any value. These operators take no value to enter.                                                   |
    | **Greater than** / **Greater or equal** / **Less than** / **Less or equal** | Numeric and duration comparisons (`>`, `≥`, `<`, `≤`) — useful for call length, latency thresholds, or any numeric extracted value. |
    | **Is between** / **Is not between**                                         | Value inside or outside a numeric range.                                                                                            |
    | **In list**                                                                 | Value matches any of several values you provide.                                                                                    |
  </Accordion>
</AccordionGroup>

### Saved views

A view captures a combination of active filters and visible column configuration so you can switch between common setups instantly.

To save the current state as a view:

1. Apply the filters and column visibility you want to save.
2. Click the **Save as view** button in the table header.
3. Give the view a name (and an optional description) and click **Save**.

Saved views appear as tabs at the top of the runs table. Click a view tab to apply it. Right-click a view tab to rename, update (overwrite with the current filters and columns), or delete it.

Views are saved per workflow and visible to all team members in your organization.

#### Ask each time (dynamic views)

When saving a view, you can turn any filter into a **parameter** instead of storing a fixed value. In the save dialog, toggle **Ask each time** on a filter pill — its value is replaced with a placeholder, and the view prompts you to enter a value for that filter every time you apply it.

This is useful for reusable views where the value changes each time — for example, a "Runs for a caller" view that asks for the phone number on each use, or a "Runs by ID" view that prompts for the run ID. A view can have multiple parameters; each one is prompted when you apply the view.

### Search

Use the search bar to find runs by ID or data values. Search queries match against run IDs and the data fields associated with each run.

### Loading more runs

The table uses infinite scrolling — as you scroll toward the bottom, older runs load automatically. There is no page size to configure.

## Run details panel

Click any run to open the details panel. The panel has three tabs: **Details**, **Analytics**, and **Graph**.

The panel header carries the run's ID with a copy button, followed by the **workflow version** the run executed on, the number of steps, and the run's duration — so you can tell which version produced a result without cross-checking the table's Version column.

### Details tab

The details tab shows the full execution timeline — every node that ran, every message exchanged, and every output produced. The view updates in real time for active runs, with new messages appearing as they arrive.

For voice agent runs, the details tab includes:

* Full conversation transcript with timestamps
* [Live listening](04-Recordings.md#listening-to-a-call-in-progress) while the call is still in progress
* Call recording playback (synced to transcript)
* Tool call results and integration responses
* Event markers (caller joined, call ended, transfer initiated, etc.)
* Artifacts — images, audio files, PDFs, and documents attached during the conversation

For non-voice runs (email, webhook, scheduled), the details tab shows:

* Node-by-node execution results
* Input/output data for each step
* Error messages for failed nodes
* Email previews for email-related nodes

See [Transcripts and Messages](03-Transcripts-and-Messages.md) for a detailed guide on reading the execution timeline.

#### Navigating loop iterations

A [Loop](../03-Core-Nodes/10-Loops.md) shows one iteration at a time in the timeline, with a pager in the loop's header. Use the arrows to step to the previous or next iteration, or open the **⌄** menu next to the pager and type an iteration number to jump straight to it — useful when a loop ran hundreds of times and the failure is somewhere in the middle. Numbers are 1-based and out-of-range entries return no result.

The selected iteration is stored in the URL as `loop_iteration`, so a link to a run opens on the iteration you were looking at. Nested loops are restored too. Selecting a different run clears the iteration.

### Analytics tab

The analytics tab shows performance metrics for the run, including:

* **Credit usage** — Breakdown of credits consumed by event type (STT, TTS, LLM, etc.). The LLM row is expandable — click it to see a per-node breakdown, and expand each node further to see costs by individual model.
* **Call performance** — Average sentiment, average latency, and total interactions
* **Agent data** — Session duration, input/output LLM tokens
* **Charts** — Sentiment over time, latency per message, and interaction counts

For runs with multiple voice or text sessions (e.g., a warm transfer or callback), tabs let you switch between sessions to view metrics independently.

See [Run Statuses](02-Run-Statuses.md) for more on how status affects what's shown in the analytics tab.

### Graph tab

The graph tab visualizes the workflow execution as a node graph. Each node in the graph represents a step that ran during the execution, with edges showing the path the workflow took.

Nodes are color-coded by their execution status:

| Color  | Status    |
| ------ | --------- |
| Green  | Succeeded |
| Red    | Failed    |
| Gray   | Skipped   |
| Blue   | Running   |
| Yellow | Pending   |

Use the **Vertical / Horizontal** toggle in the graph toolbar to switch the layout orientation. Vertical (default) flows top-to-bottom; Horizontal flows left-to-right, which can be easier to read for wide workflows with many parallel branches. Use the zoom controls to navigate larger graphs. Click the **fit-to-view** button (expand icon) to reset the zoom and center the graph. You can also zoom with Ctrl/Cmd + scroll wheel.

For runs that are still in progress, the graph refreshes automatically every few seconds so you can watch execution advance in real time.

#### Loop iterations in large graphs

A run that expands a [Loop](../03-Core-Nodes/10-Loops.md) inline can produce thousands of nodes. When the graph has more than 100 nodes, loop iterations are paginated: the graph draws one iteration at a time and the loop node gets a pager showing the selected iteration and the total (`3 / 24`). Use the arrows to step through iterations, or click the chevron and type an iteration number to jump straight to it. Nested loops each get their own pager, so you can drill into one iteration of an outer loop and page through the inner loop inside it. Smaller graphs keep showing every iteration at once.

Click any node to open a detail panel. Its header shows the node name and a badge with the node's execution status, and its **⋯** menu has **Copy node ID** and, when the node has one, **Copy persistent ID** — useful when correlating a run against the API or a support request. The panel body shows:

* **Input** — the data passed into the node, formatted as JSON with a copy button
* **Output** — the data produced by the node, formatted as JSON with a copy button
* **Config** — the node's static configuration (shown when non-empty)
* **Variables** — all workflow variable values at the point this node executed; click **View Variables** to expand the section, then type in the search box to filter by variable name

## Run actions

The run details panel header includes an actions menu with the following options:

| Action                | Description                                                                     |
| --------------------- | ------------------------------------------------------------------------------- |
| **Copy Link**         | Copy a shareable URL to this specific run                                       |
| **Cancel Run**        | Cancel a run that is currently `running` or `scheduled` (requires confirmation) |
| **Mark as Correct**   | Add a "correct" annotation with optional notes                                  |
| **Mark as Incorrect** | Add an "incorrect" annotation with optional notes                               |
| **Mark as Critical**  | Add a "critical" annotation with optional notes                                 |
| **Remove Annotation** | Remove an existing annotation from the run                                      |

See [Annotations](05-Annotations.md) for details on the quality assurance system.

<Info>
  Canceling a run stops all in-progress activity — active voice calls are terminated, pending node executions are skipped, and the run status changes to `canceled`. This action cannot be undone.
</Info>

## Cancel all runs

To stop all active executions for a workflow at once, click the **Cancel All Runs** button in the runs page header. This button is highlighted in orange when any runs have a `running`, `scheduled`, or `pending` status.

<Warning>
  Canceling all runs immediately terminates every active execution — active voice calls are ended, pending nodes are skipped, and all affected runs move to `canceled` status. This action cannot be undone. A confirmation dialog requires you to type the workflow name before proceeding.
</Warning>

## Exporting runs

Click the **Download Reports** button above the runs table to export run data as CSV files.

<Steps>
  <Step title="Open the export dialog">
    Click the download icon in the runs table header to open the reports dialog.
  </Step>

  <Step title="Configure the export">
    Select a **date range** (from/to) and one or more **statuses** to include. Only runs matching your criteria will be exported.
  </Step>

  <Step title="Generate the report">
    Click **Generate** to queue the export. Reports are processed asynchronously — you'll receive an email notification when the CSV is ready.
  </Step>

  <Step title="Download">
    Return to the reports dialog to download your CSV. Reports are grouped by date, with recent exports shown first. Each report shows the filters that were applied when it was generated.
  </Step>
</Steps>

<Tip>
  Export reports are retained for later access. You can return to the dialog at any time to download previously generated reports without re-running the export.
</Tip>

## Accessing runs via API

You can list, filter, and manage runs programmatically using the REST API.

<CodeGroup>
  ```bash cURL theme={null}
  curl -X GET "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&page=1&page_size=50&status=completed" \
    -H "Authorization: Bearer hr_live_abc123def456"
  ```

  ```python Python theme={null}
  import requests

  response = requests.get(
      "https://platform.happyrobot.ai/runs/",
      headers={"Authorization": "Bearer hr_live_abc123def456"},
      params={
          "use_case_id": "YOUR_USE_CASE_ID",
          "page": 1,
          "page_size": 50,
          "status": "completed",
      },
  )

  runs = response.json()
  print(f"Total runs: {runs['pagination']['totalRecords']}")
  ```

  ```javascript Node.js theme={null}
  const response = await fetch(
    "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&page=1&page_size=50&status=completed",
    {
      headers: {
        Authorization: "Bearer hr_live_abc123def456",
      },
    }
  );

  const runs = await response.json();
  console.log(`Total runs: ${runs.pagination.totalRecords}`);
  ```
</CodeGroup>

**Available query parameters:**

| Parameter              | Type     | Description                                                                 |
| ---------------------- | -------- | --------------------------------------------------------------------------- |
| `use_case_id`          | UUID     | Required. The workflow to list runs for                                     |
| `page`                 | integer  | Page number (default: 1)                                                    |
| `page_size`            | integer  | Results per page, 1–2000 (default: 100)                                     |
| `sort`                 | string   | `asc` or `desc` (default: `desc`)                                           |
| `status`               | string   | Filter by status: `scheduled`, `running`, `completed`, `canceled`, `failed` |
| `start_date`           | datetime | Runs created after this timestamp                                           |
| `end_date`             | datetime | Runs created before this timestamp                                          |
| `completed_start_date` | datetime | Runs completed after this timestamp                                         |
| `completed_end_date`   | datetime | Runs completed before this timestamp                                        |
| `annotation`           | string   | Filter by annotation: `correct`, `incorrect`, `critical`                    |

Each run in the response includes an `execution_environment` field — `development`, `staging`, or `production` — so you can tell which [environment](../02-Workflows/09-Environments.md) a run executed in without fetching the version. It is `null` for runs recorded before the field existed. The workflow-scoped `GET /workflows/{workflow_id}/runs` endpoint (and the SDK's [`workflows.listRuns`](../../02-Developer-Tools/02-TypeScript-SDK/06-Workflows.md)) returns it too.

## Keyboard shortcuts

| Shortcut   | Action                               |
| ---------- | ------------------------------------ |
| `Esc`      | Close the run details panel          |
| `Ctrl + F` | Expand or collapse the details panel |

## Next steps

<CardGroup cols={3}>
  <Card title="Run statuses" icon="circle-dot" href="02-Run-Statuses.md">
    Understand the run lifecycle and what each status means.
  </Card>

  <Card title="Transcripts" icon="message" href="03-Transcripts-and-Messages.md">
    Read conversation transcripts and execution timelines.
  </Card>

  <Card title="Recordings" icon="circle-dot" href="04-Recordings.md">
    Access and play back call recordings.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/runs/overview
