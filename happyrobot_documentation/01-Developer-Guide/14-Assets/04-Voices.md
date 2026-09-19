---
title: "Voices"
description: "Browse and preview text-to-speech voices for your agents"
---

# Voices

> Browse and preview text-to-speech voices for your agents

The Voices page is your library of text-to-speech voices available for voice agents. Browse, filter, and preview voices to find the right fit for your agent's persona. For details on configuring voices within agents, see [STT, TTS, and LLM Configuration](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#voices).

## Browsing voices

The voice library displays all available voices in a searchable, filterable list. Use the following filters to narrow your selection:

| Filter       | Options                             |
| ------------ | ----------------------------------- |
| **Gender**   | Male, Female, Neutral               |
| **Language** | Filter by supported language        |
| **Search**   | Real-time search across voice names |

The same **Gender** and **Language** facets are available in the voice picker on a voice agent node, so you can narrow the list without leaving the workflow editor.

## Previewing a voice

Select any voice to open its detail panel with two tabs:

### Text to Speech

Type custom text (up to 250 characters) and click play to hear the voice speak it. An audio waveform displays during playback so you can visualize the output. Use this to test how the voice handles your specific terminology, greetings, or conversation style.

Click the **download** icon next to play to save the generated audio as a WAV file. The file is named after the voice (e.g., `Aria.wav`), so you can keep a reference clip for review, share it with stakeholders, attach it to tickets, or A/B test voices outside the platform without re-running the playground.

For **HappyRobot voices**, an accent selector appears above the text input. You can preview the voice in any supported regional accent — for example, a voice may have a native English (US) accent but also support English (UK), English (Australia), Spanish (Mexico), and more. Native accents (the voice's original training language) are listed first, followed by cloned accents. Select an accent and click play to hear how it sounds before choosing one for your agent.

HappyRobot voices are available in multiple model versions (**v0**, **v1**, **v2**, and **v3**). The model version is shown as a badge next to the voice and in the Voice Info tab when you select a voice, and voices carrying the newest model are listed first in the voice selector.

**v3 voices** are the latest generation of HappyRobot voices. They are no longer in preview — the library shows them with a plain **v3** badge like every other model version. They cover a wide range of languages and regional accents — including English (US, UK), Spanish (Spain, Andalusia, Colombia, Mexico, Chile `es-CL`, Puerto Rico `es-PR`, Argentina `es-AR`), Catalan `ca-ES`, Galician `gl-ES`, French, Italian, Portuguese (Brazil, Portugal), Croatian `hr-HR`, Hungarian `hu-HU`, Chinese (Mandarin) `zh-CN`, Japanese `ja-JP`, Modern Standard Arabic `ar-001`, and Swedish — and, unlike ElevenLabs v3 voices, they support per-voice **speed** and **gain** adjustment. When a v3 voice offers an accented variant of a language, the generic (unaccented) option is hidden so you pick an explicit accent.

The v3 catalog is expanded over time, and individual voices are occasionally retired. A retired voice disappears from the library but keeps working in any workflow version that already references it — pick a replacement the next time you edit the agent.

<Warning>
  **HappyRobot V1 voices are being deprecated on June 12, 2026.** Workflow versions that use a V1 voice display a **V1 voices deprecation** badge in the workflow editor. Migrate those agents to V2 voices before that date. Any workflow version still using a V1 voice after the deprecation will be automatically reassigned to the equivalent V2 voice with no service disruption.
</Warning>

### Arabic voices

**Munsit** is a text-to-speech provider specialized in Arabic. Four Emirati Munsit voices ship with the platform — **Majed**, **Abdulaziz**, **Aisha**, and **Noor** — and are available to every workspace. Munsit voices speak Arabic and handle Arabic–English code-switching, and they support per-voice **speed** and **gain** adjustment.

The language filter now distinguishes Arabic varieties instead of offering only Modern Standard Arabic:

| Accent                   | Locale   |
| ------------------------ | -------- |
| Arabic (Modern Standard) | `ar-001` |
| Arabic (Emirati)         | `ar-AE`  |
| Arabic (Saudi)           | `ar-SA`  |
| Arabic (Gulf / Khaleeji) | —        |

Existing Arabic voices are classified from the accent metadata their provider reports. Varieties outside this list fall back to general Arabic.

### Voice Info

View the voice's metadata including gender, supported language, accent characteristics, quality ratings, and description. The description gives a short summary of the voice's character and tone — for example, "Expressive female voice with a joyful, uplifting tone." This helps you compare voices and pick the best match for your agent's persona and target audience.

## Using voices in agents

Voices are configured in the voice agent node settings. Key points:

* **Single voice** — Select one voice for consistent agent identity across all calls.
* **Multiple voices** — Select more than one voice to have HappyRobot randomly assign a voice per call. This is useful for A/B testing different voices to measure their impact on call outcomes.
* **Static or dynamic** — Set voices statically in the UI or dynamically via [variables](../02-Workflows/07-Variables.md) that resolve at runtime. Dynamic selection lets upstream workflow logic determine the voice based on caller data or other conditions.

For the full configuration reference, see [STT, TTS, and LLM Configuration](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md).

## Listing voices with the API

`GET /voices` returns the voice catalog available to your workspace, so you can resolve a voice ID without opening the platform. Use the returned `id` in a workflow's `agent.voices` configuration.

<CodeGroup>
  ```bash cURL theme={null}
  curl "https://platform.happyrobot.ai/api/v2/voices?language=en-GB" \
    -H "Authorization: Bearer hr_..."
  ```

  ```ts TypeScript SDK theme={null}
  const voices = await client.voice.list({ language: "en-GB" });

  for (const voice of voices) {
    console.log(voice.id, voice.name, voice.locales);
  }
  ```
</CodeGroup>

The optional `language` filter accepts either form:

* A **language prefix** such as `en` or `es` matches every accent of that language.
* A **locale or accent key** such as `en-GB` or `es-MX` matches only that locale.

Matching ignores case, and `_` is treated the same as `-` (`en_GB` and `en-GB` behave identically). Omit the parameter to list every voice.

Each voice in the response contains:

| Field               | Description                                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `id`                | The voice ID to use in `agent.voices` configuration                                                                   |
| `name`              | Display name shown in the voice library                                                                               |
| `provider`          | `happyrobot`, `elevenlabs`, `elevenlabs-non-streaming`, `cartesia`, or `munsit`                                       |
| `provider_voice_id` | Provider-specific voice ID, when available                                                                            |
| `model_id`          | Provider model the voice runs on, when available                                                                      |
| `model_family`      | `happyrobot`, `turbo`, `flash`, `eleven_v3`, or `sonic`                                                               |
| `language`          | The voice's stored primary language                                                                                   |
| `languages`         | Language prefixes the voice supports, including its primary language                                                  |
| `locales`           | Specific locales and accent keys the voice supports — any of these values can be passed back as the `language` filter |
| `gender`            | `male` or `female`                                                                                                    |

Requesting the catalog requires an API key whose role can view voices. For the SDK method signature, see [Voices](../../02-Developer-Tools/02-TypeScript-SDK/10-Resources.md#voices) in the SDK reference.

## Next steps

<CardGroup cols={3}>
  <Card title="STT, TTS, and LLM" icon="sliders" href="../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md">
    Full reference for speech and model configuration.
  </Card>

  <Card title="Inbound calls" icon="phone-arrow-down-left" href="../05-Voice-Agents/02-Inbound-Calls.md">
    Configure agents to handle incoming calls.
  </Card>

  <Card title="Outbound calls" icon="phone-arrow-up-right" href="../05-Voice-Agents/03-Outbound-Calls.md">
    Set up automated outbound calling.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/assets/voices
