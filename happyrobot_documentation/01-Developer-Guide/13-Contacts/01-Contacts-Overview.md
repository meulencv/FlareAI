---
title: "Contacts Overview"
description: "Manage your contact database"
---

# Contacts Overview

> Manage your contact database

Contacts are an automatically built database of every person your AI agents interact with. Each time an agent handles a phone call, SMS, WhatsApp message, or email, HappyRobot creates or updates a contact record — tracking interactions across channels, extracting memories and attributes with AI, and making that context available in future conversations.

## What you can do

<CardGroup cols={2}>
  <Card title="Track interactions" icon="clock-rotate-left">
    Every conversation — voice call, SMS, WhatsApp, email, or chatbot — is recorded as an interaction on the contact, with channel, timestamp, summary, tags, and extracted data.
  </Card>

  <Card title="Extract memories" icon="brain">
    AI processes each interaction to extract knowledge snippets (memories) about the contact. Agents use these memories to personalize future conversations.
  </Card>

  <Card title="Organize with tags" icon="tags">
    Define tag categories per workflow and let AI classify interactions automatically. Use tags to segment contacts and filter your contact list.
  </Card>

  <Card title="Block contacts" icon="ban">
    Block specific contacts from individual workflows. Blocked contacts are skipped during outbound campaigns and flagged in the contact list.
  </Card>
</CardGroup>

## How contacts work

<Steps>
  <Step title="Agent interacts with a person">
    A voice agent answers a call, a text agent receives an SMS, or an outbound workflow dials a phone number. Every conversation starts here.
  </Step>

  <Step title="Contact is created or matched">
    HappyRobot looks up the phone number or email address. If no contact exists for this organization, one is created automatically. If a match is found, the existing contact is used.
  </Step>

  <Step title="Interaction is recorded">
    The conversation is saved as a communication event on the contact — capturing the channel, timestamp, run reference, and session details.
  </Step>

  <Step title="AI extracts data">
    If [contact intelligence](04-Memories.md) is enabled for the workflow, AI processes the interaction to extract a summary, memories, tags, and structured attributes.
  </Step>

  <Step title="Context available in future conversations">
    The next time an agent interacts with the same contact, it can access the full history — past interactions, memories, attributes, and the AI-generated contact summary — to deliver a personalized experience.
  </Step>
</Steps>

## Contact types

Contacts are identified by a type and value. Each combination of organization, type, and value is unique — ensuring a single contact record per person per channel type.

| Type           | Value                        | Example            |
| -------------- | ---------------------------- | ------------------ |
| `phone_number` | Phone number in E.164 format | `+15551234567`     |
| `email`        | Email address                | `jane@example.com` |

## Key capabilities

<CardGroup cols={2}>
  <Card title="Multi-channel tracking" icon="diagram-venn">
    See all interactions with a contact in one place, regardless of whether they happened over voice, SMS, WhatsApp, or email.
  </Card>

  <Card title="AI memories" icon="lightbulb">
    Automatically extract and store facts about contacts. Agents reference these memories to maintain continuity across conversations.
  </Card>

  <Card title="Custom tags and attributes" icon="tag">
    Define tag categories and attribute keys per workflow. AI populates them from conversations, and you can edit attributes manually.
  </Card>

  <Card title="Per-workflow blocking" icon="shield">
    Block contacts from specific workflows without deleting them. Outbound agents respect block lists automatically.
  </Card>

  <Card title="Contact summaries" icon="file-lines">
    AI generates and maintains a summary of each contact, updated as new interactions are processed.
  </Card>

  <Card title="API access" icon="code">
    List, search, and retrieve contacts programmatically using the REST API. Integrate contact data into external systems.
  </Card>
</CardGroup>

## Next steps

<CardGroup cols={3}>
  <Card title="Managing contacts" icon="users" href="02-Managing-Contacts.md">
    Search, filter, block, and delete contacts.
  </Card>

  <Card title="Interaction history" icon="clock-rotate-left" href="03-Interaction-History.md">
    View past conversations and extracted data.
  </Card>

  <Card title="Memories" icon="brain" href="04-Memories.md">
    Configure AI memory extraction and context injection.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/contacts/overview
