---
title: "SLA and service status"
description: "Review measured platform availability, live incidents, and how uptime is calculated"
---

# SLA and service status

> Review measured platform availability, live incidents, and how uptime is calculated

The **SLA** page reports measured availability of the core platform for the region serving your workspace, alongside any incident or maintenance that is currently in progress. Open it from **Settings > Service > SLA**.

<Note>
  The page is only available to workspaces with platform availability reporting enabled on their agreement. If you don't see **SLA** in the settings sidebar, your workspace doesn't have it — contact your account team.
</Note>

## Availability

Each measured component is listed with its uptime over the **last 30 days**, as a rolling window that ends at the most recently closed hour.

| Component            | What it covers                     |
| -------------------- | ---------------------------------- |
| **Voice · Inbound**  | End-to-end inbound call handling   |
| **Voice · Outbound** | End-to-end outbound call placement |

Percentages are the ratio of successful checks to total checks over the window — a volume-weighted ratio, not an average of hourly percentages, so a quiet hour doesn't count the same as a busy one.

If measurements for your region haven't been recorded yet, the section says so. They start appearing within a few hours of the feature being enabled.

### Insufficient data

When too few of the expected checks are present for a window, the page shows `—` and **Insufficient data** with the coverage percentage instead of a number. This is deliberate: a percentage computed over a monitoring gap reads better than reality, which would hide the gap rather than report it. A number is published only once coverage reaches 95% of the checks the window should have contained.

## Current status

The **Current status** section shows what is happening right now, from the same source as the incident banner in the sidebar — so the two can never disagree:

* **All systems operational** when there is no ongoing incident or maintenance
* One entry per ongoing **incident** or **maintenance**, tagged with the affected components and linking to its status page entry

**Status page and incident history** links out to the full public status page for past incidents.

## How this is measured

Availability comes from continuous synthetic end-to-end checks run by the platform's own monitoring — once per minute per direction, in the region serving your workspace. A check exercises the full path (telephony, session orchestration, and workflow execution) and counts as successful only when it completes end to end.

Maintenance windows published on the status page are excluded from the measurement period entirely, which is standard SLA practice. Any hour a window touches is dropped from both the ratio and the coverage denominator, so a planned window doesn't read as downtime or as a monitoring gap.

## What is out of scope

The figures cover the shared platform. They deliberately don't reflect problems limited to a single workspace, workflow, or third-party system — including your own integrations with external systems. Those are handled as incidents rather than through this measurement.

## Related

<CardGroup cols={2}>
  <Card title="Organization settings" icon="building" href="01-Organization.md">
    Workspace-level configuration and data retention.
  </Card>

  <Card title="Runs overview" icon="list-check" href="../09-Runs-and-Monitoring/01-Runs-Overview.md">
    Investigate individual executions when something looks wrong.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/sla
