---
title: "Analytics Overview"
description: "Track performance and gain insights"
---

# Analytics Overview

> Track performance and gain insights

Analytics gives you a real-time view of how your workflows are performing. Track call volumes, run success rates, email counts, and call durations — across your entire organization or for a specific workflow. Build custom charts to visualize the metrics that matter most to your team, and filter everything by time range, workflow variables, or custom dimensions.

## Two views

HappyRobot provides analytics at two levels:

<CardGroup cols={2}>
  <Card title="Organization-level" icon="building">
    See aggregated metrics across all workflows. Compare call volumes and durations by workflow, monitor total run counts, and spot trends across your entire operation.
  </Card>

  <Card title="Workflow-level" icon="diagram-project">
    Drill into a single workflow to see its runs by status, call and email KPIs, and custom charts built from that workflow's node output data.
  </Card>
</CardGroup>

To access analytics, select the **Analytics** tab from the top of any workflow page. When no specific workflow is selected, you see organization-wide metrics. Select a workflow from the sidebar to see metrics scoped to that workflow.

## What's included

Every analytics view comes with a set of default metrics that update in real time, plus the ability to create custom visualizations.

### Default metrics

These are available out of the box with no configuration:

* **Total runs** — Count of workflow executions over the selected time range
* **Total calls** — Number of voice sessions (inbound and outbound)
* **Average call duration** — Mean duration across all calls, displayed as minutes and seconds
* **Total call minutes** — Aggregate voice time across all sessions
* **Total emails** — Count of email sessions processed
* **Runs by status** — Time-series chart showing completed, running, failed, and canceled runs

At the organization level, you also get:

* **Calls by workflow** — Pie chart showing how calls are distributed across workflows
* **Call minutes by workflow** — Pie chart showing how call time is distributed across workflows

### Custom charts

Build your own visualizations from workflow node output data. Custom charts let you track business-specific metrics — like classification distributions, outcome breakdowns, or volume trends segmented by any variable your workflows produce.

Supported chart types:

| Chart type         | Description                                                      |
| ------------------ | ---------------------------------------------------------------- |
| **Pie chart**      | Distribution of values for a single variable                     |
| **Line chart**     | Time-series trends, with optional segmentation by classification |
| **Sankey diagram** | Flow visualization showing how values move between stages        |

See [Workflow Metrics](03-Workflow-Metrics.md) for details on creating and configuring custom charts.

### Custom views

For advanced analytics needs, you can embed external dashboards as custom views. These appear as additional tabs alongside the default analytics view, giving your team a unified analytics experience without leaving the platform.

## Controls and filters

The analytics header provides controls that apply to all metrics on the page:

<AccordionGroup>
  <Accordion title="Date range">
    Select a preset time range or define a custom window. Preset options include: **Last 30 minutes**, **Last 1 hour**, **Last 6 hours**, **Last 12 hours**, **1 day**, **7 days** (default), **30 days**, and **1 year**. For custom ranges, use the calendar picker to set exact start and end dates.
  </Accordion>

  <Accordion title="Time interval">
    Control how data points are grouped on time-series charts. Choose **Auto** (interval selected based on your date range), **Day**, or **Week**. Day and week intervals are only available for date ranges of 1 day or longer.
  </Accordion>

  <Accordion title="Custom filters">
    Filter all analytics by workflow variable values. Click the filter icon, select a variable from any node output in the workflow, then choose one or more values to include. Multiple filters are combined with AND logic — only runs matching all selected filters are shown. Active filters display as badges in the header.
  </Accordion>

  <Accordion title="Refresh">
    Click the refresh button to manually re-fetch all analytics data. While analytics update periodically, this gives you an instant snapshot of the latest numbers.
  </Accordion>
</AccordionGroup>

## Exporting data

Every chart in the analytics view supports CSV export. Click the menu icon on any chart and select **Download to CSV** to get the underlying data.

For bulk run exports with status filtering, use the **Download Reports** feature in the [Runs tab](../09-Runs-and-Monitoring/01-Runs-Overview.md#exporting-runs).

## Quality metrics

In addition to operational analytics, HappyRobot provides a dedicated [quality and evaluation system](../11-Quality-and-Evaluation/01-Quality-and-evaluation-overview.md) that tracks agent behavioral quality. Quality metrics include northstar pass rates and audit trends — available in the **Audits** and **Evaluate** tabs of the workflow editor.

See the [quality and evaluation overview](../11-Quality-and-Evaluation/01-Quality-and-evaluation-overview.md) for details.

## Next steps

<CardGroup cols={3}>
  <Card title="KPI Dashboard" icon="gauge-high" href="02-KPI-Dashboard.md">
    Explore default metrics and what each KPI measures.
  </Card>

  <Card title="Workflow Metrics" icon="chart-pie" href="03-Workflow-Metrics.md">
    Build custom charts and visualize workflow-specific data.
  </Card>

  <Card title="Runs" icon="list-check" href="../09-Runs-and-Monitoring/01-Runs-Overview.md">
    Monitor individual run executions and access detailed transcripts.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/analytics/overview
