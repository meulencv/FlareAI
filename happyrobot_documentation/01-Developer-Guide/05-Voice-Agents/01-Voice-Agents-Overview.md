---
title: "Voice Agents Overview"
description: "Introduction to voice AI agents"
---

# Voice Agents Overview

> Introduction to voice AI agents

Voice agents handle real-time phone conversations powered by AI. They combine speech-to-text (STT), a language model (LLM), and text-to-speech (TTS) into a pipeline that listens, thinks, and speaks — all within a single phone call. You configure them as nodes inside a [workflow](../02-Workflows/01-Workflows-Overview.md), so every call benefits from the full automation engine: data extraction, integration actions, conditional logic, and more.

## What you can build

<CardGroup cols={2}>
  <Card title="Inbound call handling" icon="phone-arrow-down-left">
    Assign a phone number, configure an AI agent, and answer incoming calls automatically — extracting data, looking up records, and routing callers without human intervention.
  </Card>

  <Card title="Outbound campaigns" icon="phone-arrow-up-right">
    Trigger outbound calls via API or workflow. The agent dials, navigates phone menus, handles voicemail, and retries on failure — all with configurable limits and scheduling.
  </Card>

  <Card title="Outbound with callback" icon="phone-missed">
    Place outbound calls that support intelligent callbacks. If the recipient misses your call and calls back, the workflow resumes from a dedicated callback node with full context from the original attempt.
  </Card>

  <Card title="Multilingual conversations" icon="globe">
    Deploy agents that speak 50+ languages. Select multiple languages per agent and the STT engine adapts automatically. Voices are available from ElevenLabs and Cartesia across a wide range of languages.
  </Card>

  <Card title="Agent-free forwarding" icon="forward" href="07-Forward-call.md">
    Send an incoming call straight to a phone number with no agent on the line — the caller hears ringback and is connected as soon as someone answers.
  </Card>
</CardGroup>

## How a voice call works

<Steps>
  <Step title="Call connects">
    A call arrives on an assigned phone number (inbound) or is initiated by a workflow trigger (outbound). HappyRobot creates a session and routes the call to the voice agent.
  </Step>

  <Step title="STT transcribes speech">
    The caller's audio is streamed to the speech-to-text engine in real time. Transcription context and key terms improve accuracy for domain-specific vocabulary.
  </Step>

  <Step title="LLM generates a response">
    The transcript is sent to the language model along with the system prompt, conversation history, and any tool results. The model decides what to say — or which tool to call.
  </Step>

  <Step title="TTS speaks the response">
    The model's text response is converted to speech using the selected voice and played back to the caller. Background noise, voice speed, and gain are applied in real time.
  </Step>

  <Step title="Workflow continues">
    When the conversation ends, the workflow proceeds to downstream nodes — updating records, sending emails, writing data, or triggering additional automation.
  </Step>
</Steps>

## Voice agent types

HappyRobot offers three voice agent types, each designed for a different call pattern:

| Type                                                           | Use case                                                   | Trigger                                                 |
| -------------------------------------------------------------- | ---------------------------------------------------------- | ------------------------------------------------------- |
| [Inbound](02-Inbound-Calls.md)                         | Answer incoming calls on an assigned phone number          | Phone call arrives on a configured number               |
| [Outbound](03-Outbound-Calls.md)                       | Place calls to one or more phone numbers                   | API trigger, webhook, or workflow action                |
| [Outbound with Callback](04-Outbound-with-Callback.md) | Place calls and handle callbacks when recipients call back | API trigger with callback detection on assigned numbers |

## Key capabilities

<CardGroup cols={2}>
  <Card title="50+ languages" icon="language">
    Support for English, Spanish, French, German, Portuguese, Chinese, Japanese, Korean, Arabic, Hindi, and dozens more — with multi-language detection in a single call.
  </Card>

  <Card title="Real-time tools" icon="wrench">
    Agents can call tools mid-conversation — look up records, transfer calls, press DTMF digits, or run any workflow action — then resume speaking with the results.
  </Card>

  <Card title="Contact intelligence" icon="address-book">
    Automatically track interaction history per contact. Agents access past conversations and extracted data to personalize every call.
  </Card>

  <Card title="Recording and compliance" icon="circle-dot">
    Record calls with configurable disclaimers — a combined AI and recording disclosure, robotic or natural TTS, or custom audio. Disable recording entirely when not needed.
  </Card>

  <Card title="Business hours" icon="clock">
    Respect business hour schedules for outbound calls. Queue calls until business hours resume, or block them entirely outside configured windows.
  </Card>

  <Card title="Real-time classifiers" icon="tags">
    Classify caller sentiment and custom categories in real time during the conversation. Use classifications to drive downstream workflow logic.
  </Card>
</CardGroup>

## Next steps

<CardGroup cols={3}>
  <Card title="Inbound calls" icon="phone-arrow-down-left" href="02-Inbound-Calls.md">
    Set up agents to answer incoming calls.
  </Card>

  <Card title="Outbound calls" icon="phone-arrow-up-right" href="03-Outbound-Calls.md">
    Configure automated outbound calling.
  </Card>

  <Card title="STT, TTS, and LLM" icon="sliders" href="05-STT-TTS-and-LLM-Configuration.md">
    Tune speech, voice, and model settings.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/voice-agents/overview
