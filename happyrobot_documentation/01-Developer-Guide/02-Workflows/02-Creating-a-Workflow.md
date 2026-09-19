---
title: "Creating a Workflow"
description: "Step-by-step guide to building your first workflow"
---

# Creating a Workflow

> Step-by-step guide to building your first workflow

In this guide, you'll create a workflow from scratch — add a trigger, configure action and condition nodes, and test the result. By the end, you'll have a working automation ready to deploy.

<Info>
  **Prerequisites**

  * A HappyRobot account — [contact sales](mailto:sales@happyrobot.ai) if you don't have one yet
  * At least one integration connected in **Settings > Integrations** (for action nodes)
</Info>

## Create a new workflow

<Steps>
  <Step title="Navigate to the Workflows page">
    Go to [platform.happyrobot.ai](https://platform.happyrobot.ai) and open the **Workflows** page from the sidebar.
  </Step>

  <Step title="Create a new workflow">
    Click **New Workflow**. The creation dialog opens with three tabs:

    * **From Scratch** — Build a new workflow with a blank canvas.
    * **Templates** — Choose from pre-built templates *(coming soon)*.
    * **Upload File** — Import a previously exported workflow JSON file.

    Give the workflow a name and select a folder location. You can also choose the **Workflow Graph Engine** — **Version 3** is the default (recommended), or **Version 2 (Legacy)** for older workflows.
  </Step>

  <Step title="Open the workflow editor">
    After creating the workflow, the visual editor opens with an empty canvas. This is where you'll build the workflow.
  </Step>
</Steps>

## Import a workflow from a file

If you've previously exported a workflow as a JSON file, you can import it to create a new workflow without starting from scratch.

<Steps>
  <Step title="Open the new workflow dialog">
    Click **New Workflow** and select the **Upload File** tab.
  </Step>

  <Step title="Upload the file">
    Drag a `.json` file onto the upload area, or click **Choose File** to browse. The dialog validates the file and auto-detects the workflow version. A confirmation shows which engine version was found.
  </Step>

  <Step title="Set a name and location">
    Enter a name for the imported workflow and choose a folder. The name defaults to the filename if left blank.
  </Step>

  <Step title="Import">
    Click **Import**. HappyRobot creates the workflow and navigates to the editor.
  </Step>
</Steps>

<Note>
  Only `.json` files exported from HappyRobot are supported. The file must contain a valid `workflowVersion` field (Version 2 or Version 3).
</Note>

## Add a trigger

Every workflow starts with a trigger — the event that kicks off execution.

<Steps>
  <Step title="Click Add Trigger">
    Click the **Add Trigger** button on the canvas. A panel opens showing all available trigger types.
  </Step>

  <Step title="Choose a trigger type">
    Select a trigger type. For this example, choose **Webhook** — this lets you start the workflow with an HTTP request.
  </Step>

  <Step title="Configure the trigger">
    The webhook trigger auto-generates an endpoint URL based on your workflow slug. You can configure authentication settings (API key or Bearer token) in the trigger panel.
  </Step>
</Steps>

<Tip>
  See [Triggers](05-Triggers.md) for a full list of trigger types including inbound calls, emails, SMS, and scheduled runs.
</Tip>

## Add nodes

With the trigger in place, add nodes to define what happens when the workflow runs.

<Steps>
  <Step title="Add an action node">
    Click the **+** button after the trigger node. Select **Action** from the node type menu. Action nodes execute integration events — sending emails, querying databases, calling APIs.
  </Step>

  <Step title="Configure the action">
    In the configuration panel, select an integration (for example, **Gmail**), then choose an event (for example, **Send Email**). Fill in the parameters — recipient, subject, body. You can use variables to insert dynamic data.
  </Step>

  <Step title="Add a condition node">
    Click the **+** button again and select **Condition**. Condition nodes branch the workflow into different paths based on data. Configure a condition — for example, check if a status field equals "urgent".
  </Step>

  <Step title="Add nodes to each branch">
    Each branch of the condition can have its own sequence of nodes. Click **+** on the "true" or "false" path to add follow-up actions.
  </Step>
</Steps>

<Tip>
  Type in the node menu to search across every integration and event. Results for integrations you have already connected are listed first, so the provider you actually use outranks same-named events from providers you haven't set up.
</Tip>

## Copy and paste nodes

Instead of rebuilding a configured node from scratch, copy it to the editor clipboard and paste it somewhere else — later in the same workflow, or into a different workflow in the same organization.

### Copying from the node menu

Open a node's options menu (the **⋯** icon) and pick a copy action. Which actions appear depends on the node type:

| Node type     | Actions                                                                                                                                                        |
| ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Action**    | **Copy Node** copies the node on its own. **Copy Node & Nested** also copies everything downstream of it, and appears only when the node has nodes beneath it. |
| **Paths**     | **Copy Node & Conditions** copies the Paths block together with all of its branches.                                                                           |
| **Agent**     | **Copy Agent** copies the agent and the prompt and tool nodes nested inside it. **Copy Agent & Nested** also copies everything downstream.                     |
| **Loop**      | **Copy Loop** copies the loop and its body. **Copy Loop & Nested** also copies everything after the loop.                                                      |
| **Condition** | **Copy & Sequence** copies the condition along with the chain of nodes underneath it.                                                                          |

### Copying a selection

To copy several nodes at once, click the **Select nodes on the canvas** button in the editor toolbar, click the nodes you want, then click **Copy** in the selection toolbar.

A selection can only be copied when it forms one connected block:

* Exactly one selected node is the topmost node — every other selected node must have its parent selected too.
* If a loop is selected, its whole visible body must be selected, and a selection can't straddle the edge of a loop.
* If an agent node is selected, all of its nested nodes must be selected.
* If a Paths block is selected, its entire subtree must be selected.

When the selection doesn't qualify, the **Copy** button is disabled and reads *Select a valid sequence to copy*.

### Pasting

Copying puts the editor into **paste mode** automatically. While it's on, clicking a **+** insert point on the canvas pastes the clipboard there instead of opening the add-node menu. Only insert points that accept what you copied will paste — a copied tool goes into tool positions, a copied condition into condition positions, and so on.

Use the clipboard buttons in the toolbar to leave paste mode, re-enter it later, or clear the clipboard.

A paste is a single editor operation, so **Undo** reverses the whole thing at once.

<Note>
  The clipboard lives in your browser and holds one copy at a time. It persists across page loads, so you can copy in one workflow and paste in another — but only within the same organization.
</Note>

## Connect and configure

Data flows forward through the workflow automatically. Each node can reference outputs from any previous node.

In the workflow editor, type **@** in any text field to open the variable picker. It lists all available outputs from the trigger and previous nodes — select one to insert it.

When working with API configurations outside the UI, use double curly brace syntax instead: `{"{{variable_name}}"}`.

See [Variables](07-Variables.md) for more on referencing variables and data flow.

## Save and test

<Steps>
  <Step title="Auto-save">
    Workflows auto-save as you edit. Every change is persisted immediately — no manual save required.
  </Step>

  <Step title="Trigger a test run">
    Send a test request to your webhook endpoint (or trigger the workflow through your configured trigger) to verify everything works. Check the **Runs** tab to see the execution result.
  </Step>

  <Step title="Review results">
    Open the run detail to see node-by-node execution, outputs, and any errors. Each node shows its input, output, and execution time.
  </Step>
</Steps>

### Node output schemas

Many nodes — action, event, and loop nodes — generate an output schema from a test run so downstream nodes can reference their fields with the `@` variable picker. Open a node and use the **Generate Output Schema** button (or the Testing Drawer for loop nodes) to capture an output.

Each test run is saved and listed in the **Output Schema Version** selector inside the node's testing panel. Previous outputs are labeled with their timestamp so you can switch between them — useful when comparing runs or when a downstream node was wired up against an older shape.

If you need a specific output shape that isn't easy to capture from a real run — for example, to scaffold downstream nodes before the upstream integration is ready — click the **`{ }`** (braces) icon next to the version selector to open the **Custom Output** dialog. Paste or edit a JSON object in the editor and save it; the custom output becomes the active schema for downstream variable resolution, just like any other test output.

<Note>
  Custom outputs are only available while the workflow version is editable. Published versions are immutable, so the braces button is disabled.
</Note>

For nodes nested under a tool, the generated schema also decides what the agent can see. Newly generated fields start hidden, and you expose the ones the agent needs from the [Tool Call Result](../04-Tools/03-Tool-Call-Result.md) panel. Regenerating a schema — or replacing it with a custom output — keeps your existing choices and hides only the fields it discovers for the first time.

## Next steps

<CardGroup cols={2}>
  <Card title="Node types" icon="shapes" href="04-Node-Types.md">
    Learn about action, prompt, tool, condition, loop, and module change nodes.
  </Card>

  <Card title="Triggers" icon="bolt" href="05-Triggers.md">
    Explore all trigger types and configuration options.
  </Card>

  <Card title="Variables" icon="brackets-curly" href="07-Variables.md">
    Master template variables and dynamic data flow.
  </Card>

  <Card title="Versions and publishing" icon="rocket" href="08-Versions-and-Publishing.md">
    Publish your workflow and manage versions.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/workflows/creating-a-workflow
