---
title: "EU AI Act and GDPR requirements"
description: "Disclosure and recording requirements for agents that interact with people in the EU"
---

# EU AI Act and GDPR requirements

> Disclosure and recording requirements for agents that interact with people in the EU

If your agents interact with people in the European Union, two sets of legal requirements apply: the transparency obligations of the EU AI Act and the GDPR rules governing the recording and storage of conversations. Both apply to every channel. Voice calls and chatbot conversations are equally in scope, along with SMS, WhatsApp, and email. The determining factor is whether the workflow is directed at people in the European Union, not where your company is established.

<Warning>
  This page describes how these requirements map to HappyRobot platform features. It is not legal advice. Your legal team should review disclosure wording, lawful basis decisions, and retention policies for your specific deployment.
</Warning>

## Responsibility model

When HappyRobot implementation teams build or configure workflows on your behalf, the EU AI Act disclosure and the GDPR recording notice are activated by default on all workflows. These defaults reduce risk, but they do not transfer it: under the EU AI Act your organization is the deployer of the AI system, and under the GDPR it is the controller of the personal data processed in conversations. In both roles, your organization remains ultimately responsible for compliance.

In practice, your organization should:

* Verify the disclosure remains enabled on every EU-facing workflow, including workflows your team creates or modifies after handover.
* Approve the disclosure and recording wording with your legal team.
* Maintain the lawful basis documentation and privacy notices that the platform configuration supports but cannot provide for you.

## What the regulations require

**EU AI Act.** Article 50 requires that people are informed they are interacting with an AI system at the latest at the moment of first interaction, unless this is already obvious from the context. A phone call does not qualify as obvious, and chatbots should be treated the same way: the defensible position is an explicit disclosure at the start of every conversation.

**GDPR.** Recording a call or storing conversation transcripts is processing that involves personal data. Your organization needs a lawful basis (typically consent or a documented legitimate-interest assessment), notice at the time of processing, retention limits consistent with your privacy policy, and a process for data subject rights such as access and erasure. On voice, the notice **must be played at the start of the call**. On text channels, it **must be stated in your privacy policy** and, for chatbots, in or near the widget.

### Workflows intended for the US only

These obligations attach to workflows that are directed at people in the EU. A workflow designed and operated for a US audience, with US phone numbers and a US business context, does not need the EU disclosure. A small number of unintended calls involving EU-located callers does not by itself bring the workflow into scope: incidental contact is not targeting, and you do not need to add the disclosure because a workflow occasionally reaches someone in the EU. Reassess if EU contacts become a regular part of the workflow's traffic, or if you deliberately start routing EU numbers to it. At that point, treat the workflow as EU-facing and enable the disclosure.

## Voice agents

There are three ways to deliver the disclosure at the start of a call, listed here from most to least robust.

**Pre-recorded disclaimer (recommended).** Select **AI and recording disclosure** in the **Recording disclaimer** setting on the voice agent node. It plays a spoken disclosure at the very start of the call, before the agent's initial message, covering both the AI disclosure and the recording notice. The standard wording is a single sentence, spoken in the conversation language:

> "This is a recorded call with an AI agent."

On EU deployments this option is the default for new inbound, outbound, and callback voice agent nodes, and selecting anything else raises a warning on the node. Leave **Recording language** on **Auto** to play the disclosure in the call's conversation language; pin a specific language, or template the language code from a [variable](../02-Workflows/07-Variables.md), when the language is decided upstream rather than by the conversation.

Because the disclaimer is node configuration rather than prompt content, prompt edits, greeting changes, and [experiment variants](../10-Experiments/01-Experiments.md) cannot remove it, and it does not stop if the caller interrupts or it picks up background noise. Where your legal team requires specific wording, the **Custom recording** style accepts an approved audio asset that plays verbatim on every call; for recorded calls with EU numbers, it should cover both notices.

**Initial message protected from interruptions.** Put the disclosure at the start of the agent's **Initial message** (**Receiving initial message** for inbound calls) on the [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md), and enable **Protect initial message from interruptions** so the agent finishes the disclosure before it starts listening. The initial message is fixed text spoken verbatim, not model output, so the wording is guaranteed. The interruption protection is what makes this option defensible: without it, a caller who talks over the greeting has not been informed.

**Prompt.** Instruct the agent in the system prompt to open every call with the disclosure. This is the weakest of the three options: the sentence is generated on each call rather than guaranteed, the caller can interrupt it, and a later prompt edit can silently drop it. Use it only when neither of the other two options fits, and verify in transcripts that the disclosure is actually being spoken.

If recordings are not needed, turn off the **Record call** toggle on the voice agent node and no audio is stored; the AI disclosure obligation still applies to the conversation itself.

See [Recordings](../09-Runs-and-Monitoring/04-Recordings.md) and the configuration reference in [Inbound calls](../05-Voice-Agents/02-Inbound-Calls.md#recording-and-disclaimers).

## Chatbots

[Chatbot agents](../06-Text-Agents/05-Chatbot.md) are inbound only: the visitor writes first, so the disclosure must be present from the start of the conversation. Choose one of the two options:

* **Label the widget.** Set the **Agent name** shown in the widget header so the nature of the agent is clear, for example "Acme AI Assistant" rather than "Support Team".
* **Disclose in the first response.** Use the **Deliver Text Session Message** node to send a fixed opening line before any AI-generated reply: "Hi, you're chatting with \[Company]'s AI assistant. How can I help?"

## SMS and WhatsApp

The disclosure goes in the first message the agent sends. Place it in the configured message template rather than relying on the model to produce it.

* **SMS.** Open the first message with the disclosure and keep it within a single segment: "Hi \[Name], this is \[Company]'s AI assistant. \[Reason]."
* **WhatsApp.** Business-initiated conversations start from a pre-approved message template, so include the disclosure in the template text: "Hi \[Name], you're chatting with \[Company]'s AI assistant about \[reason]."

## Email

A short footer on every email is sufficient: "This email was generated with the help of AI on behalf of \[Company]." Add it to the email body template so it cannot be dropped by the model.

<Info>
  HappyRobot supports full EU data residency for customers that require it, with the platform deployed in EU regions. Contact your account team if your GDPR posture requires EU-resident processing.
</Info>

## Compliance checklist

| Requirement                           | Voice                                                                                                                    | Chatbot                                                                                        |
| ------------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| AI disclosure at first interaction    | **AI and recording disclosure** enabled (default on implemented workflows), or an interruption-protected initial message | Widget **Agent name** states AI, or a fixed first message via **Deliver Text Session Message** |
| Recording / storage notice            | Covered by **AI and recording disclosure**, or a custom approved asset                                                   | Notice in privacy policy and widget                                                            |
| Lawful basis documented               | Consent or legitimate-interest assessment on file                                                                        | Consent or legitimate-interest assessment on file                                              |
| Retention aligned with privacy policy | Recording retention reviewed                                                                                             | Transcript retention reviewed                                                                  |

---

Fuente original: https://docs.happyrobot.ai/compliance/eu-ai-act-and-gdpr
