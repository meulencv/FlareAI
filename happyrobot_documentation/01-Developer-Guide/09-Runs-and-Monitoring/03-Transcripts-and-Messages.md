---
title: "Transcripts and Messages"
description: "View conversation transcripts and message history"
---

# Transcripts and Messages

> View conversation transcripts and message history

The run details panel shows the full execution timeline for every run — transcripts of voice conversations, messages exchanged in text sessions, tool call results, integration outputs, and system events. This is your primary interface for understanding exactly what happened during a workflow execution.

## Reading the execution timeline

Open any run and select the **Details** tab to see the execution timeline. Events are displayed in chronological order, grouped by workflow step. For voice agent runs, the timeline is structured around the conversation; for non-voice runs, it follows the node execution sequence.

### Message types

The timeline contains several types of entries, each with a distinct visual treatment:

| Type                  | Description                                                                                                                                                                       |
| --------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **User message**      | Speech from the caller (voice) or message from the user (text). Shows the transcribed text with timestamps.                                                                       |
| **Assistant message** | The AI agent's response. Includes the spoken or written text, plus latency breakdown for voice calls.                                                                             |
| **Rep message**       | A human representative's speech during a warm transfer or handoff. Marked with a "Rep" label to distinguish from AI-generated responses.                                          |
| **Tool call**         | A function the agent invoked mid-conversation — like looking up a record, sending an email, or transferring the call. Shows the tool name, input parameters, and returned result. |
| **Event**             | System events that mark key moments in the run — caller joined, call ended, transfer initiated, business hours check, etc.                                                        |
| **Node output**       | The result of a non-voice workflow node (action, condition, or integration). Shows the output data and execution status.                                                          |

### Prompt node outputs

When a prompt node executes, its row in the timeline shows the **resolved prompt** — the exact text sent to the model, with every variable already substituted — rendered as readable Markdown rather than as escaped JSON. Use the copy button to grab the prompt as-is, for example to paste it into a model playground while debugging.

Expand **Raw output** on the same row to see the underlying execution data (`INPUT`, `PAYLOAD`, and `OUTPUT`) that other node types show by default.

<Tip>
  Reading the resolved prompt is the fastest way to diagnose an agent that behaved unexpectedly — it shows whether a variable came through empty, a knowledge base snippet was included, or a component rendered the way you expected.
</Tip>

### Agent actions

Each agent block in the timeline has an actions menu on its header row:

* **Copy transcript** — copies the agent's full transcript to the clipboard as plain text, so you can paste a conversation into a ticket, a model playground, or a message to a colleague. Disabled with a *No transcript available* tooltip when the agent produced none — a session that failed before its first turn, for example.
* **Open in Chat Playground** — reopens the conversation in the [Chat Playground](../05-Voice-Agents/06-Prompts-and-Tools.md) to continue testing from where it left off. Available on completed runs, and only after the run has finished processing — the tooltip tells you how many minutes are left if you get there first.

## Translating a transcript

When a run is in a language you don't read, open the **⋯** menu on the session header — next to **Copy transcript** — and choose **Translate this run**. Every message in that session is rewritten into your browser's language, and the menu item becomes **Show original** so you can switch back. Both voice and text transcripts can be translated, including transcripts from earlier dial attempts you page back to.

How it behaves:

* Translation runs **on your device**, using your browser's built-in translation models. Nothing is sent to a translation service and no run data leaves the browser.
* The **target** language is your browser's language. The **source** language is detected per message, so a run that mixes languages still translates.
* The action is hidden when the transcript is already in your browser's language, and stays available when detection is inconclusive.
* The first translation of a language pair may pause briefly while your browser downloads its language pack for that pair.
* Messages the browser cannot translate are left in their original language. If nothing at all could be translated, you get a message saying that your browser has no on-device model for the language or could not detect one.

To translate every run automatically, turn on **Automatically translate run transcripts** in your profile preferences. Automatic translation only runs when the required on-device models are already downloaded — a pack is fetched only when you explicitly ask for a translation. Choosing **Show original** on a run keeps that run untranslated for as long as it stays open, even with the preference on.

<Note>
  The translate action and the preference only appear in browsers that expose on-device translation and language detection. In other browsers, transcripts are always shown in their original language.
</Note>

## Voice transcripts

For voice agent runs, the transcript shows the full conversation between the caller and the AI agent. Each message includes:

* **Role** — Who said it (user or assistant)
* **Content** — The transcribed or generated text
* **Timestamp** — When the message occurred during the call

### Latency breakdown

Assistant messages in voice calls include a detailed latency breakdown showing how long each stage of the response pipeline took. This helps you identify bottlenecks and optimize response times.

The breakdown visualizes each component as a colored segment:

| Component                 | Color  | What it measures                                               |
| ------------------------- | ------ | -------------------------------------------------------------- |
| **Transcriber**           | Purple | Time for the STT engine to convert the caller's speech to text |
| **LLM**                   | Blue   | Time for the language model to generate a response             |
| **TTS**                   | Green  | Time for the text-to-speech engine to produce audio            |
| **Conversational engine** | Gray   | Orchestration overhead between pipeline stages                 |

The total latency is displayed alongside the breakdown, so you can quickly see whether a slow response was caused by transcription, the model, or speech synthesis.

<Tip>
  If you notice consistently high LLM latency, consider switching to a faster model in your [STT, TTS, and LLM configuration](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md). If TTS latency is high, try a different voice provider or a voice with lower generation time.
</Tip>

### Message indicators

Assistant messages may include additional indicators depending on the conversation:

* **Interrupted** — The caller interrupted the agent mid-response
* **Early response** — The agent played an early response to reduce perceived latency while the full reply was being generated
* **LLM fallback** — The [secondary model](../05-Voice-Agents/05-STT-TTS-and-LLM-Configuration.md#secondary-model) answered this turn because the primary model was too slow. Hover the badge to see which provider and model produced the message

Caller messages can carry a **DTMF** badge, which marks a turn that arrived from the phone keypad rather than from speech. Use it to tell a pressed `1` apart from a spoken "one" — both look identical in the transcript text otherwise. When consecutive short caller turns are merged into a single bubble, the badge stays if any turn in the group was a keypress.

### Event markers

System events appear inline in the transcript to mark significant moments. Common events include:

* **User joined** — The caller connected to the call
* **User hung up** — The caller disconnected
* **Media timeout** — The call ended because audio stopped flowing, either from a network problem or a hang-up signal that never reached the platform. The run ends at this marker even though no explicit hang-up was received
* **Agent hung up** — The AI agent ended the call
* **User missed call** — The outbound call was not answered
* **Warm transfer** — A warm handoff to a human representative was initiated
* **Rep joined call** — A human representative joined the conversation
* **Direct transfer** — The call was transferred to another number
* **Escalation requested / Escalation started** — The agent invoked its escalation tool to hand the conversation to a human. The milestone is shown even while the underlying tool call details remain expandable below it.
* **Max call duration reached** — The call ended automatically because it hit the [max call duration](../05-Voice-Agents/02-Inbound-Calls.md#call-duration-limits) configured on the agent node
* **Session canceled** — The session was terminated by the system
* **Phone tones played** — DTMF tones were sent during the call
* **On hold** — The caller was placed on hold (with or without music)
* **Call failed** — The call ended on an error. Hover the marker for the reason: a SIP code and its plain-English meaning when the carrier reported one, otherwise a description of what went wrong on the platform side

Failure reasons that don't come from the carrier cover the agent's own startup and runtime:

| Reason                                      | What it means                                                                                                                                                                                                                            |
| ------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Prompt too large**                        | The agent's prompt exceeded what the model provider accepts. Usually an unfiltered API response or a whole [knowledge base](../14-Assets/01-Knowledge-Bases.md) being interpolated into it — trim the variable or filter the tool output feeding it |
| **Agent configuration could not be loaded** | The published configuration for the agent couldn't be read when the call started                                                                                                                                                         |
| **Voice agent failed to start up**          | The voice pipeline didn't come up in time                                                                                                                                                                                                |
| **Agent failed to join the call**           | The call connected but the agent never joined the room                                                                                                                                                                                   |
| **Outbound call could not be placed**       | The outbound leg was never created                                                                                                                                                                                                       |

## Text agent transcripts

Text agent sessions (SMS, email, WhatsApp, Slack) display messages in a chat-like format with the same role indicators as voice transcripts. Text sessions don't include latency breakdowns since there's no speech pipeline, but they do show:

* Message content and timestamps
* Tool call results
* Event markers for session lifecycle
* **Delivery status** — For outbound messages, a status indicator shows the message state: queued, sending, sent, delivered, read, or failed
* **Reactions** — When a WhatsApp contact reacts to a message, the timeline shows a compact line with the emoji and the message that was reacted to, rather than a full message bubble

For inbound emails, the message has two tabs: **Preview** renders the original HTML exactly as the sender's email client formatted it, and **Text** shows the plain-text version the agent actually processed.

Images that the sender embedded in the body — signature logos, screenshots pasted inline — are rendered in **Preview** alongside the text. An embedded image that HappyRobot could not retrieve shows a placeholder in its place rather than a broken image.

## Tool call details

When the agent invokes a tool during a conversation, the timeline shows an expandable tool call block containing:

* **Tool name** — Which function was called
* **Input parameters** — The data sent to the tool (displayed as formatted JSON)
* **Response** — The data returned by the tool
* **Status** — Whether the tool call succeeded or failed

Tool calls are critical for debugging — if the agent made an unexpected decision, check the tool responses to see what data it was working with.

## Artifacts

Messages can include attached artifacts — media and files generated or referenced during the run. The timeline renders these inline:

| Artifact type      | Display                                                   |
| ------------------ | --------------------------------------------------------- |
| **Audio**          | Embedded audio player for playback                        |
| **Images**         | Inline image preview (click to expand)                    |
| **PDFs**           | Document preview with download option                     |
| **Spreadsheets**   | CSV, Excel files with download link                       |
| **Word documents** | Document files with download link                         |
| **Other files**    | JSON, plain text, and other file types with download link |

Artifacts are commonly generated by tool calls — for example, an email action might attach a PDF, or a voice agent might reference an uploaded document.

When an audio attachment has been transcribed by the text agent's [media processing](../06-Text-Agents/01-Text-Agents-Overview.md#media-processing) pipeline, a **Transcription** toggle appears beneath the audio player. Expand it to read the transcript that was fed to the LLM, so you can see exactly what the agent heard without re-listening to the clip.

## Giving feedback on a message

Hovering a message in the timeline reveals an action bar. What it offers depends on who was speaking.

### Assistant messages

Click the **Give feedback** button (thumbs down) on an assistant or rep message to open the feedback panel. Pick what kind of problem it is:

| Kind                               | What it does                                                                                                                        |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------- |
| **General issue**                  | Creates a message [issue](../11-Quality-and-Evaluation/05-Issues.md) with a priority, the correct message, and the reason the response was wrong             |
| **Violates an existing Northstar** | Creates one issue per [northstar](../11-Quality-and-Evaluation/02-Northstars.md) the response broke, so the failure is tracked against the rule it violated  |
| **Missing Northstar**              | Hands the message to [Frontal](../02-Workflows/03-Frontal-AI-assistant.md) to check whether any northstar covers this behavior and propose one if none does |

**Violates an existing Northstar** lists only the northstars that actually apply to the message — those owned by the prompt node that produced it, by any [prompt component](../14-Assets/02-Components.md) it embeds, by the agent, and by any workflow that called into it. Disabled northstars are left out. Search the list, tick every northstar the response broke, set a priority, and optionally add what the agent should have said and why it was a violation. Each selected northstar gets its own issue, and the northstar's name appears as a badge on the issue in the **Flags** subtab.

**Missing Northstar** opens Frontal with the response and the workflow version already attached, and asks it to find the relevant prompt, check its existing northstars, and propose the smallest non-overlapping addition. Frontal reports back rather than editing anything, so you decide whether to add the northstar.

### User messages

Click **Flag** on a user message to create an issue about what the platform heard. Pick a priority, then a type:

* **Transcriber** — the transcription is wrong. Enter the correct transcription.
* **End of Sentence** — the agent took its turn at the wrong moment.
* **Interruption** — the turn was interrupted incorrectly.

### Audit remarks

When an [audit](../11-Quality-and-Evaluation/03-Automated-audits.md) fails a northstar on a message, a badge appears on the message bubble. Open it to read the northstar, why the response failed, and the suggested improvement — and to rate the audit itself with thumbs up or thumbs down without leaving the transcript. See [audit feedback](../11-Quality-and-Evaluation/03-Automated-audits.md#audit-feedback) for what happens to that rating.

<Note>
  These actions depend on your permissions for the workflow. Creating issues requires issue-creation permission, the northstar options additionally require permission to view northstars, and rating audit remarks requires permission to view northstar audits.
</Note>

## Multi-session runs

Some runs contain multiple agent sessions. This happens when:

* A voice agent **transfers** the call to another agent (warm transfer)
* An **outbound call with callback** receives a return call
* A workflow contains multiple voice or text agent nodes in sequence

Each session is displayed as a separate collapsible section in the timeline, labeled hierarchically:

* **Call 1** — The primary voice session
* **Call 1.1** — A nested session (e.g., warm transfer from Call 1)
* **Chat 1** — A text agent session
* **Chat 1.1** — A nested text session

Click the session header to expand or collapse its messages. Each session shows its own duration and phone numbers (for voice calls).

### Outbound retry attempts

When an outbound call is retried, every dial attempt is grouped under a single call section instead of appearing as separate calls in the timeline. The section header shows an **Attempt *n*/*total*** pager — use the arrows to step through attempts and read each one's transcript, events, and recording in place. The pager opens on the final attempt. Hover the counter to see that attempt's number, status, and timestamp; on the final attempt it shows the retry outcome (**Completed**, **Max attempts reached**, or **Callback received**).

Between attempts, the timeline shows a line reading *Attempt *n* failed. Waiting to retry* — with the approximate time of the next dial when one is scheduled.

## Accessing transcripts programmatically

Transcript data can be exported via the [CSV export](01-Runs-Overview.md#exporting-runs) feature in the platform. Run exports include message content, timestamps, and metadata for all sessions within matching runs.

You can also list runs and filter by status, date range, and annotation to identify specific runs of interest before reviewing their transcripts in the platform.

<CodeGroup>
  ```bash cURL theme={null}
  # List runs to find specific transcripts to review
  curl -X GET "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&status=completed&page_size=50" \
    -H "Authorization: Bearer hr_live_abc123def456"
  ```

  ```python Python theme={null}
  import requests

  # List runs to find specific transcripts to review
  response = requests.get(
      "https://platform.happyrobot.ai/runs/",
      headers={"Authorization": "Bearer hr_live_abc123def456"},
      params={
          "use_case_id": "YOUR_USE_CASE_ID",
          "status": "completed",
          "page_size": 50,
      },
  )

  runs = response.json()
  for run in runs["data"]:
      print(f"Run {run['id']} - {run['status']} - {run['timestamp']}")
  ```

  ```javascript Node.js theme={null}
  // List runs to find specific transcripts to review
  const response = await fetch(
    "https://platform.happyrobot.ai/runs/?use_case_id=YOUR_USE_CASE_ID&status=completed&page_size=50",
    {
      headers: {
        Authorization: "Bearer hr_live_abc123def456",
      },
    }
  );

  const runs = await response.json();
  runs.data.forEach((run) => {
    console.log(`Run ${run.id} - ${run.status} - ${run.timestamp}`);
  });
  ```
</CodeGroup>

## Next steps

<CardGroup cols={3}>
  <Card title="Recordings" icon="circle-dot" href="04-Recordings.md">
    Play back call recordings synced to transcripts.
  </Card>

  <Card title="Annotations" icon="tags" href="05-Annotations.md">
    Mark runs for quality review and feedback.
  </Card>

  <Card title="Run statuses" icon="circle-dot" href="02-Run-Statuses.md">
    Understand what each run status means.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/runs/transcripts-and-messages
