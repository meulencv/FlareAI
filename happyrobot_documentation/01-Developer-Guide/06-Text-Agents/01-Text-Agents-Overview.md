---
title: "Text Agents Overview"
description: "Introduction to text-based AI agents"
---

# Text Agents Overview

> Introduction to text-based AI agents

Text agents handle asynchronous, message-based conversations powered by AI. Unlike [voice agents](../05-Voice-Agents/01-Voice-Agents-Overview.md) — which operate in real time over phone calls — text agents exchange messages over SMS, WhatsApp, email, and embedded chatbots. Each message goes through a language model that reads the conversation history, generates a response, and sends it back through the same channel. You configure them as nodes inside a [workflow](../02-Workflows/01-Workflows-Overview.md), so every conversation benefits from the full automation engine: data extraction, integration actions, conditional logic, and more.

## What you can build

<CardGroup cols={2}>
  <Card title="Inbound message handling" icon="message-arrow-down">
    Receive incoming messages on SMS, WhatsApp, email, or a website chatbot. The AI agent responds automatically — answering questions, collecting data, and routing conversations without human intervention.
  </Card>

  <Card title="Outbound campaigns" icon="message-arrow-up">
    Trigger outbound messages via API or workflow. The agent sends the first message over SMS, WhatsApp, or email, then manages the full back-and-forth conversation asynchronously.
  </Card>

  <Card title="Email automation" icon="envelope">
    Connect Gmail or Outlook mailboxes and let AI agents handle incoming emails — reading thread context, filtering senders, and replying with full conversation awareness.
  </Card>

  <Card title="Website chatbot" icon="browser">
    Embed a chat widget on your website. Visitors start conversations instantly with no credentials or phone numbers required — just a script tag and a list of allowed domains.
  </Card>
</CardGroup>

## How a text conversation works

<Steps>
  <Step title="Message arrives">
    An inbound message is received (SMS, WhatsApp, email, or chatbot) or an outbound workflow trigger sends the first message to a recipient.
  </Step>

  <Step title="Session created or resumed">
    HappyRobot creates a new conversation session or resumes an existing one if the contact has an active thread. Session state persists across messages.
  </Step>

  <Step title="LLM generates a response">
    The message and full conversation history are sent to the language model along with the system prompt and any tool results. The model decides what to say — or which tool to call.
  </Step>

  <Step title="Response delivered">
    The model's response is sent back through the same channel — as an SMS, WhatsApp message, email reply, or chatbot bubble. No speech synthesis is needed.
  </Step>

  <Step title="Conversation continues or ends">
    The session stays open for follow-up messages until an idle timeout expires, the agent ends the conversation, or escalation hands off to a human. When the session ends, the workflow proceeds to downstream nodes.
  </Step>
</Steps>

## Text agent types

HappyRobot offers two text agent types that map to message direction:

| Type     | Use case                                              | Trigger                                                            |
| -------- | ----------------------------------------------------- | ------------------------------------------------------------------ |
| Inbound  | Respond to incoming messages on any supported channel | Message arrives on a configured number, mailbox, or chatbot widget |
| Outbound | Send the first message and manage the conversation    | API trigger, webhook, or workflow action                           |

## Supported channels

<CardGroup cols={2}>
  <Card title="SMS" icon="comment-sms" href="02-SMS.md">
    Two-way SMS conversations via Twilio. Use an existing HappyRobot toll-free number or bring your own Twilio account.
  </Card>

  <Card title="WhatsApp" icon="whatsapp" href="03-WhatsApp.md">
    WhatsApp Business API conversations via Meta. Requires approved message templates for outbound and timeout messages.
  </Card>

  <Card title="Email" icon="envelope" href="04-Email.md">
    Gmail and Outlook email conversations with thread context, sender filtering, and multiple sending strategies.
  </Card>

  <Card title="Chatbot" icon="browser" href="05-Chatbot.md">
    Embedded website chat widget. Inbound only — no external credentials needed, just register your domains.
  </Card>

  <Card title="Microsoft Teams" icon="users" href="06-Microsoft-Teams.md">
    Teams chats and channel messages. Bot-based architecture with no per-channel subscription setup.
  </Card>

  <Card title="Slack" icon="slack" href="07-Slack.md">
    Slack channels, group DMs, and direct messages. Threaded replies in channels with full context awareness.
  </Card>
</CardGroup>

## Inbound trigger output schema

The **Inbound Text** trigger's output schema is channel-specific — the fields it exposes to downstream nodes depend on the channel of the Inbound Text Agent connected to it. For email it also depends on the email provider, since Gmail and Outlook carry attachment processing, threading, and artifact fields that Postmark and SendGrid don't.

Because of that, generate the trigger's output schema *after* the agent's channel is set:

* Until a channel is resolved, the trigger's testing panel notes that it is showing **common fields only**. Channel-specific fields (`to_email`, `from_email`, thread data, artifacts, and so on) appear once a connected agent has a channel selected and you regenerate the schema.
* If you later switch the connected agent to a different channel — or to a different email provider — the trigger node shows a warning glyph reading *Connected agent changed to …*. Regenerate the output schema so the `@` [variable picker](../02-Workflows/07-Variables.md) reflects the fields the trigger will actually deliver.

## Key capabilities

<CardGroup cols={2}>
  <Card title="Prompts and tools" icon="message">
    Text agents use the same prompt and tool system as voice agents. Write a system prompt, attach tools for lookups and actions, and the LLM handles the rest. See [Prompts and tools](../05-Voice-Agents/06-Prompts-and-Tools.md).
  </Card>

  <Card title="Timeout and reminders" icon="clock">
    Configure an idle timeout to end stale conversations, and an optional maximum session duration to cap them overall. Send reminders before the timeout expires — with AI-generated, fixed, or no message — to re-engage the contact.
  </Card>

  <Card title="Escalation" icon="user-headset">
    Hand conversations off to humans when the agent can't resolve an issue. Escalation modes include HappyRobot platform, CXone, and email-in-thread (with CC, forward, and handoff actions).
  </Card>

  <Card title="End conversation" icon="circle-check">
    Give the agent a tool to end the conversation when the interaction is complete. Configure whether the agent sends a closing message (AI-generated, fixed, or none).
  </Card>

  <Card title="Contact intelligence" icon="address-book">
    Automatically track interaction history per contact. Agents access past conversations and extracted data to personalize every message. Available on inbound agents.
  </Card>

  <Card title="Anthropic models" icon="brain">
    Text agents use Anthropic Claude models. Model selection is configured in the prompt node — see [Prompts and tools](../05-Voice-Agents/06-Prompts-and-Tools.md) for details.
  </Card>
</CardGroup>

## Common agent settings

All text agent channels share a set of configurable behaviors for timeouts, reminders, escalation, and conversation endings. These are configured once per agent and apply regardless of the channel.

They are split across two nodes:

| Where                                                   | Settings                                                                                                                                                           |
| ------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Agent node** — **Behavior** and **Intelligence** tabs | Channel and credentials, timeout behavior, reminders, delivery error handling, contact intelligence.                                                               |
| **Prompt node** — **Built-in** tab                      | The agent's [built-in tools](../04-Tools/04-Built-in-Tools.md#the-built-in-tab): escalation, end conversation, media processing, interactive messages, and the email actions. |

Anything the model can decide to *call* lives with the prompt that instructs it, in the **Built-in** tab. Expand a row there to configure that tool. A prompt node with active built-ins shows a **built-in** badge on the canvas that lists them and links straight into the matching row.

### Timeout behavior

Text conversations don't have a natural "hang up" moment like phone calls. Instead, sessions end when the contact stops responding. The idle timeout controls how long the agent waits before closing the conversation.

| Setting                      | Description                                                                                                                                                                                                                                                                                   |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Idle timeout minutes**     | Minutes of inactivity before the conversation ends. Minimum 1 minute. Supports [variables](../02-Workflows/07-Variables.md) — set the value dynamically from trigger data or a previous node. When the timeout expires, the agent sends the idle timeout message (if configured) and the session closes. |
| **Idle timeout message**     | The message sent to the contact when the timeout expires. Supports [variables](../02-Workflows/07-Variables.md). Leave empty to close the session silently.                                                                                                                                              |
| **Maximum session duration** | An overall wall-clock cap on the conversation, in minutes. Leave empty for no maximum. Supports [variables](../02-Workflows/07-Variables.md).                                                                                                                                                            |

#### Maximum session duration

The idle timeout only measures silence, so a conversation that keeps getting replies can run indefinitely. **Maximum session duration** puts a hard ceiling on it.

* Accepts a whole number of minutes between **1** and **525600** (one year) when set statically.
* Timing starts when the session opens. For outbound agents, it starts after the initial message is sent.
* Incoming messages, reminders, and tool calls do **not** reset it.
* When the cap is reached, the agent closes the conversation silently — no idle timeout message is sent — and the workflow continues to downstream nodes.

<Note>
  The numeric timeout and reminder fields (idle timeout, maximum session duration, reminder count, and reminder intervals) accept [variables](../02-Workflows/07-Variables.md) in addition to static numbers, so you can drive them from trigger data or upstream node output. When a static value is used, the minimum and range limits below apply; dynamic values are resolved at runtime.
</Note>

### Reminders

Reminders re-engage contacts who haven't responded, before the idle timeout expires. When enabled, the agent sends follow-up messages at configured intervals.

| Setting          | Description                                                                                                                                                                                                          |
| ---------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enabled**      | Turn reminders on or off.                                                                                                                                                                                            |
| **Count**        | Number of reminders to send (1–12 when set statically). Supports [variables](../02-Workflows/07-Variables.md).                                                                                                                  |
| **Mode**         | **Uniform** — all reminders use the same interval. **Custom** — set a different interval for each reminder.                                                                                                          |
| **Intervals**    | Time in seconds between each reminder. Minimum 10 seconds per interval. Supports [variables](../02-Workflows/07-Variables.md). In uniform mode, one interval applies to all. In custom mode, you set one interval per reminder. |
| **Message type** | **AI** — the LLM generates the reminder using a description you provide. **Fixed** — a specific message you write, with variable support. **None** — reminder fires (resets timeout tracking) but sends no message.  |

<Tip>
  For WhatsApp, reminders sent outside the 24-hour conversation window must use an approved message template. See the [WhatsApp page](03-WhatsApp.md) for details.
</Tip>

### Escalation

Escalation gives the agent a tool to hand conversations to a human when it can't resolve an issue. The agent decides when to escalate based on the description you provide.

Turn it on with the **Escalate to human** switch in the prompt node's **Built-in** tab, then expand the row to configure it. The configuration is split in two: the agent-facing behavior (when to escalate and what to say) and **Handoff setup** (where the conversation goes and how to connect to it).

| Setting          | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                        |
| ---------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Description**  | Instructions telling the agent when to escalate (e.g., "Escalate when the customer asks for a manager or the issue can't be resolved"). Required.                                                                                                                                                                                                                                                                                                                  |
| **Message type** | **AI** — the agent generates an escalation message using a description. **Fixed** — a specific message you write. **None** — escalation happens silently.                                                                                                                                                                                                                                                                                                          |
| **Mode**         | Under **Handoff setup**. **HappyRobot Platform** — escalates within HappyRobot. **CXone** — escalates to a NICE CXone contact center (requires credential and channel ID). **Richpanel** — escalates to a Richpanel helpdesk queue (requires credential). **Generic Webhook** — escalates to any HTTP endpoint with configurable outbound events and an inbound URL for replies. **Email in thread** — escalates via email actions within the conversation thread. |

When using **Generic Webhook** mode, the agent escalates by calling your endpoint over HTTP. The setup is grouped by direction, and each group carries a status badge so you can tell at a glance whether it is ready:

| Group               | Direction                        | Description                                                                                                                                                                                           |
| ------------------- | -------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inbound API**     | Your handoff system → HappyRobot | Lets your handoff system reply, resume the agent, or close the conversation. Shows **Ready** once an inbound secret exists, **Setup required** until then.                                            |
| **Outbound events** | HappyRobot → your handoff system | Chooses which escalation events HappyRobot sends you. Shows **Disabled** when no event is enabled, **n enabled** when they're configured, or **n need setup** when an enabled event is missing a URL. |

| Field               | Description                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Inbound Secret**  | Bearer token your operator system uses to authenticate requests to both inbound endpoints below. Sent as `Authorization: Bearer <inbound secret>`. Generated for you when you switch to Generic Webhook mode. Required.                                                                                                                                                                                                                                                                                                                                                                                                                                                                                     |
| **Inbound APIs**    | Two copyable endpoints your operator or external system calls back into HappyRobot. **Inbound Reply** (`POST /generic-escalation/webhook`) sends a human reply into an escalated session. **Escalation Control** (`POST /generic-escalation/control`) ends an active escalation — see below. Request and response schemas are shown inline next to the endpoints.                                                                                                                                                                                                                                                                                                                                           |
| **Outbound events** | Three independently configurable webhooks, each collapsible with its own **Disabled** / **Setup required** / **Enabled** badge: **Escalation Start** (fires when the agent hands the conversation to a human escalation path), **User Message** (fires for each new user message while escalated), and **Escalation End** (fires when escalation closes and the conversation returns to normal handling). Each supports URL, headers, body (schema builder), content type (`application/json` or `application/x-www-form-urlencoded`), and authentication (None, API Key, Bearer, Basic). Escalation Start and User Message are enabled by default with a prefilled body; Escalation End is off by default. |

Variables available inside hook bodies include `session_id`, `event_type`, `reason`, `message_id`, `message_body`, `identity`, `channel`, and `history`. Only the variables that a given event actually carries are offered on that event — `message_id`, `message_body`, and `identity` on **User Message**, and `reason` on the start and end events.

The **Inbound APIs** section exposes two HappyRobot endpoints your operator or external escalation system can call back into. Both authenticate with the same **Inbound Secret**.

**Inbound Reply** — `POST /generic-escalation/webhook`

Use when a human operator wants to send a reply back into an escalated session. Body schema:

```json theme={null}
{
  "session_id": "uuid",
  "message_body": "string",
  "identity": "string",
  "metadata": {}
}
```

**Escalation Control** — `POST /generic-escalation/control`

Use to end an active escalation without sending a reply. Body schema:

```json theme={null}
{
  "session_id": "uuid",
  "action": "back_to_agent" | "close_session",
  "reason": "optional"
}
```

* `back_to_agent` — Returns control to the AI agent; the session continues with the LLM responding to subsequent messages.
* `close_session` — Ends the escalation and the underlying text session.

When using **Email in thread** mode, you can enable specific escalation actions:

| Action                                   | Description                                                                                                                                           |
| ---------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **CC + Reply with Conversation History** | Replies to the thread with a CC recipient and includes the full conversation history.                                                                 |
| **Forward Thread**                       | Forwards the entire email thread to specified recipients.                                                                                             |
| **End Conversation After Handoff**       | Ends the AI conversation after the handoff email is sent, instead of continuing in escalation mode. Requires at least one other action to be enabled. |

### End conversation

The end conversation tool lets the agent close the session when the interaction is complete — for example, after collecting all required data or answering the contact's question. Configure it in the **End conversation** row of the prompt node's **Built-in** tab.

| Setting          | Description                                                                                                                                                                               |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enabled**      | Turn the end conversation tool on or off.                                                                                                                                                 |
| **Description**  | Instructions telling the agent when to end the conversation (e.g., "End the conversation when all questions have been answered and the customer confirms they don't need anything else"). |
| **Message type** | **AI** — the agent generates a closing message using a description. **Fixed** — a specific farewell message you write. **None** — the session ends silently.                              |

### Skip turn

Some events don't need a reply — a status update the contact doesn't have to acknowledge, a signal that only matters as context. **Skip turn** gives the agent a way to say so explicitly instead of inventing a message. Turn it on in the **Skip turn** row at the bottom of the prompt node's **Built-in** tab; it's off by default and available on every channel-backed text agent.

When the agent skips a turn, nothing is sent, no configured tool or workflow action runs, and the event is marked as handled. The agent is not left waiting — the next message, signal, reminder, or tool result is handled under the agent's normal response settings. See [Skip turn](../04-Tools/04-Built-in-Tools.md#text-agent-built-in-tools) for the full behavior.

The same control is available in the **Behavior** settings of a **Reasoning Agent** node. Turn it off there when an orchestrating reasoning agent should stay open and wait for a [signal](../02-Workflows/06-Signals.md) instead of ending on its own.

### Delivery error handling

**End session on delivery error** — When enabled, the session ends immediately if the channel reports that a message failed to deliver. The error metadata is exposed as node outputs so downstream nodes can inspect and respond to the failure — for example, to log the error, notify a human, or retry through a different channel.

When disabled (the default), delivery errors are ignored and the session continues. This setting is available on outbound text agents for every channel except email — SMS, WhatsApp, chatbot, Microsoft Teams, and Slack.

### Contact intelligence (inbound only)

Contact intelligence gives inbound agents memory across conversations. When enabled, the agent can see who's messaging, what they've discussed before, and any attributes extracted from past interactions.

| Setting                          | Description                                                                                                                                                                            |
| -------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enable memory**                | Activates contact intelligence. The agent receives the contact's record and interaction history.                                                                                       |
| **Interaction limit**            | How many past interactions to include in context (0–10). More history means richer context but higher token usage. Start with 3–5.                                                     |
| **Disable auto contact context** | By default, contact context is appended to the end of the prompt. Enable this to manually place `@contact_intelligence_context` in your prompt for more control over where it appears. |

### Media processing

Text agents can process file attachments from contacts. Two processing capabilities are available with Standard, Advanced, and Frontier profiles:

| Capability                                               | Standard | Advanced | Frontier  |
| -------------------------------------------------------- | -------- | -------- | --------- |
| **Document processing** (image/document text extraction) | Gemini   | Reducto  | Anthropic |
| **Audio transcription**                                  | Whisper  | Soniox   | Soniox    |

Media processing is available for all text agent channels — configure it in the **Automatically process media** row of the prompt node's **Built-in** tab. Each capability is a single dropdown with four choices: **Disabled**, **Standard**, **Advanced**, or **Frontier**, each showing its credit estimate so you can weigh accuracy against cost. Pick the profile that fits your accuracy and cost requirements, and set the two capabilities independently. Advanced remains available for agents configured before Frontier was introduced.

**Frontier** is the highest-quality profile: for document processing it reads the file with a frontier vision model rather than a dedicated OCR engine, which helps most on messy scans, mixed layouts, and documents whose meaning depends on surrounding context.

**Language hints (Advanced and Frontier transcription)** — Supply one or more **Language hints** so the engine knows which languages to expect in the audio. Add hints from the searchable list (any combination of supported languages). Leave the field empty to let the engine auto-detect. Hints improve accuracy for non-English audio and for calls that mix languages.

Transcribed audio also appears inline on the run details panel: each audio artifact gets a **Transcription** accordion that lazily loads the transcript text when expanded.

#### Media processing limits

When either processing capability is enabled, expand **Advanced limits** to configure the shared per-turn processing budget:

| Setting                     | Default     | Allowed range  |
| --------------------------- | ----------- | -------------- |
| **Max files per turn**      | 25          | 1–25           |
| **Max size per file**       | 50 MB       | 1–50 MB        |
| **Max total size per turn** | 100 MB      | 1–100 MB       |
| **Processing timeout**      | 240 seconds | 10–480 seconds |
| **Max attempts**            | 2           | 1–5            |

The file-count and total-size limits are shared across document and audio processing in a turn. Attachments above a processing limit are still captured and shown; only extraction or transcription is skipped. **Max attempts** counts the initial attempt and retries when starting processing fails. The processing timeout cannot exceed the time remaining on a bounded parent workflow.

Use **Reset to Defaults** to put all five values back. The defaults are the platform maximums for files and sizes, so an agent configured before these controls existed behaves exactly as it did until you change them.

Email providers also have separate limits on capturing inbound files and sending outbound files. See [Email attachment limits](04-Email.md#attachment-limits-and-processing) for the provider matrix, supported types, and the exact data the agent receives for completed, skipped, limited, and failed files. See the [Chatbot page](05-Chatbot.md#media-processing) for browser-upload behavior.

**Reply with voice notes (WhatsApp only)** — WhatsApp agents can send their replies as voice notes. Switch on the separate **Send voice notes** row, set **Reply mode** to *Always send as voice note* or *Let the agent decide*, pick the **Languages** the notes are spoken in, and pick a text-to-speech voice. See [WhatsApp → Reply with voice notes](03-WhatsApp.md#reply-with-voice-notes).

**Send images and documents (WhatsApp only)** — WhatsApp agents can send an image or PDF to the contact. Switch on the **Send images and documents** row and configure when to send and what caption to use. See [WhatsApp → Sending images and documents](03-WhatsApp.md#sending-images-and-documents).

## Next steps

<CardGroup cols={2}>
  <Card title="SMS" icon="comment-sms" href="02-SMS.md">
    Set up two-way SMS conversations via Twilio.
  </Card>

  <Card title="WhatsApp" icon="whatsapp" href="03-WhatsApp.md">
    Deploy agents on WhatsApp Business.
  </Card>

  <Card title="Email" icon="envelope" href="04-Email.md">
    Connect Gmail or Outlook for email automation.
  </Card>

  <Card title="Chatbot" icon="browser" href="05-Chatbot.md">
    Embed a chat widget on your website.
  </Card>

  <Card title="Microsoft Teams" icon="users" href="06-Microsoft-Teams.md">
    Deploy agents in Teams chats and channels.
  </Card>

  <Card title="Slack" icon="slack" href="07-Slack.md">
    Deploy agents in Slack channels and DMs.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/text-agents/overview
