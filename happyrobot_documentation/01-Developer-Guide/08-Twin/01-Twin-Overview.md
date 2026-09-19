---
title: "Twin Overview"
description: "A managed PostgreSQL database for your organization, built into the platform"
---

# Twin Overview

> A managed PostgreSQL database for your organization, built into the platform

Twin is a dedicated PostgreSQL database provisioned for your organization by HappyRobot. You get a visual schema builder, a SQL console, workflow nodes, a REST API, and an MCP server — all backed by the same database — so you can store and query structured data without standing up infrastructure yourself.

## What you can do with Twin

<CardGroup cols={2}>
  <Card title="Persist data across runs" icon="floppy-disk">
    Keep state, lookup tables, configuration, and cached results in tables your workflows can read from and write to between runs.
  </Card>

  <Card title="Sync data from external APIs" icon="arrows-rotate">
    Define [polling tables](03-Polling-Tables.md) that pull from any HTTP endpoint on a schedule and keep themselves in sync as data changes upstream.
  </Card>

  <Card title="Capture workflow analytics" icon="chart-line">
    Use [workflow run dumps](04-Workflow-Run-Dumps.md) to snapshot run outputs into a table after every completed run — without adding nodes to your workflow.
  </Card>

  <Card title="Back your custom Apps" icon="browser">
    Apps deployed on HappyRobot can read and write Twin data through a managed REST gateway, with the endpoint injected as an environment variable. See [using Twin in Apps](06-Using-Twin-in-Apps.md).
  </Card>
</CardGroup>

## Key features

<CardGroup cols={2}>
  <Card title="Dedicated database" icon="server">
    Each organization gets an isolated RDS PostgreSQL instance with encrypted storage. Provisioned automatically — no infrastructure to manage.
  </Card>

  <Card title="Visual schema builder" icon="table">
    Create tables, columns, foreign keys, and views in the UI. Type validation and orphan-row checks happen before changes apply.
  </Card>

  <Card title="Polling tables" icon="bolt">
    Point a table at an HTTP endpoint, configure a cursor, and HappyRobot keeps the table synced on an interval. Schema is auto-inferred from the response.
  </Card>

  <Card title="SQL console" icon="terminal">
    Run ad-hoc SQL straight from the platform for inspection, migrations, and exploration. Results stream back inline.
  </Card>

  <Card title="Workflow nodes" icon="diagram-project">
    Use the **Read from Twin** and **Write to Twin** nodes inside any workflow to query or insert rows with workflow variables.
  </Card>

  <Card title="REST API and MCP" icon="code">
    Every table is reachable via a managed REST gateway and an [MCP server](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md) so AI agents and external apps can query and mutate data.
  </Card>
</CardGroup>

## Core concepts

| Concept            | Description                                                                                                |
| ------------------ | ---------------------------------------------------------------------------------------------------------- |
| **Twin database**  | The PostgreSQL instance provisioned for your organization. One per org.                                    |
| **Table**          | A typed schema of columns you create in the Twin workspace. Backs the rest of the feature.                 |
| **Polling table**  | A table whose rows are automatically synced from an external HTTP endpoint on an interval.                 |
| **Dump table**     | A table whose rows are populated automatically by mapping workflow run outputs to columns.                 |
| **View**           | A read-only saved SQL query that appears alongside tables.                                                 |
| **API Gateway**    | An optional REST endpoint that exposes your Twin database to external apps via JWT-authenticated requests. |
| **Instance class** | The RDS instance type backing your database (e.g., `db.t3.medium`). Controls compute and memory.           |

## How Twin fits into the platform

Twin is the persistence layer that everything else can talk to:

<Steps>
  <Step title="Workflows read and write rows">
    The [Read from Twin and Write to Twin nodes](../15-Integrations/06-Data-and-Storage/07-Twin-database.md) connect any workflow directly to your tables. No credentials to manage — workflows authenticate as your organization automatically.
  </Step>

  <Step title="Apps consume Twin via a REST gateway">
    [Apps](../07-Apps/01-Apps-Overview.md) you build on HappyRobot get the Twin gateway URL injected as `NEXT_PUBLIC_TWIN_GATEWAY` at build time, so they can read and write Twin data without you wiring up a separate backend.
  </Step>

  <Step title="AI agents query Twin via MCP">
    The [Twin MCP server](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md) lets any MCP-compatible agent — including Claude Desktop, your own agents, and the HappyRobot Frontal assistant — explore schemas, run queries, and mutate rows.
  </Step>

  <Step title="External services use the REST API">
    Anything outside the platform can call the Twin REST API directly, authenticated by your HappyRobot API key and scoped to your organization.
  </Step>
</Steps>

## Getting started

<Steps>
  <Step title="Check that Twin is provisioned">
    Open **Settings → Twin Database**. Your org's Twin instance is provisioned automatically. If the status is **Available**, you're ready to go. If it shows **Provisioning** or **Failed**, contact support.
  </Step>

  <Step title="Create your first table">
    Navigate to **Twin** in the sidebar and click **New Table**. See [managing tables](02-Managing-Tables.md) for the full flow, including column types and foreign keys.
  </Step>

  <Step title="Use it from a workflow or an App">
    Add a [Read from Twin or Write to Twin node](../15-Integrations/06-Data-and-Storage/07-Twin-database.md) to a workflow, or [consume Twin from an App](06-Using-Twin-in-Apps.md) using the auto-injected gateway URL.
  </Step>
</Steps>

## Permissions

Twin access is split into separate actions, so you can let someone edit rows without letting them reshape the schema or resize the database. Add them to a [custom role](../16-Account-and-Settings/03-Custom-Roles.md) from **Settings > Roles**.

| Action                            | What it allows                                                                                                                                         |
| --------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **View Twin**                     | Browse tables, views, and rows. Required by every action below.                                                                                        |
| **Edit Twin data**                | Insert, update, delete, and import rows.                                                                                                               |
| **Manage Twin schema**            | Create, alter, and delete tables and views, and manage polling, workflow run dumps, and backfills.                                                     |
| **Manage Twin database instance** | Provision, resize, and delete the Twin database instance.                                                                                              |
| **Manage Twin settings**          | Change Twin settings, including alert recipients.                                                                                                      |
| **Full Twin access**              | Everything above, plus unrestricted SQL execution in the [SQL console](05-SQL-Console-and-Capacity.md). Selecting it selects the narrower actions too. |

What you can do maps onto the UI directly:

* Without **Edit Twin data**, the table view is read-only — inline editing, row inserts, and row deletes are unavailable, and a banner explains why
* Without **Manage Twin schema**, the **New table** and **New view** actions, column editing, table and view deletion, and the polling and dump controls are hidden
* Without **Manage Twin database instance**, the capacity dialog is read-only and the **Enable Twin** and retry actions don't appear
* Running ad-hoc SQL requires **Full Twin access**, because a query can read or change anything in the database

<Note>
  Members who already had Twin management keep every capability: existing roles carrying the old Twin management action were granted the narrower actions. The **Editor** system role receives **Edit Twin data** only.
</Note>

Twin isn't taggable, so all Twin actions are full-scope-only — a member reaching Twin through a [Scope Tag](../16-Account-and-Settings/04-Scope-Tags.md) grant alone won't have them.

## Limits and supported types

| Surface                | Limit                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------- |
| Supported column types | `int8`, `int4`, `float8`, `float4`, `text`, `boolean`, `timestamp`, `uuid`, `jsonb`                |
| Table name             | Lowercase letters, numbers, underscores; must start with a letter or underscore; max 63 characters |
| Polling interval       | Minimum 6 seconds, maximum 86,400 seconds (24 hours)                                               |
| SQL query timeout      | 20 seconds (5 seconds for MCP)                                                                     |
| `SELECT` result cap    | 500 rows or 1 MB, whichever is hit first                                                           |
| Backfill window (beta) | Up to 90 days; max 20,000 runs per job                                                             |

## Next steps

<CardGroup cols={3}>
  <Card title="Manage tables" icon="table" href="02-Managing-Tables.md">
    Create tables, columns, foreign keys, and views.
  </Card>

  <Card title="Polling tables" icon="arrows-rotate" href="03-Polling-Tables.md">
    Auto-sync data from any HTTP endpoint.
  </Card>

  <Card title="Workflow run dumps" icon="chart-line" href="04-Workflow-Run-Dumps.md">
    Capture workflow outputs into a table.
  </Card>

  <Card title="SQL console and capacity" icon="server" href="05-SQL-Console-and-Capacity.md">
    Run SQL and configure the database.
  </Card>

  <Card title="Using Twin in Apps" icon="browser" href="06-Using-Twin-in-Apps.md">
    Read and write Twin data from a deployed App.
  </Card>

  <Card title="Twin MCP server" icon="robot" href="../../02-Developer-Tools/01-MCP/04-Twin-MCP.md">
    Tools for AI agents to query Twin.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/twin/overview
