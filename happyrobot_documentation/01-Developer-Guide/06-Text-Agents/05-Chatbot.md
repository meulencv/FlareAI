---
title: "Chatbot"
description: "Embed a chatbot widget on your website"
---

# Chatbot

> Embed a chatbot widget on your website

Chatbot agents provide an embedded chat widget for your website. Unlike other text agent channels, chatbots are **inbound only** — visitors initiate conversations by clicking the widget. No external credentials or phone numbers are required. You register the domains where the widget should be active, embed a script tag, and the agent handles conversations directly through HappyRobot's infrastructure using Pusher for real-time message transport.

## Setting up a chatbot agent

<Steps>
  <Step title="Add an inbound trigger">
    Every chatbot workflow starts with an **Inbound Text** trigger node. Select this trigger in the workflow editor — it listens for incoming chatbot messages from your registered domains.
  </Step>

  <Step title="Add an inbound text agent node">
    Add an **Inbound Text Agent** action node and select **Chatbot** as the channel.
  </Step>

  <Step title="Register your domains">
    Add every domain where the chatbot widget will be embedded. The widget only loads on registered domains — requests from unregistered domains are rejected. Include all variations (e.g., `example.com`, `www.example.com`, `app.example.com`).
  </Step>

  <Step title="Configure the agent">
    Set the agent name (this is visible to visitors in the widget), write a prompt in the nested [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md), and configure timeout, reminder, and other settings. Optionally enable media processing for file uploads.
  </Step>

  <Step title="Publish and embed">
    Publish your workflow, then add the embed script to your website. See [Embedding the widget](#embedding-the-widget) for the script tag.
  </Step>
</Steps>

## Passing custom data to the chatbot (params)

Chatbot workflows can declare named **params** on the trigger node. Params let your website pass structured data into the workflow at the moment a visitor starts a conversation — for example, the current user's account ID, the page URL, or a selected product.

### Declaring params

1. Open the workflow editor and select the **Inbound Text** trigger node.
2. In the **Params** list, add one or more param names (for example, `user_id`, `page_url`).
3. A JSON schema is shown in the panel — copy it as a reference for your embed integration.

### Sending params from your website

Set `window.HappyRobotConfig` with a `payload` object before the widget initializes. The keys must match the param names declared on the trigger node:

```html theme={null}
<script>
  window.HappyRobotConfig = {
    payload: {
      user_id: "acct_123",
      page_url: window.location.href
    }
  };
</script>
<!-- HappyRobot embed script -->
<script src="..."></script>
```

When the visitor opens the widget, the payload is sent as part of the session start event. Params are available as workflow variables in downstream nodes.

<Info>
  If no params are declared on the trigger node, `window.HappyRobotConfig` is ignored. The payload must be a flat JSON object — nested objects are not supported as individual param values.
</Info>

### Testing params in the workflow editor

The chatbot preview dialog in the workflow editor shows a **Payload** textarea pre-filled with a JSON template based on your declared params. Edit the values to test different inputs before deploying.

***

## Configuration reference

### Agent name

The agent name is displayed to visitors in the chat widget header. Choose something that matches your brand — for example, "Support Assistant" or "Acme Help". This is required.

### Registered domains

A whitelist of domains where the chatbot widget is allowed to load. The widget checks the page's origin against this list and refuses to initialize on unregistered domains.

<Warning>
  You must list every domain variation separately. `example.com` and `www.example.com` are treated as different domains. If you miss a variation, the widget won't load on that domain.
</Warning>

### Prompt and tools

The system prompt and tools are configured in the [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md) nested inside the text agent node. Text agents use Anthropic Claude models. The prompt defines the agent's personality, instructions, and conversation flow. Attach [tools](../04-Tools/01-Tools-Overview.md) for any actions the agent needs — lookups, API calls, data extraction, etc.

### Media processing

When a visitor uploads an image, document, or audio file, the agent can process it using document processing or transcription. Video transcription is not currently supported. Media processing can also be configured for other text channels — see [media processing](01-Text-Agents-Overview.md#media-processing).

| Capability              | Standard tier                                          | Advanced tier                                                          | Frontier tier                                                                                                |
| ----------------------- | ------------------------------------------------------ | ---------------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| **Document processing** | Gemini — good for most images and documents            | Reducto — higher accuracy for complex layouts, tables, and handwriting | Claude Opus — reads the document with a frontier vision model, for messy scans and context-dependent content |
| **Audio transcription** | Whisper — reliable general-purpose audio transcription | Soniox — better accuracy for noisy audio and specialized domains       | Soniox — the same engine as the advanced tier                                                                |

Each capability is enabled independently. When disabled, the agent acknowledges the upload but can't extract content from it. The [shared processing limits](01-Text-Agents-Overview.md#media-processing-limits) apply to chatbot uploads.

<Tip>
  Start with the standard tier for both OCR and transcription. Move up to advanced or frontier only if you see accuracy issues with your specific document types or audio quality — each tier costs more credits per file.
</Tip>

Per-turn limits on file count, file size, timeout, and retries are set in the same panel under **Advanced limits**. See [media processing → Advanced limits](01-Text-Agents-Overview.md#media-processing-limits).

### Agent settings

Timeout, reminders, escalation, and end conversation settings are shared across all text agent channels. See [common agent settings](01-Text-Agents-Overview.md#common-agent-settings) for the full reference.

### Environments

Chatbot agents are configured per [environment](../02-Workflows/09-Environments.md) (production, staging, development), the same as other text agent channels. Use staging or development to test prompt and tool changes against your registered domains before promoting to production.

## Chatbot message flow

1. A visitor loads a page on a registered domain. The embed script initializes the chat widget.
2. The visitor clicks the widget and types a message.
3. The message is sent to HappyRobot via the Pusher real-time transport.
4. HappyRobot matches the chatbot to a workflow trigger and starts a new run (or resumes an existing session if the visitor has an active conversation).
5. A text session is created and the message is added to the conversation history.
6. The LLM generates a response using the prompt, conversation history, and any tool results.
7. The response is delivered back to the widget via Pusher in real time.
8. The session stays open for follow-up messages. If the visitor uploads a file and media processing is enabled, the file is processed (OCR or transcription) and the extracted content is provided to the LLM as context.

## Delivering a message into a session

The **Deliver Text Session Message** action node pushes a templated message directly into a running text agent session — for example, the chatbot widget — without invoking the LLM. The message is delivered verbatim, so use it when you want deterministic, scripted output (a status update, a payload card, a handoff notice) rather than an AI-generated reply.

<Steps>
  <Step title="Add a Deliver Text Session Message node">
    In the workflow editor, click **+** and select **Deliver Text Session Message** under the Text category.
  </Step>

  <Step title="Reference the session">
    Set **Session ID** to the session you want to deliver into — typically the agent node's session id, e.g. `@Agent.session_id`. Variables are supported with `@`.
  </Step>

  <Step title="Write the message">
    Fill in **Message** with the text to deliver. Both fields are required and support [variables](../02-Workflows/07-Variables.md).
  </Step>
</Steps>

<Note>
  Delivery is deterministic — the message bypasses the model and is sent exactly as written. Because it targets an existing session, the session must still be active when the node runs.
</Note>

## Embedding the widget

To add the chatbot to your website, include the HappyRobot chatbot script tag on any page where you want the widget to appear. The script tag is available in the workflow editor after you publish — copy it from the chatbot node's configuration panel.

The script loads asynchronously and renders a floating chat button in the corner of the page. Clicking it opens the conversation interface. The widget handles:

* Message sending and receiving via Pusher
* File uploads (when media processing is enabled)
* Session persistence across page navigations (within the same domain)
* Responsive layout for mobile and desktop

<Info>
  The widget only initializes if the page's domain matches one of your registered domains. If you add the script to an unregistered domain, it silently fails without rendering.
</Info>

## Differences from other channels

| Feature                         | Chatbot                                            | SMS / WhatsApp / Email                      |
| ------------------------------- | -------------------------------------------------- | ------------------------------------------- |
| **Direction**                   | Inbound only                                       | Inbound and outbound                        |
| **Credentials**                 | None required                                      | Twilio, Meta, or email provider credentials |
| **Media processing**            | OCR and transcription for uploads                  | Available (configure in agent settings)     |
| **Transport**                   | Pusher (real-time WebSocket)                       | Carrier/provider webhooks                   |
| **Domain restriction**          | Required — widget only loads on registered domains | Not applicable                              |
| **Environment-specific config** | Required for staging/development                   | Required for staging/development            |

## Next steps

<CardGroup cols={3}>
  <Card title="Overview" icon="book-open" href="01-Text-Agents-Overview.md">
    Review common settings shared across all channels.
  </Card>

  <Card title="Prompts and tools" icon="message" href="../05-Voice-Agents/06-Prompts-and-Tools.md">
    Write effective prompts and attach tools.
  </Card>

  <Card title="Tools" icon="wrench" href="../04-Tools/01-Tools-Overview.md">
    Build custom tools for your agent.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/text-agents/chatbot
