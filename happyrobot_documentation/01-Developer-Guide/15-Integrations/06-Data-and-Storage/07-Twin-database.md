---
title: "Twin database"
description: "Read from and write to your organization's managed database"
---

# Twin database

> Read from and write to your organization's managed database

<Info>
  This page covers the **Read from Twin**, **Write to Twin**, and **Query Twin with SQL** workflow nodes specifically. For the full Twin feature — managing tables, polling tables, workflow run dumps, SQL console, capacity, and consuming Twin from Apps — see the [Twin section](../../08-Twin/01-Twin-Overview.md).
</Info>

Twin is a managed PostgreSQL database provisioned per organization by HappyRobot. It gives your workflows a persistent, structured store for data that needs to survive across runs — lookup tables, state, configuration, cached results, or any other tabular data your workflows need to share.

## Overview

Each organization gets a dedicated Twin database. You interact with it from workflows using three nodes:

* **Read from Twin** — query rows from a table with optional filters
* **Write to Twin** — insert or upsert a row into a table
* **Query Twin with SQL** — run a read-only SQL query for joins, aggregations, and other cases the Read node can't express

Tables and columns are managed in the [Twin workspace](../../08-Twin/02-Managing-Tables.md) — Twin nodes pick from the current schema at configuration time.

## Setting up Twin

The Twin database is provisioned automatically for your organization. To check its status and optionally deploy an API gateway:

<Steps>
  <Step title="Open Settings">
    Navigate to **Settings** and find the **Twin Database** section.
  </Step>

  <Step title="Check database status">
    The **Twin Database** card shows the current status: **Available**, **Provisioning**, or **Not provisioned**. No action is needed to provision the database — contact support if provisioning is stuck or failed.

    The status card also shows RDS-level details when available: instance class, allocated storage, current database size, storage usage, and any pending configuration changes.
  </Step>

  <Step title="Deploy the API gateway (optional)">
    If you want external applications to access your Twin database directly via REST, click **Deploy Gateway**. The gateway exposes your database as a REST API secured with JWT tokens.

    Once deployed, the settings page shows:

    * The gateway **endpoint URL** (copy it to use in external apps)
    * The required request header: `x-org-id: <your-org-id>`

    The gateway is only needed for external access. Workflow nodes connect to the database directly without it.
  </Step>
</Steps>

## Read from Twin

The **Read from Twin** node queries rows from a table and returns the results for use in subsequent nodes.

### Configuration

| Field        | Required | Description                                                                                                                                                                                   |
| ------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Table**    | Yes      | The Twin table to query                                                                                                                                                                       |
| **Filters**  | No       | Conditions to filter rows. Each filter specifies a column, an operator, and a value. All filter conditions must match for a row to be returned. Supports dynamic values (workflow variables). |
| **Order by** | No       | Sort results by a column. Select the column and choose **Ascending** or **Descending** direction. Only one sort column is supported.                                                          |
| **Limit**    | No       | Maximum number of rows to return. Supports dynamic values.                                                                                                                                    |

**Filter operators by column type:**

| Column type               | Available operators                                                         |
| ------------------------- | --------------------------------------------------------------------------- |
| Text                      | Equals, Not equal, Contains                                                 |
| Integer, Float, Timestamp | Equals, Not equal, Greater than, Less than, Greater or equal, Less or equal |
| UUID, Boolean, JSONB      | Equals, Not equal                                                           |

### Output

The node outputs the matching rows as an array. Each row is an object with keys corresponding to the table's column names.

### Example use cases

* Look up configuration values stored in a Twin table by a key variable
* Retrieve a list of items to process in a loop
* Fetch cached data that was written by a previous run

## Write to Twin

The **Write to Twin** node inserts or upserts a row into a table.

### Configuration

| Field             | Required           | Description                                                                                                                     |
| ----------------- | ------------------ | ------------------------------------------------------------------------------------------------------------------------------- |
| **Table**         | Yes                | The Twin table to write to                                                                                                      |
| **Column values** | Yes (at least one) | The column-value pairs to write. Each column specifies its name, type, and value. Supports dynamic values (workflow variables). |

### Upsert behavior

If a column is marked as the primary key (indicated in the column picker), the node performs an **upsert**: if a row with that primary key value already exists, it is updated with the new values. If no row exists, a new row is inserted.

Auto-incremented integer primary keys are read-only — they are managed by the database and cannot be set from the node.

### Example use cases

* Store run results or outcomes for later retrieval
* Maintain a running tally or state table updated each run
* Cache computed values that are expensive to recalculate

## Query Twin with SQL

The **Query Twin with SQL** node runs a **read-only** SQL query against your Twin database and returns the result rows for use in subsequent nodes. Use it when the filter-and-order options on the Read from Twin node aren't enough — for example, joins across tables, aggregations, or expressions.

### Configuration

| Field        | Required | Description                                                                                                                                               |
| ------------ | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **SQL**      | Yes      | The query to run. Must be read-only — it has to start with `SELECT` or `WITH`. Only a single statement is allowed. Type `@` to insert workflow variables. |
| **Max rows** | No       | Maximum number of rows to return. Defaults to **100**; values are clamped between **1** and **1000**.                                                     |

### Using workflow variables

Insert workflow variables into the query by typing `@` and picking the variable — it appears as a pill in the editor. Variables are passed to the database as **parameterized query values**, not interpolated into the SQL string, so they are safe against SQL injection. You never need to add quotes around a variable yourself.

```sql theme={null}
SELECT id, status, rate
FROM loads
WHERE load_id = @load_id
ORDER BY created_at DESC
```

### Formatting the query

Click **Format** above the editor to lay the query out — selected fields one per line, and `WHERE`, `GROUP BY`, `HAVING`, `ORDER BY`, `LIMIT`, `OFFSET`, and `RETURNING` each on their own line, with `AND` and `OR` indented under the clause they belong to.

Formatting only moves whitespace. Variable pills, string literals, dollar-quoted blocks, commas inside function calls, and SQL comments are left exactly as you wrote them.

### Read-only enforcement

Only read queries are allowed. The node rejects anything that isn't a single `SELECT` or `WITH` statement — including multiple statements, mutating CTEs, and any DDL/DML (`INSERT`, `UPDATE`, `DELETE`, `DROP`, and so on). To write data, use the [Write to Twin](#write-to-twin) node instead.

### Output

The node outputs:

* **rows** — an array of result rows, each an object keyed by column name
* **fields** — the returned columns and their types
* **rowCount** / **returnedRows** — how many rows the query produced and how many were returned
* **truncated** — `true` when results were cut off by the row cap or the response-size limit, along with the reason

Results are capped by the **Max rows** setting and by an overall response-size limit, so very large result sets are truncated.

<Info>
  This node requires a provisioned Twin database. If your organization's Twin isn't available yet, the node shows a **Twin Not Provisioned** state — see [Setting up Twin](#setting-up-twin).
</Info>

## Twin Dump

Twin Dump automatically saves workflow run data to a Twin table after each run completes. Instead of using a Write node inside your workflow, a dump configuration captures a snapshot of selected node outputs and persists them without adding steps to the workflow itself.

This is useful for building audit trails, storing run results for reporting, or accumulating data across many runs without modifying the workflow logic.

### Create a dump

<Steps>
  <Step title="Open the Twin workspace">
    Navigate to **Integrations → Twin**.
  </Step>

  <Step title="Create a new dump">
    Click **New dump** and select the workflow to connect. Each dump is linked to a single workflow.
  </Step>

  <Step title="Define the table">
    Enter a table name and define the columns:

    * **Name** — the column name (lowercase, alphanumeric, underscores, max 63 characters)
    * **Type** — `text`, `uuid`, `int8`, `float8`, `timestamp`, `boolean`, or `jsonb`
    * **Variable** — the workflow variable or node output to map to this column
    * **Primary key** — optional; drives upsert behavior if set
  </Step>

  <Step title="Activate">
    Save the dump. Once active, every completed run of the linked workflow inserts a row into the dump table using the mapped variable values.
  </Step>
</Steps>

Two workflow runtime variables are always available as column sources:

| Variable           | Description                             |
| ------------------ | --------------------------------------- |
| `__run_id__`       | The unique ID of the completed run      |
| `__completed_at__` | The UTC timestamp when the run finished |

### Edit column mappings

To update which workflow variable maps to each column after a dump is created:

1. Open the dump configuration in the Twin workspace.
2. Click **Edit mappings**.
3. Update the variable reference for any column using the `@` picker.
4. Save changes.

Column names, types, and primary key flags cannot be changed through the edit interface. To restructure the table, add or drop columns using the schema editor.

### Pause and resume

Click the status toggle on a dump to pause it. While paused, runs complete normally but no rows are inserted. Resume to start persisting again.

### Backfill historical runs (Beta)

Backfills replay completed workflow runs into a dump table so existing run history shows up alongside rows added going forward. You can start a backfill at the time you create the dump, or later from the table detail page.

**Start a backfill at table creation:**

1. In the **New dump** sheet, scroll to the **Also start a backfill** option and check it.
2. Pick a **From** and **Until** datetime for the window of completed runs to replay.
3. The sheet shows an estimate of how many completed runs fall in the window before you submit.
4. Save the dump — the backfill is queued automatically once the table is created.

**Start a backfill on an existing dump table:**

1. Open the dump table from the Twin workspace.
2. Click **Backfill** in the toolbar.
3. Click **Create backfill**, set the time window, and submit.

The backfill sheet lists every job for this table with its status (queued, running, succeeded, failed), window, processed/succeeded/failed counts, creator, and creation time.

<Info>
  **Backfill limits in beta:**

  * Maximum window: **90 days**
  * Maximum runs per job: **20,000** — narrow the window or run multiple smaller backfills if you exceed this cap
  * Only one backfill can be queued or running per table at a time

  For best results, map a primary-key column to **Workflow Runtime → Workflow Run ID** before backfilling. Without a stable primary column, retries can insert duplicate rows.
</Info>

## Import data via CSV

The Twin workspace includes a CSV import tool for loading data into a table in bulk.

<Steps>
  <Step title="Open the Twin workspace">
    Navigate to **Integrations → Twin** and open the table you want to import into.
  </Step>

  <Step title="Click Import CSV">
    Click the **Import CSV** button in the table toolbar. A side panel opens.
  </Step>

  <Step title="Upload a file">
    Drag and drop a `.csv` file onto the upload area, or click to browse. The first row is treated as the header row and must match the table's column names.
  </Step>

  <Step title="Preview and validate">
    The panel shows a preview of your rows and highlights any column mapping issues. Fix any header mismatches before continuing.
  </Step>

  <Step title="Import">
    Click **Import**. Rows are inserted in batches and a progress bar tracks the operation. When complete, a summary shows how many rows were inserted and any errors encountered.
  </Step>
</Steps>

<Note>
  Each import batch can contain up to 500 rows. Large files are split into multiple batches automatically.
</Note>

## Bulk insert rows via API

To insert rows programmatically, use the bulk insert endpoint.

```http theme={null}
POST /twin/tables/{tableName}/rows/bulk
```

**Request body:**

```json theme={null}
{
  "rows": [
    { "column_a": "value1", "column_b": 42 },
    { "column_a": "value2", "column_b": 99 }
  ]
}
```

* `rows` — An array of row objects. Each object maps column names to values. Up to 500 rows per request.

**Response:**

```json theme={null}
{
  "success": true,
  "insertedCount": 2
}
```

## Update a row via API

In addition to workflow nodes, you can update a single row directly through the REST API.

```http theme={null}
PATCH /twin/tables/{tableName}/rows
```

**Request body:**

```json theme={null}
{
  "primaryKey": { "id": 42 },
  "updates": { "status": "completed", "resolved_at": "2026-03-18T10:00:00Z" }
}
```

* `primaryKey` — An object mapping primary key column name(s) to their values, used to identify the row to update.
* `updates` — An object of column-value pairs to apply to the matched row.

## Foreign keys

Twin tables support foreign-key constraints that link a column on one table to a column on another. Use them to enforce referential integrity (a value must exist in the referenced table) and to make table relationships explicit in the Twin workspace.

### Add a foreign key

You can add foreign keys when creating a table (draft mode) or to an existing table.

<Steps>
  <Step title="Open the Foreign keys section">
    In the Create Table sheet, the Edit Columns sheet, or the table preview panel, expand the **Foreign keys** section.
  </Step>

  <Step title="Click Add foreign key">
    A side sheet opens with the foreign-key configuration.
  </Step>

  <Step title="Select the source column">
    Pick the column on the current table that holds the reference.
  </Step>

  <Step title="Select the referenced table and column">
    Pick the target table and the column to reference. The target column type must match the source column type.
  </Step>

  <Step title="Choose ON UPDATE and ON DELETE actions">
    Set how the database reacts when the referenced row is updated or deleted:

    | Action          | Behavior                                                               |
    | --------------- | ---------------------------------------------------------------------- |
    | **NO ACTION**   | Reject the change if dependent rows exist (default).                   |
    | **RESTRICT**    | Same as NO ACTION, evaluated immediately.                              |
    | **CASCADE**     | Propagate the update or delete to dependent rows.                      |
    | **SET NULL**    | Null out the source column. Requires the source column to be nullable. |
    | **SET DEFAULT** | Set the source column back to its default value.                       |
  </Step>

  <Step title="Preview and apply">
    For an existing (live) table, HappyRobot checks for orphan rows that would violate the constraint. If any are found, the constraint is blocked and a sample is shown — fix or remove those rows in the SQL editor, then retry. For a draft table, the foreign key is recorded and applied when the table is created.
  </Step>
</Steps>

Foreign keys appear in the **Foreign keys** section of each table, listed by name with the source column, referenced table, and ON UPDATE / ON DELETE actions. The Twin canvas also draws an edge between related tables. To remove a foreign key, click its row and choose **Remove**.

## SQL editor

The Twin settings page includes a built-in SQL editor for running queries directly against your database. Use it to inspect schema, test queries, explore data, or run one-off operations without needing an external database client.

<Note>
  The SQL editor is intended for development and debugging. For production data access, use the **Read from Twin** and **Write to Twin** workflow nodes.
</Note>

## Capacity configuration

You can adjust the underlying RDS instance that powers your Twin database from the **Twin Database** settings page.

| Setting                    | Description                                                                             |
| -------------------------- | --------------------------------------------------------------------------------------- |
| **Instance class**         | The RDS instance type that determines compute and memory (for example, `db.t3.medium`). |
| **Allocated storage (GB)** | The storage capacity allocated to the database.                                         |

Changes to capacity may take a few minutes to apply. The settings page shows any pending modifications under the database status.

<Warning>
  Downgrading the instance class or reducing storage may cause downtime. Contact support before making capacity changes in a production environment.
</Warning>

## Using dynamic values

Both workflow nodes support dynamic values (workflow variables) in most fields. Wrap variable references in double curly braces to reference them, for example: `{{contact_phone_number}}`.

This means you can write different rows or apply different filters on each run based on the inputs your workflow receives.

## Next steps

<CardGroup cols={3}>
  <Card title="Twin overview" icon="database" href="../../08-Twin/01-Twin-Overview.md">
    The full Twin feature — tables, polling, dumps, capacity, and more.
  </Card>

  <Card title="Workflow variables" icon="brackets-curly" href="../../02-Workflows/07-Variables.md">
    Use variables as dynamic inputs to Twin node fields.
  </Card>

  <Card title="Data integrations" icon="database" href="../01-Integrations-Overview.md">
    See other data integrations available in workflows.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/twin
