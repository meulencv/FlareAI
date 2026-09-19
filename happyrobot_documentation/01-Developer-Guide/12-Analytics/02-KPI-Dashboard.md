---
title: "KPI Dashboard"
description: "Monitor key performance indicators"
---

# KPI Dashboard

> Monitor key performance indicators

The KPI dashboard is the default analytics view for every workflow. It shows a set of built-in metrics that track run volume, call activity, email throughput, and status breakdowns — with no configuration required. All metrics respond to the date range, time interval, and custom filter controls in the analytics header.

## Default KPIs

Three metric cards appear at the top of the analytics view, giving you an at-a-glance summary of call activity.

### Total calls

The total number of voice sessions within the selected time range. Includes inbound, outbound, and outbound-with-callback calls. A call is counted from the moment it starts ringing.

### Total call minutes

The aggregate duration of all voice sessions in minutes — the entire time an agent is on the phone. Voicemails are included in this total.

### Average call duration

The mean duration across all calls in the selected time range, displayed as minutes and seconds (e.g., **2m 34s**). Use this to track whether conversations are getting longer or shorter over time.

<Tip>
  Hover over any KPI card title to see a tooltip describing exactly what the metric measures.
</Tip>

### Total emails

The count of email sessions processed within the selected time range. This appears when your workflows include email-based nodes.

<Info>
  KPIs are available at both the organization level (across all workflows) and the workflow level (scoped to a single workflow). The metrics are identical — only the scope changes.
</Info>

## Runs by status

The runs by status chart is a stacked area chart that shows how workflow executions are distributed across statuses over time. Each status is color-coded:

| Status        | Color | Description                                          |
| ------------- | ----- | ---------------------------------------------------- |
| **Completed** | Green | Runs that finished successfully                      |
| **Running**   | Blue  | Runs currently in progress                           |
| **Failed**    | Red   | Runs that encountered an error                       |
| **Canceled**  | Gray  | Runs that were manually or programmatically canceled |

The total run count for the selected time range appears in the chart header.

### Interacting with the chart

* **Hover** over any point to see exact counts for each status at that timestamp.
* **Click a legend item** to toggle its visibility. Hidden statuses appear at reduced opacity in the legend and are excluded from the chart.
* **Export** the chart data by clicking the menu icon and selecting **Download to CSV**.

## Call distribution charts

At the organization level (when no specific workflow is selected), two additional pie charts appear:

### Calls by workflow

Shows how total calls are distributed across your workflows. Each slice represents a different workflow, sized by its share of total calls. This helps you identify which workflows are driving the most call volume.

### Call minutes by workflow

Shows how total call time is distributed across workflows. A workflow that handles fewer calls but with longer durations will appear larger in this chart compared to the calls chart.

### Interacting with pie charts

* **Hover** over a slice to see the exact count for that workflow.
* **Click a legend item** to toggle a slice's visibility and recalculate the chart.
* **Show more** — If you have more than 10 workflows, click "Show more" in the legend to reveal additional entries.
* **Export** the data by clicking the menu icon and selecting **Download to CSV**.

<Tip>
  Use the calls pie chart alongside the call minutes pie chart to identify workflows with high call volumes but short durations versus workflows with fewer but longer calls. This can inform where to focus optimization efforts.
</Tip>

## Date range controls

The date range selector determines the time window for all metrics on the page. Select a preset or define a custom range.

| Preset          | Window                                               |
| --------------- | ---------------------------------------------------- |
| Last 30 minutes | Rolling 30-minute window                             |
| Last 1 hour     | Rolling 1-hour window                                |
| Last 6 hours    | Rolling 6-hour window                                |
| Last 12 hours   | Rolling 12-hour window                               |
| 1 day           | Rolling 24-hour window                               |
| 7 days          | Rolling 7-day window (default)                       |
| 30 days         | Rolling 30-day window                                |
| 1 year          | Rolling 1-year window                                |
| Custom          | User-defined start and end dates via calendar picker |

Changing the date range immediately re-fetches all metrics and charts.

## Time interval grouping

Control how data points are grouped on time-series charts (like runs by status). This affects the granularity of the x-axis.

| Interval | Behavior                                                | Availability                             |
| -------- | ------------------------------------------------------- | ---------------------------------------- |
| **Auto** | Interval selected automatically based on the date range | Always available                         |
| **Day**  | Each data point represents a 24-hour period             | Available for ranges of 1 day or longer  |
| **Week** | Each data point represents a 7-day period               | Available for ranges of 7 days or longer |

<Info>
  Auto interval adjusts dynamically. For a 30-minute range, data points are grouped in 30-second intervals. For a 7-day range, they're grouped in 15-minute intervals. For a 1-year range, they're grouped in 24-hour intervals.
</Info>

## Custom filters

Filter all dashboard metrics by workflow variable values. This is useful when you want to narrow analytics to a specific subset of runs — for example, only runs where `caller_intent` equals `"billing"` or where `region` is `"northeast"`.

<Steps>
  <Step title="Open the filter menu">
    Click the filter icon in the analytics header. A dropdown shows all available variables from your workflow's node outputs.
  </Step>

  <Step title="Select a variable">
    Choose the variable you want to filter by. You can search by variable name to find it quickly.
  </Step>

  <Step title="Choose values">
    Select one or more values for that variable. Only runs where the variable matches one of the selected values will be included in the analytics. You can search within values to find specific entries.
  </Step>

  <Step title="Apply additional filters">
    Repeat to add more filters. Multiple filters use AND logic — a run must match all active filters to be included. Active filter count appears as a badge on the filter button.
  </Step>
</Steps>

To remove a filter, click the **X** on its badge in the header, or reopen the filter menu and deselect the values.

## Next steps

<CardGroup cols={3}>
  <Card title="Workflow Metrics" icon="chart-pie" href="03-Workflow-Metrics.md">
    Build custom charts from workflow node output data.
  </Card>

  <Card title="Run Statuses" icon="circle-dot" href="../09-Runs-and-Monitoring/02-Run-Statuses.md">
    Understand what each run status means.
  </Card>

  <Card title="Runs Overview" icon="list-check" href="../09-Runs-and-Monitoring/01-Runs-Overview.md">
    Monitor individual runs and access transcripts.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/analytics/kpi-dashboard
