---
title: "Creating Tools"
description: "How to create and configure tools for your agents"
---

# Creating Tools

> How to create and configure tools for your agents

Custom tools let you define functions that your voice or text agent can call during a conversation. Each tool has a description (so the agent knows when to use it), parameters (the data the agent passes in), and a message configuration (what the caller hears or the user sees while the tool runs).

## Configuration

### Description

A rich-text description that tells the agent what this tool does and when to use it. The description is passed directly to the language model as part of the tool definition.

Supports variables — type `@` in the editor to insert values from previous nodes or workflow variables.

<Tip>
  Write the description from the agent's perspective. Instead of "This tool looks up load status", write "Use this tool when the caller asks about the status of a load. Requires a reference number."
</Tip>

### Message

Controls what happens while the tool is executing — what the caller hears (voice) or the user sees (text).

| Type      | Behavior                                                                                               | Configuration                                                             |
| --------- | ------------------------------------------------------------------------------------------------------ | ------------------------------------------------------------------------- |
| **AI**    | The agent generates a natural message before executing the tool (e.g., "Let me look that up for you.") | Optional description to guide the AI's message. Optional example message. |
| **Fixed** | A pre-written message is played or sent exactly as configured.                                         | Enter the exact message text.                                             |
| **None**  | No message — the tool runs silently.                                                                   | No additional configuration.                                              |

<AccordionGroup>
  <Accordion title="AI message">
    The agent generates a contextual message based on the conversation. You can provide a description (e.g., "Tell the caller you're checking their load status") and an example message to guide the tone.
  </Accordion>

  <Accordion title="Fixed message">
    A specific message that plays or sends every time the tool is invoked, regardless of context. Useful when you want consistent phrasing like "One moment while I check that for you."
  </Accordion>

  <Accordion title="No message">
    The tool executes silently. Best for fast-executing tools where a message would feel unnecessary or disruptive.
  </Accordion>
</AccordionGroup>

### Parameters

Parameters define the data the agent must collect from the conversation before calling the tool.

| Field            | Required | Description                                                                                                                                                           |
| ---------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**         | Yes      | The parameter key (e.g., `reference_number`, `email_address`).                                                                                                        |
| **Description**  | Yes      | Tells the agent what this parameter represents and how to extract it from the conversation.                                                                           |
| **Example**      | No       | A sample value to guide the model (e.g., `"ABC-12345"`).                                                                                                              |
| **Required**     | No       | When toggled on, the agent must collect this value before calling the tool. Defaults to off.                                                                          |
| **Value source** | No       | **Agent decides** (default) — the agent fills the parameter in from the conversation. **Fixed value** — you pin the value and the parameter is hidden from the agent. |

#### Fixed parameter values

Switching a parameter to **Fixed value** replaces its example field with a templated editor. The value you enter — literal text, [variables](../02-Workflows/07-Variables.md), or a mix — is sent to the tool exactly as configured on every call, and the parameter is not offered to the model, so it can't be guessed or omitted.

Use it for values the agent has no business choosing: a tenant identifier, an account code from the trigger payload, a fixed source system.

<Warning>
  A **required** parameter pinned to a fixed value must actually carry a value. The node reports `Fixed value required for: <parameter>` until you fill it in or hand the parameter back to the agent — otherwise the parameter would be hidden from the agent *and* missing from the call.
</Warning>

<Info>
  Parameter values become available as variables in the tool's child action nodes. For example, a parameter named `reference_number` can be referenced as `@reference_number` in a child Webhook node's URL or body.
</Info>

### Hold music

Controls what the caller hears while the tool's child nodes execute (voice agents only).

| Option              | Description                                                                                                               |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **Acoustic**        | Built-in acoustic background music.                                                                                       |
| **Ring tones**      | Built-in ring tone audio (North American cadence).                                                                        |
| **Ring tones (EU)** | Built-in European ring tone audio — the ETSI ringback cadence (1 second on, 4 seconds off) that callers in Europe expect. |
| **Custom**          | Upload or select a custom audio file from [Assets > Voices](../14-Assets/04-Voices.md).                                              |
| **None**            | Silence while the tool runs.                                                                                              |

Each option in the hold music dropdown has a **play button**, so you can hear a clip before selecting it. Starting a second preview stops the first.

<Tip>
  For tools that execute quickly (under 1–2 seconds), consider setting hold music to **None** to avoid an abrupt audio clip.
</Tip>

### Execution

Controls whether the conversation waits for the tool to finish. Set it in the tool's **Advanced** settings — available on tools attached to voice agents, text agents, and [MCP tools](05-MCP-Tools.md).

| Mode                      | Behavior                                                                                                                                        |
| ------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Blocking** (default)    | The agent waits until the tool finishes before continuing the conversation.                                                                     |
| **Background — silent**   | The tool runs in parallel so the conversation can continue. When it finishes, the result is recorded quietly and is available on the next turn. |
| **Background — announce** | Same as silent, but when the tool finishes the agent briefly tells the user the outcome — even if the conversation has moved on.                |

Use a background mode for slow lookups that don't block what the agent says next — enriching a contact record, writing to a CRM. Keep a tool blocking when the agent's next sentence depends on its result.

The **info** button next to the Execution selector describes all three modes in the node itself. On a text agent, note that a blocking tool can hold the conversation for up to 24 hours — text conversations have no live caller waiting, so a slow child node stalls the reply for far longer than it would on a call. Prefer a background mode for anything that isn't fast.

<Warning>
  Tools that transfer, end the session, or play hold music must stay blocking. When a tool is configured to do one of those things, the Execution selector is disabled and the node shows a **Background execution unavailable** warning.
</Warning>

### End call after tool

For voice agents, you can configure the tool to end the call immediately after its child nodes finish executing. Enable **End call after this tool** in the tool's Advanced settings. The call ends as soon as the tool returns — no further turn from the agent.

A tool that contains a [Genesys Transfer](../15-Integrations/04-Communication/05-Genesys-Audio-Connector.md#handing-the-call-back-to-architect) node always ends the call: the setting is turned on for you and locked on while the transfer is there, because the transfer's output variables only reach the Genesys Architect flow on the disconnect.

When end call is enabled, you can add custom SIP **BYE headers** that are sent on the BYE message back to the carrier. Useful for passing routing or metadata to your SBC or downstream systems. Each header is a key/value pair, and values support [variables](../02-Workflows/07-Variables.md).

Common header examples: `X-RouteReason`, `X-RouteType`, `X-RouteValue`, `X-MetaData`.

## Child nodes

Tools can have action nodes nested beneath them in the workflow editor. When the agent invokes the tool, these child nodes execute in sequence and their output is returned to the agent.

Common child node types include:

* **Webhook** — call an external API with the tool's parameters.
* **Custom Code** — run JavaScript or Python logic.
* **Integration actions** — interact with connected services (TMS, CRM, etc.).

Every output-producing node in the branch contributes to the tool's result — the agent receives one step per node, in execution order, containing the fields you chose to expose. Open **View Tool Call Result** at the bottom of the tool's configure panel to preview that payload and set field visibility. See [Tool Call Result](03-Tool-Call-Result.md).

<Note>
  Fields start hidden. A tool returns nothing to the agent until you expose the fields it needs, and a new tool blocks publishing until its Tool Call Result has been opened once — including tools you copy, duplicate, or import. Opening the panel executes nothing.
</Note>

## Example

A freight broker's voice agent needs to look up load status during calls.

1. **Tool name:** `check_load_status`
2. **Description:** "Use this tool when the caller asks about the status of their load or shipment. Requires a reference number."
3. **Parameters:** `reference_number` (required) — "The load reference number, e.g., ABC-12345."
4. **Message:** AI — "Tell the caller you're checking their load status."
5. **Hold music:** Ring tones
6. **Child node:** A Webhook node that calls the TMS API with `@reference_number` and returns the load status.

When a caller says "Can you check on load ABC-12345?", the agent extracts the reference number, says "Let me check on that for you", plays ring tones while the webhook runs, and then relays the result back to the caller.

## Related

<CardGroup cols={3}>
  <Card title="Tool Call Result" icon="eye" href="03-Tool-Call-Result.md">
    Preview and choose the payload the tool returns to the agent.
  </Card>

  <Card title="MCP Tools" icon="plug" href="05-MCP-Tools.md">
    Import tools from external MCP servers instead of building them manually.
  </Card>

  <Card title="Webhook" icon="globe" href="../03-Core-Nodes/06-Webhook.md">
    Call external APIs from your workflows.
  </Card>

  <Card title="Tool Call Result" icon="eye" href="03-Tool-Call-Result.md">
    Preview what the tool returns and choose which fields the agent sees.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/tools/creating-tools
