---
title: "Outlook"
description: "Send and receive emails with Microsoft Outlook"
---

# Outlook

> Send and receive emails with Microsoft Outlook

The Outlook integration connects your workflows to Microsoft 365 email. Send emails, monitor inboxes for new messages, read threads, and forward messages — all through the Microsoft Graph API.

## Authentication

Outlook supports three credential types:

| Credential type                  | Best for                                     | Flow                                       |
| -------------------------------- | -------------------------------------------- | ------------------------------------------ |
| **User Mailbox**                 | Individual Microsoft 365 accounts            | OAuth — redirects to Microsoft sign-in     |
| **Service Principal**            | Organizational mailboxes via app credentials | Form — Client ID, Tenant ID, Client Secret |
| **Azure Communication Services** | High-volume transactional email (100k+/hour) | Form — ACS Endpoint, Access Key            |

### User Mailbox (OAuth)

<Steps>
  <Step title="Enable the Outlook integration">
    Go to **Settings > Integrations** and enable **Outlook**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and select **User Mailbox**. You'll be redirected to Microsoft's sign-in page.
  </Step>

  <Step title="Grant permissions">
    Sign in and approve the requested permissions (read/write mail, send mail, read user profile).
  </Step>
</Steps>

### Service Principal

<Steps>
  <Step title="Register an application in Azure AD">
    In the Azure portal, register an application and grant it `Mail.ReadWrite` and `Mail.Send` application permissions.
  </Step>

  <Step title="Add the credential in HappyRobot">
    Click **Add Credential**, select **Service Principal**, and fill in:

    * **Client ID** — the application (client) ID from Azure
    * **Tenant ID** — your Azure AD tenant ID
    * **Client Secret** — a client secret generated in Azure
    * **Target Mailbox** — the email address to access
    * **Target Mailbox Name** — a display name for this mailbox
  </Step>

  <Step title="Test the connection">
    Click **Test** to verify the service principal can access the target mailbox.
  </Step>
</Steps>

### Azure Communication Services

<Steps>
  <Step title="Set up ACS in Azure">
    Create an Azure Communication Services resource and configure an email domain.
  </Step>

  <Step title="Add the credential in HappyRobot">
    Click **Add Credential**, select **Azure Communication Services**, and fill in:

    * **ACS Endpoint** — the endpoint URL from your ACS resource
    * **Access Key** — the access key from your ACS resource
    * **Sender Domain** — the verified sender username/domain
  </Step>

  <Step title="Test the connection">
    Click **Test** to verify the ACS configuration.
  </Step>
</Steps>

## Available events

### Triggers

| Event         | Description                                                                               |
| ------------- | ----------------------------------------------------------------------------------------- |
| **New Email** | Fires when a new email arrives in the connected mailbox. Requires an active subscription. |

### Actions

| Event                   | Description                                     |
| ----------------------- | ----------------------------------------------- |
| **Send Email**          | Sends a new email from the connected account    |
| **Send Reply**          | Sends a reply to an existing email thread       |
| **Get Email**           | Retrieves a single email by ID                  |
| **Get Thread Messages** | Retrieves all messages in a conversation thread |
| **Forward Email**       | Forwards an email to another recipient          |

### Attachment processing

The **Get Email** and **Get Thread Messages** actions can extract text from email attachments inline. Enable **Process attachments** in the node configuration, then choose an **Attachment processor**:

| Processor    | Best for                                                                       |
| ------------ | ------------------------------------------------------------------------------ |
| **Standard** | Fast extraction for simple, text-based documents.                              |
| **Advanced** | Higher-accuracy extraction for complex layouts, tables, and scanned documents. |
| **Frontier** | The most capable processor for the hardest documents.                          |

When **Process attachments** is enabled, you must select a processor before the node is valid.

## Subscription management

The **New Email** trigger requires an active subscription to receive events via Microsoft Graph webhooks. Manage subscriptions from the **Subscriptions** tab.

### Advanced subscription settings

When creating or editing an Outlook subscription, expand the **Advanced** section to access:

**Drop quoted history from inbound emails** — When enabled, only the new content from the sender is kept when an inbound email arrives. Quoted prior messages from the thread are removed before the email is processed by your workflow. Enable this to reduce noise in email thread processing when you only need to act on the latest message rather than the full conversation history.

**Preserve rich formatting in conversation history (Beta)** — Controls how prior messages are rendered when a [text agent's](../../06-Text-Agents/04-Email.md) email tool includes conversation history in a reply. With it on, earlier emails keep their original paragraphs, tables, links, and spacing where that formatting is available; plain-text turns keep their text and line spacing. With it off, the existing plain-text renderer is used.

The setting applies to the **mailbox**, not the individual subscription — saving it updates every active subscription on the same mailbox so the thread renders consistently. Existing subscriptions stay opted out until you explicitly turn it on and save.

<Warning>
  Long threads produce larger outbound emails, which can increase usage costs. When the original rich formatting isn't available, the text and spacing are preserved in safe HTML so the reply still sends. Behavior and billing may change while the setting is in beta.
</Warning>

<Note>
  This changes only how existing conversation history is rendered. It does not add history to replies — that's the **Include conversation history** argument on the [Reply to email tool](../../06-Text-Agents/04-Email.md#email-built-in-tools).
</Note>

<Tip>
  Outlook supports environment-specific configuration — use different credentials for development and production to avoid processing test emails in live workflows.
</Tip>

## Example use case

A new email arrives in a shared support mailbox. The workflow uses **AI Classify** to categorize the request, looks up the customer in Snowflake, and sends a **Send Reply** with a personalized response — escalating to a human via Slack if the classification confidence is low.

## Related

<CardGroup cols={2}>
  <Card title="Gmail" icon="envelope" href="01-Gmail.md">
    Google Gmail email integration.
  </Card>

  <Card title="Credentials" icon="key" href="../02-Credentials.md">
    Learn about credential types and management.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/outlook
