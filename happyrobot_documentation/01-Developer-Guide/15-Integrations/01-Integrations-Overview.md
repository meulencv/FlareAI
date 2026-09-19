---
title: "Integrations Overview"
description: "Connect HappyRobot to your existing tools and services"
---

# Integrations Overview

> Connect HappyRobot to your existing tools and services

Integrations let your workflows interact with external services — send emails, post Slack messages, query databases, update TMS records, and more. Each integration provides a set of **events** (triggers and actions) that you can add as nodes in the workflow editor.

## Integration categories

<CardGroup cols={2}>
  <Card title="Communication" icon="envelope">
    Email, messaging, and voice services — Gmail, Outlook, Slack, Microsoft Teams, Genesys, Twilio SMS, WhatsApp, SendGrid, and HappyRobot Email.
  </Card>

  <Card title="Business Systems" icon="building">
    Transportation management systems and business tools — McLeod, Turvo, TPro, 3PL, Custom TMS, Broker App, and CXone.
  </Card>

  <Card title="Data and Storage" icon="database">
    Data stores and utilities — Google Sheets, Snowflake, Redis, Kafka, Google Maps, and Salesforce.
  </Card>

  <Card title="Marketplace" icon="store" href="03-Integrations-marketplace.md">
    A wide range of additional integrations — CRM, HRIS, ATS, Accounting, Ticketing, and File Storage.
  </Card>
</CardGroup>

## All native integrations

The following integrations are built into HappyRobot. For an even larger catalogue of CRM, HRIS, ATS, accounting, ticketing, file storage, and marketing providers, see the [integrations marketplace](03-Integrations-marketplace.md).

<AccordionGroup>
  <Accordion title="Communication">
    Gmail, Outlook, Microsoft Teams, Slack, Genesys, Twilio SMS, WhatsApp, SendGrid, HappyRobot Email, Richpanel.
  </Accordion>

  <Accordion title="Transportation Management Systems (TMS)">
    McLeod, Turvo, Transport Pro (TPro), 3PL Systems, Alvys, Tai, Revenova, Custom TMS, Broker App.
  </Accordion>

  <Accordion title="Carrier identity & fleet">
    My Carrier Packets (MCP), Highway, Samsara.
  </Accordion>

  <Accordion title="Data & databases">
    Google Sheets, Google Calendar, Google Maps, Snowflake, Redis, Kafka, MongoDB, Notion, AWS (S3), Salesforce.
  </Accordion>

  <Accordion title="Contact center & support">
    CXone, Richpanel.
  </Accordion>

  <Accordion title="Workflow building blocks">
    AI (Extract / Classify / Generate), AI Agent (voice), AI Text Agent, Code (Python), Conditions, File, Schedule, Webhook, Negotiation, Phone Calls, Capacity, Locate, Auditor, Workflow Function.
  </Accordion>

  <Accordion title="Authentication & developer tools">
    OAuth 2.0 (API Client, Service Account, Client Certificate for mTLS, and Identity Provider), Basic Auth, MCP Server, Custom LLM Server, LinkedIn.
  </Accordion>
</AccordionGroup>

## How integrations work

Every integration follows the same pattern inside a workflow:

<Steps>
  <Step title="Enable the integration">
    Navigate to **Settings > Integrations** and click **Enable** on the integration you want to use. Some integrations are enabled by default.
  </Step>

  <Step title="Add credentials">
    Most integrations require credentials — an OAuth connection, API key, or service account. Add credentials from the integration's settings page. See [Credentials](02-Credentials.md) for details.
  </Step>

  <Step title="Add an action node to your workflow">
    In the workflow editor, click **+** to add a node, select the integration, and choose the event you want. Configure the event's fields in the side panel.
  </Step>

  <Step title="Use data from previous nodes">
    Action node fields support template variables. Reference outputs from upstream nodes — for example, type `@` and select an extracted email address to insert it into a "Send Email" action.
  </Step>
</Steps>

## Triggers vs actions

Integrations provide two types of events:

| Type        | Description                                                        | Example                                                   |
| ----------- | ------------------------------------------------------------------ | --------------------------------------------------------- |
| **Trigger** | Starts a workflow when something happens in an external service    | Gmail "New Email" fires when an email arrives             |
| **Action**  | Performs an operation in an external service during a workflow run | Slack "Send Channel Message" posts a message to a channel |

Triggers appear at the top of a workflow as the entry point. Actions appear as nodes in the body of the workflow and execute in sequence.

<Tip>
  Some integrations only provide actions (no triggers). You can still use them in workflows that are started by other triggers — for example, a webhook trigger followed by a Snowflake query action.
</Tip>

## Subscription management

Certain trigger-based integrations — Gmail, Outlook, and Microsoft Teams — require active **subscriptions** to receive events. A subscription tells the external service to notify HappyRobot when something happens (like a new email arriving). You manage subscriptions from the integration's settings page under the **Subscriptions** tab.

## Next steps

<CardGroup cols={3}>
  <Card title="Credentials" icon="key" href="02-Credentials.md">
    Set up authentication for your integrations.
  </Card>

  <Card title="Gmail" icon="envelope" href="04-Communication/01-Gmail.md">
    Send and receive emails with Gmail.
  </Card>

  <Card title="Slack" icon="hashtag" href="04-Communication/03-Slack.md">
    Send messages and monitor channels.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/overview
