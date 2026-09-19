---
title: "Outbound Calls"
description: "Set up automated outbound calling campaigns"
---

# Outbound Calls

> Set up automated outbound calling campaigns

Outbound voice agents place calls to one or more phone numbers on your behalf. You configure the destination, caller ID, voicemail behavior, retry logic, and scheduling — then trigger the workflow via API, webhook, or another workflow action. Outbound calls are rate-limited per organization to manage concurrency and comply with carrier requirements.

## Setting up an outbound voice agent

<Steps>
  <Step title="Create a workflow with a trigger">
    Outbound workflows are typically started by a **Webhook** trigger or an **API** call. The trigger payload provides the data your agent needs — phone numbers, customer names, reference IDs, etc.
  </Step>

  <Step title="Add an outbound voice agent node">
    Add an **Outbound Voice Agent** action node. This node handles dialing, agent configuration, voicemail detection, and call behavior.
  </Step>

  <Step title="Configure destination and caller ID">
    Set the **To** field with the recipient phone number(s) and select a **From number** from your organization's phone numbers. Both fields support [variables](../02-Workflows/07-Variables.md) for dynamic values from the trigger payload.
  </Step>

  <Step title="Configure agent behavior">
    Set the agent's prompt, voice, language, and all call settings — recording, voicemail handling, business hours, and more.
  </Step>

  <Step title="Add downstream nodes">
    After the voice agent, add follow-up actions that process the conversation results — update a CRM, send a summary email, trigger another workflow, or branch based on the call outcome.
  </Step>
</Steps>

## Configuration reference

### Destination and caller ID

The destination settings control who the agent calls and what caller ID the recipient sees. Getting these right is critical — a wrong number wastes resources, and an unfamiliar caller ID means people won't pick up.

**To** — The phone number(s) to dial. This almost always comes from a [variable](../02-Workflows/07-Variables.md) in the trigger payload — for example, `@trigger.phone_number` when a webhook passes in the number to call. You can also hard-code a number for testing. At least one number is required.

**To extension** — An extension to dial after the call connects. The agent waits for the call to connect, then sends DTMF tones for the extension. Useful when calling into a business PBX system where you need to reach a specific person or department — for example, `@trigger.extension` or a fixed extension like `"4521"`.

**From number** — The caller ID shown to the recipient. Select from phone numbers registered in your organization's [telephony settings](https://docs.happyrobot.ai/settings). This is required — outbound calls cannot be placed without a valid from number. Choose a number with the same area code as your recipients when possible, since people are more likely to answer local numbers.

**Verified caller ID** — An optional override that replaces the standard from number as the displayed caller ID. The field has two modes:

* **Verified** (default) — Pick a number from the dropdown of completed verified caller IDs. If a saved static value no longer matches a verified number, a warning is shown so you can clear it before placing calls that would otherwise fail.
* **Dynamic** — Click **Use a dynamic value** to enter a templated value with variables (for example `@trigger.caller_id` or a literal `{{...}}`). Use this when you pick the caller ID at runtime, have many verified numbers, or verify on a carrier whose numbers don't appear in the dropdown. Dynamic values are not checked against your verified caller IDs — calls fail if the resolved number isn't actually verified.

Verify external numbers from **Assets > Telephony > Verified Numbers** — see [Verified numbers](../14-Assets/03-Telephony.md#verified-numbers) for the self-serve verification flow. Use this when you need to show a specific number to the recipient that differs from the actual originating number — for example, showing a customer's dedicated support line as the caller ID while routing through a shared SIP trunk.

### Agent identity

The agent section defines the conversational identity — who the agent is, what language it speaks, and what it sounds like. These are configured the same way as [inbound agents](02-Inbound-Calls.md#agent-identity).

**Prompt** — The system prompt is configured in the [prompt node](06-Prompts-and-Tools.md) nested inside the voice agent. For outbound calls, the prompt usually includes the reason for the call, talking points, and what information to collect. The agent also has an **initial message** — the first thing it says when the recipient picks up (e.g., "Hi, this is Sarah from Acme Freight. I'm calling about load number 4521.").

**Languages** — Select the language(s) the agent expects the recipient to speak. Can be static or dynamic via [variables](../02-Workflows/07-Variables.md). See the [full language list](05-STT-TTS-and-LLM-Configuration.md#languages).

**Voices** — Choose the TTS voice(s). When multiple are selected, one is randomly assigned per call. Browse and preview voices in **Assets > Voices**.

### Recording and disclaimers

Recording configuration works the same as for [inbound agents](02-Inbound-Calls.md#recording-and-disclaimers). Calls are recorded by default, and you can enable a disclaimer before the agent speaks.

Choose a **Recording disclaimer** option to control how the disclaimer sounds:

* **AI and recording disclosure** — A pre-recorded disclosure covering both the AI notice and the recording notice. **Recording language** defaults to **Auto** (the call's conversation language) and can be pinned to a specific language or templated from a [variable](../02-Workflows/07-Variables.md). Required for EU-facing calls — see [EU AI Act and GDPR requirements](../17-Compliance/01-EU-AI-Act-and-GDPR-requirements.md).
* **Recording robotic disclosure** — Standard TTS. No extra configuration needed.
* **Recording natural disclosure** — Natural-sounding TTS. Requires a **recording language** to be selected.
* **Custom recording** — Your own disclaimer, either as a **Static** audio asset from **Assets > Audio** or as a **Dynamic** templated string that the TTS engine reads at runtime.
* **No disclaimer** — The agent speaks first; nothing plays before it.

<Tip>
  For outbound calls, the recording disclaimer plays immediately after the recipient picks up and before the agent's initial message. Keep it brief so you don't lose the recipient's attention.
</Tip>

### Error handling

**Gracefully handle invalid number** — When enabled, an invalid destination phone number surfaces as an error in the node output and the workflow continues after retries are exhausted. When disabled (default), an invalid number causes the node to fail and halts the workflow. Enable this when you want to handle bad phone numbers in downstream nodes — for example, to flag invalid data in your CRM, send an alert, or skip to the next contact in a batch.

### Voicemail handling

When the agent reaches voicemail instead of a live person, the **voicemail action** determines what happens next. This is one of the most important outbound settings — the right voicemail strategy can significantly impact callback rates and campaign effectiveness.

**Hang up** — The agent disconnects without leaving a message. Use this when voicemail messages aren't part of your strategy, or when you plan to retry the call instead. The session ends with a `voicemail` status, which downstream workflow logic can check.

**Fixed message** — The agent plays a specific, pre-written voicemail message. Write the exact text in the **voicemail prompt** field, and the TTS engine reads it aloud. This gives you full control over the message:

> "Hi, this is a call from Acme Freight about a shipment pickup. Please call us back at 555-0100 at your earliest convenience. Thank you."

Use this when you need consistent, approved messaging across all calls — such as compliance-sensitive industries.

**AI message** — The agent generates a voicemail message on the fly, guided by instructions you provide in the **voicemail prompt**. This allows the message to be personalized with conversation context and variables. For example:

> "Leave a brief voicemail mentioning that we're calling about load @trigger.load\_id and ask them to call back at @trigger.callback\_number. Keep it under 20 seconds."

The agent uses the LLM to compose and speak a natural-sounding message. This is useful when each voicemail needs to be different based on the specific call context.

### Phone tree navigation

When calling businesses, the agent often hits an automated phone menu (IVR) before reaching a human. Phone tree navigation equips the agent with a `press_digit` tool that sends DTMF tones to navigate these menus.

This is configured in the prompt node's **Built-in** tab, not on the agent node. Open the prompt node inside the agent, switch to **Built-in**, and expand **Press digit**.

**Press digit** — Enable this to give the agent the ability to press digits during the call. When disabled (the default), the agent can only speak — it cannot interact with IVR systems.

**Instructions** — Instructions that tell the agent how to navigate the menu, in the expanded **Press digit** row. Be as specific as possible about the expected menu structure:

> "When you hear the main menu, press 1 for English. Then press 3 for the dispatch department. If asked for an account number, enter @trigger.account\_number followed by the pound key. If you reach a person, proceed with the normal conversation."

The agent listens to the IVR prompts, follows your instructions, and presses the appropriate digits. It switches to normal conversation mode once it reaches a live person.

<Info>
  Phone tree navigation works best with clear, specific instructions. If the IVR changes frequently, consider using more flexible instructions like "Listen to the options and press the number for the billing or accounts department."
</Info>

### Audio environment

Audio settings control what the call sounds like. These are configured identically to [inbound agents](02-Inbound-Calls.md#audio-environment):

* **Background noise** — Ambient sound (default: Call center). Options: Call center, Coffee shop, Office, Reception, Random, No background noise, or a custom audio asset.
* **Voice speed** — 0.70 to 1.20 (default: 1.00 Normal).
* **Voice gain** — 1.00 to 1.50 (default: 1.00 Normal).
* **Disable time fillers** — Suppress "One moment..." phrases while processing.

**Stay silent** — allowing the agent to stay quiet when appropriate — now lives in the prompt node's **Built-in** tab. See [Voice agent built-in tools](../04-Tools/04-Built-in-Tools.md#voice-agent-built-in-tools).

### Transcription accuracy

Transcription settings work identically to [inbound agents](02-Inbound-Calls.md#transcription-accuracy). Key settings:

* **Transcription context** — Narrative hints about expected speech patterns. Up to 5,000 characters.
* **Key terms** — Specific words to prioritize for recognition. Up to 100 terms of 50 characters each.
* **Enable denoised STT** — Voice focus model for noisy environments.
* **Numerals** — Convert spoken numbers to digits (default: enabled).
* **End-of-turn detection** — English, Multilingual v1, or Text heuristics.

For outbound calls, pay special attention to transcription context — the people you're calling may be in noisy environments you can't predict. Denoised STT can help when recipients answer from warehouses, loading docks, or while driving.

### Call duration and transfer

**Max call duration** — The maximum length of the call in seconds before it's automatically terminated. Defaults to 600 seconds (10 minutes). Set this based on your expected conversation length:

* Simple confirmation calls: 120–180 seconds
* Standard business conversations: 300–600 seconds
* Complex negotiations or data collection: 900–1200 seconds

This protects against edge cases where the agent gets stuck in a loop or the conversation goes off-track. It also caps costs for per-minute pricing.

**Max duration transfer number** — Instead of abruptly ending the call when the timer expires, transfer the caller to a human agent or backup number. The agent can be prompted to say something like "I need to connect you with a colleague who can continue helping you" before the transfer happens.

**Max duration notices** — Schedule up to five instructions that reach the agent a set number of seconds before the limit, so it can wrap up on its own terms. See [Max duration notices](02-Inbound-Calls.md#call-duration-limits).

### User-to-User Information (UUI)

User-to-User Information (UUI) passes custom data to the receiving system as SIP headers when the outbound call is placed. Use it to share context — tracking IDs, account numbers, routing hints, or other metadata — with the endpoint that answers the call. Configure it in the node's **Advanced** settings.

| Setting                    | Description                                                                                                                                                                       |
| -------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Data format**            | **JSON Object (structured data)** — define data as key-value pairs. **Plain Text** — send a single free-form text value.                                                          |
| **Key-value pairs**        | *(JSON format)* The data to send, entered as key-value pairs. Both keys and values support [variables](../02-Workflows/07-Variables.md) — type `@` to insert dynamic values.                 |
| **Enter text**             | *(Plain text format)* The raw text payload to send. Supports variables.                                                                                                           |
| **Encoding**               | How the value is put on the wire. See [Encoding options](#encoding-options).                                                                                                      |
| **Omit purpose parameter** | The header normally ends with `;purpose=app`. Turn this on when the receiving system expects only `;encoding=…`, or rejects the purpose parameter outright.                       |
| **Genesys compatibility**  | Enable to set the UUI protocol discriminator for compatibility with Genesys contact center platforms. Not available with **Pre-encoded hex**, where the discriminator is ignored. |

#### Encoding options

| Option              | Behavior                                                                                                                                                                                                                                                                        |
| ------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Hex**             | Encodes your value to hex before sending it. Default.                                                                                                                                                                                                                           |
| **Pre-encoded hex** | Sends your value unchanged as `;encoding=hex`. Pick this when the value is *already* hex — for example, a User-to-User header you read off an inbound call. Choosing plain **Hex** for such a value encodes it a second time, and the receiving system reads the wrong payload. |
| **ASCII**           | Sends your value unchanged.                                                                                                                                                                                                                                                     |
| **Base64**          | Encodes your value to Base64 before sending it.                                                                                                                                                                                                                                 |

<Note>
  **Pre-encoded hex** is only offered when **Data format** is **Plain Text**. In JSON mode the payload is a marshalled object, so there is nothing pre-encoded to pass through — switching the data format back to JSON resets the encoding to **Hex**.

  **Genesys compatibility** is also unavailable with **Pre-encoded hex**: the value is sent as-is, so it must already include the discriminator prefix the far end expects.
</Note>

The same UUI configuration is also available on [Outbound with Callback](04-Outbound-with-Callback.md) nodes and on the [Direct Transfer](06-Prompts-and-Tools.md#call-transfer) action.

### Business hours

Business hours controls prevent the agent from placing calls outside appropriate windows — essential for compliance and for avoiding calls at inconvenient times.

**Respect business hours** — Enable this to enforce a schedule on outbound calls. When a call is triggered outside the configured hours, the **out-of-hours action** determines what happens.

**Business hours setting name** — The name of the schedule to apply (defaults to **Default**). Configure schedules in [workflow settings](../16-Account-and-Settings/10-Workflow-Settings.md#out-of-office-business-hours) with specific days and time windows. You can create multiple named schedules for different use cases — for example, a `"weekdays"` schedule for business calls and an `"extended"` schedule that includes Saturday mornings.

The field takes either a fixed schedule from the dropdown or a [variable](../02-Workflows/07-Variables.md), so the schedule can be picked per contact at runtime — useful for multi-timezone campaigns where each row of the trigger payload carries its own schedule name. Switch the field to dynamic and reference the variable, for example `@trigger.business_hours`.

<Note>
  A dynamic value that doesn't match any schedule name on the workflow falls back to **Default** rather than failing the node. Keep the values you pass in sync with the schedule names in workflow settings.
</Note>

**Out-of-hours action** — What to do when a call is triggered outside business hours:

* **Sleep** — The call is queued and placed automatically when business hours resume. The workflow pauses at the voice agent node and continues when the call is eventually made. Use this when timing doesn't matter much and you simply want to avoid calling at odd hours.
* **Block** — The call is cancelled entirely and the workflow continues without making the call. The session is created with a `canceled` status. Use this when the call is time-sensitive and wouldn't make sense if delayed — for example, a same-day delivery confirmation that expires overnight.

<Warning>
  When using **Sleep**, calls accumulate during off-hours and all attempt to dial when business hours resume. If you trigger many calls overnight, they'll all queue up and may hit your concurrency limits when the business hours window opens. Plan your batch sizes accordingly.
</Warning>

### Contact intelligence

Contact intelligence gives the agent context about past interactions with the recipient. This is especially valuable for outbound calls where the recipient may have spoken with your agents before.

**Enable memory** — Activates contact intelligence. When calling a known contact, the agent receives their interaction history and any extracted attributes, enabling personalized openers like "I see we spoke last Tuesday about the Chicago pickup — I'm following up on that."

**Interaction limit** — How many past interactions to include (0–10). More history means more context but longer prompts and higher token usage. Start with 3–5.

**Disable auto contact context** — By default, contact context is appended to the end of the prompt. Enable this to manually place `@contact_intelligence_context` in your prompt where it makes the most sense.

**Enable contact block** — When enabled, the agent will skip calls to contacts that have been blocked in your contact list. The session is created but immediately cancelled without dialing. Use this for do-not-call lists or contacts who have opted out of outreach. The workflow continues without making the call, and downstream nodes can check the session status.

### Real-time analysis

Real-time classifiers work the same as for [inbound agents](02-Inbound-Calls.md#real-time-analysis):

* **Sentiment classifier** — Automatic positive/negative/neutral tracking per turn.
* **Custom classifiers** — Your own categories with custom prompts and classes.

For outbound calls, consider adding a custom classifier for **call disposition** — categories like "Interested", "Not interested", "Call back later", "Wrong number". This gives you structured data for campaign analytics without relying on the agent to explicitly extract it.

## Outbound call flow

When an outbound call is triggered:

1. The workflow trigger fires (webhook, API, or upstream action) and execution begins.
2. The outbound voice agent node creates a session with status `queued` and type `outbound`.
3. The call enters the outbound queue with the destination number, SIP trunk, and caller ID.
4. The batcher service polls the queue every second, enforcing per-organization concurrency limits and per-trunk calls-per-second (CPS) limits.
5. When capacity is available, the batcher creates a SIP participant and dials the recipient.
6. The voice agent joins the call and begins the conversation.
7. On completion, the session status updates and the workflow continues with downstream nodes.

## Concurrency and rate limiting

Outbound calls are subject to several limits that prevent overloading carriers and ensure fair resource allocation:

| Limit                      | Scope            | Description                                                                                                                                                      |
| -------------------------- | ---------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Max concurrent calls**   | Per organization | Maximum simultaneous outbound calls. Configured in your organization settings. Once this limit is reached, additional calls queue until an active call finishes. |
| **Calls per second (CPS)** | Per SIP trunk    | How many new calls can be initiated per second through a single trunk. Prevents carrier-level throttling and SIP errors.                                         |
| **Global limit**           | Platform-wide    | Maximum total concurrent calls across all organizations (default: 100).                                                                                          |

<Info>
  Inbound calls are never subject to concurrency limits — they are always processed first and immediately. Outbound calls queue behind inbound calls and are processed in order, respecting all rate limits.
</Info>

## Session statuses

After an outbound call completes, the session status tells you what happened. Use these in downstream conditions to branch your workflow:

| Status      | Meaning                                                                                                                                                                                                        |
| ----------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `completed` | The call connected and the conversation finished normally.                                                                                                                                                     |
| `busy`      | The recipient's line was busy.                                                                                                                                                                                 |
| `missed`    | No answer — the call rang but wasn't picked up.                                                                                                                                                                |
| `voicemail` | The call went to voicemail. If a voicemail action was configured, the message was delivered.                                                                                                                   |
| `failed`    | The call could not be placed due to a technical error (SIP failure, etc.). When **Gracefully handle invalid number** is enabled, an invalid destination number produces node output instead of a hard failure. |
| `canceled`  | The call was cancelled — either by business hours blocking, contact block, or manual cancellation.                                                                                                             |

## Next steps

<CardGroup cols={3}>
  <Card title="Outbound with callback" icon="phone-missed" href="04-Outbound-with-Callback.md">
    Handle callbacks from missed outbound calls.
  </Card>

  <Card title="Prompts and tools" icon="message" href="06-Prompts-and-Tools.md">
    Write prompts and attach tools to your agent.
  </Card>

  <Card title="STT, TTS, and LLM" icon="sliders" href="05-STT-TTS-and-LLM-Configuration.md">
    Tune speech, voice, and model settings.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/voice-agents/outbound-calls
