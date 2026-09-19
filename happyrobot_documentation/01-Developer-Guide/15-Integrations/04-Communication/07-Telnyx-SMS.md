---
title: "Telnyx SMS"
description: "Send and receive SMS messages via Telnyx"
---

# Telnyx SMS

> Send and receive SMS messages via Telnyx

The Telnyx SMS integration connects your HappyRobot workflows to Telnyx's SMS service. It provides phone number management for SMS-based text agents, letting you assign Telnyx numbers to your workflows for inbound and outbound text messaging. Telnyx is offered as a **bring-your-own** provider alongside Twilio — connect your own Telnyx account and use your own numbers.

## Authentication

Telnyx SMS uses a Bearer API key, plus a webhook public key and messaging profile ID for inbound message verification.

<Steps>
  <Step title="Enable the Telnyx SMS integration">
    Go to **Settings > Integrations** and enable **Telnyx SMS**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    * **API Key** — your Telnyx API (Bearer) key. Required.
    * **Webhook Public Key** — your Telnyx account's Ed25519 public key, used to verify the signature of inbound webhook payloads.
    * **Messaging Profile ID** — the UUID of the Telnyx messaging profile that the numbers on this credential belong to.
  </Step>

  <Step title="Verify the connection">
    The credential validates automatically once the API key is provided. Once active, your Telnyx phone numbers are available for selection in workflows.
  </Step>
</Steps>

<Warning>
  To **receive** SMS (inbound agents), both the **Webhook Public Key** and the **Messaging Profile ID** are required. The inbound webhook handler looks up the verification key by the payload's messaging profile ID, so a blank profile ID or missing public key means inbound webhooks fail signature verification and are rejected. You can leave these fields blank only for **send-only (outbound)** use.
</Warning>

## Phone number management

After connecting your Telnyx account, your available phone numbers are loaded from the Telnyx API. You can assign these numbers to SMS text agent nodes in your workflows by selecting **Bring your own Telnyx** as the SMS provider.

### Toll-free numbers

US and Canadian toll-free numbers can be bought on Telnyx from **Assets > Telephony**. Buying one submits a toll-free verification with the carrier, and SMS stays blocked on the number until that verification is approved. Telnyx requires business registration details for every business type — including sole proprietors — and an opt-in image URL. See [US and Canadian toll-free numbers](../../14-Assets/03-Telephony.md#us-and-canadian-toll-free-numbers).

## Usage with text agents

The Telnyx SMS integration is used with [SMS text agents](../../06-Text-Agents/02-SMS.md). In the text agent configuration, choose **Bring your own Telnyx** as the SMS provider, select your Telnyx credential, and pick the phone number to use for sending and receiving SMS messages.

<Tip>
  For detailed instructions on setting up SMS-based AI agents, see the [SMS text agents](../../06-Text-Agents/02-SMS.md) documentation.
</Tip>

## Related

<CardGroup cols={2}>
  <Card title="SMS text agents" icon="message-sms" href="../../06-Text-Agents/02-SMS.md">
    Set up AI agents that communicate via SMS.
  </Card>

  <Card title="Twilio SMS" icon="message-sms" href="06-Twilio-SMS.md">
    Use Twilio as your SMS provider instead.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/telnyx-sms
