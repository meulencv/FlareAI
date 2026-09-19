---
title: "STT, TTS, and LLM Configuration"
description: "Configure speech-to-text, text-to-speech, and language model settings"
---

# STT, TTS, and LLM Configuration

> Configure speech-to-text, text-to-speech, and language model settings

Every voice agent relies on three core components: speech-to-text (STT) for understanding the caller, a language model (LLM) for generating responses, and text-to-speech (TTS) for speaking those responses aloud. This page covers how to configure each component for optimal performance.

## Speech-to-text (STT)

The STT engine transcribes the caller's speech in real time. Accuracy depends on language selection, domain context, and audio quality.

### Languages

Select the languages your agent should expect in the conversation. The STT engine uses this to optimize recognition accuracy. You can select multiple languages — when more than one is chosen, the engine detects which language is being spoken and adapts automatically.

Languages can be configured as:

* **Static** — Select specific languages from the list in the UI.
* **Dynamic** — Reference a [variable](../02-Workflows/07-Variables.md) that resolves to a language code at runtime, allowing different languages per call.

<AccordionGroup>
  <Accordion title="Supported languages">
    HappyRobot supports 50+ languages and regional variants:

    | Language   | Codes                                       |
    | ---------- | ------------------------------------------- |
    | English    | `en-US`, `en-GB`, `en-AU`, `en-NZ`, `en-IN` |
    | Spanish    | `es-ES`, `es-AR`, `es-MX`, `es-419`         |
    | Portuguese | `pt-PT`, `pt-BR`                            |
    | French     | `fr-FR`, `fr-CA`                            |
    | German     | `de-DE`, `de-CH`                            |
    | Chinese    | `zh-CN`, `zh-TW`, `zh-HK`                   |
    | Japanese   | `ja`                                        |
    | Korean     | `ko`                                        |
    | Arabic     | `ar`                                        |
    | Hindi      | `hi`                                        |
    | Italian    | `it`                                        |
    | Dutch      | `nl`                                        |
    | Russian    | `ru`                                        |
    | Polish     | `pl`                                        |
    | Turkish    | `tr`                                        |
    | Swedish    | `sv`                                        |
    | Danish     | `da`                                        |
    | Norwegian  | `no`                                        |
    | Finnish    | `fi`                                        |
    | Czech      | `cs`                                        |
    | Romanian   | `ro`                                        |
    | Hungarian  | `hu`                                        |
    | Bulgarian  | `bg`                                        |
    | Croatian   | `hr`                                        |
    | Greek      | `el`                                        |
    | Slovak     | `sk`                                        |
    | Ukrainian  | `uk`                                        |
    | Urdu       | `ur-PK`                                     |
    | Bengali    | `bn-BD`                                     |
    | Slovenian  | `sl-SI`                                     |
    | Vietnamese | `vi`                                        |
    | Indonesian | `id`                                        |
    | Malay      | `ms`                                        |
    | Thai       | `th`                                        |
    | Hebrew     | `he`                                        |
    | Filipino   | `fil`                                       |
    | Tamil      | `ta`                                        |

    And many more including Catalan, Estonian, Latvian, Lithuanian, Serbian, Georgian, Armenian, Kazakh, Uzbek, Kyrgyz, Nepali, Gujarati, Kannada, Malayalam, Punjabi, Telugu, and others.
  </Accordion>

  <Accordion title="Multi-language support">
    When multiple languages are selected, the STT engine detects the spoken language automatically. Full multi-language detection (simultaneous use in a single call) is supported for these languages:

    * English (`en` variants)
    * Spanish (`es` variants)
    * French (`fr` variants)
    * German (`de` variants)
    * Portuguese (`pt` variants)
    * Italian (`it`)
    * Dutch (`nl`)
    * Russian (`ru`)
    * Japanese (`ja`)
    * Hindi (`hi`)

    Other languages work best when selected individually or paired with one of the above.
  </Accordion>
</AccordionGroup>

<Note>
  For HappyRobot voices, the agent's **initial message** is spoken in the **first selected language** — or, when languages are set dynamically, the first language resolved at runtime. Order your languages so the most likely opening language comes first.
</Note>

### Transcription context

Provide contextual hints to the STT engine so it can better recognize domain-specific speech. This is free-form text that describes what the caller is likely to say.

**Examples:**

* "The caller will mention US city names and ZIP codes."
* "Expect freight industry terminology: BOL numbers, MC numbers, and carrier names."
* "The caller will spell out email addresses letter by letter."

Transcription context is capped at **5,000 characters**. [Variable](../02-Workflows/07-Variables.md) references don't count toward the limit — only the literal text you type does. Go over and the field shows how far over you are, and the node is marked incomplete until you trim it.

### Key terms

Add specific words or phrases the STT engine should prioritize. Key terms are especially useful for:

* Company and product names
* Industry jargon and acronyms
* Proper nouns that the engine might not recognize
* Alphanumeric codes (e.g., "MC-123456", "BOL-789")

You can add up to **100 key terms**, each up to **50 characters**. Empty rows are ignored, and variable references don't count toward a term's length. As with transcription context, exceeding either limit marks the node incomplete.

<Warning>
  An over-limit transcription context or key term list blocks [publishing](../02-Workflows/08-Versions-and-Publishing.md) — the node reports an error such as *"Transcription context exceeds 5,000 characters"* or *"Transcription keyterms exceed 100 entries"*. Existing agents saved before these limits existed keep working; you only need to trim them the next time you edit and publish the node.
</Warning>

### Numerals

When enabled (default), the transcription converts spoken numbers to digits — "twenty-five" becomes "25", "one hundred and fifty" becomes "150". Disable this if you need the spoken form preserved in the transcript.

### Denoised STT

Enable denoised STT to apply a voice-focus model that removes background speech and noise from the caller's audio before transcription. This improves accuracy in noisy environments but may slightly reduce audio quality or miss very quiet speech.

### End-of-turn detection

The end-of-turn (EOS) model determines when the caller has finished speaking, so the agent can begin responding. Choose the model that best fits your use case:

| Model               | Description                                                                                                                  |
| ------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| **English**         | Optimized for English conversations. Best latency and accuracy for English-only calls.                                       |
| **Multilingual v1** | Supports multiple languages. Use this when your agent handles non-English calls.                                             |
| **Text heuristics** | Rule-based detection that doesn't rely on an ML model. Most consistent behavior but less nuanced than model-based detection. |

## Text-to-speech (TTS)

The TTS engine converts the agent's text responses into spoken audio. Configuration covers voice selection, speed, volume, and ambient sound.

### Voices

Select one or more voices for the agent to use. When multiple voices are configured, one is randomly assigned per call — useful for A/B testing or adding variety. Voices can be configured as:

* **Static** — Select specific voices from the voice library in the UI.
* **Dynamic** — Reference a [variable](../02-Workflows/07-Variables.md) to choose voices at runtime.

Browse and preview available voices in **Assets > Voices**. Each voice has metadata including:

* **Provider** — HappyRobot, ElevenLabs, Cartesia, or Munsit
* **Language** — Primary language(s) the voice supports. HappyRobot voices support a range of regional accents, including English (US, UK), Spanish (Spain, Andalusia, Colombia, Mexico, Chile, Puerto Rico), Catalan, Galician, French, Italian, Portuguese, Arabic, and Swedish. [Munsit voices](../14-Assets/04-Voices.md#arabic-voices) cover Arabic — including Emirati, Saudi, and Gulf varieties — with Arabic–English code-switching
* **Gender** — Male or female
* **Style** — Voice characteristics and personality

HappyRobot voices also carry a **model version** (v0–v3); **v3** is the newest, highest-quality tier and is listed first in the selector. See [Voices](../14-Assets/04-Voices.md) for the full library.

#### Per-voice settings (V3)

In V3 workflows, each selected static voice can carry its own **agent name**, **gain**, and **speed**. When a voice is randomly assigned to a call, the agent uses the settings tied to that specific voice — allowing different personas, volumes, and speaking rates per voice.

To configure per-voice settings, click the settings icon next to a voice after adding it. The settings panel shows:

| Setting        | Description                                                             | Range    |
| -------------- | ----------------------------------------------------------------------- | -------- |
| **Agent name** | The name the agent uses when introducing itself for this voice          | Any text |
| **Gain**       | Volume multiplier for this voice, overriding the top-level gain setting | 0.5–1.5  |
| **Speed**      | Playback speed for this voice, overriding the top-level speed setting   | 0.7–1.2  |

Speed is available for ElevenLabs, Cartesia, Munsit, and HappyRobot **v3** voices. (Earlier HappyRobot voice versions and ElevenLabs v3 voices don't support speed.) Leave a field empty to fall back to the voice's default setting.

Once every selected voice has a per-voice name set, the top-level agent name field is hidden automatically to avoid duplication. Similarly, when all voices have explicit gain or speed settings, the top-level gain and speed controls are hidden.

<Note>
  **ElevenLabs v3 voices** (model family `eleven_v3`) do not support **gain** or **speed** adjustment — the controls are hidden when a v3 voice is selected, and a fixed expressive stability of `0.75` is used internally. Use a non-v3 ElevenLabs or Cartesia voice if you need per-voice gain or speed overrides.
</Note>

#### Dynamic voice overrides

When using a dynamic voice (a variable that resolves to a voice ID at runtime), you can supply optional per-call overrides below the variable field:

| Field     | Description                                                                                                  |
| --------- | ------------------------------------------------------------------------------------------------------------ |
| **Name**  | Agent name to use when this dynamic voice is selected. Supports variable templating.                         |
| **Gain**  | Volume multiplier for this voice. Overrides the voice's default gain. Supports variable templating.          |
| **Speed** | Playback speed multiplier for this voice. Overrides the voice's default speed. Supports variable templating. |

Leave any override field empty to fall back to the voice's default setting.

### Voice speed

Adjust the playback speed of the agent's speech:

| Setting  | Speed change         |
| -------- | -------------------- |
| 0.70     | -30% (slower)        |
| 0.80     | -20% (slower)        |
| 0.90     | -10% (slower)        |
| 0.95     | -5% (slower)         |
| **1.00** | **Normal (default)** |
| 1.05     | +5% (faster)         |
| 1.10     | +10% (faster)        |
| 1.15     | +15% (faster)        |
| 1.20     | +20% (faster)        |

### Voice gain

Adjust the volume of the agent's speech:

| Setting  | Volume change        |
| -------- | -------------------- |
| **1.00** | **Normal (default)** |
| 1.10     | 10% louder           |
| 1.20     | 20% louder           |
| 1.30     | 30% louder           |
| 1.40     | 40% louder           |
| 1.50     | 50% louder           |

### Background noise

Add ambient sound to the call to make the conversation feel more natural:

| Option                  | Description                                         |
| ----------------------- | --------------------------------------------------- |
| **Call center**         | Call center ambience (default)                      |
| **Coffee shop**         | Coffee shop background noise                        |
| **Office**              | Office environment sound                            |
| **Reception**           | Reception area ambience                             |
| **Random**              | Randomly selected from the above                    |
| **No background noise** | Silent background                                   |
| **Custom**              | Upload your own ambient audio in **Assets > Audio** |

### Time fillers

By default, the agent says brief filler phrases like "One moment..." while processing tool calls or generating longer responses. Disable time fillers if you prefer the agent to remain silent during processing.

### Transcribe keypresses

By default, caller keypresses (DTMF tones) are transcribed and treated as user turns, so the agent can react to them and an in-progress utterance is interrupted. Disable this if accidental keypresses are derailing conversations — for example, when callers tap their phone while talking — and the agent should ignore the tone instead.

Available in the **Advanced** section of inbound, outbound, and outbound-with-callback voice agent nodes.

## Language model (LLM)

The LLM generates the agent's responses based on the system prompt, conversation history, and tool results. Model selection is configured in the [prompt node](06-Prompts-and-Tools.md) nested inside the voice agent.

### Choosing a model

The model picker asks for up to three things:

| Control              | Description                                                                                                                                                        |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Model**            | The model family, grouped by provider. The picker shows each family's typical latency, marks the recommended families for voice, and flags newly added ones.       |
| **Reasoning effort** | How much the model deliberates before answering — from no reasoning up to max. Only shown for families that offer more than one level.                             |
| **Speed**            | **Standard** or **Fast**, where Fast uses the provider's priority tier. Only shown when your organization has priority capacity and the family has a Fast variant. |

Voice agents default to **gpt-5.6-luna** with no reasoning. **gpt-5.2-instant** and **claude-haiku** are the other recommended options for voice.

<Warning>
  Reasoning effort is audible on a call. Each step up adds hundreds of milliseconds to seconds before the agent starts speaking, so keep voice agents on **No reasoning** or **Low** unless the conversation genuinely needs deliberation — and move that work into a tool's child nodes where a pause is expected.
</Warning>

For the full catalog — every family, its effort levels, the exact IDs, and latencies — see [Models](../14-Assets/05-Models.md).

### Secondary model

Voice agents run a **secondary model** alongside the primary one to keep responses from stalling when the primary model is slow. The secondary model only takes over a turn once the primary passes a latency threshold — the rest of the time the primary answers and the secondary result is discarded.

The **Secondary Model** picker sits directly below **Model** in the prompt node of an inbound, outbound, or outbound-with-callback voice agent. You have three choices:

| Choice           | Behavior                                                                                                                                                                                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Default**      | **GPT-5.6 Luna**, routed through Azure on HappyRobot's credentials. Listed first in the picker as **Default · Azure**. This is what a prompt node uses when you never touch the setting, and it applies even if your organization brings its own key for that provider. |
| A model you pick | Overrides the default. The list holds the models available to your organization, minus anything in the same family as the primary model. The field also supports [variable](../02-Workflows/07-Variables.md) templating for runtime selection.                                     |
| **None**         | Turns the secondary model off, so every turn waits on the primary model. Choose it from the picker's source menu.                                                                                                                                                       |

The primary and secondary models must come from different model families. Picking the same family for both is rejected, and a prompt node saved that way can't be published until you change one of them.

<Note>
  The secondary model is voice-only. Text agents and non-agent prompt nodes generate every turn with the primary model.
</Note>

When the secondary model wins a turn, that assistant message carries an **LLM fallback** badge in the run transcript, and the badge tooltip names the provider and model that actually answered. See [Message indicators](../09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#message-indicators).

<Note>
  A node that explicitly selected a secondary model keeps it. Nodes left on the default follow the platform default, which is now GPT-5.6 Luna rather than GPT-4.1.
</Note>

### Dynamic model selection

The model field supports [variable](../02-Workflows/07-Variables.md) templating, so you can select the model dynamically at runtime. A dynamic value must resolve to a [model ID](../14-Assets/05-Models.md#model-ids) — the effort and speed are part of that ID, so `gpt-5.6-luna-high` and `fast-gpt-5.6-luna` are both valid values. This is useful for:

* Using different models for different customer tiers
* A/B testing model performance across calls
* Defaulting to a fast model and upgrading to a reasoning model for specific scenarios

### LLM source: model catalog or custom LLM server

By default a voice agent picks a model from HappyRobot's curated catalog of integrated providers (OpenAI, Anthropic, Google, Mistral, xAI) — this covers most use cases. Alternatively, you can route LLM traffic to your own Chat Completions-compatible endpoint (vLLM, Ollama, Groq, Together, Azure, OpenRouter, Cerebras, or any server implementing the same API). HappyRobot still handles voice orchestration and built-in tools like hangup and transfer, but all LLM calls go to your endpoint instead of the built-in models.

To use your own endpoint:

<Steps>
  <Step title="Add a Custom LLM Server credential">
    Go to **Integrations** and add a **Custom LLM Server** credential. Enter your endpoint URL (e.g. `https://your-server.com/v1`) and API key.
  </Step>

  <Step title="Switch the prompt node over">
    Open your voice agent's prompt node, open the **Model** picker, and choose the **Custom LLM server** command at the bottom of the list. The model and prompt fields are replaced by a credential selector.
  </Step>

  <Step title="Select the credential">
    Pick the **Custom LLM Credential** you created. The model, system prompt, and tool definitions from your workflow configuration are forwarded to your endpoint.
  </Step>
</Steps>

To go back to the curated catalog, open the credential selector and choose the **Model Catalog** command.

<Note>
  Your endpoint must accept chat completion requests in the OpenAI API format. Custom LLM servers are available for voice agents only — text agents use the built-in model selection. Built-in tools stay configurable in the prompt node's **Built-in** tab either way.
</Note>

## Next steps

<CardGroup cols={3}>
  <Card title="Prompts and tools" icon="message" href="06-Prompts-and-Tools.md">
    Write effective prompts and attach tools.
  </Card>

  <Card title="Inbound calls" icon="phone-arrow-down-left" href="02-Inbound-Calls.md">
    Configure inbound call handling.
  </Card>

  <Card title="Outbound calls" icon="phone-arrow-up-right" href="03-Outbound-Calls.md">
    Set up automated outbound calling.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/voice-agents/stt-tts-llm-configuration
