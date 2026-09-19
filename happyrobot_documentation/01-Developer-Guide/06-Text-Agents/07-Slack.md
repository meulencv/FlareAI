---
title: "Slack"
description: "Deploy text agents in Slack channels and direct messages"
---

# Slack

> Deploy text agents in Slack channels and direct messages

Slack text agents handle two-way conversations inside Slack workspaces. The agent receives messages in channels, group DMs, and direct messages — and replies automatically using the same prompt and tool system as other text agents. The HappyRobot Slack app installs once per workspace and works across every conversation it's added to, with no per-channel setup.

## Prerequisites

Before configuring a Slack text agent, complete the one-time setup on the [Slack integration page](../15-Integrations/04-Communication/03-Slack.md):

<Steps>
  <Step title="Install the HappyRobot Slack app">
    A Slack workspace admin opens the installation link provided by your HappyRobot account team and approves the requested OAuth scopes. The app is **not** listed on the Slack App Marketplace — installation happens through this direct link. See the integration page's [setup section](../15-Integrations/04-Communication/03-Slack.md#setup) and [permissions reference](../15-Integrations/04-Communication/03-Slack.md#permissions) for what's requested.
  </Step>

  <Step title="Create a Slack credential in HappyRobot">
    In **Settings > Integrations**, enable Slack and add a credential. Complete the OAuth flow to connect the workspace.
  </Step>

  <Step title="Add the bot to channels">
    The bot only sees messages in channels where it has been added. For each target channel, run `/invite @HappyRobot` or add the app from **Channel Settings > Integrations > Add App**. DMs require no setup.
  </Step>
</Steps>

## Setting up an inbound Slack agent

<Steps>
  <Step title="Add an inbound trigger">
    Every inbound Slack workflow starts with an **Inbound Text** trigger node. Select this trigger in the workflow editor — it listens for incoming Slack messages.
  </Step>

  <Step title="Add an inbound text agent node">
    Add an **Inbound Text Agent** action node to your workflow and select **Slack** as the channel.
  </Step>

  <Step title="Select a credential">
    Choose the Slack credential to use. This determines which workspace the agent monitors.
  </Step>

  <Step title="Choose message types">
    Select which types of Slack messages the agent should respond to:

    * **Group Direct Messages** — Multi-party DMs that include the bot
    * **Channel Messages** — Messages in channels where the bot is a member (requires @mention)
  </Step>

  <Step title="Select channels (channel messages only)">
    If you selected **Channel Messages**, an optional **Channels** picker appears. Pick specific channels to scope the agent — leave empty to respond in every channel where the bot is a member. Only channels the bot has been added to are listed.
  </Step>

  <Step title="Configure the agent">
    Write a prompt in the nested [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md), and configure timeout, reminder, and escalation settings. See [common agent settings](01-Text-Agents-Overview.md#common-agent-settings) for details on shared configuration.
  </Step>

  <Step title="Publish and test">
    Publish your workflow, then `/invite @HappyRobot` in a target channel and @mention the bot — or DM the bot directly. Review the run in the Runs tab to see the full conversation thread and node outputs.
  </Step>
</Steps>

## Setting up an outbound Slack agent

<Steps>
  <Step title="Create a workflow with a trigger">
    Outbound Slack workflows are typically started by a **Webhook** trigger or an **API** call. The trigger payload provides the recipient information and any data the agent needs.
  </Step>

  <Step title="Add an outbound text agent node">
    Add an **Outbound Text Agent** action node and select **Slack** as the channel.
  </Step>

  <Step title="Select a credential">
    Choose the Slack credential to use.
  </Step>

  <Step title="Set the message type and recipient">
    Choose where to send the first message:

    | Message type             | Required fields                                                     |
    | ------------------------ | ------------------------------------------------------------------- |
    | **Direct Message**       | Select the Slack user to message                                    |
    | **Group Direct Message** | Enter a JSON array of Slack user IDs (e.g., `["U12345", "U67890"]`) |
    | **Channel**              | Select a channel from your workspace                                |

    All fields support [variables](../02-Workflows/07-Variables.md), so recipient information can be resolved dynamically from upstream workflow data.
  </Step>

  <Step title="Configure and publish">
    Write a prompt, configure conversation settings, then publish and trigger the workflow to test.
  </Step>
</Steps>

## How conversations work

### Mentions and threading

Slack agents follow Slack's conventions for staying out of conversations they weren't addressed in:

| Context                | Mention required? | Notes                                            |
| ---------------------- | ----------------- | ------------------------------------------------ |
| Direct Message         | No                | Every message is routed to the agent             |
| Group Direct Message   | Yes               | The user must @mention the bot for it to respond |
| Channel (top-level)    | Yes               | The user must @mention the bot to start a thread |
| Channel (thread reply) | Yes               | Mention required even inside a thread            |

In channels, every agent reply lands in a thread attached to the original message — keeping the main channel clean. In DMs, replies flow as a normal conversation without threading.

### Context awareness (backseat mode)

In channels and group DMs, when the bot has an active session and someone posts a message **without** an @mention, the agent silently records the message but doesn't respond. The next time someone @mentions the bot in that thread, it has full context of what was discussed in the meantime.

If the bot has no session in that thread, messages without an @mention are ignored entirely — no run is created.

### Thread history on new sessions

When someone @mentions the bot mid-thread (no existing session), HappyRobot fetches prior thread messages from Slack and includes them in the agent's prompt as context. This lets the agent understand what was discussed before it was brought in.

### Bot message filtering

Messages from other bots, and the agent's own messages, are automatically ignored. This prevents infinite loops between bots.

## Configuration reference

### Credential

Select the Slack OAuth credential that authorizes access to your workspace. You must add a credential on the [Slack integration page](../15-Integrations/04-Communication/03-Slack.md) before it appears in this list.

For inbound agents, credentials cannot be set dynamically — you must select a static credential.

### Message types (inbound only)

Select one or more message types the agent monitors:

| Type                      | Description                                                            |
| ------------------------- | ---------------------------------------------------------------------- |
| **Group Direct Messages** | Multi-person DMs that include the bot                                  |
| **Channel Messages**      | Messages posted to channels the bot is a member of (requires @mention) |

At least one message type is required to save the inbound configuration.

### Channels (inbound, optional)

When **Channel Messages** is selected, you can optionally pick specific channels to scope the agent. Only channels the bot has been added to are listed in the dropdown. Leave the field empty to respond in all channels where the bot is a member.

### Send to (outbound only)

Configure where the agent sends its first message. The message type determines which additional fields are required:

* **Direct Message** — Select or dynamically provide a Slack user
* **Group Direct Message** — Provide a JSON array of Slack user IDs
* **Channel** — Select a channel from your workspace

For channels and group DMs, the first outbound message creates a new thread, and all subsequent messages reply inside that thread automatically.

### User resolution

When specifying users for outbound messages, you can identify them by:

| Format        | Example                      |
| ------------- | ---------------------------- |
| Email address | `john.smith@company.com`     |
| Display name  | `john.smith` or `John Smith` |
| Slack user ID | `U12345ABC`                  |

Email is the most reliable method.

## Slack message flow

### Inbound flow

1. A user sends a message in a DM, group DM, or channel where the bot is a member.
2. Slack delivers the message event to HappyRobot via the Events API.
3. HappyRobot validates the request signature and checks bot membership.
4. For channels and group DMs, HappyRobot checks whether the user @mentioned the bot. Without a mention, the message is either tracked silently (if a session is active) or ignored.
5. With an @mention or in a DM, HappyRobot creates or resumes a session and routes the message to the agent.
6. The LLM generates a response using the prompt, conversation history, and any tool results.
7. The response is sent back to Slack — into a thread for channels, or directly into the DM.
8. The session stays open for follow-up messages until the idle timeout expires or the agent ends the conversation.

### Outbound flow

1. The workflow trigger fires (webhook, API, or upstream action) and execution begins.
2. The outbound text agent node creates a session and posts the first message to the recipient (DM, group DM, or channel).
3. Replies are routed back to the same session, and the LLM generates responses.
4. The conversation continues until the idle timeout expires or the agent ends it.
5. When the session closes, the workflow proceeds to downstream nodes.

## Slack formatting

Agent responses go straight to Slack — there's no separate send step. The agent can use Slack's standard formatting in its replies:

| Format      | Syntax                                |
| ----------- | ------------------------------------- |
| Bold        | `*text*`                              |
| Italic      | `_text_`                              |
| Inline code | `` `text` ``                          |
| Code block  | ` ```text``` `                        |
| Link        | `<https://example.com\|display text>` |

## Limitations

* **Plain text only.** Slack's Block Kit (buttons, dropdowns, rich layouts) is not supported for agent-generated responses.
* **No file handling.** The agent cannot send files or images and does not extract content from files shared by users.
* **No emoji reactions.** The agent can only send text replies — it cannot add emoji reactions as part of its response.
* **One workspace per credential.** To support multiple Slack workspaces, create separate credentials for each.
* **Bot must be a channel member.** The agent only sees and responds in channels where it has been added with `/invite @HappyRobot`.
* **Thread history shows raw user IDs.** When the bot joins a thread mid-conversation, prior messages are referenced by Slack user IDs (e.g., `U08FQ04Q3E1`) rather than display names.

## Next steps

<CardGroup cols={2}>
  <Card title="Slack integration" icon="slack" href="../15-Integrations/04-Communication/03-Slack.md">
    Install the HappyRobot Slack app and review the requested scopes.
  </Card>

  <Card title="Text agents overview" icon="messages" href="01-Text-Agents-Overview.md">
    Common settings for timeouts, reminders, escalation, and conversation endings.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/text-agents/slack
