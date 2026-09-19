---
title: "SMS"
description: "Deploy text agents over SMS"
---

# SMS

> Deploy text agents over SMS

SMS text agents handle two-way conversations over standard text messages. You can receive inbound messages on a phone number and respond automatically, or trigger outbound messages to start conversations with contacts. HappyRobot manages the webhook routing between your SMS provider and your workflow — you just configure the agent and assign a number. SMS supports two providers: **Twilio** and **Telnyx**.

## Setting up an inbound SMS agent

<Steps>
  <Step title="Add an inbound trigger">
    Every inbound SMS workflow starts with an **Inbound Text** trigger node. In the workflow editor, select this trigger — it listens for incoming SMS messages on your configured numbers.
  </Step>

  <Step title="Add an inbound text agent node">
    Add an **Inbound Text Agent** action node to your workflow and select **SMS** as the channel.
  </Step>

  <Step title="Configure one or more phone numbers">
    Each inbound SMS agent can listen on multiple numbers. For each row, choose the SMS provider — **Use existing toll-free** for a HappyRobot-managed number, **Bring your own Twilio** for your own Twilio account and phone number, or **Bring your own Telnyx** for your own Telnyx account and phone number — and select the specific number. Click **Add phone number** to register additional numbers on the same agent. See [Multiple inbound phone numbers](#multiple-inbound-phone-numbers) for details.
  </Step>

  <Step title="Configure the agent">
    Set the agent name, write a prompt in the nested [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md), and configure timeout, reminder, and escalation settings. See [common agent settings](01-Text-Agents-Overview.md#common-agent-settings) for details on shared configuration.
  </Step>

  <Step title="Publish and test">
    Publish your workflow and send a text message to any of the assigned numbers. Review the run in the Runs tab to see the full message thread and node outputs.
  </Step>
</Steps>

### Multiple inbound phone numbers

A single inbound SMS agent can answer messages sent to any number of phone numbers. Each row in the **Phone numbers** list registers one number — toll-free or Twilio — with the agent. When a message arrives, HappyRobot routes it to this agent based on which number received it.

* Click **Add phone number** to register another number. The button only appears once at least one row is fully configured.
* Mix providers freely: one agent can include both a toll-free number and a Bring-Your-Own-Twilio number.
* A given phone number can only be assigned to one published inbound agent at a time — already-assigned numbers are hidden from the picker.
* Numbers in this list use static selection only. Use a dynamic [variable](../02-Workflows/07-Variables.md) on outbound nodes when you need to choose the sending number per run.

## Setting up an outbound SMS agent

<Steps>
  <Step title="Create a workflow with a trigger">
    Outbound SMS workflows are typically started by a **Webhook** trigger or an **API** call. The trigger payload provides the recipient phone number and any data the agent needs.
  </Step>

  <Step title="Add an outbound text agent node">
    Add an **Outbound Text Agent** action node and select **SMS** as the channel.
  </Step>

  <Step title="Configure the SMS provider">
    Choose your SMS provider — the same options as inbound: **Use existing toll-free**, **Bring your own Twilio**, or **Bring your own Telnyx**.
  </Step>

  <Step title="Set the recipient number">
    Set the **Recipient number** field with the phone number to message. This typically comes from a [variable](../02-Workflows/07-Variables.md) in the trigger payload — type `@` and select `trigger.phone_number`. The number must be in E.164 format (e.g., `+15551234567`).
  </Step>

  <Step title="Configure and publish">
    Set the agent name, prompt, and conversation settings. Add downstream nodes to process the conversation results, then publish and trigger the workflow to test.
  </Step>
</Steps>

## Configuration reference

### SMS provider

The provider setting determines which account and phone number the agent uses to send and receive messages. For inbound agents, each row in the **Phone numbers** list selects its provider independently.

**Use existing toll-free** — Use a HappyRobot-managed toll-free number. Select the number from the dropdown — these numbers are provisioned and configured automatically. This is the simplest option when you don't need a specific number or branding.

**Bring your own Twilio** — Connect your own Twilio account. You'll need to:

1. Add your Twilio credentials in [Credentials](../15-Integrations/02-Credentials.md) (select the Twilio SMS integration).
2. Select the credential in the agent configuration.
3. Choose the Twilio phone number to use from your account.

**Bring your own Telnyx** — Connect your own Telnyx account. You'll need to:

1. Add your Telnyx credentials in [Credentials](../15-Integrations/02-Credentials.md) (select the [Telnyx SMS integration](../15-Integrations/04-Communication/07-Telnyx-SMS.md)).
2. Select the credential in the agent configuration.
3. Choose the Telnyx phone number to use from your account.

Bringing your own provider gives you full control over the sending number, which is important for brand recognition and when contacts expect messages from a specific number.

### Agent name

A label for the agent, visible in the workflow editor and run logs. This is required for all channels.

### Recipient number (outbound only)

The phone number to send the first message to. Must be in E.164 format. Supports [variables](../02-Workflows/07-Variables.md) for dynamic values from the trigger payload — type `@` and select the phone number variable (e.g., `@trigger.phone_number` or `@nodes.lookup.output.mobile`).

### Prompt and tools

The system prompt and tools are configured in the [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md) nested inside the text agent node — the same system used by voice agents. Text agents use Anthropic Claude models. Write your prompt to define the agent's personality, instructions, and conversation flow, then attach tools for any actions the agent needs to take mid-conversation.

### Agent settings

Timeout, reminders, escalation, and end conversation settings are shared across all text agent channels. See [common agent settings](01-Text-Agents-Overview.md#common-agent-settings) for the full reference.

## Sending a one-off SMS

To send a single SMS message from a workflow without starting a back-and-forth conversation, use the **Send SMS** action node. This is a fire-and-forget send — no session is created, and the agent does not reply to inbound replies on that message.

<Steps>
  <Step title="Add a Send SMS node">
    In the workflow editor, click **+** and select **Send SMS** under the Text category.
  </Step>

  <Step title="Set the recipient and message">
    Fill in **To** with the recipient phone number in E.164 format (variables supported with `@`) and **Message** with the message body.
  </Step>

  <Step title="Configure the SMS provider">
    Choose **Use existing toll-free** to send from a HappyRobot-managed toll-free number, or **Bring your own Twilio** / **Bring your own Telnyx** to send from your own provider account and number. The provider options match the inbound and outbound agent configuration above.
  </Step>
</Steps>

<Note>
  The older **Send Text** node is deprecated. It continues to work, but it is no longer maintained — migrate to **Send SMS** for new workflows.
</Note>

## SMS message flow

### Inbound flow

1. A person sends an SMS to your configured phone number.
2. Your SMS provider (Twilio or Telnyx) receives the message and forwards it to HappyRobot via webhook.
3. HappyRobot matches the phone number to a workflow trigger and starts a new run (or resumes an existing session if the contact has an active conversation).
4. A text session is created with type `text` and the message is added to the conversation history.
5. The LLM generates a response using the prompt, conversation history, and any tool results.
6. The response is sent back as an SMS via the same provider.
7. The session stays open for follow-up messages until the idle timeout expires or the agent ends the conversation.

### Outbound flow

1. The workflow trigger fires (webhook, API, or upstream action) and execution begins.
2. The outbound text agent node creates a session and sends the first message to the recipient via your configured SMS provider.
3. The recipient receives the SMS and can reply.
4. Each reply is routed back to the same session, and the LLM generates a response.
5. The conversation continues until the idle timeout expires or the agent ends it.
6. When the session closes, the workflow proceeds to downstream nodes.

## Next steps

<CardGroup cols={3}>
  <Card title="WhatsApp" icon="whatsapp" href="03-WhatsApp.md">
    Deploy agents on WhatsApp Business.
  </Card>

  <Card title="Prompts and tools" icon="message" href="../05-Voice-Agents/06-Prompts-and-Tools.md">
    Write effective prompts and attach tools.
  </Card>

  <Card title="Twilio SMS" icon="comment-sms" href="../15-Integrations/04-Communication/06-Twilio-SMS.md">
    Set up your Twilio SMS integration.
  </Card>

  <Card title="Telnyx SMS" icon="comment-sms" href="../15-Integrations/04-Communication/07-Telnyx-SMS.md">
    Set up your Telnyx SMS integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/text-agents/sms
