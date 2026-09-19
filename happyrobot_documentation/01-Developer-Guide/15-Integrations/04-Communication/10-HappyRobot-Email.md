---
title: "HappyRobot Email"
description: "Use HappyRobot's built-in email service"
---

# HappyRobot Email

> Use HappyRobot's built-in email service

HappyRobot Email is the platform's built-in email service. It lets you send and receive emails without configuring an external email provider — no OAuth setup, no API keys, and no third-party accounts required.

## Authentication

No external credentials are needed. HappyRobot Email is available by default once the integration is enabled.

<Steps>
  <Step title="Enable the integration">
    Go to **Settings > Integrations** and enable **HappyRobot Email**.
  </Step>

  <Step title="Start using it in workflows">
    Add HappyRobot Email events to your workflow nodes. No credential configuration is required.
  </Step>
</Steps>

## Available events

### Triggers

| Event                 | Description                                                     |
| --------------------- | --------------------------------------------------------------- |
| **New Inbound Email** | Fires when a new email arrives at your HappyRobot email address |

### Actions

| Event                | Description                                          |
| -------------------- | ---------------------------------------------------- |
| **Send Email**       | Sends a new email from your HappyRobot email address |
| **Send Reply Email** | Sends a reply to an existing email thread            |
| **Parse Attachment** | Extracts and processes email attachments             |

## When to use HappyRobot Email

HappyRobot Email is ideal when:

* You want to get started quickly without configuring OAuth or API keys
* You don't need to send from a specific branded email address
* You want a simple trigger for email-based workflows

<Tip>
  If you need to send emails from your organization's domain (e.g., `support@yourcompany.com`), use the [Gmail](01-Gmail.md), [Outlook](02-Outlook.md), or [SendGrid](09-SendGrid.md) integration instead.
</Tip>

## Example use case

A HappyRobot Email address receives carrier rate confirmations. The **New Inbound Email** trigger fires, **Parse Attachment** extracts the rate sheet PDF, **AI Extract** pulls the rates and lane details, and the workflow updates the carrier record in the Broker App.

## Related

<CardGroup cols={2}>
  <Card title="Gmail" icon="envelope" href="01-Gmail.md">
    Send from your Gmail account with OAuth.
  </Card>

  <Card title="SendGrid" icon="paper-plane" href="09-SendGrid.md">
    High-volume transactional email via SendGrid.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/happyrobot-email
