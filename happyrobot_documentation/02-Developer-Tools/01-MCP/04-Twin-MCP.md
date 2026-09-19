---
title: "Twin MCP"
description: "Available tools for the Twin database MCP server"
---

# Twin MCP

> Available tools for the Twin database MCP server

The Twin MCP server provides tools for exploring schemas, running queries, and managing tables in your organization's [Twin database](../../01-Developer-Guide/08-Twin/01-Twin-Overview.md). It's available at the `/twin/mcp` path.

For installation, authentication, and service-to-service setup, see the [MCP servers overview](01-MCP-servers.md).

## Prerequisites

You need a **provisioned Twin database** for your organization. Check status under [Settings → Twin Database](../../01-Developer-Guide/08-Twin/05-SQL-Console-and-Capacity.md#api-gateway).

## Available tools

<AccordionGroup>
  <Accordion title="Schema and read access">
    | Tool             | Description                                                                                                                                            |
    | ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | `get_schema`     | List all tables and views with columns, types, and primary keys. Use this first to explore the database structure.                                     |
    | `get_table_data` | Read paginated rows from a table or view. Results are ordered by primary key — supports `limit` (default `50`, max `500`) and `offset` for pagination. |
  </Accordion>

  <Accordion title="Row mutations">
    | Tool          | Description                                                                                                                                         |
    | ------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `insert_row`  | Insert a single row into a table. Values are passed as string key-value pairs — PostgreSQL handles type coercion. Returns the inserted row.         |
    | `update_row`  | Update a single row by primary key. Provide the primary key to identify the row and the columns to update. Returns the updated row.                 |
    | `delete_rows` | Delete one or more rows by primary key. Provide an array of primary key objects (e.g. `[{ id: 1 }, { id: 2 }]`). Returns the count of deleted rows. |
  </Accordion>

  <Accordion title="Schema mutations">
    | Tool                   | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                   |
    | ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | `create_table`         | Create a new table with typed columns. `int8` primary keys auto-use `BIGSERIAL`; `uuid` primary keys auto-use `gen_random_uuid()`.                                                                                                                                                                                                                                                                                                                            |
    | `create_workflow_dump` | Create a [workflow run dump](../../01-Developer-Guide/08-Twin/04-Workflow-Run-Dumps.md) table bound to a workflow's variables, so every completed run populates a row automatically. The server resolves the workflow's variable catalog for you — pass `workflowId` and `tableName`, optionally `include` (a subset of variables) and `pk` (a variable to use as the primary key instead of a synthetic `run_id`). Use this — not `create_table` — whenever you want run data landed in Twin. |
    | `delete_workflow_dump` | Delete a [workflow run dump](../../01-Developer-Guide/08-Twin/04-Workflow-Run-Dumps.md#deleting-a-dump) by table name. Removes the run-capture config and keeps the table by default; pass `dropTable: true` to also drop the table and all its data. Asks you to confirm before running.                                                                                                                                                                                                      |
    | `drop_table`           | Drop a table permanently from the Twin database. **Irreversible** — all data in the table is lost. For dump tables, use `delete_workflow_dump` instead so the capture config goes away with the table.                                                                                                                                                                                                                                                        |
  </Accordion>

  <Accordion title="Arbitrary SQL">
    | Tool          | Description                                                                                                                            |
    | ------------- | -------------------------------------------------------------------------------------------------------------------------------------- |
    | `execute_sql` | Run arbitrary SQL against the Twin database. Supports `SELECT`, `INSERT`, `UPDATE`, `DELETE`, `CREATE TABLE`, `ALTER TABLE`, and more. |

    <Tip>
      Use `execute_sql` only when the dedicated tools above cannot fulfill the operation — for example `JOIN`s, aggregations, `ALTER TABLE`, complex `WHERE` clauses, or multi-statement migrations. Prefer the typed tools when they apply.
    </Tip>
  </Accordion>
</AccordionGroup>

## Limits

The Twin REST API enforces the following limits on MCP queries:

| Limit                      | Value         |
| -------------------------- | ------------- |
| SQL query timeout          | **5 seconds** |
| `SELECT` row cap           | **500 rows**  |
| `SELECT` response size cap | **1 MB**      |

If a `SELECT` exceeds these limits, the response is truncated and the tool returns a `truncated: true` flag with a `truncationReason` indicating which limit was hit.

## Example session

A typical session with the Twin MCP server might look like this:

<Steps>
  <Step title="Explore the schema">
    Ask your assistant: *"What tables are in my Twin database?"* — it calls `get_schema` and lists every table and view.
  </Step>

  <Step title="Inspect data">
    *"Show me the first 20 rows of the `customers` table"* — calls `get_table_data` with `limit: 20`.
  </Step>

  <Step title="Run analytical queries">
    *"How many runs completed yesterday, grouped by workflow?"* — uses `execute_sql` with a `GROUP BY` query.
  </Step>

  <Step title="Migrate the schema">
    *"Add an `email` column to the `customers` table"* — calls `execute_sql` with `ALTER TABLE`.
  </Step>
</Steps>

## Related

<CardGroup cols={3}>
  <Card title="MCP servers overview" icon="server" href="01-MCP-servers.md">
    Installation, authentication, and service-to-service setup.
  </Card>

  <Card title="Workflows tools" icon="sitemap" href="03-Workflows-MCP.md">
    Workflow management, integrations, and testing tools.
  </Card>

  <Card title="Twin database" icon="database" href="../../01-Developer-Guide/08-Twin/01-Twin-Overview.md">
    The full Twin feature — tables, polling, dumps, capacity, and Apps integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/developer-tools/mcp-twin
