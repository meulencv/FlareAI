---
title: "Twilio SMS"
description: "Send and receive SMS messages via Twilio"
---

# Twilio SMS

> Send and receive SMS messages via Twilio

The Twilio SMS integration connects your HappyRobot workflows to Twilio's SMS service. It provides phone number management for SMS-based text agents, letting you assign Twilio numbers to your workflows for inbound and outbound text messaging.

## Authentication

Twilio SMS uses API credentials for authentication.

<Steps>
  <Step title="Enable the Twilio SMS integration">
    Go to **Settings > Integrations** and enable **Twilio SMS**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    * **Account SID** — your Twilio account SID (found on the Twilio console dashboard)
    * **Auth Token** — your Twilio auth token
  </Step>

  <Step title="Verify the connection">
    The credential will validate automatically. Once active, your Twilio phone numbers will be available for selection in workflows.
  </Step>
</Steps>

## Phone number management

After connecting your Twilio account, your available phone numbers are loaded dynamically from the Twilio API. You can assign these numbers to SMS text agent nodes in your workflows.

## Usage with text agents

The Twilio SMS integration is primarily used with [SMS text agents](../../06-Text-Agents/02-SMS.md). In the text agent configuration, select a Twilio phone number to use for sending and receiving SMS messages.

<Tip>
  For detailed instructions on setting up SMS-based AI agents, see the [SMS Text Agents](../../06-Text-Agents/02-SMS.md) documentation.
</Tip>

## Example use case

A workflow assigns a Twilio phone number to an SMS text agent. When a customer texts the number, the AI agent responds conversationally — checking order status, scheduling appointments, or collecting information — all via SMS.

## Related

<CardGroup cols={2}>
  <Card title="SMS text agents" icon="message-sms" href="../../06-Text-Agents/02-SMS.md">
    Set up AI agents that communicate via SMS.
  </Card>

  <Card title="WhatsApp" icon="phone" href="08-WhatsApp.md">
    WhatsApp Business messaging integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/twilio-sms
