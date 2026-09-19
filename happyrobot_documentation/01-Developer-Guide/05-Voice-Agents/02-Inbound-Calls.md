---
title: "Inbound Calls"
description: "Configure agents to handle incoming phone calls"
---

# Inbound Calls

> Configure agents to handle incoming phone calls

Inbound voice agents answer incoming phone calls on numbers you assign in HappyRobot. When a call arrives, the platform creates a session, routes the caller to the AI agent, and executes the rest of the workflow after the conversation ends. Inbound calls are always processed immediately with no concurrency limits.

## Setting up an inbound voice agent

<Steps>
  <Step title="Add an inbound phone trigger">
    Every inbound workflow starts with an **Inbound to Number** trigger node. In the workflow editor, select this trigger and assign a phone number from your organization's [telephony settings](https://docs.happyrobot.ai/settings). This number is where callers will reach your agent.
  </Step>

  <Step title="Add a voice agent node">
    Add an **Inbound Voice Agent** action node to your workflow. This node contains all the configuration for how the AI agent behaves during the call.
  </Step>

  <Step title="Configure the agent">
    In the voice agent node, configure the agent's prompt, voice, language, and call settings. The agent automatically answers the call from the workflow's trigger — there's no call source to select.
  </Step>

  <Step title="Add downstream nodes">
    After the voice agent node, add any follow-up actions — data extraction, API calls, email notifications, or conditional branching based on the conversation outcome.
  </Step>

  <Step title="Publish and test">
    Publish your workflow and call the assigned phone number to test the agent. Review the run in the Runs tab to see transcripts, recordings, and node outputs.
  </Step>
</Steps>

## Configuration reference

### Call source

Inbound voice agents automatically use the workflow's **root trigger** as their call source — there's no call source field to configure on the agent node. The agent joins whichever call session the trigger opens when it fires.

For the workflow to publish, the root trigger must be one of the following call-compatible triggers:

* **Inbound to Number** — a phone number assigned in your telephony settings.
* **Web Call** — a browser-based call session.
* **Workflow Function Request** — a live call handed off from another workflow (the workflow must be [call compatible](../03-Core-Nodes/12-Call-Workflow.md#making-a-workflow-callable)).
* **[Genesys Audio Connector](../15-Integrations/04-Communication/05-Genesys-Audio-Connector.md)** — streams call audio from Genesys Cloud to the agent over a WebSocket instead of a phone number.

If the root trigger isn't one of these, publishing is blocked with an error asking you to use a call-compatible trigger.

### Agent identity

The agent identity section defines **who** the agent is and **how** it sounds. These settings shape the caller's first impression.

**Prompt** — The system prompt is the core of your agent. It's configured in the [prompt node](06-Prompts-and-Tools.md) nested inside the voice agent, not on the agent node itself. The prompt defines personality, instructions, conversation flow, and guardrails. See [Prompts and tools](06-Prompts-and-Tools.md) for a full guide on writing effective prompts.

**Languages** — Select the language(s) the agent should expect callers to speak. This directly affects the STT engine's accuracy — if you expect Spanish-speaking callers, adding `es-MX` or `es-419` ensures the engine optimizes for Spanish phonetics and vocabulary rather than trying to interpret everything as English.

You can select multiple languages when your agent handles a multilingual caller base. The STT engine will detect which language is being spoken and adapt per utterance. Languages can be set **statically** (fixed selection in the UI) or **dynamically** (via a [variable](../02-Workflows/07-Variables.md) that resolves at runtime), which is useful when upstream logic determines the caller's language before the agent joins.

See [STT, TTS, and LLM Configuration](05-STT-TTS-and-LLM-Configuration.md) for the full list of 50+ supported languages.

**Voices** — Choose which voice the agent uses for text-to-speech. Browse available voices in **Assets > Voices**, where you can filter by language, gender, and provider (ElevenLabs or Cartesia) and preview how each voice sounds.

When you select multiple voices, HappyRobot randomly assigns one per call. This is useful for A/B testing different voices to measure their impact on call outcomes, or simply to add natural variety across your call volume. Like languages, voices can be set statically or dynamically via variables.

### Recording and disclaimers

Call recording is enabled by default. Recordings are stored with the run and accessible from the run details page, where you can play them back alongside the full transcript.

**Recording disclaimer** — Many jurisdictions require you to inform callers that the call is being recorded. The **Recording disclaimer** dropdown selects what plays at the very start of the call, before the agent speaks. The disclaimer plays once and then the conversation begins normally.

Pick one of the recording styles:

* **AI and recording disclosure** — A pre-recorded disclosure that covers both that the caller is talking to an AI agent and that the call is recorded — "This is a recorded call with an AI agent." Use this for EU-facing workflows, where both notices are required. Set the **Recording language** to control which recording plays:
  * **Auto** (the default) — The disclosure is played in the call's conversation language.
  * A specific language — Always play that language's recording.
  * **Dynamic** — Template the language code from a [variable](../02-Workflows/07-Variables.md), for use when upstream logic determines the language.
* **Recording robotic disclosure** — A standard text-to-speech voice reads a generic recording notice. No additional configuration needed.
* **Recording natural disclosure** — A more natural-sounding TTS voice reads the disclaimer. Select a **recording language** so the disclaimer is spoken in the correct language. Supported disclaimer languages include English, Spanish, French, German, Portuguese, Japanese, Korean, and 20+ others.
* **Custom recording** — Use your own disclaimer. Two sub-modes are available via the static/dynamic selector:
  * **Static** — Pick a pre-recorded audio file from **Assets > Audio**. This gives you full control over the exact wording, voice, and tone.
  * **Dynamic** — Provide a templated string (with [variables](../02-Workflows/07-Variables.md)) that the TTS engine reads aloud at runtime. Use this when the disclaimer needs to vary per call — for example, by region or campaign.
* **No disclaimer** — The call begins with the agent's first message. No disclaimer is played.

On EU deployments, new voice agent nodes default to **AI and recording disclosure**, and choosing any other option shows a warning that EU calls must disclose AI use and recording at the start of the call. See [EU AI Act and GDPR requirements](../17-Compliance/01-EU-AI-Act-and-GDPR-requirements.md).

<Tip>
  If you operate in a two-party consent jurisdiction (like California or the EU), enable recording disclaimers. Where your legal team requires exact wording, the **Custom recording** style with a static asset lets them approve the audio that plays on every call.
</Tip>

If you don't need recordings at all, set **Record** to `false` to disable recording entirely — no audio will be stored.

### Audio environment

These settings control what the call sounds like beyond the agent's words. They significantly impact how natural and professional the conversation feels.

**Background noise** — By default, calls include subtle **call center** ambience. This makes the conversation feel like it's coming from a real office rather than a silent void, which many callers find unsettling. Choose the ambience that matches the persona your agent is portraying:

* **Call center** — Professional, busy office. Good default for customer service agents.
* **Coffee shop** — Casual, warm atmosphere. Fits conversational or sales-oriented agents.
* **Office** — Quiet, professional environment. Suitable for business-to-business calls.
* **Reception** — Lobby-like ambience. Works for agents acting as receptionists or front-desk staff.
* **Random** — Randomly selects from the above options each call.
* **No background noise** — Completely silent background.

You can also upload **custom background audio** in **Assets > Audio** for a branded or specific ambience.

Each option in the background noise dropdown has a **play button** so you can hear the clip before selecting it. The same preview button appears on the custom audio asset pickers and on the **Custom recording** disclaimer picker. Starting one preview stops whichever was already playing. Options that aren't a single clip — **Random** and **No background noise** — have no preview.

**Voice speed** — Adjust how fast the agent speaks, from 0.70 (-30% slower) to 1.20 (+20% faster). The default of 1.00 works well for most scenarios. Consider slowing the agent down (0.90–0.95) when dealing with elderly callers or complex information, and speeding it up slightly (1.05–1.10) for high-volume, simple interactions where efficiency matters.

**Voice gain** — Adjust the agent's volume from 1.00 (normal) to 1.50 (+50% louder). Increase the gain if callers frequently report difficulty hearing the agent, particularly when the agent's voice is naturally soft or when callers are in noisy environments.

**Disable time fillers** — By default, the agent says brief filler phrases like "One moment..." or "Let me check on that..." while it processes tool calls or generates longer responses. These fillers reduce perceived latency and make the agent sound more human. Disable them if your use case requires the agent to stay completely silent during processing — for example, when hold music is configured on tools.

### Conversation built-ins

**Stay silent** and **Press digit** are configured in the prompt node's **Built-in** tab, not on the agent node. Open the prompt node inside the agent and switch to **Built-in**.

**Stay silent** — When enabled, the agent can choose not to respond during its turn when silence is more natural. For example, if the caller says "hang on, let me find that number," the agent won't fill the pause with unnecessary speech. Turn it off if the agent should always say something on every turn.

**Play acknowledgement** — Nested under **Stay silent** and on by default. The agent says a brief "Mhmm." before staying quiet, so the caller knows it's still there. Turn it off for complete silence.

**Press digit** — When enabled, the agent gets a `press_digit` tool that lets it send DTMF tones (`0`–`9`, `*`, `#`) during the call. Inbound agents sometimes need this to navigate an automated phone menu (IVR) — for example, when the call is bridged through an internal extension system before reaching the agent. When disabled (the default), the agent can only speak.

Unlike outbound agents, inbound agents don't have a separate phone tree instructions field. Put any IVR navigation instructions directly in the agent's [main prompt](06-Prompts-and-Tools.md) — for example, "If you reach an automated menu, press 3 for dispatch, then 0 to reach a person."

See [Voice agent built-in tools](../04-Tools/04-Built-in-Tools.md#voice-agent-built-in-tools) for details on both tools.

### Transcription accuracy

These settings improve how accurately the STT engine converts the caller's speech to text. Poor transcription leads to misunderstandings, so tuning these settings for your domain is important.

**Transcription context** — A free-text field where you describe what callers are likely to say. The STT engine uses this to bias its recognition toward relevant vocabulary and patterns. Be specific:

* *Good:* "Callers will mention US city names, ZIP codes, and freight industry terms like BOL numbers, MC numbers, and DOT numbers."
* *Less useful:* "Business phone calls."

**Key terms** — A list of specific words or phrases the STT engine should prioritize. Unlike transcription context (which is narrative), key terms are exact strings. Add terms that the engine might otherwise misrecognize:

* Company names (e.g., "Acme Logistics", "TQL", "C.H. Robinson")
* Industry jargon (e.g., "deadhead", "lumper fee", "reefer")
* Alphanumeric codes (e.g., "MC-123456", "PRO number")
* Proper nouns unique to your business

Both fields are capped: transcription context holds up to **5,000 characters**, and the key term list holds up to **100 terms of 50 characters each**. Exceeding a limit marks the node incomplete and blocks publishing — see [Transcription limits](05-STT-TTS-and-LLM-Configuration.md#transcription-context).

**Enable denoised STT** — Applies a voice-focus model that strips background noise and other voices from the caller's audio before transcription. This is helpful when callers are in loud environments (truck stops, warehouses, busy offices), but it can occasionally clip very quiet speech. Test with your typical caller environment before enabling broadly.

**Numerals** — Enabled by default. Converts spoken numbers to digit form in the transcript — "twenty-five" becomes "25", "one eight hundred five five five twelve hundred" becomes "1-800-555-1200". This is essential when your workflow extracts phone numbers, reference IDs, or quantities from the conversation. Disable it only if you need the raw spoken form.

**End-of-turn detection** — The model that determines when the caller has finished speaking, so the agent knows when to respond. Choosing the wrong model can cause the agent to interrupt callers or wait too long:

* **English** — Best for English-only calls. Lowest latency and highest accuracy for detecting natural English speech pauses.
* **Multilingual v1** — Handles multiple languages. Use this when your agent supports non-English callers, since different languages have different pause patterns.
* **Text heuristics** — Rule-based detection that doesn't use an ML model. Most predictable behavior but less nuanced — it won't adapt to individual speaking styles. Useful as a fallback if model-based detection causes issues.

### Call duration limits

**Max call duration** — Defaults to 600 seconds (10 minutes). When the limit is reached, the call ends automatically. Set this based on your expected call length — shorter for simple confirmations (120–180 seconds), longer for complex conversations (900–1200 seconds). This protects against runaway calls that would otherwise rack up costs.

**Max duration transfer number** — Instead of simply hanging up when the time limit is reached, transfer the caller to a human agent or another number. This ensures the caller isn't abruptly cut off mid-conversation. The transfer happens automatically when the timer expires.

**Max duration notices** — Schedule up to **five** instructions that reach the agent as the call approaches its limit, so it can wrap up or warn the caller instead of being cut off mid-sentence. Click **Add notice** and set:

| Field                  | Description                                                                                                                                |
| ---------------------- | ------------------------------------------------------------------------------------------------------------------------------------------ |
| **Seconds before end** | How long before max call duration the notice fires. Must be at least 1 second, unique across notices, and less than the max call duration. |
| **Instruction**        | What the agent should say or do at that point. Supports [variables](../02-Workflows/07-Variables.md). Required.                                       |

Notices are shown on a timeline ordered by when they fire, and each one can be edited or deleted. If you shorten **Max call duration** below a scheduled notice, the field flags the conflict and blocks the change until you reschedule the notice or raise the duration.

<Tip>
  A common pattern is two notices: one a few minutes out telling the agent to steer toward a conclusion, and one near the end telling it to summarize and offer a callback.
</Tip>

Max duration notices are available on inbound, outbound, and outbound-with-callback voice agents.

A call cut short by the duration limit shows a **Max call duration reached** [event marker](../09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#event-markers) in the run timeline, so a truncated conversation isn't mistaken for a hang-up.

### Business hours

For inbound agents, business hours are **disabled by default** — you typically want to answer every call regardless of the time. However, you can enable them if your agent should only be available during specific windows.

**Respect business hours** — When enabled, applies the business hours schedule to incoming calls. Calls outside business hours won't be answered by the agent.

**Business hours setting name** — The name of the schedule to apply (defaults to **Default**). Configure business hour schedules in [workflow settings](../16-Account-and-Settings/10-Workflow-Settings.md#out-of-office-business-hours), where you define the days and times the agent is available. The field accepts either a fixed schedule from the dropdown or a [variable](../02-Workflows/07-Variables.md), so upstream logic can choose the schedule at runtime. A dynamic value that matches no schedule name falls back to **Default**.

<Info>
  Even with business hours disabled, you can use workflow conditions to handle off-hours calls differently — for example, playing a different greeting or routing to voicemail — without rejecting the call entirely.
</Info>

### Real-time analysis

Real-time classifiers run during the conversation, analyzing each caller turn as it happens. Classifier outputs become available as node outputs for use in downstream workflow logic.

**Sentiment classifier** — A built-in classifier that tracks the caller's emotional tone (positive, negative, neutral) throughout the call. Enable this when you want to:

* Route angry callers to human agents via a tool
* Log sentiment trends across your call volume
* Trigger different follow-up actions based on how the conversation went

**Custom classifiers** — Build your own classifiers for domain-specific analysis. Each custom classifier has three parts:

1. **Name** — A label for the classifier (e.g., "Urgency", "Call Intent", "Customer Tier")
2. **Prompt** — Instructions telling the classifier what to look for (e.g., "Determine how urgent the caller's request is based on their language and tone")
3. **Classes** — The categories to classify into (e.g., "Low", "Medium", "High", "Critical")

Classifiers update after each caller turn, so you can use them in real-time tool decisions within the conversation, not just in post-call analysis.

### Contact intelligence

Contact intelligence gives the agent memory across calls. When enabled, the agent can see who's calling, what they've discussed before, and any attributes extracted from past interactions.

**Enable memory** — Activates contact intelligence for this agent. The agent will receive the caller's contact record and interaction history as additional context, so it can say things like "I see you called last week about shipment #4521 — are you following up on that?"

**Interaction limit** — Controls how many past interactions (0–10) are included in the context. More history gives the agent richer context but increases prompt length and token usage. Start with 3–5 and adjust based on how much history the agent needs.

**Disable auto contact context** — By default, contact context is automatically appended to the end of the agent's prompt. If you want more control over where it appears, enable this option and manually place the `@contact_intelligence_context` variable in your prompt. This is useful when you want the agent to weight contact history differently — placing it near the top makes it highly influential, while placing it at the bottom makes it supplementary.

## Testing with mock SIP headers

The play button starts a browser-based test call, which carries no SIP headers — so branches that read `raw_headers` or `user_to_user` never fire in a preview. To exercise them, open the chevron menu next to the play button and choose **Test call with SIP headers**.

<Steps>
  <Step title="Open the dialog">
    Click the chevron next to the play button and select **Test call with SIP headers**. The chevron menu appears on a live version, and the item itself only when the root trigger is an **Inbound to Number** trigger — a web call entrypoint has no headers to mock.
  </Step>

  <Step title="Add header rows">
    Enter up to 20 header name/value pairs, for example `X-Account-Id` / `ACME-42`. Blank rows are ignored.
  </Step>

  <Step title="Start the test call">
    Click **Start test call**. The headers are attached to the call the same way a carrier's INVITE headers are, so the run reads them from `raw_headers` exactly as it would in production.
  </Step>
</Steps>

The last set of headers you used is remembered per workflow, so repeat tests are one click.

<Info>
  Header names arrive **lowercased**, matching what the SIP stack writes — `X-Account-Id` reads back as `x-account-id`. Names must be valid SIP tokens — letters, digits, and the limited punctuation a real SIP header name allows — and `statusCode` / `statusText` are rejected, because the platform sets those when a call ends rather than the caller. The caller is still a web call, so `from_number` and `to_number` stay `web`.
</Info>

## Inbound call flow

When a call arrives on an assigned number:

1. The SIP trunk accepts the call and routes it to HappyRobot.
2. HappyRobot matches the phone number to a workflow trigger and starts a new run.
3. A session is created with status `queued` and type `inbound`.
4. The call is immediately processed (inbound calls have no concurrency limits).
5. The voice agent joins the call and begins the conversation.
6. When the call ends, the session status updates to `completed` (or `missed`, `failed`, etc.) and the workflow continues with downstream nodes.

<Info>
  Inbound calls are always prioritized over outbound calls and are never subject to concurrency limits. Your agents will answer immediately regardless of how many outbound calls are in progress.
</Info>

## Next steps

<CardGroup cols={3}>
  <Card title="Prompts and tools" icon="message" href="06-Prompts-and-Tools.md">
    Write effective prompts and attach tools to your agent.
  </Card>

  <Card title="STT, TTS, and LLM" icon="sliders" href="05-STT-TTS-and-LLM-Configuration.md">
    Tune speech recognition, voice, and model settings.
  </Card>

  <Card title="Outbound calls" icon="phone-arrow-up-right" href="03-Outbound-Calls.md">
    Set up automated outbound calling.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/voice-agents/inbound-calls
