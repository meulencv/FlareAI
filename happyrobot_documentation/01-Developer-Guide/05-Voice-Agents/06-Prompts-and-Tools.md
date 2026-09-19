---
title: "Prompts and Tools"
description: "Write prompts and attach tools to voice agents"
---

# Prompts and Tools

> Write prompts and attach tools to voice agents

Every voice agent contains a **prompt node** that defines the agent's personality, instructions, and conversation behavior. Beneath the prompt node, you can attach **tool nodes** — functions the agent can call mid-conversation to look up data, transfer calls, or perform actions. This page covers how to write effective prompts and configure tools for voice agents.

## Prompt node

The prompt node is automatically created inside every voice agent. It controls what the agent says, how it behaves, which LLM model it uses, and which [built-in tools](../04-Tools/04-Built-in-Tools.md) are available to it.

### Prompt node tabs

The prompt node's configuration panel is split into tabs:

| Tab          | Contents                                                                                                                                                                                             |
| ------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Behavior** | The prompt, initial message, and the rest of the fields in the table below.                                                                                                                          |
| **Built-in** | The [built-in tools](../04-Tools/04-Built-in-Tools.md#the-built-in-tab) for this agent — hang up, stay silent, and press digit on voice agents; channel-specific tools on [text agents](../06-Text-Agents/01-Text-Agents-Overview.md). |

On an [outbound agent with callback](04-Outbound-with-Callback.md), the first tab splits into **Outbound** and **Inbound** so each direction gets its own prompt, and **Built-in** applies to both.

A prompt node with active built-ins shows a **built-in** badge on the canvas listing them, so you can see what the agent can call without opening the panel.

### Prompt fields

| Field                                          | Description                                                                                                                                                                                                                                                                                                                                                      |
| ---------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prompt**                                     | The main system prompt — instructions, personality, conversation flow, and rules the agent follows. This is the primary prompt used for outbound calls.                                                                                                                                                                                                          |
| **Inbound prompt**                             | A separate prompt used when the agent handles inbound calls. If left empty, the main prompt is used for both directions. Useful when the same workflow handles both outbound and inbound callback scenarios.                                                                                                                                                     |
| **Initial message**                            | The first thing the agent says when it joins the call. If left empty, the agent waits for the caller to speak first. For outbound calls, this is typically a greeting like "Hi, this is Sarah from Acme Corp."                                                                                                                                                   |
| **Receiving initial message**                  | The first thing the agent says when receiving an incoming call. Separate from the outbound initial message so the agent can greet differently based on call direction.                                                                                                                                                                                           |
| **Model**                                      | The language model used to generate responses, along with its reasoning effort and speed where the family offers a choice. See [choosing a model](05-STT-TTS-and-LLM-Configuration.md#choosing-a-model). Supports static selection or dynamic [variables](../02-Workflows/07-Variables.md).                                                                             |
| **No initial message**                         | When enabled, the agent does not speak first — it waits silently for the caller to say something. Useful for inbound calls where the caller initiates the conversation.                                                                                                                                                                                          |
| **Protect initial message from interruptions** | *(Voice agents only)* When enabled, the caller cannot interrupt the agent's initial message — the agent finishes its greeting before it starts listening. Disabled by default. Use this when the opening message contains required information (such as a recording disclaimer or identification) that must be heard in full.                                    |
| **Delay initial message**                      | *(Voice agents only)* How long to wait, in seconds, before speaking the initial message, so the agent doesn't talk over the other party as the call connects. Empty (the default) greets immediately. Accepts up to 10 seconds in 0.5-second steps. If the other party speaks first, the wait ends early and the initial message becomes the agent's first turn. |

<Tip>
  Use **Delay initial message** when the far end tends to say something as the call connects — a "hello?" or an automated greeting — so the agent doesn't talk over it. A half-second to a second is usually enough.
</Tip>

### Writing effective prompts

<AccordionGroup>
  <Accordion title="Structure your prompt clearly">
    Organize your prompt into clear sections:

    1. **Identity** — Who the agent is (name, role, company)
    2. **Objective** — The goal of the conversation
    3. **Instructions** — Step-by-step conversation flow
    4. **Rules** — Guardrails and restrictions
    5. **Context** — Background information the agent needs

    ```
    You are Sarah, a logistics coordinator at Acme Freight.

    Your objective is to confirm shipment details with the carrier and collect
    the estimated pickup time.

    Instructions:
    1. Greet the carrier and confirm you're calling about load @trigger.load_id
    2. Verify the pickup address: @trigger.pickup_address
    3. Ask for their estimated arrival time
    4. Confirm the details and thank them

    Rules:
    - Never disclose rate or payment information
    - If the carrier asks about rate, say "I'll have our billing team follow up"
    - Keep the conversation professional and concise
    ```
  </Accordion>

  <Accordion title="Use variables for dynamic data">
    Reference data from trigger payloads, previous nodes, or environment variables using the `@` picker in the prompt editor.

    Common variable patterns:

    * `@trigger.customer_name` — Data from the workflow trigger
    * `@node_name.output_field` — Output from a previous workflow node
    * `@env.company_name` — Organization or workflow environment variable
    * `@contact_intelligence_context` — Past interaction history with the caller

    Variables are resolved at runtime, so the same prompt can handle different callers with personalized data.
  </Accordion>

  <Accordion title="Reference tools by name">
    Rather than typing a tool's runtime identifier into the prompt, type `/` in the prompt editor and pick the tool from the menu. It's grouped into **Built-in tools**, **Custom tools** (the tool nodes attached below this prompt), and **MCP tools**.

    The tool is inserted as a chip that resolves to the tool's runtime name at call time and follows renames automatically. If the tool is later switched off or deleted, the chip renders as disabled — so an instruction that points at a tool the agent doesn't have is visible before you publish.

    The `/` menu also inserts blocks: headings and lists, a saved [prompt component](../14-Assets/02-Components.md), and a [conditional prompt component](../14-Assets/02-Components.md#conditional-prompt-components) that swaps in a different component depending on the run's data. The editor toolbar has a button for each of these, plus one for inserting a variable (`@`).
  </Accordion>

  <Accordion title="Handle edge cases">
    Anticipate scenarios the agent might encounter and provide explicit instructions:

    * What to do if the caller is confused or asks to repeat
    * How to handle requests outside the agent's scope
    * When to escalate or transfer the call
    * How to end the conversation gracefully
    * What to do if the caller is hostile or uncooperative
  </Accordion>
</AccordionGroup>

### Prompt playground

The prompt editor includes a **Chat Playground** button that lets you test your prompt in an interactive chat interface before deploying. Use it to verify the agent's behavior, test edge cases, and refine the prompt.

### Metaprompter

The prompt editor also includes an AI assistant that helps you build and improve prompts. It can suggest structure, fill in sections, and refine language based on your workflow description.

## Tool nodes

Tool nodes define functions the agent can call during a conversation. When the agent decides a tool is relevant, it pauses the conversation, executes the tool, and resumes speaking with the results.

### Adding a tool

<Steps>
  <Step title="Open the voice agent">
    In the workflow editor, click on the voice agent node to expand it and see the prompt node inside.
  </Step>

  <Step title="Add a tool node">
    Click the **+** button below the prompt node and select **Tool**. The tool node is added as a child of the prompt, making it available to the agent during conversation.
  </Step>

  <Step title="Configure the tool">
    Set the tool's description, message behavior, parameters, and any child actions.
  </Step>
</Steps>

### Tool configuration

| Field           | Description                                                                                                                                                                                                          |
| --------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Description** | Tells the agent **when** to use this tool. Write a clear description of what the tool does and when it should be called. Example: "Use this tool when the caller asks to be transferred to a human agent." Required. |
| **Message**     | What the agent says (or does) when it decides to use the tool. Three options:                                                                                                                                        |

* **AI generated** — The agent decides what to say before calling the tool (e.g., "Let me look that up for you").
* **Fixed message** — A specific message is always played (e.g., "Please hold while I transfer you").
* **None** — The tool executes silently with no announcement.

| Field          | Description                                                                                                                                                                                                                                                                                                                                                                                                                     |
| -------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Parameters** | Input parameters passed to the tool. Each parameter has a name, description, and optional examples. By default the agent populates them from conversation context; a parameter can instead be pinned to a [fixed value](../04-Tools/02-Creating-Tools.md#fixed-parameter-values) that is hidden from the agent and always sent as configured.                                                                                              |
| **Hold music** | Audio played while the tool executes. Useful for tools that take time (API calls, database lookups). Choose a built-in track — including **Ring tones** (North American ringback) and **Ring tones (EU)** (the ETSI 425 Hz tone European callers expect) — or a hold-music track from your [Audio Library](../14-Assets/03-Telephony.md#uploading-hold-music). Can be a static selection or dynamic via [variables](../02-Workflows/07-Variables.md). |

### Tool execution flow

When a tool is called during a voice conversation:

1. The agent recognizes the need for a tool based on the conversation and tool description.
2. The agent extracts parameter values from the conversation context.
3. If configured, the agent speaks the tool message (or plays hold music).
4. The tool's child nodes execute — these can be any workflow nodes: webhooks, integrations, AI operations, conditions, etc.
5. The tool returns its output to the agent.
6. The agent incorporates the result into the conversation and continues.

### Common tool patterns

<CardGroup cols={2}>
  <Card title="Call transfer" icon="phone-arrow-right">
    Add a **Direct Transfer** action as a child of the tool node. The agent transfers the caller to another number or extension when triggered. Supports warm handoff, whisper transfer, and SIP header passing.
  </Card>

  <Card title="Data lookup" icon="magnifying-glass">
    Add a **Webhook** or integration action as a child. The agent queries an external API (CRM, TMS, database) and uses the response in the conversation.
  </Card>

  <Card title="Record extraction" icon="file-lines">
    Add an **AI Extract** node as a child. The agent extracts structured data from what the caller said and stores it for downstream workflow use.
  </Card>

  <Card title="Conditional routing" icon="code-branch">
    Add a **Condition** node as a child. The tool evaluates data and routes to different actions based on the result — different departments, different responses, etc.
  </Card>
</CardGroup>

### MCP tools

Tools can also come from [MCP (Model Context Protocol) servers](https://docs.happyrobot.ai/tools). MCP tools appear with a badge in the tool list and have a pre-defined structure (description and parameters). You can still customize the message and hold music for MCP tools.

## Call transfer

One of the most common tool use cases is transferring a call to a human agent or another phone number. HappyRobot supports several transfer modes via the **Direct Transfer** integration:

### Transfer types

| Type                 | Description                                                                                                                         |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **Direct transfer**  | Immediately transfer the call to the target number. The AI agent disconnects once the transfer is initiated.                        |
| **Warm handoff**     | The agent speaks to the human recipient first to provide context before connecting the caller. The recipient can accept or decline. |
| **Whisper transfer** | A message is whispered to the recipient before the caller is connected. The caller doesn't hear the whisper.                        |

### Transfer configuration

| Field                                | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                  |
| ------------------------------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Number**                           | Phone number to transfer to, in E.164 format (for example `+12223334444`). Supports [variables](../02-Workflows/07-Variables.md). **Warm handoffs only accept a phone number** — a SIP URI fails at transfer time, and the editor warns you when the field looks like one. Use **To extension** under **Advanced Telephony** to reach an extension. Direct and whisper transfers still take a SIP URL, and one is required when User-to-User Information is configured. |
| **Extension**                        | Extension to dial after connecting. Only shown for **Warm handoff** transfers — direct and whisper transfers do not support an extension.                                                                                                                                                                                                                                                                                                                    |
| **Fallback number**                  | Backup number if the primary transfer fails.                                                                                                                                                                                                                                                                                                                                                                                                                 |
| **Transfer timeout**                 | How long to wait for the transfer to be answered before falling back.                                                                                                                                                                                                                                                                                                                                                                                        |
| **Connect immediately (no message)** | Warm handoff only. Connects the caller as soon as the recipient answers — no handoff message, no intro audio, and no press-1/press-9 handshake. Use it when you want direct-transfer behavior but still need to dial an extension. While it's on, the handoff message, intro audio, voice speed, and spoken-digit fields are hidden.                                                                                                                         |
| **Warm handoff message**             | What the agent tells the recipient before connecting the caller.                                                                                                                                                                                                                                                                                                                                                                                             |
| **Whisper message**                  | Message whispered to the recipient before the call connects. Limited to **1,024 characters** — the message rides in a SIP header and anything past that is truncated at transfer time. Variables count toward the limit once they expand, so the editor warns on the literal text you typed and the runtime enforces the real length.                                                                                                                        |
| **Recording**                        | Warm handoff and whisper transfer only. What is captured once the human is on the line: **Audio + Transcription** (the default, and the most useful for self-improving agents), **Audio** only, **Transcription** only, or **Off**. Nodes created before this setting existed behave as **Audio** until you re-select the transfer type.                                                                                                                     |
| **SIP headers / UUI**                | Pass custom User-to-User Information (UUI) via SIP headers during the transfer. Send the payload as JSON or plain text, encoded as hex, pre-encoded hex, ASCII, or Base64, with an option to omit the trailing `;purpose=app` parameter. See [Encoding options](03-Outbound-Calls.md#encoding-options).                                                                                                                                              |
| **Preserve UUI parameters**          | Keeps UUI parameters such as `;encoding=hex` literal in the transfer's Refer-To URI instead of percent-encoding them. Turn this on when the receiving system reports the UUI header arriving with `%3B`/`%3D` in place of `;`/`=`. Off by default.                                                                                                                                                                                                           |

<Note>
  A call streamed in from Genesys Cloud is transferred differently: there's no SIP leg for HappyRobot to redirect, so the agent hands the call back to the Architect flow and the flow routes it. Use the **Genesys transfer** node instead of Direct Transfer. See [Handing the call back to Architect](../15-Integrations/04-Communication/05-Genesys-Audio-Connector.md#handing-the-call-back-to-architect).
</Note>

#### Whisper message length limit

The whisper message rides in a SIP header, so it is truncated to **1,024 characters** at transfer time. The editor shows a warning as soon as the text you've typed passes that limit, along with the current character count.

[Variables](../02-Workflows/07-Variables.md) count toward the limit once they expand at runtime, so a message that looks short in the editor can still be cut. Keep whispers to the few facts the recipient needs — a reference number, the caller's name, the reason for the transfer.

## Real-time classifiers

Real-time classifiers analyze the conversation as it happens, categorizing each caller turn into predefined classes. Use them to track sentiment, detect intent, or flag specific topics during the call.

### Sentiment classifier

Enable the built-in sentiment classifier to automatically track caller sentiment (positive, negative, neutral) throughout the conversation. Results are available as node outputs for downstream workflow logic.

### Custom classifiers

Define your own classifiers with custom categories:

| Field       | Description                                                                                                                   |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Name**    | Identifier for the classifier (e.g., "Intent", "Urgency", "Topic").                                                           |
| **Prompt**  | Instructions for how to classify the conversation. Example: "Classify the caller's urgency based on their tone and language." |
| **Classes** | The categories to classify into. Example: "Low", "Medium", "High", "Critical".                                                |

Classifiers run after each caller turn and update in real time. Use classifier outputs in downstream conditions to route the workflow based on conversation dynamics.

## Contact intelligence

When contact intelligence is enabled, the agent has access to the caller's history — past interactions, extracted attributes, and persistent memories. This allows the agent to personalize the conversation.

| Field                            | Default | Description                                                                                                                                               |
| -------------------------------- | ------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enable memory**                | `false` | Activate contact intelligence for this agent.                                                                                                             |
| **Interaction limit**            | —       | Number of past interactions to include in context (0–10). Higher values provide more history but increase prompt length.                                  |
| **Disable auto contact context** | `false` | By default, contact context is automatically appended to the prompt. Enable this to place it manually using the `@contact_intelligence_context` variable. |

<Tip>
  Place `@contact_intelligence_context` strategically in your prompt when using manual placement. Put it near the top if context should heavily influence the agent's behavior, or near the bottom if it should be supplementary.
</Tip>

## Next steps

<CardGroup cols={3}>
  <Card title="STT, TTS, and LLM" icon="sliders" href="05-STT-TTS-and-LLM-Configuration.md">
    Configure speech, voice, and model settings.
  </Card>

  <Card title="Variables" icon="brackets-curly" href="../02-Workflows/07-Variables.md">
    Learn about template variables and data flow.
  </Card>

  <Card title="Core nodes" icon="shapes" href="../03-Core-Nodes/01-Core-Nodes-Overview.md">
    Explore built-in nodes you can use as tool children.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/voice-agents/prompts-and-tools
