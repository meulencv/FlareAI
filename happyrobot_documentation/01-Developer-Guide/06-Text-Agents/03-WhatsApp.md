---
title: "WhatsApp"
description: "Deploy text agents on WhatsApp"
---

# WhatsApp

> Deploy text agents on WhatsApp

WhatsApp text agents handle conversations through the WhatsApp Business API via Meta. WhatsApp has specific requirements around message templates and conversation windows that differ from other channels — outbound messages and messages sent outside the 24-hour window must use pre-approved templates. HappyRobot handles the template routing and window management automatically, but you need to configure your templates and WhatsApp Business credentials.

## Setting up an inbound WhatsApp agent

<Steps>
  <Step title="Add an inbound trigger">
    Every inbound WhatsApp workflow starts with an **Inbound Text** trigger node. Select this trigger in the workflow editor — it listens for incoming WhatsApp messages on your configured business phone numbers.
  </Step>

  <Step title="Add an inbound text agent node">
    Add an **Inbound Text Agent** action node and select **WhatsApp** as the channel.
  </Step>

  <Step title="Connect one or more WhatsApp phone numbers">
    Each inbound WhatsApp agent can listen on multiple business numbers. For each row, select the WhatsApp credential, business, business account, and phone number. Click **Add phone number** to register additional numbers on the same agent. These dropdowns are populated from your Meta Business Manager account — set up your WhatsApp integration in [Credentials](../15-Integrations/02-Credentials.md) first. See [Multiple inbound phone numbers](#multiple-inbound-phone-numbers) for details.
  </Step>

  <Step title="Configure templates (optional)">
    For inbound agents, templates are optional but recommended for timeout and reminder messages. If the contact's last message was more than 24 hours ago, regular text replies won't be delivered — you'll need an approved template. Configure timeout and reminder templates per phone number if you use those features.
  </Step>

  <Step title="Configure and publish">
    Set the agent name, prompt, and conversation settings. Publish and send a WhatsApp message to any of the configured numbers to test.
  </Step>
</Steps>

### Multiple inbound phone numbers

A single inbound WhatsApp agent can answer messages sent to any number of business phone numbers — across one or more credentials. Each row in the **Phone numbers** list registers one number with the agent.

* Click **Add phone number** to register another number. The button only appears once at least one row is fully configured.
* Each row can use a different WhatsApp credential, business account, or phone number.
* Timeout and reminder templates are configured **per phone number** — the Timeout Message Template and Reminder Message Template sections show one configurator per registered phone, since approved templates are scoped to the WhatsApp Business Account that owns the number.
* A given WhatsApp phone number can only be assigned to one published inbound agent at a time. Already-assigned numbers are hidden from the picker.
* Phone numbers that are currently claimed by another HappyRobot cluster — for example, a number routed through a different deployment region — appear dimmed in the picker with a link to **Cloud settings**. Resolve the claim in **Assets > Telephony > Phone Numbers** by choosing **Sync messaging** on the number's row before assigning it to a new agent. See [Numbers claimed by another region](../15-Integrations/04-Communication/08-WhatsApp.md#numbers-claimed-by-another-region).

## Setting up an outbound WhatsApp agent

<Steps>
  <Step title="Create a workflow with a trigger">
    Outbound WhatsApp workflows are started by a **Webhook** trigger or **API** call. The trigger payload provides the recipient's phone number and any template parameter values.
  </Step>

  <Step title="Add an outbound text agent node">
    Add an **Outbound Text Agent** action node and select **WhatsApp** as the channel.
  </Step>

  <Step title="Connect your WhatsApp Business account">
    Select your WhatsApp credential and choose the business, business account, and phone number — the same setup as inbound.
  </Step>

  <Step title="Configure the initial outbound template">
    The first message sent to the recipient **must** be an approved WhatsApp template. Select a template and map its parameters. See [Message templates](#message-templates) below for details.
  </Step>

  <Step title="Set the recipient number">
    Enter the recipient's phone number. This typically comes from a [variable](../02-Workflows/07-Variables.md) — type `@` and select `trigger.phone_number`. The number must be in E.164 format.
  </Step>

  <Step title="Configure and publish">
    Set the agent name, prompt, timeout/reminder templates, and conversation settings. Add downstream nodes, then publish and trigger the workflow to test.
  </Step>
</Steps>

## Configuration reference

### WhatsApp Business credentials

Connecting to WhatsApp requires a Meta Business Manager account with the WhatsApp Business API enabled. Configure these in [Credentials](../15-Integrations/02-Credentials.md) using the WhatsApp integration.

| Setting              | Description                                                                                               |
| -------------------- | --------------------------------------------------------------------------------------------------------- |
| **Credential**       | Your WhatsApp API credential, configured in the Credentials page.                                         |
| **Business**         | The Meta Business from your account. Selected from a dropdown populated by your credential.               |
| **Business account** | The WhatsApp Business Account under the selected business.                                                |
| **Phone number**     | The WhatsApp phone number to send and receive messages on. Must be registered with your Business Account. |

All four fields are required. The business, business account, and phone number dropdowns populate hierarchically — select each in order.

### Message templates

WhatsApp requires that certain messages use pre-approved templates. This applies to:

* **Initial outbound messages** — The first message to a contact must always be a template (required for outbound agents).
* **Timeout messages** — If the conversation window has closed, the timeout message must be a template.
* **Reminder messages** — Same rule — reminders sent outside the 24-hour window must use templates.

<Warning>
  Templates must be approved by Meta before they can be used. Create and submit templates in your Meta Business Manager or WhatsApp Business Platform dashboard. Only approved templates appear in the HappyRobot template picker.
</Warning>

#### Template input modes

Each template slot supports two input modes:

**Static mode** — Select a template from a dropdown populated by your WhatsApp Business Account. The UI shows the template preview with its components, and you map parameters visually:

| Parameter type        | Description                                                                                                        |
| --------------------- | ------------------------------------------------------------------------------------------------------------------ |
| **Header parameters** | Values for placeholders in the template header (e.g., a customer name or order number). Supports up to 1 variable. |
| **Body parameters**   | Values for placeholders in the template body text. Supports multiple variables.                                    |
| **Button parameters** | Values for dynamic URL button suffixes and coupon codes. Each button supports 1 variable.                          |

Each parameter supports [variables](../02-Workflows/07-Variables.md), so you can fill template placeholders dynamically from your workflow data.

**Positional and named placeholders** — Template placeholders can be numeric (`{{1}}`, `{{2}}`) or named (`{{customer_name}}`, `{{order_id}}`). When you map a parameter, its key must match the placeholder exactly — use `"1"` for `{{1}}` or `"customer_name"` for `{{customer_name}}`. In the parameter mapper, click a badge like `{{customer_name}}` to edit its value. The template's own text is fixed and can only be changed by creating or editing the template in Meta Business Manager.

**Media headers** — For templates with an image, video, or document header, supply the media at runtime through the dedicated `{{media_url}}` parameter. Point it at a variable that resolves to the file URL.

**Coupon code buttons** — Templates with a copy-code button expose a `{{coupon_code}}` parameter. Map it to the code you want the recipient to copy.

**Dynamic mode** — The template name comes from a variable, and parameters are provided as JSON. This is useful when the template selection itself needs to be dynamic — for example, sending different templates based on the contact's language or the workflow context.

| Setting                    | Description                                               |
| -------------------------- | --------------------------------------------------------- |
| **Template name variable** | A variable that resolves to the template name at runtime. |
| **Header parameters JSON** | JSON array of header parameter values.                    |
| **Body parameters JSON**   | JSON array of body parameter values.                      |
| **Button parameters JSON** | JSON array of button parameter values.                    |

#### Required parameters

A static template slot isn't finished until every placeholder the approved template declares has a value. The node reports itself incomplete and publishing is blocked — the error names the slot, for example *"Initial outbound template is missing required values. Select a template and fill in every required parameter."* — until you fill in:

* Every named or numbered placeholder in the header and body text
* A media URL for an image, video, or document header
* A URL suffix for each dynamic URL button, and a code for each copy-code button
* The same set again, per card, for a [carousel template](#carousel-templates)

Quick-reply payloads are optional and never block completeness, and templates saved before this change keep working. **Dynamic mode** slots are only checked for a template name variable, since the referenced template — and therefore its placeholders — isn't known until runtime; a missing parameter there surfaces as a Meta send error on the run instead.

#### Carousel templates

WhatsApp **carousel** templates — a message with a swipeable row of cards, each with its own media, text, and buttons — are supported anywhere you select a template. When you pick a carousel template, the parameter mapper renders each card separately under a **Card 1**, **Card 2**, … header:

| Per-card parameter      | Description                                                                                                                                          |
| ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Media URL**           | The image or video for the card's header. Point it at a [variable](../02-Workflows/07-Variables.md) that resolves to the file URL, or paste a static HTTP link. |
| **Body parameters**     | Values for the placeholders in the card's body text, mapped the same way as a regular template body.                                                 |
| **Quick-reply payload** | Optional payload string sent back to the workflow when the recipient taps the card's quick-reply button.                                             |

Each card's parameters are scoped to that card, so values never collide between cards. The template and every one of its cards must be approved by Meta before it appears in the picker. When a carousel is sent, it's marked with a badge on the [Runs](../09-Runs-and-Monitoring/01-Runs-Overview.md) page so you can see it in the conversation history.

You can use a carousel template as the **initial outbound message** for an outbound agent, or as an optional inbound greeting — see [Carousel with first message](#carousel-with-first-message).

### Recipient number (outbound only)

The WhatsApp phone number to send the initial template message to. Must be in E.164 format. Supports [variables](../02-Workflows/07-Variables.md).

### Carousel with first message

Inbound WhatsApp agents can send a carousel template right after the agent's first reply on a new conversation — a richer greeting than plain text. This is optional and off unless you configure it.

Configure it in the inbound agent's **Carousel With First Message** section. Only approved [carousel templates](#carousel-templates) are selectable, and you map each card's media, body parameters, and quick-reply payload the same way as any other carousel template.

Because approved templates are scoped to the WhatsApp Business Account that owns a number, the carousel is configured **per phone number** — when an agent listens on [multiple numbers](#multiple-inbound-phone-numbers), each registered number gets its own carousel configurator.

Once enabled, the carousel is treated like any other template slot: the node stays incomplete until a template is selected and every card's [required parameters](#required-parameters) are filled in.

### Delivery error handling

**End session on delivery error** — When enabled, the session ends immediately if a message fails to deliver. Error details are surfaced as node output variables so that downstream nodes can inspect and respond to the failure — for example, to log the error, notify a human, or retry via a different channel.

When disabled (the default), delivery errors are ignored and the session continues.

This setting is available on outbound text agents for every channel except email — see [common agent settings](01-Text-Agents-Overview.md#delivery-error-handling).

<Note>
  Delivery errors differ from the 24-hour window restriction. A delivery error means WhatsApp could not deliver the message to the recipient's device, regardless of the conversation window status.
</Note>

### Sending images and documents

WhatsApp agents can share an image or a PDF in the conversation, so the contact can view or download it without leaving the thread — a rate confirmation, a BOL, a photo of a damaged pallet.

Switch on **Send images and documents** in the prompt node's **Built-in** tab. The row is off by default and only appears on the WhatsApp channel.

| Setting         | Description                                                                                                                                                                           |
| --------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Description** | When the agent should send media. Supports [variables](../02-Workflows/07-Variables.md). Defaults to "Send images and PDF documents in the conversation so the user can view or download them."  |
| **Caption**     | The caption shown on the media — **AI** writes one from the conversation, **Fixed** uses exact text you supply, and **None** sends the media without a caption. Defaults to **None**. |

Enabling the setting registers the `hr_builtin_tool__send_whatsapp_media` [built-in tool](#built-in-tools). The agent decides when to call it based on your description and prompt.

### Reply with voice notes

WhatsApp agents can send their replies as voice notes instead of text. When a reply is sent as a voice note, it is synthesized to speech using a text-to-speech voice you select and delivered as a WhatsApp voice note.

Switch on **Send voice notes** in the prompt node's **Built-in** tab — the row only appears on the WhatsApp channel — and configure:

| Setting        | Description                                                                                                                                                                                                                                                                                  |
| -------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Reply mode** | **Always send as voice note** converts every reply to a voice note. **Let the agent decide** replies with text by default and lets the agent send a voice note when it judges it appropriate — or when your prompt tells it to — via the `send_voice_note` [built-in tool](#built-in-tools). |
| **Languages**  | The languages voice notes are synthesized in. Required when voice notes are enabled — pick at least one.                                                                                                                                                                                     |
| **Voice**      | The text-to-speech voice used to synthesize replies. Required when voice notes are enabled. Pick from the [voice library](../14-Assets/04-Voices.md) using the searchable selector.                                                                                                                     |

#### Languages and accents

Choose the languages voice notes are spoken in before you pick the voice. The selector lists the same languages and regional accents as the [voice library](../14-Assets/04-Voices.md) — for example **Spanish (Mexico)**, **Spanish (Spain)**, or **Portuguese (Brazil)** — each with its flag and its accent code (`es-MX`, `es-ES`, `pt-BR`), which you can copy from the row.

* **One accent per language.** Picking a second accent for a language you already selected replaces the first, so a language is never listed twice with conflicting accents.
* **All Languages** selects every language the voice library supports. Selecting it clears any individual picks; conversely, selecting every individual language collapses the selection to **All Languages**.

Once languages are selected, the **Voice** picker reorders itself so voices that speak them come first — voices with a native accent for a selected language, then voices with a cloned accent for it, then everything else. The full library stays searchable.

<Warning>
  Voice notes cannot be published without at least one language and a voice. A prompt node with voice notes enabled and either field empty is marked incomplete with *"Missing language selection. When voice notes are enabled, at least one language must be selected."*
</Warning>

<Note>
  Voice notes apply to the agent's regular text replies. Template messages (initial outbound, timeout, and reminder templates) are always sent as WhatsApp templates and are not converted to voice notes. Inbound voice messages from contacts are handled separately by [media processing](01-Text-Agents-Overview.md#media-processing) transcription.
</Note>

<Note>
  With **Let the agent decide**, whether a voice note is sent is an AI decision and is not guaranteed — the agent may occasionally reply with text when a voice note was expected, or vice versa. Choose **Always send as voice note** if every reply must be a voice note.
</Note>

### Interactive messages

WhatsApp agents can send native **interactive messages** — tappable list pickers and quick-reply buttons — instead of plain text when asking the contact to choose from a set of options. The agent decides when to use them based on the conversation.

| Setting                  | Description                                                                                                                                                                        |
| ------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Interactive messages** | Switch on in the prompt node's **Built-in** tab to let the agent send WhatsApp list pickers and quick-reply buttons. Off by default. The row only appears on the WhatsApp channel. |

When enabled, interactive messages are marked with a badge on the [Runs](../09-Runs-and-Monitoring/01-Runs-Overview.md) page so you can see when the agent sent a list or a set of buttons rather than a text reply.

<Note>
  Interactive messages are supported only on the WhatsApp channel. Enabling this setting on any other text channel produces a validation error.
</Note>

### Reactions

When a contact reacts to one of the agent's messages with an emoji, the reaction is delivered to the agent as a turn in the conversation, so the agent can acknowledge it or treat it as an answer if your prompt tells it to — for example, reading a 👍 on a confirmation question as a yes.

In the [run timeline](../09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#text-agent-transcripts), a reaction renders as a compact line showing the emoji and the message that was reacted to, rather than a full message bubble.

<Note>
  Whether the agent responds to a reaction at all is up to the prompt. If reactions should carry meaning in your conversation, say so explicitly — otherwise the agent may ignore them or reply with a generic acknowledgement.
</Note>

### Built-in tools

Beyond any tools you attach to the agent, WhatsApp agents can call a set of built-in tools mid-conversation. Each one is only registered when its corresponding setting is enabled in the prompt node's **Built-in** tab, so the agent only sees the tools relevant to how you've configured it. Type `/` in the prompt to reference one of them by name — see [Built-in tools](../04-Tools/04-Built-in-Tools.md#referencing-a-built-in-from-the-prompt).

| Tool                          | Tool ID                                  | Enabled when                                         | What it does                                                                                                                                    |
| ----------------------------- | ---------------------------------------- | ---------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Send list**                 | `hr_builtin_tool__send_whatsapp_list`    | Interactive messages are on                          | Sends a tappable list picker (up to 10 rows) for the contact to choose one option. Best for 4+ options or options that need short descriptions. |
| **Send buttons**              | `hr_builtin_tool__send_whatsapp_buttons` | Interactive messages are on                          | Sends 1–3 quick-reply buttons for short, mutually-exclusive choices (e.g. Yes/No).                                                              |
| **Send voice note**           | `hr_builtin_tool__send_voice_note`       | Voice notes are on and set to *Let the agent decide* | Replies with a spoken voice note instead of text: the reply text is synthesized to speech and delivered as a WhatsApp voice note.               |
| **Send images and documents** | `hr_builtin_tool__send_whatsapp_media`   | Send images and documents is on                      | Sends an image or PDF document in the conversation for the contact to view or download, with an optional caption.                               |
| **Escalate to human**         | `hr_builtin_tool__escalate_to_human`     | Escalation is enabled                                | Transfers the conversation to a human when the agent can't help or the contact asks for a person.                                               |
| **End conversation**          | `hr_builtin_tool__end_conversation`      | End conversation is enabled                          | Ends the conversation once the contact indicates they need no further help.                                                                     |
| **Read media**                | `hr_builtin_tool__read_media`            | Media processing is enabled                          | Extracts text from a document or transcribes an audio/voice message the contact sent, so the agent can act on its contents.                     |

<Note>
  There is **no built-in tool for sending WhatsApp message templates mid-conversation.** Templates are sent automatically by HappyRobot in fixed slots — the initial outbound message, and timeout/reminder messages outside the 24-hour window (see [Message templates](#message-templates) and [The 24-hour conversation window](#the-24-hour-conversation-window)). The agent cannot choose to send an arbitrary template from its prompt.
</Note>

### Agent settings

Timeout, reminders, escalation, and end conversation settings are shared across all text agent channels. See [common agent settings](01-Text-Agents-Overview.md#common-agent-settings) for the full reference.

For WhatsApp specifically, timeout and reminder templates are configured separately from the regular timeout/reminder messages. When a template is enabled for timeout or reminders, HappyRobot sends the template instead of a regular text message whenever the conversation is outside the 24-hour window.

## WhatsApp message flow

### Inbound flow

1. A person sends a WhatsApp message to your configured business phone number.
2. Meta delivers the message to HappyRobot via the WhatsApp Business API webhook.
3. HappyRobot matches the phone number to a workflow trigger and starts a new run (or resumes an existing session).
4. A text session is created and the message is added to the conversation history.
5. The LLM generates a response and sends it as a WhatsApp message.
6. The session stays open for follow-up messages until the idle timeout expires or the agent ends the conversation.

### Outbound flow

1. The workflow trigger fires and execution begins.
2. The outbound text agent sends the initial template message to the recipient via the WhatsApp Business API.
3. The recipient receives the template message and can reply, which opens a 24-hour conversation window.
4. Within the window, the LLM responds with regular text messages. Outside the window, it uses approved templates.
5. The conversation continues until the idle timeout expires or the agent ends it, then the workflow proceeds to downstream nodes.

## The 24-hour conversation window

Meta enforces a 24-hour conversation window rule: after a user sends a message, your business can reply with regular (non-template) messages for 24 hours. After that window closes, you can only send approved template messages.

HappyRobot handles this automatically:

* **Within the window** — The agent sends regular text responses generated by the LLM.
* **Outside the window** — If a timeout or reminder fires and the window has closed, HappyRobot sends the configured template instead of a regular message. If no template is configured for that slot, the message is skipped.
* **Reopening the window** — When the contact sends a new message, the 24-hour window resets, and the agent can resume sending regular messages.

<Tip>
  Always configure timeout and reminder templates for WhatsApp agents, even if you don't expect conversations to last 24 hours. Edge cases happen — contacts get busy, time zones differ, and having templates ready prevents silent failures.
</Tip>

## Next steps

<CardGroup cols={3}>
  <Card title="Email" icon="envelope" href="04-Email.md">
    Deploy agents for email conversations.
  </Card>

  <Card title="Prompts and tools" icon="message" href="../05-Voice-Agents/06-Prompts-and-Tools.md">
    Write effective prompts and attach tools.
  </Card>

  <Card title="WhatsApp integration" icon="whatsapp" href="../15-Integrations/04-Communication/08-WhatsApp.md">
    Set up your WhatsApp Business credentials.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/text-agents/whatsapp
