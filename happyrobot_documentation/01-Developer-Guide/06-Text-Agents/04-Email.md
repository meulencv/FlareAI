---
title: "Email"
description: "Deploy text agents for email conversations"
---

# Email

> Deploy text agents for email conversations

Email text agents handle conversations over Gmail, Outlook, and direct providers like SendGrid and Postmark. The agent reads incoming emails with full thread context, generates responses using the LLM, and replies within the same thread. For outbound workflows, the agent composes and sends the first email, then manages the back-and-forth. With Gmail and Outlook you pick a sending strategy (same mailbox, transactional, or pooled); with a **direct provider** (SendGrid, Postmark) the provider handles both receiving and sending on your own domain.

## Setting up an inbound email agent

<Steps>
  <Step title="Add an inbound trigger">
    Every inbound email workflow starts with an **Inbound Text** trigger node. Select this trigger in the workflow editor — it listens for incoming emails on a connected mailbox.
  </Step>

  <Step title="Add an inbound text agent node">
    Add an **Inbound Text Agent** action node and select **Email** as the channel.
  </Step>

  <Step title="Configure the email provider">
    Select your email provider — **Gmail**, **Outlook**, or a direct provider (**SendGrid**, **Postmark**) — then choose your credential. See [Email provider](#email-provider) for credential types, and [Direct email providers](#direct-email-providers-sendgrid-postmark) for the SendGrid/Postmark inbound (MX + Inbound Parse) setup.
  </Step>

  <Step title="Choose a sending strategy">
    For **Gmail** and **Outlook**, select how the agent sends replies: **Direct** (same mailbox), **Transactional** (via SendGrid or ACS), or **Pooled** (coming soon) — see [Sending strategy](#sending-strategy). Direct providers (SendGrid, Postmark) always send through themselves, so there's no separate strategy to pick.
  </Step>

  <Step title="Configure email filters (optional)">
    Set up filters to block or allow emails based on sender, subject, or body content. This prevents the agent from responding to newsletters, automated notifications, or other unwanted emails.
  </Step>

  <Step title="Configure and publish">
    Set the agent name, prompt, and conversation settings. Publish your workflow and send a test email to the connected mailbox.
  </Step>
</Steps>

## Setting up an outbound email agent

<Steps>
  <Step title="Create a workflow with a trigger">
    Outbound email workflows are started by a **Webhook** trigger or **API** call. The trigger payload provides the recipient email address(es) and any data the agent needs.
  </Step>

  <Step title="Add an outbound text agent node">
    Add an **Outbound Text Agent** action node and select **Email** as the channel.
  </Step>

  <Step title="Configure the email provider and sending strategy">
    Select your email provider (Gmail or Outlook), credential, and sending strategy — the same setup as inbound.
  </Step>

  <Step title="Set email recipients">
    Configure the recipients using **static** mode (To, CC, BCC fields) or **dynamic** mode (JSON variable). See [Email recipients](#email-recipients-outbound-only) for details.
  </Step>

  <Step title="Compose the initial email">
    Set the email subject and body for the first outbound message. The body can be plain text or HTML. Both fields support [variables](../02-Workflows/07-Variables.md).
  </Step>

  <Step title="Configure and publish">
    Set the agent name, prompt, and conversation settings. Add downstream nodes, then publish and trigger the workflow to test.
  </Step>
</Steps>

## Configuration reference

### Email provider

Select the email service that hosts the mailbox. Each provider supports specific credential types:

| Provider              | Credential types              | Receives inbound via                      |
| --------------------- | ----------------------------- | ----------------------------------------- |
| **Gmail**             | User OAuth, Service Account   | Mailbox subscription                      |
| **Outlook**           | User OAuth, Service Principal | Mailbox subscription                      |
| **SendGrid** (direct) | API key                       | Inbound Parse webhook (MX on a subdomain) |
| **Postmark** (direct) | API key                       | Inbound webhook (hosted inbound address)  |

Configure your credentials in [Credentials](../15-Integrations/02-Credentials.md) using the [Gmail](../15-Integrations/04-Communication/01-Gmail.md) or [Outlook](../15-Integrations/04-Communication/02-Outlook.md) integration. The credential type determines the authentication method — User OAuth authenticates as a specific user, while Service Account (Gmail) and Service Principal (Outlook) authenticate as an application with delegated access.

**SendGrid** and **Postmark** are *direct providers* — they authenticate with an API key (configured via the [SendGrid](../15-Integrations/04-Communication/09-SendGrid.md) integration) and handle both receiving and sending on your own domain, with no separate mailbox to connect. See [Direct email providers](#direct-email-providers-sendgrid-postmark) for their inbound setup and the apex-address routing model.

### Sending strategy

The sending strategy controls how outbound emails (replies and initial messages) are sent. This is separate from the inbound credential that receives emails.

**Direct** — Send replies from the same mailbox that receives emails. Requires an outbound credential for the same provider. This is the simplest setup — replies come from the same address, which looks natural to recipients.

**Transactional** — Send replies through an external transactional email service. The inbound mailbox still receives emails, but outgoing messages are routed through a dedicated sending service. This is useful for high-volume scenarios or when you need better deliverability tracking.

| Setting             | Description                                                                                                                                 |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Sending service** | **SendGrid** or **ACS** (Azure Communication Services).                                                                                     |
| **Credential**      | The credential for the sending service, configured in [Credentials](../15-Integrations/02-Credentials.md).                                             |
| **From email**      | The sender email address displayed to recipients.                                                                                           |
| **Display name**    | Optional name shown alongside the from email. Supports [variables](../02-Workflows/07-Variables.md) — see [Sender display name](#sender-display-name). |

**Pooled** — Distribute outbound emails across a pool of mailboxes. This option is coming soon.

### Sender display name

Every email sender configuration — both direct strategies, all three transactional sending services, and the Gmail/Outlook direct path — has a **Display name** field for the name recipients see in the `From` header, next to the address.

The field accepts [variables](../02-Workflows/07-Variables.md), so one workflow can send under a different sender identity per run — for example `Dispatch at {{ibo.brand_name}}` for a per-tenant brand. Leave it empty to use the mailbox default.

<Note>
  SendGrid and Postmark show the sender identity fields on inbound and outbound agents alike, and require them only for outbound.
</Note>

### Direct email providers (SendGrid, Postmark)

Selecting **SendGrid** or **Postmark** as the provider makes it a *direct provider*: the same provider both receives inbound mail and sends outbound, so there's no Gmail/Outlook mailbox to connect and no separate sending strategy to choose. Pick the API-key credential from the [SendGrid](../15-Integrations/04-Communication/09-SendGrid.md) integration.

#### Inbound (receiving mail)

The provider delivers incoming mail to a webhook. When you select the credential, the agent config shows a generated **Inbound Webhook URL**. For SendGrid, route mail to it:

<Steps>
  <Step title="Add an MX record on a subdomain">
    Point a dedicated subdomain — e.g. `parse.yourcompany.com` — at SendGrid with an `MX` record: `parse.yourcompany.com` → `mx.sendgrid.net`. MX is per-hostname, so this affects **only that subdomain** — your apex mailboxes (`@yourcompany.com`) keep their existing mail provider and are untouched.
  </Step>

  <Step title="Create a SendGrid Inbound Parse setting">
    In SendGrid, add an **Inbound Parse** setting for that subdomain that POSTs to the **Inbound Webhook URL** shown in the agent config. SendGrid will POST every message it receives at the subdomain to that URL.
  </Step>
</Steps>

<Note>
  Postmark differs: it provides a hosted inbound address, so it needs no MX record or Inbound Parse setting. SendGrid has no hosted inbound address, so a subdomain MX'd to `mx.sendgrid.net` is always the inbound sink.
</Note>

#### Sender identity (the From)

Set the **From** address recipients see. It can be a branded apex address like `support@yourcompany.com` — the domain must be authenticated in SendGrid (DKIM/SPF) or match a verified single sender. The From does **not** need to be on the parse subdomain.

#### Reply-To (routing replies back to the agent)

Because the From can be your apex domain — whose mail SendGrid never receives — set a **Reply-To** on the parse subdomain, e.g. `support@parse.yourcompany.com`. The agent rewrites it per conversation to a plus-addressed variant (`support+{session}@parse.yourcompany.com`) and sets it as the Reply-To, so recipient replies route to the Inbound Webhook while the visible From stays your apex address. Threading is preserved by the message ID regardless of the From/Reply-To split, and the plus-address adds a routing signal that survives clients stripping threading headers.

#### Receiving mail at your apex address (inbound-initiated agents)

The Reply-To covers replies, but the **first** email a customer sends goes to whatever address they type. If you publish an apex address like `support@yourcompany.com`, that message lands on your normal provider's MX (Google Workspace / Microsoft 365) — not SendGrid — so the agent never sees it. Two setups keep the apex identity working:

* **Forward the one address (keeps the apex identity).** Keep `support@yourcompany.com` at your mail provider and add a routing/forwarding rule that forwards **only that address** to `support@parse.yourcompany.com` (the SendGrid subdomain). Only that address is diverted — every other apex mailbox is untouched. Forwarding preserves the original sender and `Message-ID`/`In-Reply-To`/`References` headers, and the agent routes by the webhook's secret (not by the address it arrived at), so it sees the real sender and threads correctly. The rule is only exercised for the **opening** message — once the agent replies, its subdomain Reply-To keeps the rest of the thread on SendGrid directly.
* **Publish the subdomain address.** Have customers email `support@parse.yourcompany.com` (or a cleaner subdomain like `mail.yourcompany.com`) directly. No forwarding rule, but the public address isn't the bare apex.

<Warning>
  MX can't be split within a domain, and SendGrid only receives mail on a (sub)domain that's MX'd to it. So an apex-addressed **inbound** agent always needs either the forwarding rule or a published subdomain address — there is no DNS-only way to send just some apex mail to SendGrid without routing all of it.
</Warning>

### Email filters (inbound only)

Email filters let you control which incoming emails the agent processes. Filters are built as a tree of conditions grouped with AND/OR logic.

| Setting        | Description                                                                                                              |
| -------------- | ------------------------------------------------------------------------------------------------------------------------ |
| **Action**     | **Block** — emails matching the filter are ignored. **Allow** — only emails matching the filter are processed.           |
| **Conditions** | Each condition has a field, operator, and value. Combine conditions with AND/OR logic and nest groups for complex rules. |

Available filter fields:

| Field           | Description                                                  |
| --------------- | ------------------------------------------------------------ |
| `sender_email`  | The sender's full email address.                             |
| `sender_domain` | The domain portion of the sender's email (e.g., `acme.com`). |
| `subject`       | The email subject line.                                      |
| `body`          | The email body content.                                      |

Available operators:

| Operator                    | Description                                            |
| --------------------------- | ------------------------------------------------------ |
| `equals` / `not_equals`     | Exact string match.                                    |
| `contains` / `not_contains` | Substring match.                                       |
| `starts_with` / `ends_with` | Prefix or suffix match.                                |
| `matches_regex`             | Regular expression match.                              |
| `is_empty` / `not_empty`    | Check whether the field has content (no value needed). |

<Tip>
  Use a **Block** filter with `sender_domain contains "noreply"` and `sender_domain contains "mailer-daemon"` to ignore automated emails. Or use an **Allow** filter with specific sender domains to restrict the agent to emails from known partners.
</Tip>

### Email recipients (outbound only)

Outbound email agents need to know who to send the initial email to. Two modes are available:

**Static mode** — Set recipients directly in the configuration:

| Field   | Description                                                                               |
| ------- | ----------------------------------------------------------------------------------------- |
| **To**  | Primary recipients. At least one is required. Supports [variables](../02-Workflows/07-Variables.md). |
| **CC**  | Carbon copy recipients. Optional.                                                         |
| **BCC** | Blind carbon copy recipients. Optional.                                                   |

**Dynamic mode** — Provide recipients as a JSON variable. Set the **Recipients JSON** field to a variable that resolves to a JSON object with `to`, `cc`, and `bcc` arrays at runtime. This is useful when the recipient list comes from an upstream node or external API.

### Initial email content (outbound only)

The first email sent by an outbound agent uses a configured subject and body — the LLM doesn't generate the initial message.

| Setting         | Description                                                                                                                                                                                                                                                                                         |
| --------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Subject**     | The email subject line. Supports [variables](../02-Workflows/07-Variables.md).                                                                                                                                                                                                                                 |
| **Body**        | The email body content.                                                                                                                                                                                                                                                                             |
| **Body type**   | **Plain** — plain text body. **HTML** — HTML-formatted body.                                                                                                                                                                                                                                        |
| **Attachments** | Optional. One or more public URLs separated by commas (or one per line). Each URL is fetched server-side and attached to the initial email. Supports [variables](../02-Workflows/07-Variables.md) — useful for sending per-recipient documents like contracts or invoices. Each attachment is capped at 25 MB. |

After the initial email is sent, subsequent replies in the thread are generated by the LLM based on the prompt and conversation history.

### Attachment limits and processing

Email attachments pass through two separate stages:

1. **Capture** — HappyRobot downloads and stores the raw file from the email provider. A captured file remains available in the run even when automatic media processing is disabled.
2. **Processing** — HappyRobot optionally extracts text from a document or transcribes audio so the agent can use the contents. Configure this in the prompt node's **Built-in** tab under **Automatically process media**.

An attachment must be captured before the media-processing settings apply. A provider or capture failure cannot be fixed by raising the agent's processing limits.

<Note>
  The limits below use binary megabytes: 1 MB is 1,048,576 bytes.
</Note>

#### Inbound attachments

Inbound capture behavior depends on the receiving provider:

| Provider              | Raw attachment behavior                                                                                                                   | HappyRobot capture limits                                                                                                                                                                     |
| --------------------- | ----------------------------------------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Gmail**             | Files are downloaded from Gmail and stored as run artifacts.                                                                              | Up to 50 attachments per email, 25 MB per attachment, and 100 MB across all attachments in the email. Files beyond a limit are reported as capture failures and are not stored.               |
| **Outlook**           | Files are downloaded from Microsoft Graph and stored as run artifacts.                                                                    | No additional HappyRobot file-count, per-file-size, or total-size cap. Downloading and storage have a 70-second attachment-processing budget; Microsoft mailbox and Graph limits still apply. |
| **SendGrid** (direct) | The inbound event reports that the email had attachments, but attachment files are not currently exposed as run artifacts or agent input. | The complete Inbound Parse request, including files, is capped at 30 MB.                                                                                                                      |
| **Postmark** (direct) | The inbound event reports that the email had attachments, but attachment files are not currently exposed as run artifacts or agent input. | No additional HappyRobot attachment cap is configured; Postmark's inbound webhook limits apply.                                                                                               |

For Gmail and Outlook, inline images such as signature logos are stored for the email preview but hidden from the downloadable attachment list. Other captured files remain visible in the run whether processing completes, fails, exceeds a processing limit, or is disabled.

<Warning>
  Disabling document processing or audio transcription does not reject Gmail or Outlook attachments. It prevents content extraction only. The raw captured file, filename, media type, and size remain available to the run and agent. This does not apply to direct SendGrid and Postmark inbound attachments, which are not currently exposed as artifacts.
</Warning>

#### Automatic processing limits

The processing budget is shared by document and audio attachments in one agent turn. Existing agents without saved limit settings use the defaults below.

| Setting                     | Default     | Builder range  | Behavior when exceeded                                                                                                               |
| --------------------------- | ----------- | -------------- | ------------------------------------------------------------------------------------------------------------------------------------ |
| **Max files per turn**      | 25          | 1–25           | Remaining captured files are marked limited and are not processed in that turn.                                                      |
| **Max size per file**       | 50 MB       | 1–50 MB        | The captured file is marked limited and is not processed.                                                                            |
| **Max total size per turn** | 100 MB      | 1–100 MB       | Once processing the next file would cross the total, that file and subsequent over-budget files are not processed in that turn.      |
| **Processing timeout**      | 240 seconds | 10–480 seconds | Processing that does not finish in time is marked failed. The timeout is shortened when the parent workflow has less time remaining. |
| **Max attempts**            | 2           | 1–5            | Caps total attempts to start processing, including the first attempt.                                                                |

The maximum size per file cannot be greater than the maximum total size per turn. Open **Advanced limits** under **Automatically process media** to change the file, size, [processing timeout, and attempt controls](01-Text-Agents-Overview.md#media-processing-limits).

These limits control extraction, not capture. For example, Gmail can capture 50 valid attachments, while an agent using the default processing settings processes at most 25 of them in the first turn. Files limited by the per-turn count or total-size budget can be processed in a later turn. A file over the per-file limit remains limited until you increase the setting within the allowed range.

#### Supported processing types

HappyRobot routes these captured file types for automatic processing:

| Capability              | File types                                                                                                                                                                                       |
| ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Document processing** | PDF; Word (`.doc`, `.docx`); Excel (`.xls`, `.xlsx`); PowerPoint (`.ppt`, `.pptx`); plain text (`.txt`); Markdown (`.md`); JSON; CSV; and images, including JPEG, PNG, GIF, WebP, TIFF, and BMP. |
| **Audio transcription** | OGG, MP3, M4A/MP4 audio, WAV, WebM audio, FLAC, AAC, and AMR.                                                                                                                                    |

Video files are not currently transcribed. A file with another type can still be captured and shown, but automatic processing fails as unsupported. The **Frontier** document profile accepts PDF and image inputs only; use **Standard** or **Advanced** for the other document types.

JPEG, PNG, GIF, and WebP images are supplied to the model through vision and do not require OCR text extraction. Document processing applies to other images and document files.

#### Processing outcomes

| Outcome        | What happens                                                                               | What the agent receives                                                                                                                                                                 |
| -------------- | ------------------------------------------------------------------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Completed**  | Extraction or transcription succeeded.                                                     | The filename and metadata plus extracted content. Supported vision images are supplied as images.                                                                                       |
| **Processing** | A requested operation is still running.                                                    | File metadata and a notice that content will be supplied automatically when ready.                                                                                                      |
| **Skipped**    | Document processing or audio transcription is disabled for that file type.                 | File metadata and a general notice that one or more received attachments were not processed. No extracted content.                                                                      |
| **Limited**    | A file exceeded the configured file-count, per-file-size, or total-size processing budget. | File metadata and a general notice that one or more received attachments were not processed. A `read_media` call returns the specific limit it hit. No extracted content for that turn. |
| **Failed**     | The processor could not start, timed out, rejected the type, or returned an error.         | File metadata and a document- or audio-specific failure notice. A `read_media` call returns the file-specific error and can retry a processable file.                                   |

Capture failures are reported separately in the inbound event's `attachment_processing` output. This output includes the number expected, downloaded, and stored plus affected filenames; Gmail also includes a failed count and per-file failure reasons. The email is still delivered to the agent after attachment work reaches a terminal outcome, so one bad file does not silently discard the message.

#### Outbound attachments

Outbound agents can attach public URLs to the initial email. Email built-in tools can also send captured or generated artifacts and explicitly provided public URLs. These are attached to the outgoing message as files; HappyRobot does not OCR or transcribe them as part of sending.

| Provider or sending path                          | Per-file limit | File-count limit               | Total-size limit               |
| ------------------------------------------------- | -------------- | ------------------------------ | ------------------------------ |
| **Gmail**, **SendGrid**, **Postmark**, or **ACS** | 25 MB          | No additional HappyRobot limit | No additional HappyRobot limit |
| **Outlook direct**                                | 3 MB           | No additional HappyRobot limit | No additional HappyRobot limit |

There is no HappyRobot file-type allowlist for outbound email attachments. Each URL must be publicly reachable, and the receiving provider must accept the resulting media type. Provider message-size and attachment rules still apply and can be lower than HappyRobot's URL-download cap; if the provider rejects the message, the send fails.

### Email signature

Add a signature that's appended to every outbound email the agent sends — both the initial email and all replies. Available on inbound and outbound email agents.

| Setting             | Description                                                                                                                                                                                               |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Email signature** | HTML content added to the end of each outbound email. Supports [variables](../02-Workflows/07-Variables.md) via the `@` picker — for example `<p>Best regards,<br>{{agent.name}}</p>`. Leave empty for no signature. |

### Email built-in tools

Email agents get three built-in tools for acting on mail directly. They appear in the prompt node's **Built-in** tab when the agent's provider is Gmail, Outlook, Postmark, or SendGrid:

| Tool               | What it does                                  |
| ------------------ | --------------------------------------------- |
| **Send email**     | Starts a new email thread.                    |
| **Reply to email** | Replies in the current thread.                |
| **Forward email**  | Forwards the current email to new recipients. |

Every argument on these tools defaults to being chosen by the agent from the conversation. Expand a tool and switch an argument to a fixed value when it must not vary:

| Argument                         | Tools          | Description                                                                                        |
| -------------------------------- | -------------- | -------------------------------------------------------------------------------------------------- |
| **To**                           | All three      | Recipients for the email.                                                                          |
| **CC** / **BCC**                 | All three      | Optional copied and hidden recipients.                                                             |
| **Subject**                      | Send email     | Subject for the new thread.                                                                        |
| **Body**                         | All three      | Body of the email. On **Forward email** this is the introductory text above the forwarded message. |
| **Reply to all**                 | Reply to email | Include every original recipient in the reply. Fixed as true or false.                             |
| **Include conversation history** | Reply to email | Include previous messages in the sent reply. Fixed as true or false.                               |

<Note>
  For Gmail and Outlook mailboxes, **Preserve rich formatting in conversation history** controls how those included messages are rendered — keeping the original paragraphs, tables, and links instead of flattening them to plain text. It's a mailbox-level setting under the subscription's **Advanced** section, currently in beta. See [Gmail](../15-Integrations/04-Communication/01-Gmail.md#advanced-subscription-settings) or [Outlook](../15-Integrations/04-Communication/02-Outlook.md#advanced-subscription-settings).
</Note>

Text and recipient values support [variables](../02-Workflows/07-Variables.md), so you can pin a recipient list that comes from upstream data while still letting the agent write the body.

<Warning>
  An argument you switch to a fixed value must actually have a value. Leaving it blank blocks publishing with `Missing custom value for <tool>: <argument>` — either fill it in or hand the argument back to the agent.
</Warning>

### Escalation (email-specific)

In addition to the standard escalation modes described in [common agent settings](01-Text-Agents-Overview.md#escalation), email agents support the **Email in thread** escalation mode. This mode gives the LLM tools to escalate by performing email-specific actions within the conversation thread:

| Action                                   | What it does                                                                                                                                       |
| ---------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| **CC + Reply with Conversation History** | Sends a reply in the thread, adding the escalation target as a CC recipient, with the full conversation history included.                          |
| **Forward Thread**                       | Forwards the entire email thread to the escalation target.                                                                                         |
| **End Conversation After Handoff**       | Ends the AI conversation after performing the handoff, rather than continuing in escalation mode. Must be combined with at least one other action. |

### Email subscription

Email agents require an active subscription to the connected mailbox. The subscription status is shown in the configuration panel. If the subscription becomes invalid (for example, due to a credential refresh or permission change), you'll need to resubscribe before the agent can process new emails.

<Note>
  A given inbound email address can only be assigned to one published inbound agent at a time. If you try to publish a second workflow that monitors the same mailbox, the publish fails with a conflict error — unpublish the other agent first.
</Note>

### Agent settings

Timeout, reminders, escalation, and end conversation settings are shared across all text agent channels. See [common agent settings](01-Text-Agents-Overview.md#common-agent-settings) for the full reference.

## Email message flow

### Inbound flow

1. An email arrives in the connected mailbox.
2. HappyRobot receives the email via the mailbox subscription webhook.
3. The email is checked against configured filters. If blocked, it's ignored.
4. HappyRobot matches the email to a workflow trigger and starts a new run (or resumes an existing session if the sender has an active thread).
5. A text session is created and the email (with thread context) is added to the conversation history.
6. The LLM generates a response and sends it as an email reply in the same thread.
7. The session stays open for follow-up emails until the idle timeout expires or the agent ends the conversation.

### Outbound flow

1. The workflow trigger fires and execution begins.
2. The outbound text agent sends the initial email to the configured recipients using the subject and body you provided.
3. When the recipient replies, the response is routed back to the same session.
4. The LLM generates a reply using the prompt, full thread context, and any tool results.
5. The conversation continues until the idle timeout expires or the agent ends it.
6. When the session closes, the workflow proceeds to downstream nodes.

## Next steps

<CardGroup cols={3}>
  <Card title="SMS" icon="comment-sms" href="02-SMS.md">
    Set up two-way SMS conversations.
  </Card>

  <Card title="Gmail" icon="envelope" href="../15-Integrations/04-Communication/01-Gmail.md">
    Configure your Gmail integration.
  </Card>

  <Card title="Outlook" icon="envelope" href="../15-Integrations/04-Communication/02-Outlook.md">
    Configure your Outlook integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/text-agents/email
