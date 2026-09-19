---
title: "Quickstart"
description: "Build an outbound voice agent workflow and trigger it via API in 15 minutes"
---

# Quickstart

> Build an outbound voice agent workflow and trigger it via API in 15 minutes

In this guide you will build a complete workflow: a webhook trigger starts an outbound voice call, an AI Extract node pulls structured data from the conversation, and you trigger the whole thing via API. By the end, you will have a working pipeline from API request to phone call to extracted data.

<Info>
  **Prerequisites**

  * A HappyRobot account — [contact sales](mailto:sales@happyrobot.ai) if you don't have one yet
  * An API key from [Settings > API Keys](../16-Account-and-Settings/06-API-Keys.md)
  * A phone number assigned to your organization in [Assets > Telephony](../14-Assets/03-Telephony.md)
</Info>

## Create a workflow

<Steps>
  <Step title="Open the platform">
    Go to [platform.happyrobot.ai](https://platform.happyrobot.ai) and navigate to the **Workflows** page.
  </Step>

  <Step title="Create a new workflow">
    Click **New Workflow** and name it "Customer Support". HappyRobot generates a unique slug automatically (e.g., `V1StGXR8_Z5jdHi6B-myT`). The slug is a random identifier — it is not derived from the name. Note this slug; you will use it to trigger the workflow via API.
  </Step>
</Steps>

## Add a webhook trigger

<Steps>
  <Step title="Select the trigger type">
    In the workflow editor, click **Add Trigger** and select **Incoming hook**. This starts the workflow when an HTTP request hits the endpoint.
  </Step>

  <Step title="Note the endpoint URL">
    The trigger configuration panel shows the endpoint URL based on your workflow's auto-generated slug:

    ```
    https://platform.happyrobot.ai/hooks/V1StGXR8_Z5jdHi6B-myT
    ```

    Any JSON fields you send to this endpoint become workflow variables automatically — no schema definition required.
  </Step>
</Steps>

See [Triggers](../02-Workflows/05-Triggers.md) for all trigger types.

## Generate a test record

Downstream nodes need to know what fields the trigger provides so you can reference them in the `@` variable picker. Generating a test record teaches HappyRobot the shape of your data.

<Steps>
  <Step title="Send a test request">
    Send a POST request to your workflow's version-specific test URL. You can find this URL in the trigger configuration panel. Use curl, Postman, or any HTTP client:

    ```bash theme={null}
    curl -X POST https://platform.happyrobot.ai/hooks/V1StGXR8_Z5jdHi6B-myT/VERSION_SLUG \
      -H "Content-Type: application/json" \
      -d '{
        "phone_number": "+15551234567",
        "customer_name": "Maria Garcia",
        "order_id": "ORD-2025-8842",
        "issue_description": "Package arrived damaged"
      }'
    ```

    Replace `VERSION_SLUG` with the version slug shown in the trigger panel (e.g., `draft`). This creates a test record without executing the full workflow.
  </Step>

  <Step title="Verify the output schema">
    The test record populates the node's output schema. These fields — `phone_number`, `customer_name`, `order_id`, `issue_description` — now appear in the `@` variable picker when configuring downstream nodes.
  </Step>
</Steps>

<Info>
  Generating a test record is how HappyRobot learns what data your trigger provides. Every node in the workflow can reference these fields via the `@` variable picker. You should generate test records for each node as you build the workflow.
</Info>

## Add an outbound voice agent

<Steps>
  <Step title="Add the node">
    Click **+** after the trigger and select **Outbound Voice Agent**.
  </Step>

  <Step title="Configure the destination">
    In the voice agent configuration panel, click the **To** field and type `@` to open the variable picker. Select `phone_number` from the trigger's output. This tells the agent to call whatever number was included in the API request.

    Set the **From** number from the dropdown — this is the phone number assigned to your organization in [Assets > Telephony](../14-Assets/03-Telephony.md).
  </Step>

  <Step title="Write the agent prompt">
    In the **Prompt** field, write instructions for the voice agent. Use the `@` variable picker to inject trigger data into the conversation. Here is an example:

    ```
    You are Alex, a customer support representative at Acme Corp.

    You are calling @customer_name regarding their support request
    about order @order_id.

    Issue: @issue_description

    Instructions:
    1. Introduce yourself and reference order @order_id
    2. Explain the resolution or gather more details about the issue
    3. Confirm next steps and expected timeline
    4. Thank them and ask if there is anything else

    Rules:
    - Be professional, empathetic, and concise
    - If the customer is unavailable, leave a clear voicemail
    - Do not discuss billing or refunds
    ```

    Set the **Initial message** to:

    ```
    Hi, this is Alex from Acme Corp. I'm calling about your order
    @order_id — do you have a moment?
    ```
  </Step>

  <Step title="Configure voice and model">
    Set the core voice agent settings:

    | Setting                  | Description                                                                   |
    | ------------------------ | ----------------------------------------------------------------------------- |
    | **LLM model**            | The language model powering the conversation (e.g., GPT-4.1)                  |
    | **Voice**                | The TTS voice for spoken responses                                            |
    | **Recording disclaimer** | Plays a recording notification at the start of the call                       |
    | **Voicemail action**     | What to do when the call goes to voicemail (hang up, leave message, or retry) |

    See [Outbound calls](../05-Voice-Agents/03-Outbound-Calls.md) and [STT, TTS & LLM configuration](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md) for the full list of voice agent settings.
  </Step>
</Steps>

## Add a data extraction step

After the voice call, you can use downstream nodes to process the conversation. The AI Extract node pulls structured data from the transcript — making it available to send via email, update a CRM, post to Slack, or pass to any other integration.

<Steps>
  <Step title="Add an AI Extract node">
    Click **+** after the voice agent node and select **AI Extract**.
  </Step>

  <Step title="Configure the input">
    In the **Input** field, type `@` and select the voice agent's transcript output. This passes the full conversation into the extraction model.
  </Step>

  <Step title="Define extraction parameters">
    Add three parameters to extract from the call:

    | Parameter            | Description                                | Example                      |
    | -------------------- | ------------------------------------------ | ---------------------------- |
    | `resolved`           | Whether the issue was resolved on the call | `true`                       |
    | `next_steps`         | Agreed-upon follow-up actions              | `Send replacement by Friday` |
    | `customer_sentiment` | Overall customer tone                      | `positive`                   |
  </Step>
</Steps>

Your workflow is now complete: Webhook Trigger → Outbound Voice Agent → AI Extract.

<Tip>
  This three-node pattern is just the beginning. You can add more nodes after AI Extract — send a Slack message with the call summary, update a Google Sheet, post results to a webhook, or branch based on the extracted `resolved` field. See [Core nodes](../03-Core-Nodes/01-Core-Nodes-Overview.md) and [Integrations](../15-Integrations/01-Integrations-Overview.md) for what's available.
</Tip>

## Test and publish

<Steps>
  <Step title="Test in development">
    There are two ways to trigger a test run:

    **Option A — Use the test form in the UI.** Click **Test** to open the test panel. The form auto-generates input fields based on the trigger's output schema (e.g., `phone_number`, `customer_name`, `order_id`, `issue_description`). Fill in the fields and click **Run**.

    **Option B — Send a POST request.** Use curl or any HTTP client to POST to the version-specific test URL shown in the trigger panel:

    ```bash theme={null}
    curl -X POST https://platform.happyrobot.ai/hooks/V1StGXR8_Z5jdHi6B-myT/VERSION_SLUG \
      -H "Content-Type: application/json" \
      -d '{
        "phone_number": "+15551234567",
        "customer_name": "Maria Garcia",
        "order_id": "ORD-2025-8842",
        "issue_description": "Package arrived damaged"
      }'
    ```

    Either way, the workflow executes in the development environment — the voice agent makes a real call to the number you provide, so use your own phone number for testing.
  </Step>

  <Step title="Review the test run">
    Switch to the **Runs** tab to see the execution. Click into the run to review the conversation transcript, node outputs, and any errors.
  </Step>

  <Step title="Publish to production">
    Once the test run looks good, click **Publish** and select **Production** as the target environment. This makes the workflow live — API requests to your hook endpoint will trigger real calls.
  </Step>
</Steps>

See [Versions and publishing](../02-Workflows/08-Versions-and-Publishing.md) and [Environments](../02-Workflows/09-Environments.md) for details on the deployment lifecycle.

## Trigger via API

Send a POST request to your workflow's hook endpoint to start the workflow:

<CodeGroup>
  ```bash cURL theme={null}
  curl -X POST https://platform.happyrobot.ai/hooks/V1StGXR8_Z5jdHi6B-myT \
    -H "Content-Type: application/json" \
    -H "x-api-key: sk_live_abc123def456" \
    -d '{
      "phone_number": "+15551234567",
      "customer_name": "Maria Garcia",
      "order_id": "ORD-2025-8842",
      "issue_description": "Package arrived damaged"
    }'
  ```

  ```python Python theme={null}
  import requests

  response = requests.post(
      "https://platform.happyrobot.ai/hooks/V1StGXR8_Z5jdHi6B-myT",
      headers={
          "Content-Type": "application/json",
          "x-api-key": "sk_live_abc123def456",
      },
      json={
          "phone_number": "+15551234567",
          "customer_name": "Maria Garcia",
          "order_id": "ORD-2025-8842",
          "issue_description": "Package arrived damaged",
      },
  )

  print(response.json())
  ```

  ```javascript Node.js theme={null}
  const response = await fetch(
    "https://platform.happyrobot.ai/hooks/V1StGXR8_Z5jdHi6B-myT",
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "x-api-key": "sk_live_abc123def456",
      },
      body: JSON.stringify({
        phone_number: "+15551234567",
        customer_name: "Maria Garcia",
        order_id: "ORD-2025-8842",
        issue_description: "Package arrived damaged",
      }),
    }
  );

  const data = await response.json();
  console.log(data);
  ```
</CodeGroup>

Replace `V1StGXR8_Z5jdHi6B-myT` with your workflow slug (found in the trigger configuration panel).

<Info>
  The `x-api-key` header is only required if you have enabled **Enhanced Security** in the trigger configuration. By default, webhook triggers accept unauthenticated requests. See [Triggers](../02-Workflows/05-Triggers.md) for details on configuring authentication.
</Info>

<Tip>
  Every field in the JSON body flows into the workflow as a variable. The `@customer_name`, `@order_id`, and `@issue_description` references in your prompt are replaced with the actual values from the request.
</Tip>

<Info>
  Each environment has its own endpoint. To target staging or development, use the environment-specific URL:

  * **Staging:** `https://platform.happyrobot.ai/hooks/staging/V1StGXR8_Z5jdHi6B-myT`
  * **Development:** `https://platform.happyrobot.ai/hooks/development/V1StGXR8_Z5jdHi6B-myT`

  See [Environments](../02-Workflows/09-Environments.md) for details.
</Info>

See [Triggers](../02-Workflows/05-Triggers.md), [Variables](../02-Workflows/07-Variables.md), and [API keys](../16-Account-and-Settings/06-API-Keys.md) for more.

## Monitor the run

<Steps>
  <Step title="View the run">
    Go to the **Runs** tab in your workflow. Each row shows the run status, timestamp, and environment. Click a run to open the details panel.
  </Step>

  <Step title="Review the transcript">
    The details panel shows the full conversation between the agent and the customer, including timestamps, tool calls, and event markers. For voice runs, a recording player is synced to the transcript.
  </Step>

  <Step title="Check AI Extract output">
    Scroll down in the run details to see the AI Extract node output — the structured data extracted from the call (`resolved`, `next_steps`, `customer_sentiment`).
  </Step>
</Steps>

See [Runs overview](../09-Runs-and-Monitoring/01-Runs-Overview.md), [Transcripts and messages](../09-Runs-and-Monitoring/03-Transcripts-and-Messages.md), and [Recordings](../09-Runs-and-Monitoring/04-Recordings.md) for more on monitoring.

## Query runs via API

Retrieve run data programmatically to build dashboards, trigger follow-up actions, or export records.

<CodeGroup>
  ```bash cURL theme={null}
  curl -X GET "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&page=1&page_size=50&status=completed" \
    -H "Authorization: Bearer sk_live_abc123def456"
  ```

  ```python Python theme={null}
  import requests

  response = requests.get(
      "https://platform.happyrobot.ai/runs/",
      headers={"Authorization": "Bearer sk_live_abc123def456"},
      params={
          "use_case_id": "YOUR_USE_CASE_ID",
          "page": 1,
          "page_size": 50,
          "status": "completed",
      },
  )

  runs = response.json()
  print(f"Total runs: {runs['pagination']['totalRecords']}")
  for run in runs["data"]:
      print(f"{run['id']} — {run['status']}")
  ```

  ```javascript Node.js theme={null}
  const response = await fetch(
    "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&page=1&page_size=50&status=completed",
    {
      headers: {
        Authorization: "Bearer sk_live_abc123def456",
      },
    }
  );

  const runs = await response.json();
  console.log(`Total runs: ${runs.pagination.totalRecords}`);
  runs.data.forEach((run) => console.log(`${run.id} — ${run.status}`));
  ```
</CodeGroup>

**Key query parameters:**

| Parameter     | Type     | Description                                                                 |
| ------------- | -------- | --------------------------------------------------------------------------- |
| `use_case_id` | UUID     | Required. The workflow to list runs for                                     |
| `page`        | integer  | Page number (default: 1)                                                    |
| `page_size`   | integer  | Results per page, 1–2000 (default: 100)                                     |
| `status`      | string   | Filter by status: `completed`, `failed`, `running`, `canceled`, `scheduled` |
| `start_date`  | datetime | Runs created after this timestamp                                           |
| `end_date`    | datetime | Runs created before this timestamp                                          |

See the [API reference](https://docs.happyrobot.ai/api-reference/overview) for all available endpoints and parameters.

## Next steps

<CardGroup cols={3}>
  <Card title="Voice agents" icon="phone" href="../05-Voice-Agents/01-Voice-Agents-Overview.md">
    Configure STT, TTS, LLM, tools, and advanced call handling.
  </Card>

  <Card title="Core nodes" icon="diagram-project" href="../03-Core-Nodes/01-Core-Nodes-Overview.md">
    Add AI Extract, AI Classify, custom code, conditions, and loops to your workflows.
  </Card>

  <Card title="Tools" icon="wrench" href="../04-Tools/01-Tools-Overview.md">
    Give agents access to knowledge bases, MCP servers, and custom functions.
  </Card>

  <Card title="Integrations" icon="plug" href="../15-Integrations/01-Integrations-Overview.md">
    Connect to Gmail, Slack, Snowflake, TMS systems, and more.
  </Card>

  <Card title="Text agents" icon="message" href="../06-Text-Agents/01-Text-Agents-Overview.md">
    Deploy agents over SMS, WhatsApp, email, and chatbot.
  </Card>

  <Card title="API reference" icon="code" href="https://docs.happyrobot.ai/api-reference/overview">
    Trigger workflows, query runs, and manage contacts programmatically.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/quickstart
