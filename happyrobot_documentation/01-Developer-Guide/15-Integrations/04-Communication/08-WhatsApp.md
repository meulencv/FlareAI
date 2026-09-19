---
title: "WhatsApp"
description: "Connect to WhatsApp Business API"
---

# WhatsApp

> Connect to WhatsApp Business API

The WhatsApp integration connects your workflows to the WhatsApp Business API through Meta's platform. Manage business accounts, phone numbers, and message templates for WhatsApp-based text agents.

## Authentication

WhatsApp supports three credential types:

| Credential type                   | Best for                                                | Flow                                          |
| --------------------------------- | ------------------------------------------------------- | --------------------------------------------- |
| **System User + Embedded Signup** | Production setups with system-level access              | Form — System User Token, Partner Business ID |
| **Partner Business ID**           | Adding HappyRobot as a partner to your Business Manager | Form — WhatsApp Business Account ID           |
| **User OAuth**                    | Individual Meta app admin/developer access              | OAuth — redirects to Meta sign-in             |

### System User + Embedded Signup

<Steps>
  <Step title="Enable the WhatsApp integration">
    Go to **Settings > Integrations** and enable **WhatsApp**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential**, select **System User + Embedded Signup**, and fill in:

    * **System User Token** — a system user token from your Meta Business Manager
    * **Partner Business ID** — your partner business ID
  </Step>

  <Step title="Test the connection">
    Click **Test** to verify the system user token has the required permissions.
  </Step>
</Steps>

### Partner Business ID

<Steps>
  <Step title="Add a credential">
    Click **Add Credential**, select **Partner Business ID**, and enter your **WhatsApp Business Account ID**.
  </Step>

  <Step title="Test the connection">
    Click **Test** to verify access to the business account.
  </Step>
</Steps>

### User OAuth

<Steps>
  <Step title="Add a credential">
    Click **Add Credential**, select **User OAuth**. You'll be redirected to Meta's sign-in page.
  </Step>

  <Step title="Authorize access">
    Sign in with your Meta account and approve the requested permissions.
  </Step>
</Steps>

## Configuration

After connecting your WhatsApp Business account, you can manage:

* **Business accounts** — select which WhatsApp Business account to use
* **Phone numbers** — choose which phone number to assign to your text agent
* **Message templates** — select pre-approved message templates for outbound messages

## Send WhatsApp

The **WhatsApp > Send WhatsApp** action node sends a pre-approved template message from a workflow. Use it when you need to send a single templated message — an appointment reminder, a status update — without running a [WhatsApp text agent](../../06-Text-Agents/03-WhatsApp.md) for the conversation.

| Field                | Required | Description                                                                                                                                                                             |
| -------------------- | -------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **To**               | Yes      | The recipient's WhatsApp number in E.164 format. Supports [variables](../../02-Workflows/07-Variables.md).                                                                                            |
| **Credential**       | Yes      | The WhatsApp credential to send through.                                                                                                                                                |
| **Business account** | Yes      | The WhatsApp Business Account that owns the sending number.                                                                                                                             |
| **Phone number**     | Yes      | The number the message is sent from.                                                                                                                                                    |
| **Template**         | Yes      | An approved template and its parameter values, configured with the same template picker used by WhatsApp text agents. See [Message templates](../../06-Text-Agents/03-WhatsApp.md#message-templates). |

<Note>
  Only templates approved by Meta appear in the picker, and only templates belonging to the selected Business Account. The node sends a template — it does not start a conversation the agent then handles.
</Note>

## WhatsApp number management

WhatsApp numbers are managed from **Assets > Telephony > Phone Numbers**, next to your carrier numbers. Verification, Cloud API registration, calling settings, and messaging routing all live on the number's own row.

<Note>
  This replaces the WhatsApp integration's **Cloud Migration** tab. That tab now links straight to the WhatsApp numbers in Telephony.
</Note>

Each WhatsApp number shows a **Messaging Status** and a **Calling Status**, and the row's **…** menu offers the action the number needs next:

| Action              | What it does                                                                                                                                 |
| ------------------- | -------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sync messaging**  | Verifies the number with Meta if needed (SMS or voice code), then registers it on Cloud API and points its messaging callback at HappyRobot. |
| **Sync calling**    | Turns on WhatsApp Business Calling and routes call events to HappyRobot. Available once messaging is synced.                                 |
| **Register number** | Adds one of your Twilio or Telnyx numbers to your WhatsApp Business Account.                                                                 |

See [WhatsApp numbers](../../14-Assets/03-Telephony.md#whatsapp-numbers) for the full walkthrough.

## WhatsApp Business Calling

WhatsApp numbers with Business Calling enabled can take voice calls through HappyRobot. Once **Calling Status** reads **Synced**, the number appears in the inbound voice trigger's number picker alongside your carrier numbers. WhatsApp connections can't place outbound PSTN calls, so they're left out of outbound caller-ID pickers. See [Syncing a number already on WhatsApp](../../14-Assets/03-Telephony.md#syncing-a-number-already-on-whatsapp) for the sync flow and troubleshooting.

## Bringing your own number onto WhatsApp

If you already own a Twilio or Telnyx number in HappyRobot, you can add it to your WhatsApp Business Account instead of buying a new one from Meta. Open the number's action menu in **Assets > Telephony** and choose **Register number** under **WhatsApp** — HappyRobot adds the number to the WABA, walks you through Meta's voice verification, and registers it on Cloud API. The number keeps working for regular calls and SMS.

See [Registering a carrier number on WhatsApp](../../14-Assets/03-Telephony.md#registering-a-carrier-number-on-whatsapp) for the full walkthrough.

## Numbers claimed by another region

A number whose Meta callback points at a different HappyRobot region shows **Other region** as its calling or messaging status, with the owning cluster named in the tooltip. Choose **Sync messaging** on that row to point the subscription and callback at the current region and take ownership.

## Usage with text agents

The WhatsApp integration is primarily used with [WhatsApp text agents](../../06-Text-Agents/03-WhatsApp.md). In the text agent configuration, select a WhatsApp phone number and message template to use for conversations.

<Tip>
  For detailed instructions on setting up WhatsApp-based AI agents, see the [WhatsApp Text Agents](../../06-Text-Agents/03-WhatsApp.md) documentation.
</Tip>

## Example use case

A customer sends a WhatsApp message to your business number. The AI text agent responds conversationally, helping the customer check shipment status, schedule pickups, or get rate quotes — all within WhatsApp's familiar interface.

## Related

<CardGroup cols={2}>
  <Card title="WhatsApp text agents" icon="phone" href="../../06-Text-Agents/03-WhatsApp.md">
    Set up AI agents that communicate via WhatsApp.
  </Card>

  <Card title="Twilio SMS" icon="message-sms" href="06-Twilio-SMS.md">
    SMS messaging via Twilio.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/whatsapp
