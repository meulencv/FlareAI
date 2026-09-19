---
title: "Environment Variables"
description: "Configure environment variables for your workflows"
---

# Environment Variables

> Configure environment variables for your workflows

Environment variables are key-value pairs available to your workflows at runtime. They let you store configuration values — like API endpoints, feature flags, or external credentials — that can differ between environments.

The **Settings > Variables** page has two tabs:

* **Variables** — Custom static key-value pairs you define. Each stores separate values for Production, Staging, and Development.
* **Time Variables** — Dynamic date/time values that are computed at runtime based on a configured timezone and format.

## Scopes

Both variable types exist at two levels:

| Scope            | Visibility                                     | Managed from                      |
| ---------------- | ---------------------------------------------- | --------------------------------- |
| **Organization** | Available to all workflows in the organization | **Settings > Variables**          |
| **Workflow**     | Available only to a single workflow            | **Workflow Settings > Variables** |

## Custom variables

Custom variables store static text values per environment (Production, Staging, Development).

<Steps>
  <Step title="Navigate to Variables">
    Go to **Settings > Variables** and select the **Variables** tab.
  </Step>

  <Step title="Add a variable">
    Click **Add Variable**, enter a key name, and set values for each environment.
  </Step>

  <Step title="Manage variables">
    Edit, delete, or search existing variables from the same page.
  </Step>
</Steps>

## Time variables

Time variables are resolved at runtime to the current date/time formatted according to a configured timezone and format string. Use them to inject the current date, time, or day into any workflow node without hardcoding static values.

<Steps>
  <Step title="Navigate to Time Variables">
    Go to **Settings > Variables** and select the **Time Variables** tab.
  </Step>

  <Step title="Add a time variable">
    Click **Add Variable** and configure:

    * **Key** — the variable name to reference in workflows (e.g., `current_date`)
    * **Timezone** — IANA timezone string (e.g., `America/New_York`) that determines what "now" means when the variable is resolved
    * **Format** — how to format the current time. Choose a preset or enter a custom format:

    | Preset             | Example output      |
    | ------------------ | ------------------- |
    | `yyyy-MM-dd`       | `2026-03-20`        |
    | `MM/dd/yyyy`       | `03/20/2026`        |
    | `yyyy-MM-dd HH:mm` | `2026-03-20 14:30`  |
    | `h:mm a`           | `2:30 PM`           |
    | `EEE, MMM d, yyyy` | `Fri, Mar 20, 2026` |
  </Step>
</Steps>

Time variables appear in the `@` variable picker under **Workflow Time Variables** or **Organization Time Variables**, depending on scope.

## Workflow variables

Workflow-level variables (both custom and time) are scoped to a single workflow and managed from that workflow's settings page.

Navigate to **Workflow Settings > Variables** to add or manage workflow-level variables.

## Variable resolution order

When a workflow runs, variables are resolved in the following order (later values override earlier ones):

1. **Organization-level variables** (lowest priority)
2. **Workflow-level variables** (override org-level)
3. **Trigger and session variables at runtime** (highest priority — e.g., phone numbers, room names)

If a workflow variable has the same key as an organization variable, the workflow-level value takes precedence.

## Use cases

* **Environment-specific configuration** — use development API endpoints during testing and production endpoints when live
* **Feature flags** — toggle behavior between environments without changing workflow logic
* **External credentials** — store third-party API keys or tokens that differ per environment

<Tip>
  Set up variable values for all environments you plan to deploy to. Missing variables can cause runtime failures when publishing a workflow to a new environment.
</Tip>

## Next steps

<CardGroup cols={2}>
  <Card title="Workflow Variables" icon="sliders" href="../02-Workflows/07-Variables.md">
    Learn how variables are used inside workflows.
  </Card>

  <Card title="Workflow Settings" icon="gear" href="10-Workflow-Settings.md">
    Configure per-workflow settings including variables.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/environment-variables
