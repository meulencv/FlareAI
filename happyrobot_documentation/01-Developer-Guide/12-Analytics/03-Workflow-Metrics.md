---
title: "Workflow Metrics"
description: "Analyze workflow-level performance data"
---

# Workflow Metrics

> Analyze workflow-level performance data

Workflow metrics let you go beyond default KPIs and build custom visualizations from your workflow's node output data. Create pie charts to see outcome distributions, line charts to track trends over time, and sankey diagrams to visualize how data flows between stages. Custom charts are scoped to a specific workflow and are visible to all team members.

## Custom charts

Custom charts pull data from node outputs — the key-value pairs produced by each node during a run. Any variable your workflow generates can be charted.

### Creating a custom chart

<Steps>
  <Step title="Open the chart builder">
    Navigate to the **Analytics** tab for a specific workflow and click **Add Custom Chart** in the header. This opens the chart configuration panel.
  </Step>

  <Step title="Name your chart">
    Enter a **name** and optional **description**. The name appears as the chart title in the analytics view.
  </Step>

  <Step title="Select a chart type">
    Choose from **Pie chart**, **Line chart**, or **Sankey diagram**. Each type has different configuration options described below.
  </Step>

  <Step title="Configure the data source">
    Select the **variable** to chart. The dropdown lists all node output variables available in the workflow. Choose the node and the specific output key.
  </Step>

  <Step title="Set aggregation and classification">
    Choose how values are aggregated and optionally add classification filters. Configuration details vary by chart type — see the sections below.
  </Step>

  <Step title="Save">
    Click **Save** to add the chart to the analytics view. It appears immediately with data from the current time range.
  </Step>
</Steps>

<Info>
  Custom chart creation is available to users with **Editor** or **Owner** roles. Viewers can see existing charts but cannot create or modify them.
</Info>

### Editing and deleting charts

Click the menu icon on any custom chart to access **Edit** or **Delete** options. Editing opens the same configuration panel used during creation. Deleting removes the chart for all team members.

## Chart types

### Pie chart

Pie charts show the distribution of values for a single variable. Each unique value becomes a slice, sized by how many runs produced that value.

**Configuration:**

| Field              | Description                                       |
| ------------------ | ------------------------------------------------- |
| **Variable**       | The node output variable to chart                 |
| **Aggregation**    | Count (number of runs per value)                  |
| **Classification** | Optional. Limit the chart to specific values only |

**Use cases:** Outcome distributions (e.g., call dispositions, intent classifications, transfer reasons).

**Interactions:**

* Hover over a slice to see the exact count
* Click a legend item to toggle its visibility
* Click "Show more" in the legend if there are more than 10 values
* Export to CSV via the chart menu

### Line chart

Line charts show time-series trends for a variable. Each data point represents the aggregated value within a time bucket (controlled by the time interval setting).

**Configuration:**

| Field              | Description                                                                                            |
| ------------------ | ------------------------------------------------------------------------------------------------------ |
| **Variable**       | The node output variable to chart                                                                      |
| **Aggregation**    | **Count** (number of occurrences per time bucket) or **Sum** (total of numeric values per time bucket) |
| **Classification** | Optional. Segment the chart into multiple series — one line per classification value                   |

**Use cases:** Volume trends over time (e.g., daily call counts by disposition), numeric metric tracking (e.g., sum of order values per day).

**Interactions:**

* Hover over a point to see exact values at that timestamp
* Click a legend item to toggle a series' visibility
* X-axis formatting adapts to the selected date range and time interval
* Export to CSV via the chart menu

<Tip>
  Use the **Sum** aggregation with a numeric variable to track totals over time — like revenue, order quantities, or processing times. Use **Count** when you're interested in how often a value appears.
</Tip>

### Sankey diagram

Sankey diagrams visualize flow between stages. They show how values from one variable map to values in another, with the thickness of each connection proportional to the count or sum.

**Configuration:**

Sankey charts use a multi-layer system where each layer defines a source-to-target mapping:

| Field               | Description                                               |
| ------------------- | --------------------------------------------------------- |
| **Layers**          | One or more source-to-target variable pairs               |
| **Source variable** | The starting variable for this layer                      |
| **Target variable** | The ending variable for this layer                        |
| **Aggregation**     | **Count** or **Sum** per connection                       |
| **Label**           | Display name for the layer                                |
| **Value filter**    | Optional. Limit source or target values to a specific set |

**Use cases:** Call flow analysis (e.g., initial intent to final disposition), multi-step classification tracking, process stage progression.

## Custom filters on charts

All custom charts respect the global custom filters set in the analytics header. When you apply a filter (e.g., `region = "northeast"`), custom charts recalculate to include only runs that match.

Additionally, when configuring a pie or line chart, you can set a **classification** to limit which values appear. This acts as a chart-level filter — for example, showing only the top 5 call dispositions in a pie chart.

## Custom views

Custom views let you embed external analytics dashboards directly into the HappyRobot analytics interface. They appear as additional tabs alongside the default analytics view.

### How custom views work

A custom view embeds an external URL (typically a BI tool dashboard like Metabase, Looker, or a custom-built dashboard) in an iframe within the analytics page. This gives your team access to advanced analytics without leaving the platform.

### Managing custom views

<Steps>
  <Step title="Create a custom view">
    Click **Manage Views** in the analytics header (available to internal users). Enter a **name** and the **iframe embed URL** for the external dashboard.
  </Step>

  <Step title="Publish the view">
    Toggle the **Published** status to make the view visible to all organization members. Unpublished views are only visible to the creator.
  </Step>

  <Step title="Switch between views">
    Published custom views appear as tabs in the analytics header. Click a tab to switch between the default analytics view and any custom views.
  </Step>
</Steps>

<Info>
  Custom view management is restricted to internal users. Published views are visible to all organization members. You can create multiple custom views per organization.
</Info>

## Next steps

<CardGroup cols={3}>
  <Card title="Analytics Overview" icon="chart-line" href="01-Analytics-Overview.md">
    Return to the analytics overview for global controls and filters.
  </Card>

  <Card title="KPI Dashboard" icon="gauge-high" href="02-KPI-Dashboard.md">
    Review default metrics and call distribution charts.
  </Card>

  <Card title="Variables" icon="brackets-curly" href="../02-Workflows/07-Variables.md">
    Learn about node output variables used in custom charts.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/analytics/workflow-metrics
