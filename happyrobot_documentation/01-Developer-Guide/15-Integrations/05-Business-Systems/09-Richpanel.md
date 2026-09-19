---
title: "Richpanel"
description: "Escalate text agent conversations to human agents in Richpanel"
---

# Richpanel

> Escalate text agent conversations to human agents in Richpanel

Richpanel is a helpdesk platform for e-commerce and customer support teams. The HappyRobot integration lets text agents escalate conversations to Richpanel when the AI can't resolve an issue, handing off context to a human agent in your support queue.

## Authentication

<Steps>
  <Step title="Enable the Richpanel integration">
    Go to **Settings → Integrations** and enable **Richpanel**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and enter your Richpanel credentials:

    | Field              | Required | Description                                                                                                                                                                |
    | ------------------ | -------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | **API Key**        | Yes      | Your Richpanel API key. Find it in your Richpanel account settings.                                                                                                        |
    | **Webhook Secret** | No       | A secret used to validate incoming webhooks from Richpanel (sent as the `X-API-Key` header). Only required if you configure Richpanel to send webhooks back to HappyRobot. |
  </Step>

  <Step title="Verify the connection">
    The credential appears as **Active** once saved.
  </Step>
</Steps>

## Configure escalation on a text agent

Once you have a Richpanel credential, you can use Richpanel as the escalation mode for any text agent.

<Steps>
  <Step title="Open the text agent node">
    In the workflow editor, select the inbound or outbound text agent node you want to configure.
  </Step>

  <Step title="Enable escalation">
    In the **Escalation** section, toggle escalation on.
  </Step>

  <Step title="Select Richpanel mode">
    Set **Mode** to **Richpanel**.
  </Step>

  <Step title="Select your credential">
    Choose the Richpanel credential you configured in the previous section.
  </Step>

  <Step title="Set the description and message">
    * **Description** — tell the agent when to escalate (e.g., "Escalate when the customer requests a human agent or the issue cannot be resolved").
    * **Message type** — choose **AI**, **Fixed**, or **None** for the message sent to the contact before the handoff.
  </Step>
</Steps>

When the agent decides to escalate, HappyRobot creates a ticket in Richpanel using the conversation session as the ticket identifier, and the human support queue takes over.

## Related

<CardGroup cols={2}>
  <Card title="Text agents overview" icon="messages" href="../../06-Text-Agents/01-Text-Agents-Overview.md">
    Learn about escalation and other text agent settings.
  </Card>

  <Card title="Integrations overview" icon="plug" href="../01-Integrations-Overview.md">
    Browse all available integrations.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/richpanel
