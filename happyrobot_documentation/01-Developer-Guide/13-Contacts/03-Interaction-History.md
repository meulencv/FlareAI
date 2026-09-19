---
title: "Interaction History"
description: "View past interactions with contacts"
---

# Interaction History

> View past interactions with contacts

Every conversation between an AI agent and a contact is recorded as an interaction (communication event). Interactions capture the channel, timestamp, AI-generated summary, tags, extracted attributes, and memories — giving you a complete history of every touchpoint with a person across all your workflows.

## Channels

HappyRobot tracks interactions across five communication channels. Each channel is represented by an icon badge in the contacts list.

| Channel  | Icon          | Description                                             |
| -------- | ------------- | ------------------------------------------------------- |
| Call     | Phone icon    | Voice calls handled by inbound or outbound voice agents |
| SMS      | Message icon  | Two-way SMS conversations via Twilio                    |
| WhatsApp | WhatsApp icon | WhatsApp Business API conversations                     |
| Gmail    | Envelope icon | Email conversations via connected Gmail accounts        |
| Outlook  | Envelope icon | Email conversations via connected Outlook accounts      |

The contact list shows per-channel interaction counts as icon badges, so you can see at a glance how many times a contact has been reached on each channel.

## Viewing interactions

To view a contact's interaction history:

<Steps>
  <Step title="Open the contact sidebar">
    Click a contact row in the contacts list to open the details sidebar.
  </Step>

  <Step title="Scroll to the interactions list">
    The bottom section of the sidebar shows all interactions for the contact, ordered by timestamp.
  </Step>

  <Step title="Search interactions">
    Use the search bar above the interactions list to filter by interaction summary, tags, or memory content. Search is debounced and updates results as you type.
  </Step>

  <Step title="View interaction details">
    Click an interaction to expand it and see the full details — summary, tags, memory snippets, and extracted attributes.
  </Step>
</Steps>

Each interaction card displays:

* **Timestamp** — when the interaction occurred
* **Channel icon** — the communication channel used
* **Run link** — direct link to the workflow run that generated this interaction
* **Conversation link** — direct link to the conversation transcript

## Interaction details

Expanding an interaction reveals several tabs of AI-extracted data:

<AccordionGroup>
  <Accordion title="Context summary">
    An AI-generated summary of what happened during the interaction. This captures the key points of the conversation — who called, what they needed, and how it was resolved.
  </Accordion>

  <Accordion title="Tags">
    Tags are labels assigned to the interaction by AI based on the tag definitions configured in [contact intelligence](04-Memories.md). Examples include sentiment categories ("positive", "frustrated"), topic classifications ("billing", "tracking"), or custom categories you define. Tags appear as color-coded badges on the interaction card and in the contacts list.
  </Accordion>

  <Accordion title="Memory snippets">
    Memories extracted from this specific interaction. Each memory is an atomic fact about the contact — such as "Prefers morning calls" or "Fleet size is 50 trucks". Memories can be deleted individually by clicking the trash icon. See [Memories](04-Memories.md) for details on how extraction works.
  </Accordion>

  <Accordion title="Extracted attributes">
    Key-value pairs extracted from the interaction based on your attribute definitions. For example, an interaction might extract `mc_number: 12345` or `preferred_language: Spanish`. Attributes can be deleted individually from the interaction level.
  </Accordion>
</AccordionGroup>

## Tags

Tags are AI-assigned labels that classify interactions. They are defined per-workflow in the [contact intelligence configuration](04-Memories.md) and applied automatically when the AI processes an interaction.

Each tag definition includes:

| Field           | Description                                                        |
| --------------- | ------------------------------------------------------------------ |
| **Name**        | The tag label (e.g., "VIP", "Billing Issue", "Positive Sentiment") |
| **Description** | Instructions for the AI explaining when to apply this tag          |

Tags are aggregated across all interactions and displayed on the contact row in the contacts list. You can [filter contacts by tags](02-Managing-Contacts.md) to find contacts matching specific categories.

<Tip>
  Write clear, specific tag descriptions to improve extraction accuracy. For example, instead of "Important customer", use "Apply when the contact mentions they are a high-volume shipper with more than 100 loads per month."
</Tip>

## Interaction-level attributes

Extracted attributes are structured key-value pairs pulled from individual interactions. They differ from contact-level attributes in that they are scoped to a single interaction, giving you visibility into what was learned from each conversation.

Contact-level attributes (shown in the sidebar header) represent the latest aggregated view across all interactions. Interaction-level attributes are preserved per-event, so you can see exactly which conversation produced each piece of data.

To delete an interaction-level attribute, click the delete icon next to it in the interaction detail view.

## API access

Retrieve a contact's interaction history programmatically using the REST API:

**`GET /contacts/{contact_id}/interactions`**

Supports cursor-based pagination and sorting:

| Parameter | Type    | Description                                                                  |
| --------- | ------- | ---------------------------------------------------------------------------- |
| `cursor`  | string  | Pagination cursor from a previous response                                   |
| `limit`   | integer | Results per page (default: 25)                                               |
| `sort`    | string  | Sort order — `timestamp:asc` or `timestamp:desc` (default: `timestamp:desc`) |

See the [API Reference](https://docs.happyrobot.ai/api-reference/overview) for full endpoint documentation.

## Next steps

<CardGroup cols={3}>
  <Card title="Memories" icon="brain" href="04-Memories.md">
    Configure AI memory extraction and context injection.
  </Card>

  <Card title="Managing contacts" icon="users" href="02-Managing-Contacts.md">
    Search, filter, block, and delete contacts.
  </Card>

  <Card title="Contacts overview" icon="address-book" href="01-Contacts-Overview.md">
    Learn how contacts fit into the platform.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/contacts/interaction-history
