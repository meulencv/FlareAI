---
title: "Snowflake"
description: "Query data from your Snowflake data warehouse"
---

# Snowflake

> Query data from your Snowflake data warehouse

The Snowflake integration lets your workflows execute SQL queries against your Snowflake data warehouse. Pull data into workflows for AI processing, decision-making, and downstream actions.

## Authentication

Snowflake uses form-based credentials with your Snowflake account details.

<Steps>
  <Step title="Enable the Snowflake integration">
    Go to **Settings > Integrations** and enable **Snowflake**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    * **Account** — your Snowflake account identifier (e.g., `xy12345.us-east-1`)
    * **Username** — your Snowflake username
    * **Password** — your Snowflake password
  </Step>

  <Step title="Verify the connection">
    The credential will validate automatically and appear as **Active**.
  </Step>
</Steps>

## Available events

### Actions

| Event             | Description                                                                    |
| ----------------- | ------------------------------------------------------------------------------ |
| **Execute Query** | Runs a SQL query against your Snowflake data warehouse and returns the results |

### Execute Query configuration

Write SQL queries directly in the action configuration. Queries support template variables — type `@` to reference data from upstream nodes and build dynamic queries.

```sql theme={null}
SELECT customer_name, load_count, last_activity
FROM customer_data.carriers
WHERE mc_number = '@nodes.extract.mc_number'
LIMIT 10
```

<Warning>
  Be mindful of query performance. Large result sets can impact workflow execution time. Use `LIMIT` clauses and filter conditions to keep queries efficient.
</Warning>

## Example use case

A voice agent extracts a carrier's MC number from the conversation. The workflow uses **Execute Query** to pull the carrier's historical performance data from Snowflake — on-time delivery rate, claim history, and preferred lanes — which the agent references in the next part of the conversation.

## Related

<CardGroup cols={2}>
  <Card title="Google Sheets" icon="table" href="01-Google-Sheets.md">
    Read and write data to Google Sheets.
  </Card>

  <Card title="Redis" icon="database" href="03-Redis.md">
    Key-value caching and storage with Redis.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/snowflake
