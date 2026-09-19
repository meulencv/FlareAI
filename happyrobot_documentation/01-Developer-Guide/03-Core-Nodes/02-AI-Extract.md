---
title: "AI Extract"
description: "Extract structured data from unstructured text using AI"
---

# AI Extract

> Extract structured data from unstructured text using AI

The AI Extract node uses a language model to pull structured data out of unstructured text. Give it a block of text — an email, a transcript, a document — and define the fields you want extracted. The node returns a clean, structured object with named values.

## Use cases

<CardGroup cols={3}>
  <Card title="Parse emails" icon="envelope">
    Extract sender, subject, dates, and key details from email bodies.
  </Card>

  <Card title="Extract entities" icon="bullseye">
    Pull names, phone numbers, addresses, and other entities from free-form text.
  </Card>

  <Card title="Structure documents" icon="file-lines">
    Convert unstructured documents into structured records with named fields.
  </Card>
</CardGroup>

## Configuration

### Model

Select the AI model to use for extraction. The default is **GPT-5.6 Luna**.

The picker offers the same catalog as voice and text agents — OpenAI, Anthropic Claude, Google Gemini, Mistral, xAI Grok, and OpenRouter models — grouped by provider, with a **reasoning effort** selector for families that offer one. Three models carry a **Recommended** badge:

| Model            | ID             | Notes                                                                |
| ---------------- | -------------- | -------------------------------------------------------------------- |
| GPT-5.6 Luna     | `gpt-5.6-luna` | **Default** and top recommendation — cost-efficient with low latency |
| Claude Haiku 4.5 | `claude-haiku` | Second recommendation — fastest Claude model                         |
| Grok 4.6         | `grok-4.6`     | Third recommendation — xAI's frontier model                          |

For every available model, including effort levels, latencies, and API identifiers, see [Models](../14-Assets/05-Models.md).

<Note>
  AI nodes always run at standard speed, so they don't show the **Fast** speed option that agent prompt nodes can. The GPT-4.1 family isn't offered on AI nodes either.
</Note>

<Note>
  Older OpenAI ids — `o1`, `o3`, `o3-mini`, `o3-pro`, `gpt-4.1-nano`, and `gpt-4o-mini` — are deprecated and no longer selectable. Nodes already saved with one of these keep working, but switch them to a current model when you next edit the node.
</Note>

### Prompt

System instructions that tell the model how to extract data. Use this to provide context about what the input text represents and any special extraction rules.

Supports variables — type `@` in the editor to insert values from previous nodes.

### Input

The text to extract data from. This is typically a variable reference to output from a previous node — a transcript, email body, or document content.

Supports variables — type `@` to pick from available node outputs.

### Extraction mode

Choose how to define the structure of extracted data:

<AccordionGroup>
  <Accordion title="Parameters mode">
    Define named parameters visually. For each parameter, configure:

    * **Name** — The field name in the output (e.g., `pickup_city`, `weight`)
    * **Description** — What this field represents (helps the model extract accurately). Required — every parameter must have a non-empty description, or the node is marked incomplete.
    * **Example** — A sample value to guide the model
    * **Required** — Whether the field must be present in the output

    Add as many parameters as needed (at least one is required). The node returns an object with each parameter as a key.

    Drag the handle on the left of each parameter to reorder fields — the order you set is preserved in the extraction output.
  </Accordion>

  <Accordion title="JSON Schema mode">
    Provide a raw JSON schema that defines the extraction structure. This gives you full control over nested objects, arrays, enums, and complex types.

    The schema must be OpenAI-compatible with `additionalProperties: false` set on all object types (strict mode requirement).

    ```json theme={null}
    {
      "type": "object",
      "properties": {
        "pickup_city": { "type": "string" },
        "delivery_city": { "type": "string" },
        "weight_lbs": { "type": "number" }
      },
      "required": ["pickup_city", "delivery_city"],
      "additionalProperties": false
    }
    ```
  </Accordion>
</AccordionGroup>

## Example

An email arrives with load details. The AI Extract node receives the email body as input and extracts `origin`, `destination`, `weight`, `pickup_date`, and `reference_number` into structured fields that downstream nodes can use to create a TMS record.

<Tip>
  When using JSON Schema mode, every object in your schema must include `"additionalProperties": false`. This is required by OpenAI's strict mode — extraction will fail without it.
</Tip>

<Info>
  AI nodes and prompt nodes (voice and text agents) draw from the same model catalog. See [STT, TTS & LLM Configuration](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md) for how models are configured on agents.
</Info>

## Related

<CardGroup cols={2}>
  <Card title="AI Classify" icon="tags" href="03-AI-Classify.md">
    Classify text into predefined categories.
  </Card>

  <Card title="AI Generate" icon="sparkles" href="04-AI-Generate.md">
    Generate text content using AI.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/ai-extract
