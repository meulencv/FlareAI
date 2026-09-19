---
title: "Usage and Billing"
description: "Monitor your organization's usage and credit consumption"
---

# Usage and Billing

> Monitor your organization's usage and credit consumption

The Usage and Billing page gives you visibility into how your organization is consuming platform resources. Track credit usage over time, drill into per-workflow breakdowns, and filter by date range.

## Usage dashboard

Navigate to **Settings > Usage** to view the usage dashboard. The dashboard shows credit consumption over time, giving you a clear picture of how resources are being used.

## Date range and granularity

Use the date range selector to focus on a specific time period:

* **Last 24 hours**
* **Last 7 days**
* **Last 30 days**
* **Last 3 months**
* **Last 12 months**
* **Custom range** — pick start and end dates with the calendar picker

The chart granularity (daily, monthly, or yearly) auto-adjusts based on the selected range.

<Note>
  Usage dates are evaluated in **UTC**, not your local time zone. A day in the chart runs from 00:00 to 23:59 UTC, so totals match the values returned by the billing API regardless of where you're viewing from.
</Note>

## Filtering by workflow

Select a specific workflow from the filter dropdown to view its usage in isolation. When a workflow is selected, the dashboard shows a **Credit Distribution** breakdown by transaction type, giving you a detailed view of where credits are being consumed.

## Workflow usage table

Below the chart, a table lists per-workflow credit consumption. Click into any workflow row to see a detailed breakdown of its usage.

### Platform & Services

Some consumption belongs to the organization rather than to any one workflow. It appears in the table as **Platform & Services**.

`GET /billing/usage/credits` includes it, so the API total matches the total in **Settings > Usage**. It comes back as a row with an empty `workflow_id`, an empty `workflow_name`, and an empty `folder_path` — group by `workflow_id` rather than `workflow_name` to tell it apart, since a real workflow could legitimately be named "Platform & Services". The row is returned only to callers with workspace-level usage or billing access, and it can't be selected or excluded through the endpoint's filters.

## Wallet environment scope

When creating or editing a wallet, you can scope it to a specific environment (such as production or staging) or leave it set to **All Environments**, the default. An all-environments wallet covers usage across every environment in the organization.

## Wallet alert thresholds

Wallets support configurable alert thresholds so you receive email notifications when balance consumption crosses warning and critical points. Owners of the target organization receive these alerts.

When creating or editing a wallet, set:

| Threshold    | Default | Range | Description                                                                                                 |
| ------------ | ------- | ----- | ----------------------------------------------------------------------------------------------------------- |
| **Warning**  | 70%     | 1–99  | Sends a warning email when consumption reaches this percentage of the wallet's allocated credits.           |
| **Critical** | 90%     | 1–100 | Sends a critical email when consumption reaches this percentage. Must be higher than the warning threshold. |

<Tip>
  Pick a warning threshold low enough to give you time to react — for production-critical wallets, 60–70% is a reasonable default.
</Tip>

## API access

For programmatic access to usage data, use the API endpoints:

* **Usage endpoints** — `GET /usage/call_minutes`, `GET /usage/llm_tokens`, `GET /usage/text_count`, and more
* **Billing endpoints** — `GET /billing/usage/totals`, `GET /billing/usage/details`, `GET /billing/usage/credits`, `GET /billing/usage/runs/{run_id}`

See the [API Reference](https://docs.happyrobot.ai/api-reference/overview) for full documentation.

### Credits for a single run

`GET /billing/usage/runs/{run_id}` returns what one [run](../09-Runs-and-Monitoring/01-Runs-Overview.md) cost, broken down with the same category → subcomponent taxonomy as `GET /billing/usage/credits`:

```json theme={null}
{
  "run_id": "0c9f...",
  "workflow_id": "8a12...",
  "unit": "credits",
  "total_credits": 52.3,
  "components": [
    {
      "category": "Voice",
      "credits": 41.1,
      "subcomponents": [
        { "name": "Voice Orchestration", "credits": 41.1 }
      ]
    }
  ]
}
```

Each category is a top-level classification, each entry in `subcomponents` is the next level down, and a subcomponent can carry a nested `subcomponents` array for a third level. Categories and subcomponents are sorted by credits, descending, and rounded to two decimals.

### LLM token usage by model

In `GET /billing/usage/credits`, any subcomponent named `LLM` also carries a `usage` array breaking its tokens down by model:

```json theme={null}
{
  "name": "LLM",
  "credits": 12.4,
  "volume": 1,
  "volume_unit": "calls",
  "usage": [
    {
      "model": "claude-sonnet-4-5",
      "input_tokens": 184320,
      "cache_input_tokens": 131072,
      "cache_write_tokens": 8192,
      "output_tokens": 4096
    }
  ]
}
```

Because `usage` sits on the LLM subcomponent itself, you can tell which part of the workflow spent the tokens rather than only seeing a single per-workflow total. Tokens are split into `input_tokens`, `cache_input_tokens` (prompt cache reads), `cache_write_tokens` (prompt cache writes), and `output_tokens`.

Bring-your-own-key (BYOK) calls are included even though they consume zero HappyRobot credits, so an LLM subcomponent can report `usage` while its `credits` is `0`.

## Next steps

<CardGroup cols={2}>
  <Card title="API Reference" icon="book" href="https://docs.happyrobot.ai/api-reference/overview">
    Access usage and billing data programmatically.
  </Card>

  <Card title="Workflow Settings" icon="gear" href="10-Workflow-Settings.md">
    Configure settings for individual workflows.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/billing
