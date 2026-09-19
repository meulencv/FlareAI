---
title: "Models"
description: "Reference for every language model available in HappyRobot workflows, voice agents, and text agents"
---

# Models

> Reference for every language model available in HappyRobot workflows, voice agents, and text agents

HappyRobot supports models from OpenAI, Anthropic, Google, Mistral, xAI, and OpenRouter. The catalog is organized into model **families** — you pick a family, then how hard it should think and how fast it should run. The identifiers next to each entry are what the [API](https://docs.happyrobot.ai/api-reference/overview) accepts.

## How model selection works

Every model picker in the platform has up to three controls:

| Control              | What it does                                                                                                  |
| -------------------- | ------------------------------------------------------------------------------------------------------------- |
| **Model**            | The family, grouped by provider. Families you use most and newly added ones are called out with badges.       |
| **Reasoning effort** | How much deliberation the model does before answering. Only shown when the family offers more than one level. |
| **Speed**            | **Standard** or **Fast**. Only shown when the family has a Fast variant available to your organization.       |

### Reasoning effort

Effort levels, from cheapest and fastest to slowest and most thorough:

**No reasoning** → **Minimal** → **Low** → **Medium** → **High** → **Extra high** → **Max**

Not every family supports every level — the picker only offers the levels that family actually has. Higher effort raises both latency and cost, so on voice agents, where latency is audible, prefer no reasoning or a low level.

### Speed

**Fast** routes the request through the provider's priority tier, which cuts time-to-first-token at a higher price per token. The Fast option only appears for organizations whose plan includes priority capacity, and only for families that have Fast variants — mostly the OpenAI GPT-5.x and GPT-4.1 families.

<Note>
  Speed is deliberately absent from AI nodes, reasoning agents, custom tests, and adversarial suites — those always run at standard speed. AI nodes also don't offer the GPT-4.1 family.
</Note>

### Model IDs

A model ID encodes the family, the effort, and the speed:

| Shape                      | Example                  | Meaning                                        |
| -------------------------- | ------------------------ | ---------------------------------------------- |
| `<family>`                 | `gpt-5.6-luna`           | The family's default effort at standard speed. |
| `<family>-<effort>`        | `gpt-5.6-luna-high`      | A specific effort at standard speed.           |
| `fast-<family>[-<effort>]` | `fast-gpt-5.6-luna-high` | The same variant on the priority tier.         |

IDs that predate this scheme still work — for example `turbo-one` resolves to `gpt-4.1` and `gpt-5.2` resolves to `gpt-5.2-medium` — so stored configurations and API calls keep running. Each family below lists its variant IDs.

### Defaults per surface

When you haven't chosen a model, the platform picks one based on where the model is used:

| Surface                                | Default                    | Also recommended                  |
| -------------------------------------- | -------------------------- | --------------------------------- |
| Voice agents                           | `gpt-5.6-luna`             | `gpt-5.2-instant`, `claude-haiku` |
| Text agents                            | `gpt-5.6-luna-max`         | `grok-4.6`, `claude-sonnet-5`     |
| Reasoning agents                       | `gpt-5.6-luna-max`         | `grok-4.6`, `claude-sonnet-5`     |
| AI nodes (extract, classify, generate) | `gpt-5.6-luna`             | `claude-haiku`, `grok-4.6`        |
| [Custom tests](../11-Quality-and-Evaluation/06-Custom-tests.md) | `gpt-5.6-luna`             | —                                 |
| Adversarial suites                     | `gemini-3.5-flash-minimal` | —                                 |

## Reading the latency values

Latency values are approximate time-to-first-token in milliseconds for the standard-speed variant, sourced from [Artificial Analysis](https://artificialanalysis.ai/models) where a model has been benchmarked and extrapolated from sibling models otherwise. Fast variants are consistently lower.

| Range             | What it suits                                                                        |
| ----------------- | ------------------------------------------------------------------------------------ |
| under \~700ms     | Live voice, inline classification, and anywhere responsiveness is the priority.      |
| \~700ms to \~1.5s | Tool calls, drafting, routing, and structured outputs. Fine for most workflow steps. |
| \~1.5s and up     | Accuracy on complex prompts: deep analysis, eval judging, quality-first tasks.       |

## OpenAI

<a id="gpt-5.6-sol" />

<a id="gpt-5.6-sol-max" />

### GPT-5.6 Sol

Frontier model for complex professional work.

| Effort       | ID                   | Latency  |
| ------------ | -------------------- | -------- |
| No reasoning | `gpt-5.6-sol`        | \~950ms  |
| Low          | `gpt-5.6-sol-low`    | \~1600ms |
| Medium       | `gpt-5.6-sol-medium` | \~2800ms |
| High         | `gpt-5.6-sol-high`   | \~4500ms |
| Extra high   | `gpt-5.6-sol-xhigh`  | \~6500ms |
| Max          | `gpt-5.6-sol-max`    | \~8000ms |

<a id="gpt-5.6-terra" />

### GPT-5.6 Terra

GPT-5.6 model that balances intelligence and cost.

| Effort       | ID                     | Latency  |
| ------------ | ---------------------- | -------- |
| No reasoning | `gpt-5.6-terra`        | \~850ms  |
| Low          | `gpt-5.6-terra-low`    | \~1400ms |
| Medium       | `gpt-5.6-terra-medium` | \~2200ms |
| High         | `gpt-5.6-terra-high`   | \~3500ms |
| Extra high   | `gpt-5.6-terra-xhigh`  | \~5500ms |
| Max          | `gpt-5.6-terra-max`    | \~8500ms |

<a id="gpt-5.6-luna" />

<a id="gpt-5.6-luna-high" />

### GPT-5.6 Luna

GPT-5.6 model optimized for cost-sensitive workloads. The default for voice agents, text agents, and AI nodes.

| Effort       | ID                    | Latency  |
| ------------ | --------------------- | -------- |
| No reasoning | `gpt-5.6-luna`        | \~750ms  |
| Low          | `gpt-5.6-luna-low`    | \~1200ms |
| Medium       | `gpt-5.6-luna-medium` | \~1800ms |
| High         | `gpt-5.6-luna-high`   | \~2500ms |
| Extra high   | `gpt-5.6-luna-xhigh`  | \~4500ms |
| Max          | `gpt-5.6-luna-max`    | \~7000ms |

<a id="gpt-5.5" />

### GPT-5.5

`gpt-5.5` · \~1070ms

OpenAI's newest flagship. A new class of intelligence for coding, agentic work, and professional reasoning.

<a id="gpt-5.4" />

### GPT-5.4

`gpt-5.4` · \~750ms

Most capable GPT-5.4 model. Strong intelligence for agentic, coding, and professional workflows.

<a id="gpt-5.4-mini" />

### GPT-5.4 Mini

`gpt-5.4-mini` · \~770ms

Strongest mini model. Near gpt-5.4 quality at lower cost and latency.

<a id="gpt-5.4-nano" />

<a id="gpt-5.4-nano-medium" />

### GPT-5.4 Nano

Cheapest GPT-5.4-class model for simple high-volume tasks.

| Effort       | ID                    | Latency  |
| ------------ | --------------------- | -------- |
| No reasoning | `gpt-5.4-nano`        | \~570ms  |
| Medium       | `gpt-5.4-nano-medium` | \~1200ms |

<a id="gpt-5.2" />

<a id="gpt-5.2-medium" />

<a id="gpt-5.2-instant" />

### GPT-5.2

GPT-5.2 family for conversational, analytical, and reasoning workloads.

| Effort       | ID                | Latency  |
| ------------ | ----------------- | -------- |
| No reasoning | `gpt-5.2-instant` | \~950ms  |
| Low          | `gpt-5.2-low`     | \~2200ms |
| Medium       | `gpt-5.2-medium`  | \~4000ms |
| High         | `gpt-5.2-high`    | \~6500ms |
| Extra high   | `gpt-5.2-xhigh`   | \~9000ms |

<a id="gpt-4.1" />

<a id="turbo-one" />

### GPT-4.1

`gpt-4.1` · \~800ms

Recommended for most scenarios. Also accepted as `turbo-one`.

<a id="gpt-4.1-mini" />

<a id="turbo-one-mini" />

### GPT-4.1 Mini

`gpt-4.1-mini` · \~600ms

Cheaper sibling of GPT-4.1. Best for simple workflow steps with light or no tool calling. Also accepted as `turbo-one-mini`.

## Anthropic

<a id="claude-sonnet-5" />

### Claude Sonnet 5

`claude-sonnet-5` · \~1400ms

Anthropic's most capable Sonnet model for coding, agents, and professional work.

<a id="claude-opus-4-7" />

### Claude Opus 4.7

`claude-opus-4-7` · \~1830ms

Anthropic's newest flagship. Step-change improvement in agentic coding and complex reasoning.

<a id="claude-sonnet-4-6" />

### Claude Sonnet 4.6

`claude-sonnet-4-6` · \~1520ms

Best combination of speed and intelligence. Near-opus quality at sonnet speed.

<a id="claude-opus-4-6" />

### Claude Opus 4.6

`claude-opus-4-6` · \~1870ms

Exceptional for complex reasoning and agent tasks.

<a id="claude-haiku" />

### Claude Haiku 4.5

`claude-haiku` · \~690ms

Fastest Claude model with near-frontier intelligence.

<a id="claude-sonnet" />

### Claude Sonnet 4.5

`claude-sonnet` · \~1500ms

Previous generation sonnet. Consider Claude Sonnet 4.6 or Sonnet 5 instead.

<a id="claude-opus" />

### Claude Opus 4.5

`claude-opus` · \~1900ms

Previous generation opus. Consider Claude Opus 4.6 or 4.7 instead.

## Google

<a id="gemini-3.1-pro" />

### Gemini 3.1 Pro

Google's most intelligent reasoning model. Latest update: February 2026.

| Effort | ID                      | Latency  |
| ------ | ----------------------- | -------- |
| Low    | `gemini-3.1-pro-low`    | \~3000ms |
| Medium | `gemini-3.1-pro-medium` | \~4000ms |
| High   | `gemini-3.1-pro-high`   | \~5000ms |

<a id="gemini-3.5-flash" />

<a id="gemini-3.5-flash-minimal" />

### Gemini 3.5 Flash

Frontier-class Gemini Flash model with configurable reasoning and better performance than Gemini 3 Flash.

| Effort  | ID                         | Latency  |
| ------- | -------------------------- | -------- |
| Minimal | `gemini-3.5-flash-minimal` | \~600ms  |
| Low     | `gemini-3.5-flash-low`     | \~800ms  |
| Medium  | `gemini-3.5-flash-medium`  | \~1200ms |

<a id="gemini-3.1-flash-lite" />

### Gemini 3.1 Flash-Lite

Fast, cost-efficient Gemini model with configurable reasoning. Latest update: May 2026.

| Effort  | ID                              | Latency  |
| ------- | ------------------------------- | -------- |
| Minimal | `gemini-3.1-flash-lite-minimal` | \~940ms  |
| Low     | `gemini-3.1-flash-lite-low`     | \~1100ms |
| Medium  | `gemini-3.1-flash-lite-medium`  | \~1700ms |
| High    | `gemini-3.1-flash-lite-high`    | \~2700ms |

## Mistral

<a id="mistral-large-latest" />

### Mistral Large

`mistral-large-latest` · \~1040ms

Mistral's flagship MoE. Multimodal, strong reasoning and tool use, EU-hosted.

<a id="mistral-medium-latest" />

### Mistral Medium

`mistral-medium-latest` · \~870ms

Frontier multimodal medium tier. 256K context, agentic and coding focus.

<a id="mistral-small-latest" />

### Mistral Small

`mistral-small-latest` · \~710ms

Unified small model — instruct, reasoning, and coding in one. Cheap workflow steps.

<a id="ministral-3-14b-latest" />

### Ministral 3 14B

`ministral-3-14b-latest` · \~700ms

Edge-class 14B with vision. Strong text + multimodal at small footprint.

<a id="ministral-3-8b-latest" />

### Ministral 3 8B

`ministral-3-8b-latest` · \~580ms

Edge-class 8B with vision. Cheap classification, routing, and inline calls.

<a id="ministral-3-3b-latest" />

### Ministral 3 3B

`ministral-3-3b-latest` · \~480ms

Tiniest Mistral tier. Simple intent classification and high-volume tasks.

<a id="codestral-latest" />

### Codestral

`codestral-latest` · \~900ms

Mistral's coding specialist. Tuned for code generation, completion, and refactoring tasks.

<a id="devstral-2-latest" />

### Devstral 2

`devstral-2-latest` · \~1200ms

Mistral's coding specialist v2. Strong on agentic coding and developer workflows.

<a id="mistral-nemo-12b-latest" />

### Mistral Nemo 12B

`mistral-nemo-12b-latest` · \~800ms

Open-weight 12B model. Good general-purpose option from the Mistral labs lineup.

<a id="leanstral-latest" />

### Leanstral

`leanstral-latest` · \~600ms

Mistral labs open-source model. Lean footprint for high-volume and edge use cases.

## xAI (Grok)

<a id="grok-4.6" />

### Grok 4.6

Latest xAI frontier model for coding, agentic tasks, and knowledge work.

| Effort     | ID                | Latency  |
| ---------- | ----------------- | -------- |
| Low        | `grok-4.6-low`    | \~900ms  |
| Medium     | `grok-4.6-medium` | \~1500ms |
| High       | `grok-4.6`        | \~2500ms |
| Extra high | `grok-4.6-xhigh`  | \~4000ms |

<a id="grok-4.5" />

### Grok 4.5

xAI frontier model for coding, agentic tasks, and knowledge work.

| Effort | ID                | Latency  |
| ------ | ----------------- | -------- |
| Low    | `grok-4.5-low`    | \~900ms  |
| Medium | `grok-4.5-medium` | \~1500ms |
| High   | `grok-4.5`        | \~2500ms |

## OpenRouter

Models routed through [OpenRouter](https://openrouter.ai) with configured provider fallback, so a request is retried against a backup provider if the primary one is unavailable.

<Note>
  OpenRouter models are available on the **US** platform. They are not available in the **EU** region, and a workspace can hide them by enabling the model-visibility restriction in its settings.
</Note>

<a id="openrouter-zai-glm-5.2" />

### GLM 5.2

Z.ai GLM 5.2 routed through OpenRouter.

| Effort       | ID                             | Latency |
| ------------ | ------------------------------ | ------- |
| No reasoning | `openrouter-zai-glm-5.2-none`  | \~400ms |
| High         | `openrouter-zai-glm-5.2`       | \~490ms |
| Extra high   | `openrouter-zai-glm-5.2-xhigh` | \~900ms |

<a id="openrouter-deepseek-v4-flash" />

### DeepSeek V4 Flash 0731

July DeepSeek V4 Flash release routed through OpenRouter on Baseten.

| Effort       | ID                                  | Latency  |
| ------------ | ----------------------------------- | -------- |
| No reasoning | `openrouter-deepseek-v4-flash-none` | \~450ms  |
| Low          | `openrouter-deepseek-v4-flash-low`  | \~500ms  |
| High         | `openrouter-deepseek-v4-flash`      | \~560ms  |
| Max          | `openrouter-deepseek-v4-flash-max`  | \~1100ms |

<a id="openrouter-deepseek-v4-pro" />

### DeepSeek V4 Pro

Higher-capability DeepSeek V4 model routed through OpenRouter.

| Effort       | ID                                | Latency  |
| ------------ | --------------------------------- | -------- |
| No reasoning | `openrouter-deepseek-v4-pro-none` | \~600ms  |
| Low          | `openrouter-deepseek-v4-pro-low`  | \~650ms  |
| High         | `openrouter-deepseek-v4-pro`      | \~700ms  |
| Max          | `openrouter-deepseek-v4-pro-max`  | \~1400ms |

<a id="openrouter-kimi-k3" />

### Kimi K3

MoonshotAI Kimi K3 routed through OpenRouter, preferring Baseten, then Morph, then DigitalOcean.

| Effort       | ID                        | Latency  |
| ------------ | ------------------------- | -------- |
| No reasoning | `openrouter-kimi-k3-none` | \~900ms  |
| Low          | `openrouter-kimi-k3-low`  | \~1100ms |
| High         | `openrouter-kimi-k3-high` | \~1500ms |
| Max          | `openrouter-kimi-k3`      | \~1800ms |

<a id="openrouter-minimax-m3" />

### MiniMax M3

`openrouter-minimax-m3` · \~540ms

MiniMax M3 routed through OpenRouter with configured provider fallback.

<a id="openrouter-step-3.7-flash" />

### Step 3.7 Flash

Step 3.7 Flash routed through OpenRouter with configured provider fallback.

| Effort | ID                               | Latency |
| ------ | -------------------------------- | ------- |
| Low    | `openrouter-step-3.7-flash-low`  | \~350ms |
| Medium | `openrouter-step-3.7-flash`      | \~400ms |
| High   | `openrouter-step-3.7-flash-high` | \~650ms |

## Availability

* **EU region** — models that aren't hosted in the EU are hidden, which covers every OpenRouter family.
* **Model visibility restriction** — a workspace can hide models trained in China. On DHL deployments this is enforced at the platform level and can't be turned off.
* **Deprecated models** — GPT-4o, GPT-5, GPT-5 Mini, GPT-5 (Reasoning), GPT-5.1 Instant, o4-mini, GPT-OSS 120B, Kimi K2, Gemini 2.5 Flash, Gemini 2.5 Flash Lite, Gemini 2.5 Pro, Gemini 3 Flash, Gemini 3 Pro, Gemini 3.1 Flash Live, Grok 4.3, and Grok 4.20 are no longer offered in the pickers. Configurations that already reference them keep running, but move them to a current family — the picker's replacement suggestion for each one is in its description.

## Next steps

<CardGroup cols={2}>
  <Card title="STT, TTS, and LLM" icon="sliders" href="../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md">
    Configure model selection inside a voice agent.
  </Card>

  <Card title="Prompts and tools" icon="message" href="../05-Voice-Agents/06-Prompts-and-Tools.md">
    Pair a model with a system prompt and tools.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/assets/models
