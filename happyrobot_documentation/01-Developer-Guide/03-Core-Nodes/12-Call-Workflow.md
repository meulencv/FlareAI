---
title: "Call Workflow"
description: "Invoke another workflow and wait for its response, or start it and continue"
---

# Call Workflow

> Invoke another workflow and wait for its response, or start it and continue

The Call Workflow node lets you invoke a separate workflow from within your current one. The child workflow runs as its own execution. By default the parent waits for the child's response data before continuing; with [Fire and forget](#fire-and-forget) on, the parent continues as soon as the child starts.

<Note>
  This feature is only available for workflows using the V3 engine.
</Note>

Use this node to:

* Break complex logic into reusable sub-workflows
* Delegate specialized tasks (data enrichment, validation, external lookups) to dedicated workflows
* Share processing logic across multiple parent workflows without duplicating configuration

## Configuration

### Target workflow

Select the workflow to invoke:

* **Static** — Pick a workflow from the dropdown. Only workflows that are eligible to be called appear: they have a trigger of Predefined request, Incoming Hook, or Workflow Function Request, and have calling enabled (see [Making a workflow callable](#making-a-workflow-callable)). The current workflow is excluded. Target workflows on either engine version are listed.
* **Dynamic** — Use a [variable](../02-Workflows/07-Variables.md) that resolves to a workflow ID at runtime.

### Test output

<Note>
  This section applies when the node waits for a response. With **Fire and forget** on, there is no response to type, so the section is hidden.
</Note>

The **Test output** section is where you tell the node which response node's shape to expect, so its outputs are available to downstream nodes at design time.

* **Sample workflow** — The workflow to read the response node from. For a **static** target this mirrors your selected target workflow automatically. For a **dynamic** target, pick one explicitly — at runtime the real target still comes from the variable.
* **Sample node** — The **response node** whose output this node captures. Its output schema determines which fields are available as outputs in the parent workflow.

Response nodes are always resolved from the latest version of the sample workflow, so the schema follows the target as it evolves.

Only nodes marked as response points in the target workflow appear in the selector. To mark a node as a response node, open that workflow, click the action node, and turn on **Response node** in its configuration panel. Only action nodes can be response nodes — triggers and other node types don't have the setting.

A workflow can have more than one response node. When several are enabled, the first one to complete returns its output to the caller, so only enable multiple nodes when you want that branch-race behavior.

<Tip>
  You can also ask [Frontal](../02-Workflows/03-Frontal-AI-assistant.md) to mark or unmark a node as a response node — for example, "make the final node in this workflow a response node."
</Tip>

<Note>
  This selector determines the output schema you get to build against and what testing uses. It does not choose which node answers at runtime — that's decided by which nodes are marked as response nodes in the called workflow.
</Note>

### Version

Choose which version of the target workflow to execute. If left unset, the node always runs the latest published version.

### Environment

By default, the child workflow runs in the same environment as the calling workflow (**Use caller environment** is on). To pin the child workflow to a specific environment regardless of where the parent runs, disable this toggle and select **Staging** or **Production**.

### Timeout

Set the maximum number of seconds the parent workflow waits for the child workflow to reach its response node. If the timeout elapses before the child responds, the parent workflow proceeds with an empty output from this node — the child workflow continues running independently.

### Fire and forget

**Fire and forget** sits under **Timeout**. Turn it on when the parent has no use for the child's result: the node starts the target workflow, returns the child's run ID, and the parent continues immediately without waiting for a response node.

Use it for work that should happen alongside the caller rather than block it — kicking off a notification workflow, starting a long enrichment job whose result you'll read elsewhere, or fanning out to several workflows in sequence.

With **Fire and forget** on:

* The **Timeout** field is disabled — there is nothing to wait for.
* **Gracefully handle errors** and **Test output** are hidden. The node's only output is the child's run ID, so there is no response shape to configure and no child error to branch on.
* The target workflow does not need a response node, and the node no longer reports as incomplete when one isn't selected.

<Note>
  The child workflow's own failures are invisible to the parent in this mode. Find the child run by its run ID in the target workflow's **Runs** tab, or leave **Fire and forget** off if the parent needs to react to the outcome.
</Note>

### Gracefully handle errors

When this toggle is on, both **timeouts and errors in the child workflow** are returned as structured output from the node instead of an empty result, and the parent workflow continues. This lets you branch on whether the child responded successfully — for example, route to a fallback path when it times out or fails. The target workflow keeps running independently either way.

This setting applies only when the node waits for a response; it's hidden with **Fire and forget** on.

<Note>
  This setting was previously called **Gracefully handle timeout** and covered timeouts only. Nodes saved under the old name keep working; the setting now also covers child-workflow errors.
</Note>

### Payload

Pass data to the child workflow at invocation time. The child workflow receives this data as trigger variables. Two input modes are available:

* **Builder** — Add individual key-value pairs. Values support [variables](../02-Workflows/07-Variables.md) via the `@` picker.
* **Raw** — Enter a JSON body directly, with variable templating.

#### Expected request fields

When the target workflow is selected **statically** and its trigger declares request parameters — a **Predefined request** or **Workflow Function Request** trigger — the Payload section reads that contract and compares those parameters against the keys you've configured.

Any declared parameter you haven't added yet is called out in an info banner, which names the first three missing fields plus a count of the rest. Its **Add missing fields** button appends each one to the payload builder with an empty value for you to fill in. Keys you already configured are left untouched, and so is anything extra you send that the target doesn't declare.

<Note>
  Request-field suggestions come from the latest version of the selected target, so they follow the target workflow's contract as it changes. They aren't available for a **dynamic** target, since the target isn't known until runtime.
</Note>

## Making a workflow callable

Whether a workflow can be invoked by a Call Workflow node is controlled on the **target** workflow's trigger node, under **Advanced configuration**. These settings live on the trigger and are configured on the workflow you want to call, not on the caller.

* **Allow this workflow to be called by other workflows** — On by default. When enabled, the workflow appears in the Call Workflow target picker of other workflows. Turn it off to keep a workflow from being called.
* **Hide this workflow's execution in parent run views** — Shown only when calling is allowed. When enabled, the child workflow's execution detail is collapsed in the parent workflow's run view, so parent runs stay focused on the caller's own steps. The child still runs and appears as its own run in the target workflow's Runs tab.

Workflows triggered by a **Workflow Function Request** also expose a **Call compatible** setting. Enable it to let the entrypoint receive a live call handed off from another workflow — this exposes the call envelope parameters and makes the workflow selectable as an inbound voice agent call source. When it's enabled, the setting is enforced at publish.

<Note>
  The **calling** workflow must run on the V3 engine, but the workflow being called can be on either engine version. See [Workflow engine version](../02-Workflows/08-Versions-and-Publishing.md#workflow-engine-version-v2-and-v3).
</Note>

## Output

The output of this node matches the output schema of the selected response node in the target workflow. Reference output fields in downstream nodes using the `@` variable picker, the same way you reference any other node output.

With **Fire and forget** on, the node outputs the child workflow's run ID instead of a response payload.

## How it works

<Steps>
  <Step title="Parent workflow reaches the Call Workflow node">
    When execution arrives at this node, HappyRobot starts a new run of the target workflow, passing the configured payload as trigger data.
  </Step>

  <Step title="Child workflow runs">
    The child workflow executes independently. It appears as its own run in the target workflow's **Runs** tab, and inline within the parent run — the parent's run view shows the called workflow's name, status, and a response-node badge, and you can expand it to inspect the child's execution. Enable **Hide this workflow's execution in parent run views** on the child's trigger to collapse this detail by default.
  </Step>

  <Step title="Child workflow reaches its response node">
    When the child workflow hits a response node, its output is sent back to the parent workflow. If the workflow has several response nodes enabled, the first one to complete wins — the rest don't respond to the parent.
  </Step>

  <Step title="Parent workflow resumes">
    The parent workflow receives the response and continues from the Call Workflow node, with the child's output available for downstream references. The child workflow continues its execution independently after sending the response.
  </Step>
</Steps>

<Note>
  If a timeout is set and the child workflow does not respond in time, the parent continues with an empty output for this node. The child workflow keeps running until it completes or is canceled separately.
</Note>

With **Fire and forget** on, steps 3 and 4 don't apply — the parent resumes at step 2 with the child's run ID, and the child runs to completion on its own.

## Next steps

<CardGroup cols={2}>
  <Card title="Variables" icon="brackets-curly" href="../02-Workflows/07-Variables.md">
    Pass data between nodes and into child workflows using variables.
  </Card>

  <Card title="Workflow versions" icon="code-branch" href="https://docs.happyrobot.ai/workflows/versions">
    Understand how versioning affects which workflow version runs.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/call-workflow
