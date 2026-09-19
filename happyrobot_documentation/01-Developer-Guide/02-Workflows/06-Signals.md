---
title: "Signals"
description: "Wake running agents with real-time, event-driven messages from your systems"
---

# Signals

> Wake running agents with real-time, event-driven messages from your systems

Signals let your external systems push real-time events to a **running agent**. While a voice or text agent is on a live call or in an active conversation, you can publish a signal — a status change, an inventory update, a price confirmation — and the agent reacts to it mid-conversation, without you having to restart the run or build a polling loop.

Signals use a topic-based publish/subscribe model:

* **You subscribe** an agent to one or more topics when building the workflow.
* **Your systems publish** signals to those topics through the API while the agent is live.
* **The agent reacts** based on the prompt instructions you give it for interpreting signals.

A common example: an agent calls a carrier to confirm a load. While the rep is talking, your TMS finalizes the rate. You publish a signal carrying the confirmed rate, and the agent picks it up and quotes the number on the same call.

## How signals reach an agent

Every signal has a **key**. An agent receives a signal only when the key matches one of the topics the agent is subscribed to. When a matching signal arrives, it is delivered to the agent's event loop, and — depending on configuration — the agent either wakes up to respond immediately or factors the signal into its next turn.

### Default topics

When you enable signals on an agent, it is automatically subscribed to three scoped topics. These are filled in with real IDs at runtime:

| Topic                   | Scope                                    |
| ----------------------- | ---------------------------------------- |
| `org.<org_id>`          | Every running agent in your organization |
| `usecase.<use_case_id>` | Every running agent in this workflow     |
| `session.<session_id>`  | One specific live session                |

Use `session.<session_id>` to target a single live call or conversation — this is the most precise way to reach exactly the agent you mean. Use the `org` and `usecase` topics for broadcasts (for example, "pause all current calls").

<Note>
  The `session_id` for a live run is available from the run's data and from the [Sessions API](https://docs.happyrobot.ai/api-reference/overview). Publish to `session.<that_id>` to reach only that conversation.
</Note>

### Custom topics

Beyond the default topics, you can subscribe an agent to your own named topics. Each custom topic has one or more **binding patterns** that determine which keys it matches.

* Keys are dot-separated segments using the characters `a-z`, `A-Z`, `0-9`, `-`, `_`, `*`, `#`, up to 256 characters.
* Bindings support wildcards: `*` matches a single segment and `#` matches one or more segments. For example, the binding `load.*` matches `load.fulfilled` and `load.rejected`, while `load.#` also matches `load.us.west.fulfilled`.
* Keys cannot start with the reserved prefixes `org.`, `usecase.`, or `session.` — those are managed by the platform.

## Enabling signals on an agent

You can configure signals from two places, and they stay in sync:

* The **Agent Signals** section inside an agent node's configuration panel (inbound voice, outbound voice, outbound-with-callback, inbound text, and outbound text agents).
* The **Signals → Inbound** tab on the [workflow settings](../16-Account-and-Settings/10-Workflow-Settings.md#signals) page, which lists every agent in the workflow.

<Steps>
  <Step title="Open the agent configuration">
    Open the agent node in the workflow editor and expand the **Agent Signals** section, or open **Workflow settings → Signals → Inbound**.
  </Step>

  <Step title="Enable signals">
    Toggle signals on. The agent is immediately subscribed to the default `org`, `usecase`, and `session` topics.
  </Step>

  <Step title="Set the response behavior">
    Use the **Start agent response on signal** toggle to decide what happens when a signal arrives:

    * **On** — the agent wakes up and generates a response as soon as a matching signal arrives, even if it is currently idle or listening.
    * **Off** — the signal is still delivered, but the agent only acts on it during its next speaking turn.
  </Step>

  <Step title="Add custom topics (optional)">
    Click **Add custom topic**, give it a name (e.g. `Load updates`), and add one or more binding patterns (e.g. `load.fulfilled`, `load.*`). You can copy a ready-made signal payload for any topic from its row.
  </Step>
</Steps>

## Telling the agent how to react

Subscribing an agent to a topic only delivers the signal — it does not decide what the agent should *do* with it. That behavior comes from your prompt. In the agent's prompt, add instructions describing the signals it may receive and how to interpret each one.

For example:

```text Prompt excerpt theme={null}
You may receive signals during the call.

- A signal with `rate_confirmed` means the load rate has been approved.
  Quote the `amount` from the payload to the carrier and ask them to accept.
- A signal with `load_cancelled` means the load is no longer available.
  Apologize, end the booking flow, and close out the call politely.
```

<Tip>
  Keep signal-handling instructions specific and tied to the payload fields you actually send. The agent reasons over the prompt and the signal payload together, so the clearer the mapping, the more reliable the reaction.
</Tip>

## Publishing signals from your systems

Publish signals through the [Platform API](https://docs.happyrobot.ai/api-reference/overview) using an organization API key. All signal endpoints live under `https://platform.happyrobot.ai/api/v2/signals`. The `org_id` is always derived from your API key, so you never send it in the payload.

### Publish an immediate signal

`POST /api/v2/signals` delivers a signal right away to any running agent subscribed to a matching topic.

<CodeGroup>
  ```bash cURL theme={null}
  curl -X POST https://platform.happyrobot.ai/api/v2/signals \
    -H "Authorization: Bearer hr_..." \
    -H "Content-Type: application/json" \
    -d '{
      "key": "load.fulfilled",
      "env": "production",
      "payload": {
        "load_id": "L-4821",
        "rate_confirmed": true,
        "amount": 2450
      }
    }'
  ```

  ```json Response theme={null}
  {
    "signal_id": "sig_a1b2c3",
    "status": "published",
    "published_at": "2026-05-29T14:32:10Z"
  }
  ```
</CodeGroup>

| Field      | Required | Description                                                                                         |
| ---------- | -------- | --------------------------------------------------------------------------------------------------- |
| `key`      | Yes      | The topic key to publish to. Must match a topic the target agent is subscribed to.                  |
| `payload`  | Yes      | A JSON object delivered to the agent. Reference these fields in your prompt instructions.           |
| `env`      | No       | `production`, `staging`, or `development`. Routes the signal to agents running in that environment. |
| `metadata` | No       | A JSON object for your own tracking. Not surfaced to the agent.                                     |

### Schedule a delayed signal

`POST /api/v2/signals/scheduled-signals` sends a signal after a delay. This is useful for time-based nudges — for example, escalating if a confirmation has not arrived within a window.

<CodeGroup>
  ```bash cURL theme={null}
  curl -X POST https://platform.happyrobot.ai/api/v2/signals/scheduled-signals \
    -H "Authorization: Bearer hr_..." \
    -H "Content-Type: application/json" \
    -d '{
      "key": "session.sess_9f8e",
      "payload": { "message": "No response yet — follow up." },
      "delay_seconds": 120
    }'
  ```

  ```json Response theme={null}
  {
    "scheduled_signal_id": "ssig_d4e5f6",
    "status": "scheduled",
    "deliver_at": "2026-05-29T14:34:10Z"
  }
  ```
</CodeGroup>

`delay_seconds` is a positive integer — the number of seconds to wait before delivery.

### Update or cancel a scheduled signal

* `PATCH /api/v2/signals/scheduled-signals/{scheduled_signal_id}` — reschedule or change the `key`, `payload`, `env`, or `delay_seconds` before it fires.
* `DELETE /api/v2/signals/scheduled-signals/{scheduled_signal_id}` — cancel a scheduled signal that has not yet been delivered.

### Manage custom signal keys via API

You can also manage an agent node's custom keys programmatically — the same keys you would add through the **Add custom topic** dialog. These apply across all environments.

* `GET /api/v2/signals/keys` — list all custom signal keys configured for your organization's nodes.
* `POST /api/v2/signals/keys` — add a custom key to a node (`node_id`, `key`).
* `DELETE /api/v2/signals/keys` — remove a custom key from a node (`node_id`, `key`).

<Note>
  Every signal endpoint is documented in full, with request and response schemas, under the **Signals** tag in the [Platform V2 API reference](https://docs.happyrobot.ai/api-reference/overview).
</Note>

## Sending signals out to your systems

Signals are inbound (your systems → the agent). To go the other way — have an agent notify your systems of events — use **outbound webhooks**, configured on the same **Signals** tab under workflow settings. See [Workflow settings → Signals](../16-Account-and-Settings/10-Workflow-Settings.md#signals).

## Next steps

<CardGroup cols={2}>
  <Card title="Workflow settings" icon="gear" href="https://docs.happyrobot.ai/settings/workflow-settings#signals">
    Manage inbound subscriptions and outbound webhooks per workflow.
  </Card>

  <Card title="API reference" icon="code" href="https://docs.happyrobot.ai/api-reference/overview">
    Full request and response schemas for every signals endpoint.
  </Card>

  <Card title="Voice agents" icon="phone" href="../05-Voice-Agents/01-Voice-Agents-Overview.md">
    Build the agents that react to signals on live calls.
  </Card>

  <Card title="Triggers" icon="bolt" href="05-Triggers.md">
    Start workflows — the counterpart to signaling running agents.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/workflows/signals
