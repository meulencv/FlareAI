---
title: "Workflow Settings"
description: "Configure settings for individual workflows"
---

# Workflow Settings

> Configure settings for individual workflows

Each workflow has its own settings page where you can manage its configuration, business hours, signals, variables, and approval process.

## Accessing workflow settings

Open a workflow and click the **settings icon** in the toolbar, or navigate to **Settings > Workflows** and select the workflow you want to configure.

## General

The General tab contains basic workflow information and management actions.

* **Workflow name** — editable display name
* **Workflow icon** — choose a FontAwesome icon for visual identification
* **Workflow ID** — read-only identifier you can copy for use in API calls
* **Allow prompt publishing with open issues** — when enabled, prompts can be published even if they have unresolved review issues
* **Duplicate workflow** — creates a copy of the workflow with all its configuration. See [Duplicating a workflow](#duplicating-a-workflow)
* **Cancel all runs** — cancels every active run for this workflow
* **Delete workflow** — permanently removes the workflow (requires confirmation)

### Duplicating a workflow

The duplicate dialog asks for a name, the version to copy, and a **Destination folder**. The copy is created in the folder you choose instead of always landing next to the original — the field defaults to the source workflow's folder.

* The folder list is limited to places you can create workflows in, and to folders whose [Scope Tags](04-Scope-Tags.md) the copy is allowed to carry. If no destination is available, the dialog tells you that you don't have permission to create workflows here and the action stays disabled
* Choose the workspace root to create the copy outside any folder, when you're allowed to
* Workflow names are unique per organization across every folder, so a name already in use is rejected even when you pick a different destination

### Data retention

Under **Advanced Settings** in the General tab, you can configure automatic data deletion.

* **Enable Data Deletion** — toggle on to automatically delete workflow data (transcripts, outputs, etc.) after a retention period
* Retention period options: **7 days**, **14 days**, **30 days**, **60 days**, **90 days**, **180 days**, or **1 year**

<Tip>
  Enable data retention to comply with data handling policies. All sensitive information is removed from the platform after the configured period.
</Tip>

<Note>
  When the workspace has its own [data retention policy](01-Organization.md#data-retention), a workflow can only shorten it. Longer periods aren't offered in the picker, and a workflow that already had a longer period shows it as **exceeds workspace limit** until you pick a shorter one.
</Note>

## Out of office (business hours)

Define business hours schedules that voice agents can respect. When configured, voice agents using the `respect_business_hours` option will follow these schedules.

* A **Default** schedule always exists and cannot be deleted
* You can create additional named schedules for different scenarios
* **Timezone** — searchable dropdown sorted by UTC offset; defaults to your browser timezone

### Regular hours

Define operating hours per day of the week (e.g., Monday 9:00 AM - 5:00 PM). You can add multiple time ranges per day to handle split schedules like lunch breaks.

### Special days

Configure specific dates with custom hours — useful for holidays, closures, or extended hours on special occasions.

<Note>
  Leave the schedule empty for 24/7 availability. Only configure hours if you need to restrict when voice agents operate.
</Note>

## Signals

The **Signals** tab scopes outbound and inbound real-time signals for each agent in the workflow. It has two sub-tabs: **Outbound** for webhook delivery, and **Inbound** for agent signal subscriptions.

<Note>
  For the full picture of how signals work — the topic model, publishing from your systems, scheduled signals, and prompting agents to react — see [Signals](../02-Workflows/06-Signals.md).
</Note>

### Outbound webhooks

Send signals from your agents to external systems through webhook endpoints.

<Steps>
  <Step title="Add a webhook">
    On the **Outbound** sub-tab, click **Add Webhook** and enter the destination URL.
  </Step>

  <Step title="Add headers (optional)">
    Add key-value header pairs for authentication or routing (e.g., `Authorization: Bearer <token>`). Header keys must be unique within each webhook.
  </Step>

  <Step title="Save">
    Save the webhook. You can add multiple webhooks per workflow.
  </Step>
</Steps>

### Inbound signal subscriptions

Subscribe each agent in the workflow to signals published by your systems. While the agent is running, matching signals are delivered to its event loop and the agent can react to them through prompts and tools.

The **Inbound** sub-tab lists every agent (voice and text) in the workflow along with its current subscriptions. For each agent you can:

* **Enable or disable signals** — toggling signals on subscribes the agent to the default topics `session.<current>`, `usecase.<current>`, and `org.<current>`.
* **Add a custom topic** — open the **Subscribe to custom signals** dialog, give the topic a name, and add one or more binding patterns (e.g., `load.fulfilled` or `load.*`). Bindings follow the standard signal key pattern — dot-separated segments matching `a-z`, `0-9`, `-`, `_`, `*`, `#`, up to 256 characters. Keys starting with `org.`, `usecase.`, or `session.` are reserved.
* **Choose whether the agent responds when a signal arrives** — the **Start agent response on signal** toggle controls whether incoming signals wake the agent to generate a reply. When off, signals are still delivered but the agent only acts on them when it's already speaking.

Custom topics can be copied to the clipboard from each row, and removed individually when no longer needed.

<Note>
  The same **Agent signals** section also appears in each agent's node configuration panel — inbound voice, outbound voice, outbound-with-callback, inbound text, and outbound text agents — so you can configure subscriptions inline while editing the agent. Changes made in the workflow Signals tab and in the agent node are kept in sync.
</Note>

## Workflow variables

Workflow-level variables store environment-specific values scoped to this workflow. They follow the same structure as organization variables — each key has separate values for Production, Staging, and Development.

See [Environment Variables](08-Environment-Variables.md) for full documentation on how variables work and how they are resolved at runtime.

## Approval process

Control whether this workflow requires approval before publishing to specific environments. The same three environments are available: **Production**, **Staging**, and **Development**.

* If the organization enforces approval for an environment, it appears as **disabled** with an "(Enforced by organization)" label and cannot be turned off at the workflow level
* Only workflow owners can modify approval settings
* The **Approvers** panel shows designated approvers; Owners can approve by default

Workflows can add stricter approval requirements than the organization enforces but cannot remove organization-level enforcement. See the [Organization Settings](01-Organization.md#workflow-approval-process) page for details on org-level approval configuration.

## Next steps

<CardGroup cols={3}>
  <Card title="Workflows Overview" icon="diagram-project" href="../02-Workflows/01-Workflows-Overview.md">
    Learn how workflows are structured.
  </Card>

  <Card title="Environment Variables" icon="code" href="08-Environment-Variables.md">
    Configure variables across environments.
  </Card>

  <Card title="Organization Settings" icon="building" href="01-Organization.md">
    Manage organization-level settings.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/workflow-settings
