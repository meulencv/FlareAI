---
title: "Tool Call Result"
description: "Preview and choose the payload a tool returns to the agent"
---

# Tool Call Result

> Preview and choose the payload a tool returns to the agent

Every tool has a **Tool Call Result** panel where you preview the payload the agent receives after the tool's child nodes run, and choose field by field what the agent actually sees. Fields you don't expose stay out of the tool result but remain available for debugging and as [variables](../02-Workflows/07-Variables.md) in downstream nodes.

Use it to keep tool results small and relevant — a webhook that returns a hundred-field TMS record only needs to hand the agent the three fields its next decision depends on.

## Opening the panel

Select a tool node in the workflow editor and click **View Tool Call Result** at the bottom of the tool's configuration panel. The panel slides over the configuration and shows the preview, the tool's branch nodes, and the generation controls.

<Note>
  Opening the panel is safe — nothing executes. It only reads the output schemas already generated for the tool's branch nodes.
</Note>

## Preview of what the agent receives

The top of the panel shows a representative result as ordered `steps` — one step per output-producing node in the tool's branch, in execution order, after your visibility choices are applied.

The preview is representative, not a recording of a specific run:

* Only nodes with a valid generated schema appear.
* A node inside a loop is shown once and marked with a **list** badge. At runtime the loop emits one step per iteration.
* When the branch has multiple paths, the preview shows all of them. At runtime only the path that actually runs appears.

## Branch nodes and their state

Below the preview, each output-producing node in the branch gets a card. Expand a card to see its fields and controls. The icon on the right reports the node's state:

| State          | Indicator                                                                         | Meaning                                                                                       |
| -------------- | --------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------- |
| **Valid**      | No icon                                                                           | The node's configuration is complete and its output schema has been generated and is current. |
| **Untested**   | Warning icon — *Output schema not generated* or *Generated output is out of date* | The node needs generating before its fields can be exposed.                                   |
| **Incomplete** | Red icon with the reason                                                          | The node's configuration isn't finished yet. Generation skips it.                             |

A tool with no nodes in its branch shows **This tool has no nodes yet** — add nodes to the branch to see what the agent will receive.

## Choosing the fields to expose

Each node card lists the leaf fields of its generated schema with a toggle. Exposed fields go to the agent; hidden fields don't.

* **Expose all fields** / **Hide all fields** flips every field on the card at once.
* Toggling a parent group exposes or hides everything under it.
* Use **Search fields…** at the top of the node list to filter across every node's fields. Matching cards expand automatically.

When you regenerate a schema, your existing choices are carried forward: fields that still exist keep their setting, fields that disappeared drop out, and **newly discovered fields start hidden**. If a node starts returning something new, regenerate and then expose it deliberately.

<Tip>
  Expose the fewest fields the agent needs for its next decision. Everything you expose costs prompt tokens and gives the model more to misread — and everything you hide is still available in the run details and to downstream nodes.
</Tip>

## Sync and Generate

Generating a schema means running the node for real. Two controls sit at the bottom of the panel:

| Control                       | What it does                                                                                                                |
| ----------------------------- | --------------------------------------------------------------------------------------------------------------------------- |
| **Sync Tool Call Result**     | Reuses valid schemas and generates only the untested or out-of-date nodes. Appears when at least one node needs generating. |
| **Generate Tool Call Result** | Re-runs every testable node in the branch, whether or not its schema is current.                                            |

You can also generate a single node with the **Generate** button on its card.

<Warning>
  Sync and Generate execute nodes for real. Webhooks fire, emails send, and integration writes can happen. Prefer a single-node **Generate** or **Sync** over a full **Generate**, and check what the branch does before running it. Incomplete nodes are reported but never run.
</Warning>

## Publishing

A new tool blocks publishing until you open its Tool Call Result once. This includes tools you copy, duplicate, or import — a copy is a new tool and needs its own acknowledgement.

* The tool node shows a red warning icon on the canvas — *Tool Call Result has not been opened yet* — and the publish check lists the tool with the reason **Tool Call Result has not been opened yet. Open it to check what this tool sends to the agent**.
* Opening the panel clears the block. So does any successful Sync, Generate, or visibility change.
* Tools that predate this feature never block publishing.
* A tool whose branch has no output-producing nodes never blocks publishing.

A separate warning icon — *Tool Call Result has untested or out-of-date nodes* — flags drift after the first acknowledgement. It does **not** block publishing.

The panel is read-only on published or locked versions, the same as the rest of the editor.

## Working with Frontal

You can ask [Frontal](../02-Workflows/03-Frontal-AI-assistant.md) to set a tool's result up end to end. It can inspect the current result, sync or generate the schemas, and expose only the fields the agent needs. Frontal reports which nodes it generated, which it skipped as incomplete, and which failed.

Because generation executes nodes for real, tell Frontal to inspect first when the schemas are already valid.

## Via the API

Four endpoints mirror the panel's operations, scoped to a single tool node on an unpublished workflow version:

| Endpoint                                                                 | Operation                                                              |
| ------------------------------------------------------------------------ | ---------------------------------------------------------------------- |
| `POST /versions/{version_id}/tools/{tool_id}/tool-call-result/inspect`   | Return the current result and acknowledge the tool. Generates nothing. |
| `POST /versions/{version_id}/tools/{tool_id}/tool-call-result/sync`      | Generate only untested or out-of-date nodes.                           |
| `POST /versions/{version_id}/tools/{tool_id}/tool-call-result/generate`  | Generate every testable node.                                          |
| `PUT /versions/{version_id}/tools/{tool_id}/tool-call-result/visibility` | Replace the complete list of exposed field paths for one branch node.  |

The response includes the tool's `ack_state`, each node's `state`, `output_schema`, and `fields` (each with `path` and `exposed`), and the same `preview.steps` the panel renders. `sync` and `generate` also return `generated` and `skipped_incomplete` lists.

Sync and generate take an `environment` in the body (`development` by default) — the environment whose credentials and settings the node tests run against. Requests against a published or live version are rejected with `400`.

<Note>
  Visibility is a full replacement: send the complete list of exposed leaf-field paths for that node, or `[]` to expose none.
</Note>

See the [API reference](https://docs.happyrobot.ai/api-reference) for the full request and response schemas.

## Related

<CardGroup cols={2}>
  <Card title="Creating tools" icon="screwdriver-wrench" href="02-Creating-Tools.md">
    Configure a tool's description, parameters, messages, and child nodes.
  </Card>

  <Card title="Versions and publishing" icon="code-branch" href="../02-Workflows/08-Versions-and-Publishing.md">
    How the publish check decides whether a version can go live.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/tools/tool-call-result
