---
title: "Gmail"
description: "Send and receive emails with Gmail"
---

# Gmail

> Send and receive emails with Gmail

The Gmail integration lets your workflows send emails, receive inbound emails as triggers, read threads, forward messages, and parse attachments — all through Google's Gmail API.

## Authentication

Gmail supports two credential types:

| Credential type     | Best for                                   | Flow                                    |
| ------------------- | ------------------------------------------ | --------------------------------------- |
| **User Mailbox**    | Individual Gmail accounts                  | OAuth — redirects to Google sign-in     |
| **Service Account** | Organizational accounts (Google Workspace) | Form — paste a JSON service account key |

### User Mailbox (OAuth)

<Steps>
  <Step title="Enable the Gmail integration">
    Go to **Settings > Integrations** and enable **Gmail**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and select **User Mailbox**. You'll be redirected to Google's sign-in page.
  </Step>

  <Step title="Grant permissions">
    Sign in with the Google account you want to use and approve the requested permissions (compose, modify, and read email).
  </Step>

  <Step title="Verify the connection">
    After redirecting back, the credential will appear as **Active** in the credentials list.
  </Step>
</Steps>

### Service Account

<Steps>
  <Step title="Create a service account in Google Cloud">
    In the Google Cloud Console, create a service account with domain-wide delegation enabled and Gmail API access.
  </Step>

  <Step title="Add the credential in HappyRobot">
    Click **Add Credential**, select **Service Account**, and fill in:

    * **Service Account Key** — paste the full JSON key file contents
    * **Target Email** — the email address the service account will impersonate
    * **Target Mailbox Name** — a display name for this mailbox
  </Step>

  <Step title="Test the connection">
    Click **Test** to verify the service account can access the target mailbox.
  </Step>
</Steps>

## Available events

### Triggers

| Event         | Description                                                                               |
| ------------- | ----------------------------------------------------------------------------------------- |
| **New Email** | Fires when a new email arrives in the connected mailbox. Requires an active subscription. |

### Actions

| Event                   | Description                                       |
| ----------------------- | ------------------------------------------------- |
| **Send Email**          | Sends a new email from the connected account      |
| **Send Reply**          | Sends a reply to an existing email thread         |
| **Get Thread Messages** | Retrieves all messages in an email thread         |
| **Get Message**         | Retrieves a single email message by ID            |
| **Forward Email**       | Forwards an email to another recipient            |
| **Modify email**        | Marks a message as read or unread, or archives it |
| **Parse Attachment**    | Extracts and processes email attachments          |

#### Modify email

The **Modify email** action changes a message's state in the connected mailbox without sending anything.

| Field          | Required | Description                                                                                                                                                   |
| -------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Message id** | Yes      | The Gmail message ID to act on. Supports [variables](../../02-Workflows/07-Variables.md) — usually the ID from a **New Email** trigger or a **Get Thread Messages** action. |
| **Operation**  | Yes      | **Mark as read**, **Mark as unread**, or **Archive**. Defaults to **Mark as read**.                                                                           |

<Tip>
  Use **Archive** at the end of a workflow triggered by **New Email** so handled messages leave the inbox. If your subscription watches the **UNREAD** label, **Mark as read** has the same effect without moving the message.
</Tip>

### Attachment processing

The **Get Message** and **Get Thread Messages** actions can extract text from email attachments inline, so you don't need a separate **Parse Attachment** node. Enable **Process attachments** in the node configuration, then choose an **Attachment processor**:

| Processor    | Best for                                                                       |
| ------------ | ------------------------------------------------------------------------------ |
| **Standard** | Fast extraction for simple, text-based documents.                              |
| **Advanced** | Higher-accuracy extraction for complex layouts, tables, and scanned documents. |
| **Frontier** | The most capable processor for the hardest documents.                          |

When **Process attachments** is enabled, you must select a processor before the node is valid.

## Subscription management

The **New Email** trigger requires an active subscription to receive events. Manage subscriptions from the **Subscriptions** tab on the Gmail integration settings page.

<Note>
  The **STARRED** and **IMPORTANT** labels are not available in the watch label picker. Use **INBOX** or **UNREAD** to monitor incoming email reliably.
</Note>

### Advanced subscription settings

When creating or editing a Gmail subscription, expand the **Advanced** section to access:

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
  Gmail supports environment-specific configuration — you can use different credentials for your development and production environments.
</Tip>

## Example use case

An inbound email triggers a workflow that uses **AI Extract** to pull shipment details from the email body, queries your TMS for matching loads using **McLeod Find Load by Reference**, and sends a formatted **Send Reply** confirming the status back to the sender.

## Related

<CardGroup cols={2}>
  <Card title="Credentials" icon="key" href="../02-Credentials.md">
    Learn about credential types and management.
  </Card>

  <Card title="Outlook" icon="envelope" href="02-Outlook.md">
    Microsoft Outlook email integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/gmail
