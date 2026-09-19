---
title: "AI Generate"
description: "Generate text content using AI"
---

# AI Generate

> Generate text content using AI

The AI Generate node uses a language model to produce text content. Provide a prompt with instructions and context, and the node returns generated text — a draft email, a summary, a formatted response, or any other text output.

## Use cases

<CardGroup cols={3}>
  <Card title="Draft responses" icon="pen">
    Generate follow-up emails, SMS messages, or chat replies based on conversation context.
  </Card>

  <Card title="Summarize content" icon="file-lines">
    Condense long transcripts, documents, or data into concise summaries.
  </Card>

  <Card title="Create content" icon="sparkles">
    Produce formatted text, reports, or structured output from raw data.
  </Card>
</CardGroup>

## Configuration

### Model

Select the AI model to use for generation. Default is **GPT-5.6 Luna**.

See [AI Extract](02-AI-Extract.md#model) for how the picker is organized, and [Models](../14-Assets/05-Models.md) for the full catalog.

### Prompt

The generation instructions. This is where you define what the model should produce, including format, tone, and any specific content requirements.

Supports variables — type `@` in the editor to insert values from previous nodes. Use variables to inject dynamic context like transcripts, extracted data, or customer information.

## Output

The node returns the generated text as a string. Downstream nodes can use this output in emails, messages, API requests, or any other text field.

## Example

After a voice agent completes a call, the AI Generate node receives the transcript and extracted load details. Its prompt instructs: "Write a professional follow-up email summarizing the call and confirming the load details." The generated email is then sent via a Gmail action node.

<Tip>
  Use variables liberally in your prompt to inject context. The more relevant data you provide, the better the generated output. For example: "Summarize the following transcript for @customer\_name: @call\_transcript".
</Tip>

<Info>
  AI nodes and prompt nodes (voice and text agents) draw from the same model catalog. See [STT, TTS & LLM Configuration](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md) for how models are configured on agents.
</Info>

## Related

<CardGroup cols={2}>
  <Card title="AI Extract" icon="wand-magic-sparkles" href="02-AI-Extract.md">
    Extract structured data from unstructured text.
  </Card>

  <Card title="AI Classify" icon="tags" href="03-AI-Classify.md">
    Classify text into predefined categories.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/ai-generate
