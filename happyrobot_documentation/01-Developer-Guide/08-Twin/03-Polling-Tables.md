---
title: "Polling Tables"
description: "Keep a Twin table automatically synced from an external HTTP endpoint"
---

# Polling Tables

> Keep a Twin table automatically synced from an external HTTP endpoint

A **polling table** is a Twin table whose rows are kept in sync with an external HTTP endpoint. You point it at a URL, tell it which query parameter to use as a cursor, and HappyRobot fetches new rows on a schedule. Schema is inferred from the endpoint's response — you don't define columns by hand.

Use polling tables to mirror data from a third-party system you don't control (a TMS, a CRM, an inventory API) into Twin so your workflows and Apps can query it natively.

## How polling works

<Steps>
  <Step title="HappyRobot calls your endpoint on an interval">
    Every *N* seconds, the platform issues a `GET` to the configured URL with any filter params, the cursor param set to the last cursor value, and the optional limit/offset params.
  </Step>

  <Step title="The response is parsed">
    Each item in the response is upserted into the table by the primary-key field you selected at creation time. New items are inserted; existing items are updated.
  </Step>

  <Step title="The cursor advances">
    HappyRobot records the latest cursor value from the response so the next poll fetches only what's changed since.
  </Step>

  <Step title="Errors are surfaced">
    Failed polls are logged with the error message and visible on the table. Polling continues on the next tick — a single failure doesn't stop the table.
  </Step>
</Steps>

## Creating a polling table

<Steps>
  <Step title="Open New Polling Table">
    In the Twin workspace, click **New Polling Table**. A side sheet opens.
  </Step>

  <Step title="Name the table">
    Same rules as a regular table: lowercase letters, numbers, and underscores; must start with a letter or underscore; max 63 characters.
  </Step>

  <Step title="Configure the API endpoint">
    | Field             | Required | Description                                                                                                                                                     |
    | ----------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | **URL**           | Yes      | The full HTTP(S) endpoint to poll.                                                                                                                              |
    | **Credential**    | No       | An [authentication credential](../15-Integrations/02-Credentials.md) to attach to each request. Only credentials from the **authentication** integration group are listed. |
    | **Filter Params** | No       | Static query parameters to append to every request. Add as many key/value pairs as you need.                                                                    |
    | **Cursor Param**  | Yes      | The query parameter name used to fetch only changed records (e.g., `updated_since`, `since`, `cursor`).                                                         |
    | **Limit Param**   | No       | The query parameter name for page size, if your API supports one (e.g., `pageSize`, `limit`).                                                                   |
    | **Offset Param**  | No       | The query parameter name for offset-based pagination, if applicable (e.g., `page`, `offset`).                                                                   |
  </Step>

  <Step title="Test the connection">
    Click **Test Connection**. HappyRobot calls the endpoint exactly as polling would — including your filter params, a sample cursor value (one hour ago, in `yyyyMMddHHmmss-0000` format), and a limit of `1` if you set a limit param.

    On success, the response body is shown along with the inferred schema. On failure, the error is surfaced inline. Common failures:

    * **Unauthorized** — the credential doesn't have access; switch credentials.
    * **Forbidden** — the credential is valid but not authorized for this endpoint.
    * **Limit param not working** — the endpoint returned more than 1 item even though limit was set; the parameter name is probably wrong.
  </Step>

  <Step title="Review the schema and choose a primary key">
    The schema table shows every field returned with an inferred type: text, number, boolean, or object (`jsonb`). Pick a **Primary Key** field — HappyRobot auto-selects `id` if it exists.

    The primary key is what polling uses to upsert. Pick something stable that uniquely identifies a record in the source system.
  </Step>

  <Step title="Set the polling interval">
    Enter the polling interval in seconds (minimum 6, maximum 86,400). 60 seconds is a sensible default.
  </Step>

  <Step title="Create">
    Click **Create**. The table is created with the inferred schema and polling starts immediately.
  </Step>
</Steps>

## Inferred column types

The schema is inferred from the first item in the test response.

| Response value            | Inferred Twin type |
| ------------------------- | ------------------ |
| Number (`42`, `3.14`)     | `float8`           |
| Boolean (`true`, `false`) | `boolean`          |
| Object or array           | `jsonb`            |
| Anything else             | `text`             |

If a field is `null` in the test response, it defaults to `text`. You can change types after the fact via [Edit columns](02-Managing-Tables.md#editing-columns), but the safest approach is to test against a representative payload.

## Response shape requirements

The poller looks for an **array of objects**. Both of these shapes work:

```json theme={null}
// Top-level array
[
  { "id": 1, "name": "Alice", "updated_at": "..." },
  { "id": 2, "name": "Bob",   "updated_at": "..." }
]
```

```json theme={null}
// Object with a single array field
{ "results": [
    { "id": 1, "name": "Alice" },
    { "id": 2, "name": "Bob"   }
] }
```

If the endpoint returns a single object or no array, the schema can't be inferred and the connection test fails.

## Monitoring and adjusting

Open a polling table and click **Edit columns** to see the **Polling configuration** section.

| Field                        | Editable | Description                                                            |
| ---------------------------- | -------- | ---------------------------------------------------------------------- |
| **Source URL**               | No       | The endpoint being polled.                                             |
| **Cursor parameter**         | No       | The query parameter used to advance the cursor.                        |
| **Current cursor**           | No       | The last cursor value the poller advanced to.                          |
| **Limit / Offset parameter** | No       | Pagination parameters, if configured.                                  |
| **Interval (s)**             | Yes      | How often the poller runs. Same 6–86,400 second bounds as on creation. |
| **Last poll**                | No       | Timestamp of the most recent poll, or *Never polled* if pending.       |
| **Last error**               | No       | The error message from the most recent failed poll, if any.            |

Cursor parameter, URL, and pagination settings are immutable. To change them, drop the table and recreate it.

## When to use polling tables vs. workflows

| Use a polling table when…                                      | Use a workflow trigger instead when…                                                |
| -------------------------------------------------------------- | ----------------------------------------------------------------------------------- |
| You want a continuous mirror of an external dataset            | You want to act on each new record (send a message, transform it, call another API) |
| You'll query the data later from workflows, Apps, or analytics | The external system can push to you via webhook                                     |
| The source API has a stable cursor parameter                   | You need fine-grained control over filtering and ordering before storage            |

The two patterns compose: a polling table can act as a buffer that a workflow runs against on a [schedule](../03-Core-Nodes/07-Schedule.md).

## Limits

| Constraint               | Value                                                               |
| ------------------------ | ------------------------------------------------------------------- |
| Minimum polling interval | 6 seconds                                                           |
| Maximum polling interval | 86,400 seconds (24 hours)                                           |
| Response shape           | Array of objects, or object with one array field                    |
| Authentication           | One credential per table, from the authentication integration group |

## Next steps

<CardGroup cols={2}>
  <Card title="Credentials" icon="key" href="../15-Integrations/02-Credentials.md">
    Add an authentication credential before connecting to a protected endpoint.
  </Card>

  <Card title="Workflow run dumps" icon="chart-line" href="04-Workflow-Run-Dumps.md">
    The other automatic-populating table type — driven by workflow runs.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/twin/polling-tables
