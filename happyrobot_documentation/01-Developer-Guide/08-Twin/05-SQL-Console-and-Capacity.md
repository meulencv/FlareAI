---
title: "SQL Console and Capacity"
description: "Run SQL directly and configure your Twin database's instance class, storage, and gateway"
---

# SQL Console and Capacity

> Run SQL directly and configure your Twin database's instance class, storage, and gateway

The Twin workspace and settings page give you direct access to the database — both for ad-hoc queries and for managing the underlying compute and storage.

## SQL console

The SQL console is a query editor that runs SQL directly against your Twin database. Use it for inspection, exploration, one-off migrations, and anything the schema UI doesn't cover.

Running arbitrary SQL requires **Full Twin access**, since a statement can reach past the per-capability limits that the schema and row editors enforce. See [Twin permissions](01-Twin-Overview.md#permissions).

### Running a query

<Steps>
  <Step title="Open the SQL console">
    From the Twin workspace, open the SQL editor panel.
  </Step>

  <Step title="Type a query">
    Enter any valid SQL — `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE`, `ALTER TABLE`, `DROP`, etc.
  </Step>

  <Step title="Click Run">
    Results are streamed back inline as a table with column names, type IDs, and row data. The console also shows the command (`SELECT`, `INSERT`, etc.) and the row count.
  </Step>

  <Step title="Reset to start over">
    Click **Reset** to clear both the editor and the results panel.
  </Step>
</Steps>

### Exporting results

When a query returns rows, the result console gives you two ways to pull the data out:

* **Export CSV** — Download the full result set as a CSV file (named `twin-query-<timestamp>.csv`). Values are escaped following RFC 4180, so cells containing commas, quotes, or line breaks stay intact.
* **Copy TSV** — Copy the result set to your clipboard as tab-separated values, ready to paste directly into a spreadsheet. Tabs and line breaks inside a cell are flattened to spaces so each value lands in its own cell.

Both options export the rows currently returned by the console, so they respect the [query limits](#query-limits) below — add a `LIMIT` or narrow your `WHERE` clause if you need a specific slice.

### Query limits

The console enforces caps on how much it returns at once to keep queries fast and safe:

| Limit                      | Value      |
| -------------------------- | ---------- |
| Query timeout              | 20 seconds |
| `SELECT` row cap           | 500 rows   |
| `SELECT` response size cap | 1 MB       |

If a query exceeds a cap, the console truncates the results and surfaces a warning telling you which limit was hit — row count or response size.

<Note>
  The MCP server uses tighter limits (5-second timeout) for safety. The console uses the longer 20-second timeout because you're driving it interactively.
</Note>

### When to use the console vs. workflow nodes

| Use the SQL console for…                      | Use workflow nodes for…                    |
| --------------------------------------------- | ------------------------------------------ |
| Inspection and exploration                    | Repeatable, parameterized reads and writes |
| One-off migrations (`ALTER TABLE`, backfills) | Per-run data persistence                   |
| Cleanup queries (removing orphan rows)        | Data flow inside your workflows            |
| Analytics joins and aggregations              | Operational lookups                        |

For production data access, prefer the [Read from Twin and Write to Twin](../15-Integrations/06-Data-and-Storage/07-Twin-database.md) nodes — they're parameterized, audited, and integrate with workflow variables.

## Capacity

The Twin database runs on a managed RDS PostgreSQL instance. You can change the instance size and provisioned storage from the **Twin capacity** panel without leaving the platform. Changing capacity requires **Manage Twin database instance**; without it the panel is read-only.

### Viewing current capacity

The capacity panel shows:

* **Logical DB size** — actual data stored, with a usage progress bar and a health indicator (green / amber / red)
* **Used** and **Provisioned** in GB
* **Instance class** — the current RDS instance type (e.g., `db.t3.medium`)
* **Pending modifications**, if any change is currently being applied

### Adjusting capacity

<Steps>
  <Step title="Open the Twin capacity panel">
    Open the Twin workspace and click **Configure** on the capacity card. The panel includes the current instance class and provisioned storage.
  </Step>

  <Step title="Choose an instance class">
    Pick from the available RDS instance classes (e.g., `db.t3.micro`, `db.t3.small`, `db.t3.medium`, `db.t4g.*`). Larger classes give you more compute and memory.
  </Step>

  <Step title="Increase provisioned storage">
    Enter a new storage value in GB. Storage can only be **increased** — the input enforces the current value as the minimum.
  </Step>

  <Step title="Apply the change">
    Click the apply button. AWS applies the change in the background; the panel shows a pending-change banner while the modification is in progress.
  </Step>
</Steps>

<Warning>
  **Instance class changes** apply immediately and can **reboot the Twin database for several minutes**. During the reboot, workflows and Apps that hit Twin will fail. Plan instance-class changes during a maintenance window.

  **Storage increases** are applied online and should not block Twin usage. Note that increasing storage adds an associated monthly cost.
</Warning>

### Email alerts

Rather than watching the capacity panel, have Twin email you when performance reaches a critical threshold. Set the recipients yourself in **Settings → Twin Database → Email alerts**:

<Steps>
  <Step title="Open Twin settings">
    Go to **Settings → Twin Database**. The **Email alerts** section is available once your **Twin Database** status is **Available**.
  </Step>

  <Step title="Enter the recipients">
    Type the addresses into the **Recipients** box, separated by commas or new lines. Up to 20 addresses; duplicates and casing are normalized for you, and the counter under the box shows how many you have.
  </Step>

  <Step title="Save">
    Click **Save email alerts**. The button stays disabled until the list is valid and actually differs from what's saved.
  </Step>
</Steps>

The **Email alerts** section sits just above **API Gateway** on the page. Any valid address is accepted and recipients don't have to be HappyRobot users, so a shared inbox or an on-call alias works. Clear the box and save to turn alerts off. Editing the list requires permission to manage Twin settings — see [Team members and roles](../16-Account-and-Settings/02-Members-and-Access.md).

## API Gateway

The API Gateway is an optional managed REST endpoint that exposes your Twin database to anything outside the platform — most notably [Apps you build on HappyRobot](06-Using-Twin-in-Apps.md), but also external services and scripts.

### Deploying the gateway

<Steps>
  <Step title="Open Settings → Twin Database">
    Navigate to **Settings → Twin Database**.
  </Step>

  <Step title="Click Deploy Gateway">
    The button is available once your **Twin Database** status is **Available**. The status transitions to **Deploying** for a few minutes while infrastructure spins up.
  </Step>

  <Step title="Copy the endpoint and header">
    Once status flips to **Running**, the page shows:

    * **Endpoint** — the URL your apps and services will call (something like `https://<unique-host>/`).
    * **Required header** — `x-org-id: <your-org-id>`. Every request to the gateway must include this header.

    Use the **Copy** buttons to grab both values.
  </Step>
</Steps>

The gateway is shared across your org — there's exactly one per Twin database. Once deployed, it's used automatically by Apps and can be called from anywhere with an authenticated request.

### Gateway status

| Status           | Meaning                                                                      |
| ---------------- | ---------------------------------------------------------------------------- |
| **Not deployed** | The gateway has not been provisioned. Click **Deploy Gateway** to create it. |
| **Deploying**    | Provisioning is in progress. The page polls and updates automatically.       |
| **Running**      | The gateway is healthy and serving requests.                                 |
| **Failed**       | The deployment failed. Click **Retry Deploy** to try again.                  |

### Deleting the gateway

If you no longer need external access, click **Delete Gateway** in Twin settings. The gateway is torn down and the endpoint stops responding. Workflow nodes are unaffected — they don't go through the gateway.

<Warning>
  Deleting the gateway breaks any App or external service that relies on it. The `NEXT_PUBLIC_TWIN_GATEWAY` environment variable still appears on Apps that had it injected before deletion, but the endpoint returns connection errors.
</Warning>

## Deleting Twin

The Twin database itself can be deleted from the Twin capacity panel's **danger zone**.

<Warning>
  This action is reserved for engineering-tier users and is **irreversible**:

  * The RDS instance is destroyed after taking a final snapshot.
  * The API gateway is torn down.
  * All tables, rows, dumps, and polling configurations are gone.
  * Workflows that read or write to Twin will fail until Twin is re-provisioned.

  A confirmation dialog requires you to type your organization name before the delete proceeds.
</Warning>

Contact support if you need Twin removed and don't have engineering-tier access.

## Next steps

<CardGroup cols={3}>
  <Card title="Using Twin in Apps" icon="browser" href="06-Using-Twin-in-Apps.md">
    Consume the gateway you just deployed from a HappyRobot App.
  </Card>

  <Card title="Twin MCP" icon="robot" href="../../02-Developer-Tools/01-MCP/04-Twin-MCP.md">
    Same database, queryable by AI agents over MCP.
  </Card>

  <Card title="Workflow nodes" icon="diagram-project" href="../15-Integrations/06-Data-and-Storage/07-Twin-database.md">
    Read and write Twin data from inside any workflow.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/twin/sql-console-and-capacity
