---
title: "Workflow Run Dumps"
description: "Automatically persist workflow run outputs into a Twin table"
---

# Workflow Run Dumps

> Automatically persist workflow run outputs into a Twin table

A **workflow run dump** writes one row into a Twin table every time a workflow run completes. You define the table once, map workflow variables to columns, and HappyRobot persists the data for you — no Write to Twin node required inside the workflow.

Dumps are the easiest way to build audit trails, accumulate analytics rows, or store run outcomes for reporting without touching the workflow itself.

## How a dump works

<Steps>
  <Step title="You connect a dump to a workflow">
    Each dump is linked to a single workflow (use case). Every completed run of that workflow can write a row.
  </Step>

  <Step title="You map columns to variables">
    For each column in the dump table, you pick a workflow variable or node output. When a run finishes, HappyRobot reads the variable values and writes them into the row.
  </Step>

  <Step title="A row is inserted after each completed run">
    The row appears in the table within seconds of the run finishing. Failed runs are skipped — only completed runs trigger a dump.
  </Step>
</Steps>

## Creating a dump

<Steps>
  <Step title="Open the Twin workspace">
    Navigate to **Twin** in the sidebar.
  </Step>

  <Step title="Create a new dump">
    Click **New dump** and select the workflow this dump should listen to. Each dump is bound to one workflow.
  </Step>

  <Step title="Name the dump table">
    Table names follow the same rules as regular Twin tables: lowercase letters, numbers, and underscores; must start with a letter or underscore; max 63 characters.
  </Step>

  <Step title="Define columns and map variables">
    For each column:

    * **Name** — the column name in the resulting Twin table
    * **Type** — one of `text`, `uuid`, `int8`, `float8`, `timestamp`, `boolean`, or `jsonb`
    * **Variable** — the workflow variable or node output to write into this column on each run
    * **Primary key** — optional; mark a column as the primary key to drive [upsert behavior](#upsert-and-deduplication)

    Use the `@` picker to choose any node output or workflow-runtime variable.
  </Step>

  <Step title="(Optional) Configure a backfill">
    Check **Also start a backfill** to populate historical completed runs at the same time. Pick a date range and the dialog estimates how many runs fall in the window. See [backfilling historical runs](#backfilling-historical-runs).
  </Step>

  <Step title="Save">
    Save the dump. The table is created and dumps begin populating from the next completed run.
  </Step>
</Steps>

## Creating a dump programmatically

You don't have to build a dump in the UI — you can create one from the [API](https://docs.happyrobot.ai/api-reference) or an AI assistant:

* **API** — `POST /twin/dump` with a `workflowId` and `tableName`. The server resolves the workflow's variable catalog and binds a column to every variable by default. Pass `include` to capture only a subset of variables (by name or `group_id.variable_id`), and `pk` to use a stable variable (such as a load ID) as the primary key instead of a synthetic `run_id`.
* **Twin MCP** — the [`create_workflow_dump`](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md) tool wraps the same endpoint, so an assistant connected to the [Twin MCP server](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md) can stand up a dump table for you.

Once created, the dump behaves exactly like one built in the UI — completed runs start populating rows immediately. To backfill historical runs, open the dump table in the Twin workspace.

A table can have only one dump configuration, so creating a dump for a table that already has one updates that configuration instead of adding a second.

## Deleting a dump

Deleting a dump stops run capture. Whether the table and its rows survive is up to you:

* **API** — `DELETE /twin/dump/{tableName}` removes the run-capture configuration and keeps the table and its data. Add `?dropTable=true` to also drop the physical table and everything in it.
* **Twin MCP** — the [`delete_workflow_dump`](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md) tool wraps the same endpoint and takes the same `dropTable` choice, so you can ask an assistant to stop a dump. Use it instead of `drop_table` for dump tables — dropping the table alone would leave the capture configuration behind.

The endpoint returns `404` when the table has no dump configuration in your workspace.

<Warning>
  `dropTable=true` is irreversible — the table and every row that was ever dumped into it are deleted. Leave it off if you only want to stop capturing new runs.
</Warning>

## Built-in workflow runtime variables

Two variables are always available as column sources, regardless of which workflow you're dumping:

| Variable           | Description                                                                                  |
| ------------------ | -------------------------------------------------------------------------------------------- |
| `__run_id__`       | The unique ID of the completed run. Map this to a `uuid` primary key to deduplicate cleanly. |
| `__completed_at__` | The UTC timestamp when the run finished. Useful as a sort or partition key.                  |

<Tip>
  Map a primary-key column to `__run_id__` whenever possible. This makes dumps idempotent — re-running a backfill or replaying a run won't create duplicate rows.
</Tip>

## Upsert and deduplication

If you mark a column as the **primary key**, the dump performs an `INSERT … ON CONFLICT … DO UPDATE` — re-writing a row for the same key updates the existing row instead of creating a duplicate.

Without a primary key, every run produces a new row. That's fine for append-only audit trails, but it makes retries and backfills risky. Most dumps should pick `__run_id__` as the primary key for safety.

## Editing column mappings

Open the dump in the Twin workspace and click **Edit mappings** to change which workflow variable maps to which column.

You can:

* Re-bind a column to a different variable via the `@` picker.
* Add columns (name, type, variable).
* Delete columns from the mapping.

Use the **Batch variables** dialog to assign many variables at once when a workflow has lots of node outputs.

<Note>
  You can change which variable feeds a column, but you can't change a column's **name**, **type**, or **primary-key** flag from the mapping editor. To restructure the table itself, use [Edit columns](02-Managing-Tables.md#editing-columns) or drop and recreate the dump.
</Note>

## Pausing and resuming a dump

Toggle the status switch on a dump to pause it. While paused, runs of the linked workflow complete normally — they just don't write rows. Resume to start dumping again.

Pause is useful when:

* You're migrating column mappings and don't want partial data
* The downstream consumer of the table is down for maintenance
* You're experimenting with a workflow and don't want noisy test rows

## Backfilling historical runs

Backfills replay completed workflow runs into a dump table so historical data sits alongside rows added going forward.

### Starting a backfill at creation

In the **New dump** sheet, scroll to **Also start a backfill** and check it. Pick a **From** and **Until** datetime. The sheet shows an estimate of how many completed runs fall in the window before you submit. Save the dump — the backfill is queued automatically once the table is created.

### Starting a backfill on an existing table

<Steps>
  <Step title="Open the dump table">
    From the Twin workspace, open the dump table.
  </Step>

  <Step title="Click Backfill">
    Click **Backfill** in the toolbar to open the backfill sheet.
  </Step>

  <Step title="Create a backfill job">
    Click **Create backfill**, set the time window, and submit. The new job appears at the top of the list.
  </Step>
</Steps>

### Backfill job tracking

The backfill sheet lists every job for the table with:

* **Status** — queued, running, succeeded, failed, or canceled
* **Window** — the From / Until range
* **Processed / succeeded / failed counts** — how many runs the job has handled
* **Creator and creation time** — who started the job and when
* **Last error** — if the job failed, the most recent error message

Only one backfill can be queued or running per table at a time. Subsequent backfills wait until the active job finishes.

<Info>
  **Backfill limits (beta):**

  * Maximum window: **90 days**
  * Maximum runs per job: **20,000** — narrow the window or run multiple smaller backfills if you exceed this cap
  * Only one active job per dump table

  Map a primary-key column to `__run_id__` before backfilling. Without a stable primary key, retries can insert duplicate rows.
</Info>

## When to use a dump vs. a Write to Twin node

| Use a dump when…                            | Use a Write to Twin node instead when…                 |
| ------------------------------------------- | ------------------------------------------------------ |
| Every completed run should produce one row  | Some runs should write, others shouldn't (conditional) |
| You want the same shape across all runs     | The row shape varies based on workflow logic           |
| You don't want to add nodes to the workflow | The write needs to happen *during* the run, not after  |
| You need to backfill historical runs        | You need to write multiple rows in a single run        |

Dumps and Write nodes can also coexist — the dump captures the "final state" snapshot, while Write nodes inside the workflow record intermediate steps.

## Next steps

<CardGroup cols={3}>
  <Card title="Workflow variables" icon="brackets-curly" href="../02-Workflows/07-Variables.md">
    Use the `@` picker to pull any variable into your dump.
  </Card>

  <Card title="Managing tables" icon="table" href="02-Managing-Tables.md">
    Add columns, foreign keys, and indexes to a dump table.
  </Card>

  <Card title="SQL console" icon="terminal" href="05-SQL-Console-and-Capacity.md">
    Query the dump table directly for analytics.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/twin/workflow-run-dumps
