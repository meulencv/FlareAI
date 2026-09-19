---
title: "Recordings"
description: "Access and manage call recordings"
---

# Recordings

> Access and manage call recordings

HappyRobot records voice calls by default and stores them with the run. Recordings are available in the run details panel for playback and can be retrieved programmatically via the API. They provide an audio record of every conversation your agents handle.

## Listening to a call in progress

While a voice session is still live, the top of the **Details** tab holds a **Live call** bar instead of the recording player. Click **Listen now** to hear the conversation as it happens.

You join as a hidden, listen-only participant: neither the caller nor the agent is told anyone is there, you have no microphone, and the AI agent keeps handling the call. This is not a [takeover](../../02-Developer-Tools/02-TypeScript-SDK/04-Voice-call-tutorial.md#take-over-a-live-call) — nothing about the call changes because you're listening.

| State                  | What it means                                                                             |
| ---------------------- | ----------------------------------------------------------------------------------------- |
| **Listen now**         | The call is live and nobody from your side is listening yet.                              |
| **Listening live**     | Audio is playing. Click **Stop listening** to leave; the call is unaffected.              |
| **Audio paused**       | The browser blocked playback. Click **Enable audio** to start it from your click.         |
| **Reconnecting audio** | The connection dropped and is being retried.                                              |
| **Call ended**         | The call finished. The recording player replaces the bar once the recording is available. |

Listening requires permission to view the workflow's runs. Multiple people can listen to the same call at once.

## Playing recordings in the platform

Open any completed voice agent run and the recording player appears at the top of the **Details** tab. The player sticks to the top of the panel as you scroll through the transcript, so you can listen and read simultaneously.

The recording player includes:

* **Play/pause** controls
* **Timeline scrubber** to jump to any point in the call
* **Current time and duration** display
* **Volume control**
* **Playback rate** — speed up or slow down playback for faster review
* **Download** — save the recording audio file locally

### Transcript-linked playback

The recording is linked to the transcript timeline. Click any message in the transcript to jump the recording to that point in the conversation — the audio player seeks to where that line's speech begins, using the speech offsets reported by the transcription engine rather than the time the message was recorded, so the playhead lands at the start of the utterance even when the caller talked over the agent.

This linked playback is particularly useful for quality review — you can quickly jump to specific moments in the call to hear exactly how the agent sounded while reading what was transcribed, making it easy to spot transcription errors or tone issues.

### Following the transcript while it plays

The link works in the other direction too. While the recording is playing, the transcript follows along:

* **Messages ahead of the playhead are dimmed**, so the line currently being spoken is the last one at full opacity — you can see where you are without hunting for a highlight. Dimming only applies to the session the recording belongs to.
* **The transcript auto-scrolls** to keep the current line in view.

Scrolling, swiping, or using the arrow keys inside the transcript pauses the auto-scroll so you can read ahead without being yanked back. Scroll to the bottom again — or use the scroll-to-latest control — and following resumes.

<Tip>
  Play the call and let the transcript follow when you want to hear tone and timing together; click a specific line instead when you already know the moment you're looking for.
</Tip>

### Multi-session recordings

Runs with multiple voice sessions (transfers, callbacks, retries) have separate recordings for each session. The recording player shows the recording for the currently selected session. Switch between session tabs to access different recordings.

### Forward call recordings

A [Forward call](../05-Voice-Agents/07-Forward-call.md) node has no agent on the call, so its recording doesn't appear in the player at the top of the panel. Instead, the forward owns its own session and its recording appears inline on the Forward call node itself in the **Details** tab. Nodes where the session couldn't be created show no player.

## Recording configuration

Recording behavior is configured on each voice agent node in the workflow editor. See [Inbound Calls](../05-Voice-Agents/02-Inbound-Calls.md) or [Outbound Calls](../05-Voice-Agents/03-Outbound-Calls.md) for the full configuration reference.

Key settings:

| Setting                    | Description                                                                            |
| -------------------------- | -------------------------------------------------------------------------------------- |
| **Record**                 | Enable or disable recording for this agent (enabled by default)                        |
| **Play recording message** | Play a disclaimer at the start of the call informing the caller they're being recorded |
| **Recording style**        | How the disclaimer sounds: Robotic, Natural, or Custom audio upload                    |

<Info>
  When recording is disabled (`Record: false`), no audio is stored and the recording player won't appear in the run details. Disable recording only when you're certain you don't need audio records — for example, internal test workflows.
</Info>

## Accessing recordings via API

Retrieve signed URLs for call recordings programmatically. URLs are temporary and expire after a configurable number of days.

### Get recordings for a run

<CodeGroup>
  ```bash cURL theme={null}
  curl -X GET "https://platform.happyrobot.ai/runs/RUN_ID/recordings?url_expires_in_days=3" \
    -H "Authorization: Bearer hr_live_abc123def456"
  ```

  ```python Python theme={null}
  import requests

  response = requests.get(
      "https://platform.happyrobot.ai/runs/RUN_ID/recordings",
      headers={"Authorization": "Bearer hr_live_abc123def456"},
      params={"url_expires_in_days": 3},
  )

  recordings = response.json()
  for recording in recordings["recordings"]:
      print(f"Session: {recording['session_id']}")
      print(f"URL: {recording['url']}")
  ```

  ```javascript Node.js theme={null}
  const response = await fetch(
    "https://platform.happyrobot.ai/runs/RUN_ID/recordings?url_expires_in_days=3",
    {
      headers: {
        Authorization: "Bearer hr_live_abc123def456",
      },
    }
  );

  const { recordings } = await response.json();
  recordings.forEach((rec) => {
    console.log(`Session: ${rec.session_id}, URL: ${rec.url}`);
  });
  ```
</CodeGroup>

**Query parameters:**

| Parameter             | Type    | Default | Description                                      |
| --------------------- | ------- | ------- | ------------------------------------------------ |
| `session_id`          | UUID    | —       | Filter to a specific session's recording         |
| `url_expires_in_days` | integer | 1       | How many days the signed URL remains valid (1–7) |

**Response:**

```json theme={null}
{
  "recordings": [
    {
      "session_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
      "url": "https://storage.example.com/recordings/..."
    }
  ]
}
```

Each entry in the `recordings` array corresponds to one voice session within the run. If a run has multiple sessions (transfers, retries), you'll receive multiple recording URLs.

<Warning>
  Signed URLs are temporary. If you need to store recordings long-term, download the audio file before the URL expires and store it in your own infrastructure.
</Warning>

## Recording compliance

Many jurisdictions require informing callers that their call is being recorded. HappyRobot supports three disclaimer styles:

* **Robotic** — Standard TTS voice reads a generic notice
* **Natural** — Natural-sounding TTS in the configured language
* **Custom** — Your own pre-recorded audio file (uploaded in **Assets > Audio**)

<Tip>
  If you operate in a two-party consent jurisdiction (like California or the EU), enable recording disclaimers with the **Custom** style so your legal team can approve the exact wording.
</Tip>

See [Inbound Calls — Recording and disclaimers](../05-Voice-Agents/02-Inbound-Calls.md#recording-and-disclaimers) for full configuration details.

## Next steps

<CardGroup cols={3}>
  <Card title="Transcripts" icon="message" href="03-Transcripts-and-Messages.md">
    Read the conversation alongside the recording.
  </Card>

  <Card title="Annotations" icon="tags" href="05-Annotations.md">
    Mark run quality while reviewing recordings.
  </Card>

  <Card title="Runs overview" icon="list-check" href="01-Runs-Overview.md">
    Navigate and filter your run history.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/runs/recordings
