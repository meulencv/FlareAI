---
title: "Node Types"
description: "Understanding the different node types available in workflows"
---

# Node Types

> Understanding the different node types available in workflows

Workflows are built from nodes, where each node represents a single step in the automation. There are six primary categories — action, prompt, tool, condition, loop, and module change — plus a set of built-in core nodes for common operations.

## Action nodes

Action nodes execute integration events — they're how your workflow connects to external systems. Send an email, create a record in your TMS, query a database, or post a message to Slack.

**When to use:** Connecting to external systems, performing operations, reading or writing data.

**Key configuration:**

* **Integration** — Which service to connect to (Gmail, Slack, Snowflake, etc.)
* **Event** — The specific operation to perform (Send Email, Query Table, Post Message)
* **Parameters** — Input values for the operation, which can include variables from previous nodes
* **Retry logic** — Optional custom retry settings (attempts, delay, backoff multiplier)
* **Failure handling** — Optional setting to continue workflow execution when the node fails (see below)

See [Integrations](../15-Integrations/01-Integrations-Overview.md) for the full list of available integrations and their events.

### Failure handling

Action nodes have a **Failure handling** section in the configuration sidebar. Expand it to find the **Continue on failure** toggle. By default, a node failure stops the run and marks it as failed.

| Setting       | Behavior                                                                                               |
| ------------- | ------------------------------------------------------------------------------------------------------ |
| Off (default) | If the node fails, the workflow stops and the run is marked as failed.                                 |
| On            | If the node fails, the workflow continues to the next node. The node's output variables will be empty. |

When continue on failure is enabled:

* The node's output will be empty if the call failed
* Subsequent nodes can check whether the node succeeded using the node's output variables
* The run is not marked as failed due to this node alone

Use this when an integration call is non-critical and you want the workflow to complete regardless (for example, a logging or notification step that should not block the main flow).

<Note>
  Continue on failure is available for external integration nodes (email, Slack, Google Sheets, etc.). It is not available for AI agents, webhooks, code nodes, conditionals, loops, or built-in nodes.
</Note>

## Prompt nodes

Prompt nodes run AI-powered conversations. They're the core of HappyRobot's agent capabilities — handling voice calls, text chats, and other interactive sessions with customers.

**When to use:** Customer-facing interactions, extracting information through conversation, handling complex queries that need AI reasoning.

**Key configuration:**

* **Agent type** — Voice agent (phone calls) or text agent (SMS, WhatsApp, email, chatbot)
* **LLM model** — The language model powering the conversation
* **System prompt** — Instructions that define the agent's behavior and personality
* **Initial message** — The first message the agent sends (for outbound interactions)
* **Voice settings** — For voice agents: STT provider, TTS voice, language
* **Tool access** — Which tool nodes the agent can call during the conversation

### Agent types

Add an agent from the **Agents** category of the node picker. Three kinds are available:

* **Voice agents** handle inbound and outbound phone calls with real-time speech-to-text, language model reasoning, and text-to-speech. See [Voice agents](../05-Voice-Agents/01-Voice-Agents-Overview.md).
* **Text agents** handle written conversations over SMS, WhatsApp, email, Teams, Slack, and embedded chatbot. See [Text agents](../06-Text-Agents/01-Text-Agents-Overview.md).
* **Reasoning agents** take an input and decide how to proceed, using tools to get there. They aren't tied to a channel — there's no phone number or inbox on the other end, so nobody is being messaged and there is no recording. Use one when you want an agent's judgment and tool use in the middle of a workflow, rather than a conversation with a person. Don't use one to pull structured data out of text or to bucket it — that's what [AI Extract](../03-Core-Nodes/02-AI-Extract.md) and [AI Classify](../03-Core-Nodes/03-AI-Classify.md) are for.

All three are configured through the same prompt node interface — select the agent type, set the system prompt, and choose which tools the agent can access.

#### Reasoning agent settings

A reasoning agent takes a required **Agent name**, then splits its settings across two tabs:

| Tab              | Settings                                                                                                                                                                                                                                                                                   |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Behavior**     | **Idle session timeout** — how long the agent waits with no response before the session ends (defaults to 2 minutes). **Reminders** — follow-up nudges before that timeout, with the same uniform/custom intervals and message options as a [text agent](../06-Text-Agents/01-Text-Agents-Overview.md#reminders). |
| **Intelligence** | **Agent signals** — wake the agent when [signals](06-Signals.md) are published to its topics, subscribe to custom topics, and choose whether a signal starts a response.                                                                                                              |

Its prompt node's **Built-in** tab offers **End conversation**, **Escalate to human**, and **Read media**, all off by default. Channel-specific built-ins — the email actions, the WhatsApp tools, and [skip turn](../04-Tools/04-Built-in-Tools.md#text-agent-built-in-tools) — need a channel, so they don't apply. The idle timeout message and [contact memory](../06-Text-Agents/01-Text-Agents-Overview.md#contact-intelligence-inbound-only) are likewise unavailable, since both assume someone to send to and a contact to remember.

## Tool nodes

Tool nodes define functions that prompt nodes can call during conversations. When an AI agent needs to look up data, run a calculation, or query a system mid-conversation, it invokes a tool node.

**When to use:** Giving AI agents access to data lookup, calculations, system queries, or any operation they should perform during a conversation.

**Key configuration:**

* **Function name** — The name the agent uses to call the tool
* **Description** — What the tool does (the agent uses this to decide when to call it)
* **Parameters** — Input schema defining what data the agent provides when calling the tool
* **Return schema** — The structure of the data returned to the agent

<Info>
  Tool nodes are children of prompt nodes. They appear nested under the prompt node in the workflow editor and are only available to the agent running in that specific prompt node.
</Info>

See [Tools](../04-Tools/01-Tools-Overview.md) for more on creating and configuring tools.

## Condition nodes

Condition nodes branch the workflow into different paths based on data. They evaluate one or more conditions against values from previous nodes and route execution accordingly.

**When to use:** Routing based on intent classification, checking data values, handling different statuses, or implementing fallback logic.

**Key configuration:**

* **Conditions** — One or more rules, each with a field, operator, and value
* **Logic** — Conditions support AND groups (all must match) nested within OR groups (any group matches)
* **Fallback path** — A default branch taken when no conditions match

### Available operators

**Text operators:**

| Operator            | Description                     |
| ------------------- | ------------------------------- |
| `text_equals`       | Exact text match                |
| `text_not_equals`   | Text does not match             |
| `text_contains`     | Text contains substring         |
| `text_not_contains` | Text does not contain substring |

**Number operators:**

| Operator                          | Description              |
| --------------------------------- | ------------------------ |
| `number_equals`                   | Numeric equality         |
| `number_not_equals`               | Numeric inequality       |
| `number_greater_than`             | Greater than             |
| `number_greater_than_or_equal_to` | Greater than or equal to |
| `number_less_than`                | Less than                |
| `number_less_than_or_equal_to`    | Less than or equal to    |

**Date operators:**

| Operator        | Description          |
| --------------- | -------------------- |
| `date_before`   | Date is before value |
| `date_after`    | Date is after value  |
| `date_same_day` | Date is the same day |

**Boolean and empty operators:**

| Operator        | Description            |
| --------------- | ---------------------- |
| `boolean_true`  | Value is true          |
| `boolean_false` | Value is false         |
| `is_empty`      | Field is empty or null |

See [Conditionals](../03-Core-Nodes/09-Conditionals.md) for advanced branching patterns.

## Loop nodes

Loop nodes repeat a sequence of steps — either iterating over an array of items or running a fixed number of times. The loop body can contain any combination of other node types.

**When to use:** Processing a list of records, retrying an operation multiple times, or batch-processing data from a previous node.

**Key configuration:**

* **Iterate over** — A variable containing an array to loop through
* **Iterate for** — Alternatively, a fixed number of iterations
* **Loop variable** — The name used to reference the current item inside the loop
* **Parallel execution** — Optionally run iterations in parallel instead of sequentially

<Info>
  Loop nodes appear as a container in the workflow editor. Add nodes inside the loop body — they execute once per iteration. A loop end marker closes the loop automatically. Add a **Loop Break** node inside the body to exit the loop early once a condition is met. See [Loops](../03-Core-Nodes/10-Loops.md).
</Info>

## Module change nodes

Module change nodes switch the workflow context to a different module, allowing you to reuse shared workflow logic across multiple workflows. They pass data into the target module and receive output back.

**When to use:** Reusing common workflow patterns, organizing complex automations into modular components, or sharing logic across teams.

**Key configuration:**

* **Target module** — The module to switch to
* **Input mapping** — How to map current workflow variables to the module's expected inputs

## Core nodes

HappyRobot provides built-in utility nodes for common operations. These are ready to use without connecting an external integration.

<CardGroup cols={2}>
  <Card title="Webhook" icon="globe" href="../03-Core-Nodes/06-Webhook.md">
    Send HTTP requests to external APIs.
  </Card>

  <Card title="Schedule" icon="clock" href="../03-Core-Nodes/07-Schedule.md">
    Delay execution or wait for a specific time.
  </Card>

  <Card title="AI Extract" icon="wand-magic-sparkles" href="../03-Core-Nodes/02-AI-Extract.md">
    Extract structured data from unstructured text using AI.
  </Card>

  <Card title="AI Classify" icon="tags" href="../03-Core-Nodes/03-AI-Classify.md">
    Classify text into predefined categories using AI.
  </Card>

  <Card title="AI Generate" icon="sparkles" href="../03-Core-Nodes/04-AI-Generate.md">
    Generate text content using AI.
  </Card>

  <Card title="Custom Code" icon="code" href="../03-Core-Nodes/05-Custom-Code.md">
    Run custom JavaScript or Python code.
  </Card>

  <Card title="File Operations" icon="file" href="../03-Core-Nodes/08-File-Operations.md">
    Read, write, and transform files.
  </Card>

  <Card title="Conditionals" icon="code-branch" href="../03-Core-Nodes/09-Conditionals.md">
    Advanced branching and routing logic.
  </Card>
</CardGroup>

<Tip>
  Nodes can be reordered by dragging, copied with right-click, and collapsed to simplify the view in the visual editor.
</Tip>

---

Fuente original: https://docs.happyrobot.ai/workflows/node-types
