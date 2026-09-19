---
title: "Components"
description: "Reusable prompt components and templates"
---

# Components

> Reusable prompt components and templates

Components are reusable building blocks you can share across multiple workflows. Instead of duplicating prompt text or action configurations in every workflow, create a component once and reference it wherever you need it. There are two types: **prompt components** (reusable text and prompt snippets) and **node components** (reusable action node configurations).

## Component types

| Type                 | Description                                                                                                       |
| -------------------- | ----------------------------------------------------------------------------------------------------------------- |
| **Prompt component** | Reusable prompt text with variable inputs. Referenced inside prompt nodes across workflows.                       |
| **Node component**   | Reusable action node configuration tied to a specific integration event. Referenced as action nodes in workflows. |

## Creating a prompt component

<Steps>
  <Step title="Choose the component type">
    Go to **Assets > Components** and click **Create Component**. Select **Prompt** as the type.
  </Step>

  <Step title="Start from scratch or use a template">
    You can write your prompt from a blank canvas, or select a template from the template library to use as a starting point.
  </Step>

  <Step title="Set name and description">
    Enter a name (alphanumeric characters and underscores only) and an optional description. The name is how you'll reference this component from workflows.
  </Step>

  <Step title="Write the prompt">
    Use the rich text editor to write your prompt content. You can include variable references that will be resolved at runtime.
  </Step>

  <Step title="Define component inputs">
    Add **component inputs** — key/ID pairs that define the variables this component expects. Any workflow that uses this component must provide values for these inputs.
  </Step>

  <Step title="Add tags (optional)">
    Tag your component for easier categorization and discovery when browsing the component library.
  </Step>
</Steps>

Version 1 is published the moment you create the component, so it's immediately usable in workflows. Every edit after that starts as a draft — see [Versions and publishing](#versions-and-publishing).

### Creating a prompt component with Frontal

You can also ask the [Frontal AI assistant](../02-Workflows/03-Frontal-AI-assistant.md#manage-prompt-components) to create or edit a prompt component for you — for example, "create a prompt component for our carrier greeting" or "update the `check_call_intro` component to mention the reference number." Frontal writes the component's Markdown content and inputs.

<Note>
  Frontal's edits to an existing component are saved as a draft version, and Frontal tells you the change isn't live. Publish the draft yourself from **Assets > Components** when you want workflows to use it. Components Frontal creates from scratch are live at version 1. Frontal can't publish or delete components.
</Note>

## Creating a node component

You can build a node component from scratch in the component library, or generate one from a node you've already configured in a workflow.

### From scratch

<Steps>
  <Step title="Choose the component type">
    Go to **Assets > Components** and click **Create Component**. Select **Node** as the type.
  </Step>

  <Step title="Set name and description">
    Enter a name and optional description for the component.
  </Step>

  <Step title="Select an integration event">
    Choose the **integration event** this component wraps — for example, a specific API action from Gmail, Slack, or any other connected integration.
  </Step>

  <Step title="Configure event fields">
    Configure the event's fields, mapping them to component inputs where values should be provided by the consuming workflow.
  </Step>

  <Step title="Define component inputs">
    Define the component inputs that map to the event's configuration parameters. These become the interface that consuming workflows interact with.
  </Step>
</Steps>

### From an existing workflow node

If you've already configured an action node the way you want it, you can turn it into a node component without rebuilding it:

<Steps>
  <Step title="Select the node">
    Open the node in the workflow editor so its configuration panel is showing.
  </Step>

  <Step title="Choose Create Node Component">
    Open the **…** menu in the panel header and select **Create Node Component**.
  </Step>

  <Step title="Review the prefilled component">
    The component form opens with the node's name, integration event, and configuration already filled in. Every [variable](../02-Workflows/07-Variables.md) the node referenced is converted into a component input, so the component is portable across workflows.
  </Step>

  <Step title="Name the inputs and save">
    Rename the generated inputs to something meaningful, adjust the description and tags, and save.
  </Step>
</Steps>

The action is available on action nodes only — it doesn't appear on triggers, Paths blocks, or nodes that are already synced with a component. You also need permission to manage components in the workspace.

## Using components in workflows

Reference components from workflow nodes to reuse their logic. When you add a component to a workflow, you'll need to provide values for all of the component's defined inputs — either as static values or by mapping them to [workflow variables](../02-Workflows/07-Variables.md).

In a [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md), insert a prompt component by typing `/` and choosing **Prompt Component**, or by clicking the package icon in the editor toolbar. The component is inserted as a card showing its name and input mapping. Click the component's name on the card, or choose **Edit in Components** from its menu, to jump straight to that component in **Assets > Components**.

Workflows always resolve a prompt component to its **live version** — the version you last published, not the latest draft.

## Conditional prompt components

A conditional prompt component picks which prompt component to include based on the state of the run. Use it when the same agent needs different instructions for different situations — a different escalation policy per region, or a different script per customer tier — without duplicating the whole prompt.

<Steps>
  <Step title="Insert the block">
    In a prompt node, type `/` and choose **Conditional Prompt Component**, or click the boxes icon in the editor toolbar. The block is inserted collapsed, labeled **Conditional component**, with the names of the selected components listed next to the label.
  </Step>

  <Step title="Add cases">
    Expand the block and add a **case** for each situation. A case has two parts: a **condition** built with the same AND/OR condition builder used by [conditional nodes](../03-Core-Nodes/09-Conditionals.md#condition-builder), and the **prompt component** to include when that condition matches. Map the component's inputs the same way as a regular prompt component reference.
  </Step>

  <Step title="Order the cases">
    Drag cases to reorder them. Only the **first matching case** is included in the prompt, so put more specific conditions above general ones.
  </Step>

  <Step title="Set a fallback (optional)">
    Select a **Fallback** component to include when no case matches. Leave it empty when the prompt shouldn't say anything extra in that situation.
  </Step>
</Steps>

Conditions are evaluated against the [variables](../02-Workflows/07-Variables.md) available at that prompt node, so they can reference trigger data, upstream node outputs, and environment variables.

<Note>
  Every case needs both a complete condition and a selected prompt component. Until they all do, the prompt node reports "Every conditional prompt case requires a complete condition and prompt component" and the workflow can't be published.
</Note>

To remove the block, open its **⋯** menu and choose **Remove Conditional Prompt Component**. Removing a case or the whole block also releases the [usage records](#usage-tracking) it held on the referenced components.

## Versions and publishing

Prompt components separate *saving* from *publishing*, so you can iterate on a component that live workflows depend on without changing their behavior until you're ready.

| Action               | What happens                                                                                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Create**           | Version 1 is created and published immediately, so the component is usable right away.                                                                                          |
| **Save**             | Creates a new version as a draft. Workflows keep running the current live version.                                                                                              |
| **Save and Publish** | Creates a new version and makes it live. Every workflow referencing the component picks it up, and each affected workflow version gets a changelog entry recording the publish. |

The edit dialog header tells you which version workflows are currently using.

### Where to see version state

| Location             | What it shows                                                                                                                                |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Components table** | A **Live Version** column with the currently published version number, and a status indicator next to the component name.                    |
| **Changelog list**   | Every version in order, with a **Live** marker — a pulsing indicator — on the published one.                                                 |
| **Changelog diff**   | A side-by-side prompt and input diff. Pick any earlier version from the left-hand selector to compare it against the version you're viewing. |

### Publishing or reverting an earlier version

From the changelog diff you can act on the version you're viewing:

* **Publish** — make the selected version live. Disabled when that version is already live.
* **Revert to this Version** — copy the selected version's prompt, inputs, name, and description into a *new* version at the top of the history. Reverting doesn't delete anything and doesn't publish — publish the new version if you want workflows to use it. Disabled when you're already viewing the latest version.

<Note>
  Draft-and-publish applies to prompt components. Node components don't have a separate live version — saving a node component updates it directly.
</Note>

## Northstars for prompt components

A prompt component can carry its own [northstars](../11-Quality-and-Evaluation/02-Northstars.md) so every workflow that embeds it is graded against the same quality bar. Open the component row's action menu and choose **Manage Northstars** to create them, generate them from the component's content, or assess their coverage.

See [Northstars on prompt components](../11-Quality-and-Evaluation/02-Northstars.md#northstars-on-prompt-components) for what that page offers, and [Where prompt component northstars appear](../11-Quality-and-Evaluation/02-Northstars.md#where-prompt-component-northstars-appear) for how a component's northstars are grouped inside a workflow's table. A single workflow version can also add its own northstar to an embedded component without changing the component — see [Northstars for a single version](../11-Quality-and-Evaluation/02-Northstars.md#northstars-for-a-single-version).

## Usage tracking

The platform tracks where each component is used across workflows and environments (production, staging, development). In **Assets > Components**, a component that's live somewhere is badged **Live** (production), **Staging**, or **Development**, and its **⋯** menu has a **View Usages** action (with the usage count) that lists every workflow using it. Each workflow is grouped with its versions, and each version is marked **Live** (with its environments), **Locked** (published but not live), or **Draft**. Hover a version row and click the external-link icon to open that version in the editor.

Use this before publishing a change to see which live workflows it will affect.

Click the **Name** column header to sort the components table alphabetically; click again to reverse the order.

<Info>
  Deletion is blocked if a component has active usages. Remove all references to a component from your workflows before deleting it.
</Info>

## Next steps

<CardGroup cols={3}>
  <Card title="Workflows overview" icon="diagram-project" href="../02-Workflows/01-Workflows-Overview.md">
    Learn how to build automated workflows.
  </Card>

  <Card title="Prompts and tools" icon="message" href="../05-Voice-Agents/06-Prompts-and-Tools.md">
    Write effective prompts and attach tools to agents.
  </Card>

  <Card title="Integrations" icon="plug" href="../15-Integrations/01-Integrations-Overview.md">
    Connect third-party services to your workflows.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/assets/components
