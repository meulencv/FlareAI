---
title: "Memories"
description: "How agents remember context across conversations"
---

# Memories

> How agents remember context across conversations

Contact intelligence lets your AI agents remember context across conversations. When enabled, AI processes each interaction to extract knowledge snippets (memories), tags, and structured attributes — then makes that context available to agents in future conversations. This means a second call with the same person can pick up right where the first one left off, without the contact having to repeat themselves.

<Info>
  Contact intelligence is currently in **beta**. The feature is fully functional but the interface and capabilities may evolve.
</Info>

## Enabling contact intelligence

Contact intelligence is configured per-workflow. To enable it:

<Steps>
  <Step title="Open the Contact Intelligence dialog">
    Navigate to the **Contacts** page and click the **Contact Intelligence** button in the header. This opens a dialog listing all workflows in your organization.
  </Step>

  <Step title="Find your workflow">
    Locate the workflow you want to configure and expand it.
  </Step>

  <Step title="Toggle on">
    Switch the **Enabled** toggle to on. The configuration fields appear below.
  </Step>

  <Step title="Configure extraction settings">
    Set up your memory prompt, tag definitions, and attribute definitions (see below).
  </Step>

  <Step title="Generate the memory prompt">
    Click **Generate Prompt** to have the system create the extraction prompt from your configuration. This prompt is what the AI uses to process interactions.
  </Step>

  <Step title="Save">
    Click **Save** to apply the configuration. New interactions on this workflow will now be processed for memory extraction.
  </Step>
</Steps>

## Configuration reference

| Setting                     | Description                                                                                                                                                                                                                         |
| --------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Enabled**                 | Master toggle for contact intelligence on this workflow. When off, no memories, tags, or attributes are extracted from interactions.                                                                                                |
| **Custom memory prompt**    | Optional free-text instructions that guide how the AI extracts information. Use this to add domain-specific context — for example, "Focus on extracting freight-related details like MC numbers, lane preferences, and fleet size." |
| **Tag definitions**         | A list of name + description pairs. Each tag tells the AI what to look for. For example: name `VIP`, description "Apply when the contact indicates high volume or strategic importance."                                            |
| **Attribute definitions**   | A list of key + description pairs. Each attribute tells the AI what structured data to extract. For example: key `mc_number`, description "The motor carrier number mentioned by the contact."                                      |
| **Generated memory prompt** | Read-only field showing the AI-generated extraction prompt built from your configuration. This is the actual prompt used during interaction processing.                                                                             |
| **Regenerate prompt**       | Button to regenerate the memory prompt after making changes to tags, attributes, or the custom prompt.                                                                                                                              |

## How memory extraction works

<Steps>
  <Step title="Agent has a conversation">
    A voice or text agent interacts with a contact through any supported channel — call, SMS, WhatsApp, or email.
  </Step>

  <Step title="AI processes the interaction">
    After the conversation ends, the system uses the generated memory prompt to analyze the interaction. The prompt incorporates your tag definitions, attribute definitions, and any custom instructions.
  </Step>

  <Step title="Data is extracted and stored">
    The AI extracts memories (atomic facts), tags (classification labels), and attributes (structured key-value pairs) from the conversation. These are stored on the interaction and linked to the contact.
  </Step>

  <Step title="Contact summary is updated">
    The AI generates or updates an overall summary of the contact, incorporating the latest interaction alongside all previous data.
  </Step>

  <Step title="Context is available for future conversations">
    The next time an agent interacts with this contact, it can access the stored memories, attributes, and summary — either automatically or via a template variable.
  </Step>
</Steps>

## Using memories in agents

To make contact context available during conversations, configure memory settings on your voice or text agent nodes.

### Agent memory settings

| Setting                    | Description                                                                                                                                      |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Enable memory**          | Activates contact intelligence for this agent. When on, the agent receives the contact's record and interaction history in its prompt.           |
| **Interaction limit**      | How many past interactions to include in context (0–10). More interactions mean richer context but higher token usage.                           |
| **Auto context injection** | On by default. When enabled, the contact's memories, attributes, and summary are automatically appended to the end of the agent's system prompt. |

### Manual context placement

If you need precise control over where contact context appears in the prompt, disable auto context injection and use the `@contact_intelligence_context` variable anywhere in your system prompt.

<Tip>
  Disabling auto context injection and placing `@contact_intelligence_context` manually is useful when you want the contact history to appear in the middle of the prompt — for example, after general instructions but before specific task guidance.
</Tip>

Memory settings are available on:

* [Inbound voice agents](../05-Voice-Agents/02-Inbound-Calls.md)
* [Outbound voice agents](../05-Voice-Agents/03-Outbound-Calls.md) (also supports `enabled_contact_block` to skip blocked contacts)
* [Inbound text agents](../06-Text-Agents/01-Text-Agents-Overview.md)
* [Outbound text agents](../06-Text-Agents/01-Text-Agents-Overview.md)

## Contact summaries

The contact summary is an AI-generated overview of a contact, updated each time a new interaction is processed. It captures the key facts across all conversations — who the person is, what they typically need, and any important context.

The summary is visible in the contact details sidebar and is included in the context injected into agent prompts when memory is enabled.

## Managing memories

Memories are visible in two places in the contact details sidebar:

* **Contact-level memories** — all memories for the contact, shown in the sidebar's memories section
* **Interaction-level memories** — memories from a specific interaction, shown when you expand that interaction's detail view

To delete a memory, hover over it and click the trash icon. Deletion is permanent. Memories cannot be edited — if a memory is incorrect, delete it and let future interactions generate updated information.

## Using contact intelligence in workflows

You can read and write contact data directly from within workflows using the **Contact Intelligence** integration nodes. These are available in the workflow editor under the **Data** category.

### Read Contact

Fetches a contact's profile, extracted attributes, and recent interaction history.

| Field                  | Required | Description                                                          |
| ---------------------- | -------- | -------------------------------------------------------------------- |
| **Resolve by**         | No       | How to look up the contact: `contact_id`, `phone_number`, or `email` |
| **Contact ID / Value** | Yes      | The identifier used to find the contact                              |
| **Interaction limit**  | No       | How many past interactions to include in the output                  |

The node outputs the full contact record, including stored attributes and interactions up to the specified limit.

### Update Contact

Writes or merges attribute values onto a contact record.

| Field                  | Required | Description                                                                                                                      |
| ---------------------- | -------- | -------------------------------------------------------------------------------------------------------------------------------- |
| **Resolve by**         | No       | How to look up the contact: `contact_id`, `phone_number`, or `email`                                                             |
| **Contact ID / Value** | Yes      | The identifier used to find the contact                                                                                          |
| **Attributes**         | Yes      | Key-value pairs of attributes to update. Keys must match attribute definitions configured in your Contact Intelligence settings. |

Attributes are merged using policy-aware logic — existing values are preserved unless explicitly overwritten.

### Search Contact Memories

Runs a semantic search over a contact's memory store to find relevant past facts.

| Field                  | Required | Description                                                                   |
| ---------------------- | -------- | ----------------------------------------------------------------------------- |
| **Resolve by**         | No       | How to look up the contact: `contact_id`, `phone_number`, or `email`          |
| **Contact ID / Value** | Yes      | The identifier used to find the contact                                       |
| **Query**              | Yes      | A natural-language question or phrase to search for in the contact's memories |
| **Top K**              | No       | Maximum number of memory results to return                                    |

The node returns the memories most semantically similar to the query — useful for retrieving relevant context before a conversation starts.

<Note>
  Contact Intelligence nodes require contact intelligence to be enabled and configured for the workflow. See the [configuration steps above](#enabling-contact-intelligence).
</Note>

## API access

Retrieve a contact's memories programmatically using the REST API:

**`GET /contacts/{contact_id}/memories`**

Supports cursor-based pagination:

| Parameter | Type    | Description                                |
| --------- | ------- | ------------------------------------------ |
| `cursor`  | string  | Pagination cursor from a previous response |
| `limit`   | integer | Results per page (default: 25)             |

See the [API Reference](https://docs.happyrobot.ai/api-reference/overview) for full endpoint documentation.

## Best practices

<Tip>
  * **Start with 3–5 interaction limit** — this provides enough context without consuming excessive tokens. Increase if agents need deeper history.
  * **Define specific tag categories** — vague tags like "important" produce inconsistent results. Use clear categories like "Billing Issue", "Tracking Request", or "Positive Sentiment".
  * **Write clear attribute descriptions** — tell the AI exactly what to look for. "The motor carrier number (MC number) mentioned by the contact" is better than "MC number".
  * **Use custom memory prompts for domain-specific extraction** — if your business has unique terminology or data types, add a custom prompt to guide the AI.
  * **Review generated prompts** — after clicking **Generate Prompt**, review the read-only generated prompt to ensure it captures your intent. Regenerate after making changes.
</Tip>

## Next steps

<CardGroup cols={3}>
  <Card title="Managing contacts" icon="users" href="02-Managing-Contacts.md">
    Search, filter, block, and delete contacts.
  </Card>

  <Card title="Interaction history" icon="clock-rotate-left" href="03-Interaction-History.md">
    Explore past conversations, channels, and tags.
  </Card>

  <Card title="Voice agents" icon="phone" href="../05-Voice-Agents/01-Voice-Agents-Overview.md">
    Configure voice agents with contact intelligence.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/contacts/memories
