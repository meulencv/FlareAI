---
title: "Audio audits"
description: "Analyze transcription accuracy, conversation quality, and acoustic metrics for voice agent calls"
---

# Audio audits

> Analyze transcription accuracy, conversation quality, and acoustic metrics for voice agent calls

Audio audits give you a detailed view of the technical quality of your voice agent calls — how accurately user speech was transcribed, how smoothly conversations flowed, how responsive the agent was, and how clean the audio sounded. All metrics are computed automatically from call recordings and transcripts with no configuration required.

Navigate to **Audio Audits** in the workflow editor to access this page.

## Date range and granularity

Use the date selector at the top of the page to control the time window. Available presets: **Today**, **Last 7 Days**, **Last Week**, and **Last Month**. Hourly granularity is used for "Today"; daily granularity for all other ranges.

Click the refresh button to manually reload all data.

## Sections

The page is organized into four metric sections. Click any KPI card to expand a time-series chart below it, optionally split by language, voice, or LLM model.

### Transcription metrics

Measures how accurately user speech was understood.

| Metric                       | Description                                                                                                                                                                 |
| ---------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Semantic WER**             | Meaning-level word error rate for user speech. Measures whether words were transcribed in a way that preserves meaning — not just exact character matches. Lower is better. |
| **Leakage suppression rate** | Share of leaked echo or background user words that were successfully suppressed before they reached the LLM. Higher is better.                                              |

#### Semantic phrase insights

When you click the **Semantic WER** card, a phrase insights panel appears below the chart. This panel shows the specific phrases that contributed most to transcription errors across the selected time period.

Each row represents a phrase the system expected to hear (the reference phrase), and shows:

* **Occurrences** — how many times the phrase appeared in sessions
* **Error share** — what fraction of the total Semantic WER this phrase accounts for
* **Top transcription** — the most common incorrect transcription the model produced
* **Error types** — the categories of errors (e.g., substitution, insertion, deletion)
* **Alternate transcriptions** — other incorrect variants observed

Use the phrase insights panel to identify terms, names, or domain-specific words that the STT model struggles with most — these are strong candidates for pronunciation guides, custom vocabulary, or prompt-level cues.

### Conversational metrics

Measures the flow and dynamics of conversations.

| Metric                       | Description                                                                                             |
| ---------------------------- | ------------------------------------------------------------------------------------------------------- |
| **Interruptions**            | Percent of assistant messages cut off by the user before completing.                                    |
| **Natural cuts**             | Percent of assistant messages where the user started speaking at a natural pause (not an interruption). |
| **Fillers**                  | Percent of user messages classified as filler speech (e.g., "uh", "um", "yeah").                        |
| **Assistant speaking ratio** | Fraction of total speaking time used by the assistant. A ratio near 0.5 is typically balanced.          |

Charts in this section can be split by language or by LLM model to compare behavior across model versions.

### Latency

Shows average response latency broken down into pipeline components. This helps identify which stage contributes most to perceived delay.

The chart can be filtered by LLM model to compare latency across different models.

### Acoustics

Measures the physical quality of audio signals on both sides of the call.

| Metric                        | Description                                                                                    |
| ----------------------------- | ---------------------------------------------------------------------------------------------- |
| **User speech loudness**      | Average LUFS for user speech segments. Useful for detecting quiet or overly loud caller audio. |
| **User speech quality**       | DNSMOS quality score for user speech. Higher is better.                                        |
| **Assistant speech loudness** | Average LUFS for assistant speech segments.                                                    |
| **Assistant speech quality**  | DNSMOS quality score for assistant speech. Higher is better.                                   |

Charts can be split by voice or language to compare audio quality across voices and accents.

## Audio quality flags

The flags table at the bottom of the page lists automatically detected quality issues. Each row shows:

* The flag type and description
* How many sessions triggered the flag in the selected period
* The failure rate as a percentage of total sessions

Click a row to open a **flag detail sidebar** showing the specific sessions that triggered the flag. From there you can follow a link directly to the corresponding run for full transcript and audio review.

Flag types include:

| Flag                            | Description                                           |
| ------------------------------- | ----------------------------------------------------- |
| **High word error rate**        | User audio had poor transcription accuracy            |
| **Poor audio quality**          | Audio clarity was degraded                            |
| **Echo detected**               | Echo was present in the user audio                    |
| **Background speaker**          | Background speech interfered with transcription       |
| **Very quiet audio**            | Audio volume was too low                              |
| **Number transcription errors** | Numbers in user speech were frequently mistranscribed |
| **Empty session**               | No speech was detected in the session                 |

## Next steps

<CardGroup cols={2}>
  <Card title="Automated audits" icon="magnifying-glass" href="03-Automated-audits.md">
    See how every run is evaluated against behavioral quality criteria.
  </Card>

  <Card title="Issues" icon="flag" href="05-Issues.md">
    Track and resolve quality problems surfaced by audits and flags.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/evaluate/audio-audits
