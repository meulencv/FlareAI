---
title: "Microsoft Teams"
description: "Deploy text agents in Microsoft Teams chats and channels"
---

# Microsoft Teams

> Deploy text agents in Microsoft Teams chats and channels

Microsoft Teams text agents handle two-way conversations inside Teams. The HappyRobot bot receives messages in direct messages, group chats, and channels — and replies automatically using the same prompt and tool system as other text agents. Once the bot is installed in your Teams environment, it works across every conversation it's added to with no per-channel setup or subscription renewals.

## Prerequisites

Before configuring a Teams text agent, complete the one-time setup on the [Microsoft Teams integration page](../15-Integrations/04-Communication/04-Microsoft-Teams.md):

<Steps>
  <Step title="Upload the HappyRobot bot app package">
    Your IT administrator obtains the HappyRobot Teams app package (`.zip`) from your account team — it's **not** listed on the Microsoft Teams Marketplace. They upload it in **Microsoft Teams Admin Center > Teams apps > Manage apps > Upload new app**.
  </Step>

  <Step title="Grant admin consent">
    The administrator reviews the requested permissions (see the [permissions reference](../15-Integrations/04-Communication/04-Microsoft-Teams.md#permissions) for the full breakdown) and clicks **Grant admin consent**. The bot then appears in the Teams app store under **Built for your org**.
  </Step>

  <Step title="Distribute the bot to users">
    Either let users install the bot themselves from the Teams app store, pre-deploy it via Teams Admin Center app setup policies, or rely on automatic installation for outbound messages.
  </Step>

  <Step title="Create a Microsoft Teams credential in HappyRobot">
    In **Settings > Integrations**, enable Microsoft Teams and add a credential. Complete the OAuth flow to authorize HappyRobot's API access to your tenant for user and channel lookups.
  </Step>

  <Step title="Add the bot to channels and group chats">
    For each channel or group chat where the agent should respond, type `@HappyRobot` and confirm the prompt to add the bot. DMs require no further setup.
  </Step>
</Steps>

## Setting up an inbound Teams agent

<Steps>
  <Step title="Add an inbound trigger">
    Every inbound Teams workflow starts with an **Inbound Text** trigger node. Select this trigger in the workflow editor — it listens for incoming Teams messages.
  </Step>

  <Step title="Add an inbound text agent node">
    Add an **Inbound Text Agent** action node to your workflow and select **Teams** as the channel.
  </Step>

  <Step title="Select a credential">
    Choose the Microsoft Teams credential to use. This determines which Teams organization the agent monitors.
  </Step>

  <Step title="Choose message types">
    Select which types of Teams messages the agent should respond to:

    * **Group Chats** — Messages in group conversations that include the bot
    * **Channel Messages** — Messages posted in Teams channels (requires @mention)
  </Step>

  <Step title="Select teams and channels (channel messages only)">
    If you selected **Channel Messages**, two additional pickers appear:

    * **Teams** — Select one or more Teams workspaces to monitor. Only channels within these workspaces are visible.
    * **Channels** — Select specific channels within each selected workspace. Channels are grouped by workspace. If no channels are selected for a workspace, the agent monitors all accessible channels in that workspace.

    Both fields are required when **Channel Messages** is enabled.
  </Step>

  <Step title="Configure the agent">
    Write a prompt in the nested [prompt node](../05-Voice-Agents/06-Prompts-and-Tools.md), and configure timeout, reminder, and escalation settings. See [common agent settings](01-Text-Agents-Overview.md#common-agent-settings) for details on shared configuration.
  </Step>

  <Step title="Publish and test">
    Publish your workflow and send a message in Teams — DM the bot directly, or @mention it in a group chat or channel. Review the run in the Runs tab to see the full conversation thread and node outputs.
  </Step>
</Steps>

## Setting up an outbound Teams agent

<Steps>
  <Step title="Create a workflow with a trigger">
    Outbound Teams workflows are typically started by a **Webhook** trigger or an **API** call. The trigger payload provides the recipient information and any data the agent needs.
  </Step>

  <Step title="Add an outbound text agent node">
    Add an **Outbound Text Agent** action node and select **Teams** as the channel.
  </Step>

  <Step title="Select a credential">
    Choose the Microsoft Teams credential to use.
  </Step>

  <Step title="Set the message type and recipient">
    Choose where to send the first message:

    | Message type      | Required fields                                                           |
    | ----------------- | ------------------------------------------------------------------------- |
    | **Personal Chat** | Select the Teams user to message                                          |
    | **Group Chat**    | Enter a JSON array of Teams user IDs (e.g., `["user-id-1", "user-id-2"]`) |
    | **Channel**       | Select a team, then select a channel within that team                     |

    All fields support [variables](../02-Workflows/07-Variables.md), so recipient information can be resolved dynamically from upstream workflow data. If the bot hasn't been installed for a target user, HappyRobot installs it automatically before sending the first message (see [permissions](../15-Integrations/04-Communication/04-Microsoft-Teams.md#permissions)).
  </Step>

  <Step title="Configure and publish">
    Write a prompt, configure conversation settings, then publish and trigger the workflow to test.
  </Step>
</Steps>

## How conversations work

### Conversation types

Teams has three distinct conversation contexts:

| Type           | Description                       | Use case                                        |
| -------------- | --------------------------------- | ----------------------------------------------- |
| Direct Message | One-on-one with the bot           | Private support, personal notifications         |
| Group Chat     | Multi-party chat (2+ users + bot) | Collaborative troubleshooting, team discussions |
| Channel        | Message in a team channel         | Team-wide Q\&A, support channels, announcements |

### Mentions and threading

| Context                | Mention required? | Notes                                            |
| ---------------------- | ----------------- | ------------------------------------------------ |
| Direct Message         | No                | Every message is routed to the agent             |
| Group Chat             | Yes               | The user must @mention the bot for it to respond |
| Channel (top-level)    | Yes               | The user must @mention the bot to start a thread |
| Channel (thread reply) | Yes               | Mention required even inside a thread            |

In channels, every agent reply lands in a thread attached to the original message. In DMs and group chats, replies flow as a normal conversation without threading.

### Context awareness (silent tracking)

In group chats and channels, when the bot has an active session and someone posts a message **without** an @mention, the agent silently records the message but doesn't respond. The next time someone @mentions the bot in that conversation, it has full context of what was discussed in the meantime.

If the bot has no session in that conversation, messages without an @mention are ignored entirely.

### Reply-to-bot detection

If the bot has already responded in a group chat or channel and a user replies directly to the bot's message (using Teams' quote-reply feature), the bot will respond even without an @mention. This makes back-and-forth conversations feel natural — once the user is engaged with the bot, repeated mentions aren't required.

### Quote replies

When a user quotes a previous message in their reply, the agent receives both the quoted text and the new message. This helps the agent understand exactly what the user is referring to.

### Bot message filtering

Messages from other bots, and the agent's own messages, are automatically ignored. This prevents infinite loops between bots.

## Configuration reference

### Credential

Select the Microsoft Teams OAuth credential that authorizes access to your Teams organization. You must add a credential on the [Microsoft Teams integration page](../15-Integrations/04-Communication/04-Microsoft-Teams.md) before it appears in this list.

For inbound agents, credentials cannot be set dynamically — you must select a static credential.

### Message types (inbound only)

Select one or more message types the agent monitors:

| Type                 | Description                                                                 |
| -------------------- | --------------------------------------------------------------------------- |
| **Group Chats**      | Multi-person chat conversations that include the bot                        |
| **Channel Messages** | Messages posted to Teams channels the bot has access to (requires @mention) |

At least one message type is required to save the inbound configuration.

When **Channel Messages** is selected, two additional required fields appear:

* **Teams** — Select the workspaces whose channels you want to monitor. The list is populated from the connected credential.
* **Channels** — Select specific channels within each workspace. Channels are shown grouped by workspace. Leaving channels empty for a workspace means the agent monitors all channels in that workspace.

Selections persist if you deselect and re-select **Channel Messages** so you don't lose your configuration when toggling message types.

### Send to (outbound only)

Configure where the agent sends its first message. The message type determines which additional fields are required:

* **Personal Chat** — Select or dynamically provide a Teams user
* **Group Chat** — Provide a JSON array of Teams user IDs (HappyRobot creates a new group chat with those users and posts the first message)
* **Channel** — Select a team from your organization's Teams list, then select a channel within that team

### User resolution

When specifying users for outbound messages, you can identify them by:

| Format           | Example                                          |
| ---------------- | ------------------------------------------------ |
| Email address    | `john.smith@company.com`                         |
| Display name     | `John Smith`                                     |
| Azure AD user ID | The unique ID from your organization's directory |

Email is the most reliable method.

## Teams message flow

### Inbound flow

1. A user sends a message to the HappyRobot bot — directly, in a group chat the bot is part of, or in a channel where the bot has been added.
2. Microsoft Bot Framework delivers the message activity to HappyRobot.
3. For group chats and channels, HappyRobot checks whether the user @mentioned the bot. Without a mention, the message is either tracked silently (if a session is active) or ignored.
4. With an @mention or in a DM, HappyRobot creates or resumes a session and routes the message to the agent.
5. The LLM generates a response using the prompt, conversation history, and any tool results.
6. The response is sent back to Teams — into a thread for channel messages, or directly into the conversation for DMs and group chats.
7. The session stays open for follow-up messages until the idle timeout expires or the agent ends the conversation.

### Outbound flow

1. The workflow trigger fires (webhook, API, or upstream action) and execution begins.
2. The outbound text agent node resolves the recipient. If the bot isn't installed for the target user, HappyRobot installs it automatically.
3. The first message is sent (DM, new group chat, or channel post).
4. Replies are routed back to the same session, and the LLM generates responses.
5. The conversation continues until the idle timeout expires or the agent ends it.
6. When the session closes, the workflow proceeds to downstream nodes.

## Limitations

* **Plain text only.** Teams Adaptive Cards (rich interactive cards with buttons, forms, and structured layouts) are not supported for agent-generated responses.
* **No file or image handling.** The agent cannot send files or images and does not extract content from files shared by users.
* **No emoji reactions.** The agent can only send text replies.
* **One Microsoft 365 tenant per credential.** To support multiple tenants, create separate credentials for each.
* **Bot must be added to channels.** The agent only sees and responds in channels where it has been explicitly added by typing `@HappyRobot` in the channel and confirming the prompt to add the bot.
* **Read receipts are informational.** Teams read receipts appear in the conversation log but are not exposed to the agent or available as workflow variables.

## Next steps

<CardGroup cols={2}>
  <Card title="Microsoft Teams integration" icon="users" href="../15-Integrations/04-Communication/04-Microsoft-Teams.md">
    Set up credentials and review the bot app package and required permissions.
  </Card>

  <Card title="Text agents overview" icon="messages" href="01-Text-Agents-Overview.md">
    Common settings for timeouts, reminders, escalation, and conversation endings.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/text-agents/teams
