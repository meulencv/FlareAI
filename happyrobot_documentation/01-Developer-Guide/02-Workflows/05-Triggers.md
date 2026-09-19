---
title: "Triggers"
description: "How to configure workflow triggers"
---

# Triggers

> How to configure workflow triggers

Triggers start workflows. Every workflow begins with exactly one trigger node that defines what event kicks off execution. When that event occurs, HappyRobot creates a new run and begins processing nodes.

## Webhook (API)

Starts a workflow when an HTTP request hits the endpoint. This is the most flexible trigger — any system that can make an HTTP call can start your workflow.

**Configuration:**

* **Endpoint URL** — Auto-generated from your workflow slug: `https://platform.happyrobot.ai/hooks/{slug}`
* **Authentication** — API key or Bearer token (configured in **Settings > API Keys**)

<CodeGroup>
  ```bash cURL theme={null}
  curl -X POST https://platform.happyrobot.ai/hooks/order-status \
    -H "Content-Type: application/json" \
    -H "Authorization: Bearer hr_live_abc123def456" \
    -d '{
      "phone_number": "+15551234567",
      "customer_name": "Maria Garcia",
      "order_id": "ORD-2024-8842"
    }'
  ```

  ```python Python theme={null}
  import requests

  response = requests.post(
      "https://platform.happyrobot.ai/hooks/order-status",
      headers={
          "Content-Type": "application/json",
          "Authorization": "Bearer hr_live_abc123def456",
      },
      json={
          "phone_number": "+15551234567",
          "customer_name": "Maria Garcia",
          "order_id": "ORD-2024-8842",
      },
  )

  print(response.json())
  ```

  ```javascript Node.js theme={null}
  const response = await fetch(
    "https://platform.happyrobot.ai/hooks/order-status",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: "Bearer hr_live_abc123def456",
      },
      body: JSON.stringify({
        phone_number: "+15551234567",
        customer_name: "Maria Garcia",
        order_id: "ORD-2024-8842",
      }),
    }
  );

  const data = await response.json();
  console.log(data);
  ```
</CodeGroup>

<Tip>
  All JSON body fields are automatically available as variables in your workflow. In the UI, type `@` to reference them. In API configurations, use `{"{{field_name}}"}` syntax.
</Tip>

## Predefined request

A webhook trigger with a predefined request schema. Use this when you want to enforce a specific payload structure for incoming requests.

**Configuration:**

* **Request schema** — Define the expected fields, types, and validation rules
* **Authentication** — Same options as the standard webhook trigger

This is useful when multiple systems send data to the same workflow and you want to validate the payload structure upfront.

## Inbound phone call

Starts a workflow when a call arrives on an assigned phone number. The caller is connected to the workflow immediately — typically routed to a voice agent prompt node.

**Configuration:**

* **Phone number** — Assign a number from your organization's telephony settings (configured per environment)

The trigger automatically provides variables like `caller_number`, `called_number`, and any SIP headers from the call.

<Info>
  Phone number assignments are environment-specific. You can assign different numbers for development, staging, and production so test calls don't interfere with live traffic.
</Info>

## Web call

Starts a workflow when a visitor opens a browser-based call link and starts talking to your voice agent — no phone number required. The workflow must also contain an **Inbound Voice Agent** node, which handles the conversation once the call connects.

**Configuration:**

* **Webcall URL** — A static, shareable link to the live deployment, shown in the trigger node's **Webcall access** section. Each environment has its own URL:

  | Environment | URL                                                                      |
  | ----------- | ------------------------------------------------------------------------ |
  | Production  | `https://platform.happyrobot.ai/deployments/{workflow_slug}`             |
  | Staging     | `https://platform.happyrobot.ai/deployments/staging/{workflow_slug}`     |
  | Development | `https://platform.happyrobot.ai/deployments/development/{workflow_slug}` |

  Each URL always points to the currently published version in that environment, so the link stays the same as you publish new versions.
* **Enhanced security** — When enabled, visitors must sign in to a HappyRobot account with access to your organization before the call link opens. Configure it per environment. It is on by default.

Open the URL to load a call page showing your organization's branding and a button to start talking to the agent.

<Info>
  The enhanced security setting is configured separately for each environment, so you can lock down production while leaving development open for testing.
</Info>

<Warning>
  A web call arrives in the browser, on no phone number of its own. Any node that dials out on its behalf — a **Transfer** node's representative leg or a [Forward call](../05-Voice-Agents/07-Forward-call.md) node — therefore needs a **From number** of its own, and the editor warns on those nodes until you pick one. For the same reason, a web call cannot use a **direct transfer** (which hands over the caller's own phone leg) or the caller-ID pass-through options. See [Choosing the number to dial out from](../05-Voice-Agents/07-Forward-call.md#choosing-the-number-to-dial-out-from).
</Warning>

## Genesys Audio Connector

Starts a workflow from a call streamed out of Genesys Cloud over a WebSocket. Like the web call trigger, the workflow must also contain an **Inbound Voice Agent** node to handle the conversation. Use this to route Genesys Cloud calls to a HappyRobot voice agent without a separate phone number or SIP trunk.

**Configuration:**

* **Genesys credential** — Select the Genesys credential (API key + client secret) you created in **Settings > Integrations**.
* **Connection URL** — A read-only `wss://…/api/v1/audiohook/ws` URL. Set it as the **Audio Connector URI** in your Genesys Architect flow.
* **Connector IDs** — One read-only ID per environment (production, staging, development). Add the ID for the environment the flow should reach in the Genesys Audio Connector action under **Session Variables – Inputs** as an input variable named `node_id`, or as the action's **Connector ID**. The values stay stable when you republish the workflow, and each one pins the call to that environment, so a staging and a production Architect flow can both be live at once. `customConfig` does not apply to the Audio Connector, so a value passed that way never arrives.
* **Input variables** — Optional list of the Genesys `inputVariables` names this flow sends on the session. Names only; generate the trigger's output schema to reference them. The caller's number, the called number, language, and the Genesys conversation identifiers come through on their own.

See the [Genesys Audio Connector integration](../15-Integrations/04-Communication/05-Genesys-Audio-Connector.md) for the full setup guide, including the Genesys Architect steps.

## Email

Starts a workflow when an email is received on a connected email account. Supports Gmail, Outlook, and HappyRobot Email.

**Configuration:**

* **Email account** — Connect a Gmail, Outlook, or HappyRobot Email account in **Settings > Integrations**
* **Filtering rules** — Optional filters to only trigger on emails matching specific criteria

The trigger provides variables including `sender`, `subject`, `body`, and `attachments`.

<Info>
  Gmail and Outlook triggers require environment-specific OAuth credentials. Configure separate accounts for staging and production in **Settings > Integrations**.
</Info>

**Choosing the environment used for testing**

Because the Gmail and Outlook triggers are configured per environment, you have to say which environment's credentials and settings a test run should use. Open the environment tab you want and click **Use for testing** — the tab you pick shows a **Selected for testing** badge, and picking a different tab moves the selection. The trigger is reported as incomplete until one environment is selected.

## Inbound text

Starts a workflow when an inbound message arrives for a connected [Inbound Text Agent](../06-Text-Agents/01-Text-Agents-Overview.md) — SMS, WhatsApp, email, chatbot, Slack, or Teams. The trigger itself needs no configuration; the channel comes from the agent node connected downstream.

Its output schema is channel-specific, so the variables it exposes depend on which channel the connected agent is set to — and, for email, on the email provider, since Outlook and Gmail carry threading, attachment-processing, and artifact fields that Postmark and SendGrid don't.

**Generating the output schema**

Before you've picked a channel on the connected agent, the trigger's testing panel shows only the common fields and notes that channel-specific fields — `to_email`, `from_email`, thread data, artifacts, and so on — appear once a channel is selected. Choose the channel, then regenerate the output schema.

If you later change the connected agent's channel or email provider, the trigger node shows a warning glyph on the canvas reading *Connected agent changed to …* — regenerate the output schema so the available variables match the new channel.

## SMS

Starts a workflow when a text message arrives on a connected phone number via Twilio SMS.

**Configuration:**

* **Phone number** — The number receiving messages
* **Integration** — Connect your Twilio account in **Settings > Integrations**

The trigger provides `sender_number`, `message_body`, and `media_urls` (for MMS media).

## Slack

Starts a workflow when a message is received in a connected Slack channel or when the bot is mentioned.

**Configuration:**

* **Event type** — New channel message or new mention
* **Channel** — Select which channel(s) to monitor
* **Bot setup** — Connect your Slack bot in **Settings > Integrations**

The trigger provides `channel`, `sender`, `message_text`, and `thread_id`.

## Microsoft Teams

Starts a workflow when a message is received in a connected Teams channel.

**Configuration:**

* **Channel** — Select which channel(s) to monitor
* **Bot setup** — Connect your Teams app in **Settings > Integrations**

The trigger provides `channel`, `sender`, and `message_text`.

## File upload

Starts a workflow when a file is uploaded through the platform or via API.

**Configuration:**

* **Accepted file types** — Optionally restrict which file types trigger the workflow

The trigger provides the uploaded file as a variable, along with file metadata like name, size, and type.

## API file upload

Starts a workflow when a file is posted to a generated endpoint via `multipart/form-data`. Use this when an external system needs to deliver a file (and optional metadata) to your workflow over HTTP. Each environment (development, staging, production) gets its own unique URL.

**Configuration:**

* **Endpoint URL** — Auto-generated URL for the workflow. Available per environment (production, staging, development). Shown in the trigger node's configure panel.
* **Authentication** — API key authentication (same options as the Webhook trigger). Enhanced security (OAuth2/HMAC) is also supported.
* **Extra fields** — Any additional form fields beyond `file` are passed as workflow variables automatically.

**Sending a file:**

Send a `multipart/form-data` POST request with a `file` field. Any additional form fields are automatically available as workflow variables.

<CodeGroup>
  ```bash cURL theme={null}
  curl -X POST <endpoint-url> \
    -H "x-api-key: <your-api-key>" \
    -F "file=@document.pdf" \
    -F "customer_id=abc-123" \
    -F "order_id=ORD-2024-8842"
  ```
</CodeGroup>

You can also deliver the same multipart request to the bearer-authenticated Public API endpoint at `POST /workflows/{workflow_id}/runs` — see [Triggering with a file upload](https://docs.happyrobot.ai/api-reference/overview#triggering-with-a-file-upload) for the cURL example and SDK helper.

The uploaded file and any extra form fields are available as variables in downstream nodes. Type `@` in a node field to reference them.

<Tip>
  All form fields sent alongside the file are available as variables in your workflow. The file itself is available as a file variable you can pass to subsequent nodes.
</Tip>

<Info>
  API file upload does not support retries. If the endpoint returns an error, the client is responsible for retrying the request.
</Info>

<Info>
  The API file upload trigger uses the same enhanced security options as the Webhook trigger. Configure an API key or OAuth2 credential in the trigger node to require authentication.
</Info>

## Schedule

Runs the workflow on a recurring schedule. Useful for periodic data syncs, scheduled reports, or recurring outbound campaigns. Two scheduling modes are available:

### Interval-based

Choose a fixed polling interval. The workflow runs repeatedly at this frequency.

**Available intervals:** 1 minute, 2 minutes, 3 minutes, 4 minutes, 5 minutes, 15 minutes, 30 minutes, 1 hour, 6 hours, 12 hours.

### Cron expression

Define a custom schedule using a cron expression for more precise control.

**Configuration:**

* **Cron expression** — Standard cron syntax (e.g., `0 9 * * 1-5` for weekdays at 9 AM)
* **Timezone** — Select from all available timezones

The editor validates your cron expression in real time and shows the next 10 scheduled run times so you can verify the schedule is correct.

To test a cron schedule without waiting for the next scheduled time, open the workflow's preview and click **Trigger Workflow** in the manual trigger dialog. This fires the workflow immediately so you can confirm the schedule and logic work as expected. The workflow must be live to run a preview execution. See [The manual trigger dialog](#the-manual-trigger-dialog).

<Info>
  Execution timeout per scheduled run is 7 days. If a run exceeds this limit, it will be canceled.
</Info>

## Common trigger settings

These settings apply across trigger types that support them:

* **Multi-event behavior** — How the workflow handles multiple simultaneous triggers: `parallel` (run all concurrently), `sequential` (queue and run one at a time), or `group` (batch events together). Default is `parallel`.
* **Trigger interval** — Minimum polling interval for non-instant triggers
* **Hidden fields** — Fields that are passed to the workflow but not shown in the platform UI

## Testing triggers

Each trigger type has a different testing approach:

* **Webhook** — Send a test POST request using cURL or any HTTP client, or use the manual trigger dialog below
* **Phone calls** — Make a test call to the assigned number. To exercise logic that branches on carrier SIP headers without placing a real call, use **Test call with SIP headers** from the chevron menu next to the play button — see [Testing with mock SIP headers](../05-Voice-Agents/02-Inbound-Calls.md#testing-with-mock-sip-headers)
* **Email / SMS** — Send a test message to the connected account
* **Schedule** — Click **Trigger Workflow** in the trigger's preview to run the workflow immediately without waiting for the next interval or cron time. Works for both interval-based and cron schedules; the version must be live

### The manual trigger dialog

Open a live version's preview and click the trigger to fire a run by hand. For webhook, predefined request, incoming hook, and workflow function triggers, the dialog offers two ways to supply the payload:

| Tab         | Use for                                                                                                                                                                 |
| ----------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Builder** | One input per field in the trigger's schema. The quickest way to fill in a few known values.                                                                            |
| **JSON**    | The whole payload as JSON, in a code editor with syntax highlighting and a **Format** button. Use it for nested objects, arrays, or to paste a real payload from a log. |

The two tabs stay in sync: switching to **JSON** renders whatever you typed in the builder as JSON, and switching back reads your JSON into the builder's fields. Invalid JSON is reported inline under the editor, and while it's invalid you can neither switch back to **Builder** nor trigger the run — fix the error first.

<Tip>
  The JSON tab is the easiest way to reproduce a failing run: copy the payload out of the original run's trigger node, paste it in, and trigger.
</Tip>

---

Fuente original: https://docs.happyrobot.ai/workflows/triggers
