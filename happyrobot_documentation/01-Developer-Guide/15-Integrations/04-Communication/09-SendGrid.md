---
title: "SendGrid"
description: "Send transactional emails and run direct email agents via SendGrid"
---

# SendGrid

> Send transactional emails and run direct email agents via SendGrid

The SendGrid integration lets your workflows send emails through SendGrid's transactional email service. Use it for automated notifications, confirmations, and outreach with reliable delivery. SendGrid can also act as a **direct email provider** for [email text agents](../../06-Text-Agents/04-Email.md#direct-email-providers-sendgrid-postmark) — both receiving (via Inbound Parse) and sending — to power two-way email conversations on your own domain.

## Authentication

SendGrid uses an API key for authentication.

<Steps>
  <Step title="Enable the SendGrid integration">
    Go to **Settings > Integrations** and enable **SendGrid**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and enter your **API Key** from the SendGrid dashboard. The key must have `Mail Send` permissions at minimum.
  </Step>

  <Step title="Verify the connection">
    The credential will validate automatically and appear as **Active**.
  </Step>
</Steps>

## Available events

### Actions

| Event          | Description                               |
| -------------- | ----------------------------------------- |
| **Send Email** | Sends a new email through SendGrid        |
| **Send Reply** | Sends a reply to an existing email thread |

### Send Email configuration

When configuring the **Send Email** action, you can set:

| Field          | Description                             |
| -------------- | --------------------------------------- |
| **From Email** | The sender email address                |
| **To**         | Recipient email address(es)             |
| **Cc**         | Carbon copy recipients (optional)       |
| **Bcc**        | Blind carbon copy recipients (optional) |
| **From Name**  | Display name for the sender             |
| **Subject**    | Email subject line                      |
| **Body Type**  | Plain Text or HTML                      |
| **Body**       | The email body content                  |

All fields support template variables — type `@` to reference data from upstream nodes.

## Direct email provider for text agents

Beyond one-off workflow actions, SendGrid can power a full two-way **email text agent** on your own domain — receiving inbound mail through SendGrid Inbound Parse and sending replies through the same credential. This is the **direct** provider option in an email agent's provider list.

<Steps>
  <Step title="Select SendGrid as the agent's email provider">
    In an [email text agent](../../06-Text-Agents/04-Email.md), choose **SendGrid** and the API-key credential. The config surfaces a generated **Inbound Webhook URL**.
  </Step>

  <Step title="Point a subdomain's MX at SendGrid">
    Add an `MX` record for a dedicated subdomain — e.g. `parse.yourcompany.com` → `mx.sendgrid.net` — and a SendGrid **Inbound Parse** setting that POSTs to the Inbound Webhook URL. MX is per-hostname, so only the subdomain is affected — your apex mailboxes stay on their existing provider.
  </Step>

  <Step title="Set the From and Reply-To">
    The **From** can be a branded apex address (e.g. `support@yourcompany.com`, authenticated in SendGrid). Set the **Reply-To** to an address on the parse subdomain so replies route back to the agent while the From stays your apex address.
  </Step>
</Steps>

To let customers **start** a conversation by emailing your apex address, forward that one address to the subdomain at your mail provider — only that address is diverted, every other apex mailbox is untouched. See [Direct email providers](../../06-Text-Agents/04-Email.md#direct-email-providers-sendgrid-postmark) for the full model, including the apex-inbound forwarding rule and per-session Reply-To routing.

## Example use case

After a voice agent completes a call, the workflow uses **AI Generate** to compose a follow-up email summarizing the conversation, then sends it via **Send Email** to the customer with a professional HTML template.

## Related

<CardGroup cols={2}>
  <Card title="Gmail" icon="envelope" href="01-Gmail.md">
    Gmail email integration with trigger support.
  </Card>

  <Card title="HappyRobot Email" icon="envelope" href="10-HappyRobot-Email.md">
    Built-in email service with no external provider.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/sendgrid
