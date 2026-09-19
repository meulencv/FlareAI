---
title: "AI Classify"
description: "Classify text into predefined categories using AI"
---

# AI Classify

> Classify text into predefined categories using AI

The AI Classify node uses a language model to sort text into one of your predefined categories. Define a set of tags, provide input text, and the node returns the best-matching tag name. Use it for intent detection, sentiment analysis, routing decisions, and any scenario where you need to categorize unstructured input.

## Use cases

<CardGroup cols={3}>
  <Card title="Intent detection" icon="bullseye">
    Determine whether a customer inquiry is about pricing, scheduling, tracking, or something else.
  </Card>

  <Card title="Sentiment analysis" icon="face-smile">
    Classify messages as positive, negative, or neutral to prioritize follow-ups.
  </Card>

  <Card title="Routing" icon="code-branch">
    Route conversations to the right workflow branch based on the topic or urgency of the input.
  </Card>
</CardGroup>

## Configuration

### Model

Select the AI model to use for classification. Default is **GPT-5.6 Luna**.

See [AI Extract](02-AI-Extract.md#model) for how the picker is organized, and [Models](../14-Assets/05-Models.md) for the full catalog.

### Prompt

Instructions that tell the model how to classify the input. Describe the context, define what each category means, and specify any edge cases.

Supports variables — type `@` in the editor to insert values from previous nodes.

### Input

The text to classify. This is typically a variable reference to output from a previous node — a transcript, message, or extracted text.

Supports variables — type `@` to pick from available node outputs.

### Tags

Define the categories the model can choose from. Each tag has:

* **Name** — The category label returned as output (e.g., `urgent`, `billing`, `general_inquiry`)
* **Description** *(optional)* — Explains what this category represents to improve classification accuracy

Add as many tags as needed. The model evaluates the input against all tags and selects the best match. Drag the handle on the left of each tag to reorder them.

## Output

The node returns the **name** of the matched tag as a string. Downstream nodes can reference this value to branch logic, filter records, or trigger different actions.

## Example

A voice agent transcript is fed into the AI Classify node with tags `check_call`, `load_update`, `rate_negotiation`, and `other`. The node returns `load_update`, which a downstream condition node uses to route the workflow to the TMS update branch.

<Info>
  AI nodes and prompt nodes (voice and text agents) draw from the same model catalog. See [STT, TTS & LLM Configuration](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md) for how models are configured on agents.
</Info>

## Related

<CardGroup cols={2}>
  <Card title="AI Extract" icon="wand-magic-sparkles" href="02-AI-Extract.md">
    Extract structured data from unstructured text.
  </Card>

  <Card title="Conditionals" icon="code-branch" href="09-Conditionals.md">
    Branch workflows based on classification results.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/ai-classify
