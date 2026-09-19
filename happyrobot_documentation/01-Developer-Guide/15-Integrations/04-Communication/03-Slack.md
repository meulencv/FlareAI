---
title: "Slack"
description: "Send messages and receive events from Slack"
---

# Slack

> Send messages and receive events from Slack

The Slack integration lets your workflows send messages to channels and users, monitor channels for new messages and mentions, wait for replies and reactions, and run dedicated [Slack text agents](../../06-Text-Agents/07-Slack.md) for full back-and-forth conversations — all through the Slack API.

## Setup

Setting up Slack is a one-time process per workspace. A workspace admin installs the HappyRobot Slack app, you create a credential in HappyRobot, and the bot is invited to the channels where it should operate.

### Prerequisites

* A Slack workspace where you have admin or app-installation permissions.
* The HappyRobot Slack app installation link (provided by your HappyRobot account team — the app is **not** listed on the Slack App Marketplace).

### Step 1: Install the HappyRobot Slack app

<Steps>
  <Step title="Open the installation link">
    A workspace admin opens the installation link provided by HappyRobot. Slack will display the requested permissions for review.
  </Step>

  <Step title="Authorize the app">
    Sign in with a Slack workspace admin account, review the requested scopes (see [Permissions](#permissions)), and click **Allow**. The app is now installed in your workspace.
  </Step>

  <Step title="Approve in restricted workspaces (if needed)">
    If your workspace requires admin approval for third-party apps, the request appears in **Slack Admin > Manage Apps > App Approval Requests**. A workspace admin must approve it before the bot becomes active.
  </Step>
</Steps>

### Step 2: Create a Slack credential

<Steps>
  <Step title="Enable the Slack integration">
    In HappyRobot, go to **Settings > Integrations** and enable **Slack**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and select **Slack**. You'll be redirected to Slack's authorization page.
  </Step>

  <Step title="Select your workspace">
    Choose the Slack workspace you want to connect and approve the requested scopes.
  </Step>

  <Step title="Verify the connection">
    After redirecting back, the credential appears as **Active**. HappyRobot can now access the workspace's channels and users.
  </Step>
</Steps>

### Step 3: Add the bot to channels

The bot only sees messages in channels where it has been added. For each channel where the agent should operate:

* Type `/invite @HappyRobot` in the channel, **or**
* Open **Channel Settings > Integrations > Add App** and add the HappyRobot app.

DMs require no setup — once the app is installed, users can message the bot directly. Group DMs require an `@HappyRobot` mention to add the bot to the conversation.

## Permissions

Slack permissions (called "scopes") are approved during installation. Your workspace administrator handles this — you don't need to configure them yourself. Slack splits scopes into **Bot Token Scopes** (what the bot can do on its own) and **User Token Scopes** (what the bot can do on behalf of the installing user).

### What the bot can do

| Capability                         | What it means                                                             |
| ---------------------------------- | ------------------------------------------------------------------------- |
| Send messages                      | Reply in channels, DMs, and group DMs the bot is part of                  |
| Read messages in its conversations | See messages in channels, DMs, and group DMs where the bot has been added |
| Join public channels               | Auto-join public channels for outbound messaging                          |
| Look up users                      | Find users by email or display name to send them messages                 |
| Read channel info                  | See channel names and basic info for routing                              |
| Add and read emoji reactions       | React to messages and observe user reactions                              |
| Create and manage Slack reminders  | Schedule reminders as part of conversation flows                          |

### What the bot cannot do

| Restriction                           | Details                                                           |
| ------------------------------------- | ----------------------------------------------------------------- |
| Read messages in channels it isn't in | Only sees messages in channels where it's been added              |
| Access private channels uninvited     | Must be invited to private channels — cannot self-join            |
| Delete or edit messages               | Cannot modify any messages, including its own                     |
| Access files                          | Cannot upload files or extract content from files shared by users |
| Create or archive channels            | Cannot modify your workspace structure                            |
| Access DMs between other users        | Only sees DMs sent directly to the bot                            |
| Manage workspace settings             | No admin capabilities                                             |

### Bot Token Scopes

These are the permissions the bot uses to operate in your workspace.

#### Messaging

| Scope                  | Why it's needed                                                                                                                   |
| ---------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
| **app\_mentions:read** | Detects when someone @mentions the bot in channels and group DMs. Without this, the bot cannot tell when users are addressing it. |
| **chat:write**         | Core scope for replying to users. Every response the agent generates is sent using this scope.                                    |
| **chat:write.public**  | Lets outbound agents post to channels the bot hasn't been added to yet, without requiring someone to invite it first.             |
| **incoming-webhook**   | Posts automated notifications and status updates to specific channels configured during setup (e.g., workflow completion alerts). |

#### Channel history

These scopes power backseat-mode tracking and thread-history fetching when the bot joins a conversation mid-way.

| Scope                | Why it's needed                                                                                                       |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **channels:history** | Reads messages in public channels the bot has been added to — used for thread history and backseat context tracking.  |
| **groups:history**   | Same as `channels:history`, but for private channels. Required for the bot to read or respond in any private channel. |
| **im:history**       | Reads direct messages sent to the bot. Core scope for DM conversations.                                               |
| **mpim:history**     | Reads messages in group DMs the bot is part of.                                                                       |

#### Channel and workspace info

| Scope             | Why it's needed                                                                                                                                          |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **channels:read** | Lists public channels and verifies the bot's membership before processing messages.                                                                      |
| **channels:join** | Lets outbound agents auto-join public channels instead of requiring a manual `/invite`. Public channels only — private channels still require an invite. |
| **groups:read**   | Same as `channels:read`, for private channels the bot has been invited to.                                                                               |
| **im:read**       | Reads basic info about DM conversations during message routing.                                                                                          |

#### Users

| Scope          | Why it's needed                                                                                       |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| **users:read** | Looks up users by display name for outbound messages, and identifies who said what in thread history. |

#### Reactions

| Scope               | Why it's needed                                                                                           |
| ------------------- | --------------------------------------------------------------------------------------------------------- |
| **reactions:read**  | Sees emoji reactions on messages — used by reaction-triggered workflows (e.g., a thumbs-up for approval). |
| **reactions:write** | Lets the bot add emoji reactions to messages.                                                             |

#### Reminders

| Scope               | Why it's needed                                                          |
| ------------------- | ------------------------------------------------------------------------ |
| **reminders:read**  | Views reminders the bot has created, to avoid duplicates.                |
| **reminders:write** | Creates and manages Slack reminders for users as part of a conversation. |

#### Files

| Scope          | Why it's needed                                                                                      |
| -------------- | ---------------------------------------------------------------------------------------------------- |
| **files:read** | Sees that a file was shared in the conversation. The agent does not currently extract file contents. |

### User Token Scopes

These scopes act on behalf of the user who installed the app and are used during initial setup and configuration flows.

| Scope                | Why it's needed                                                                                         |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| **channels:history** | Verifies the workspace connection during setup by confirming access to the installer's public channels. |
| **groups:history**   | Same as above, for private channels the installer can see.                                              |
| **groups:read**      | Lists private channels the installer can access — used in outbound configuration dropdowns.             |
| **im:history**       | Verifies DM connectivity during setup.                                                                  |
| **reactions:read**   | Surfaces reaction events with the installer's context during configuration and testing.                 |

### How permissions work in practice

| Scenario                                                    | Scopes used                                                                                    |
| ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------- |
| User sends a DM to the bot                                  | `im:history` (read), `chat:write` (reply)                                                      |
| User @mentions the bot in a public channel                  | `app_mentions:read`, `channels:history`, `channels:read`, `chat:write`                         |
| User @mentions the bot mid-thread (new session)             | `app_mentions:read`, `channels:history` or `groups:history` (fetch prior thread), `chat:write` |
| Outbound DM to a user resolved by email                     | `users:read`, `chat:write`                                                                     |
| Outbound message to a public channel the bot hasn't joined  | `channels:join`, `chat:write` or `chat:write.public`                                           |
| Backseat mode — message without `@mention` in active thread | `channels:history` or `groups:history` (silent read)                                           |

### Data privacy

The bot only accesses data it needs to function:

* It reads messages **only** in conversations where it is a member.
* It looks up users **only** when configured to message someone.
* It does not scan, index, or store messages from channels it isn't in.
* All message data is processed in accordance with HappyRobot's data handling policies.

## Available events

### Triggers

| Event                   | Description                                               |
| ----------------------- | --------------------------------------------------------- |
| **New Channel Message** | Fires when a new message is posted in a monitored channel |
| **New Mention**         | Fires when the connected bot is mentioned in a channel    |

### Actions

| Event                         | Description                                                                  |
| ----------------------------- | ---------------------------------------------------------------------------- |
| **Send Channel Message**      | Posts a message to a Slack channel                                           |
| **Send Direct Message**       | Sends a direct message to a Slack user                                       |
| **Wait for Thread Reply**     | Pauses the workflow until someone replies to a specific thread               |
| **Wait for Message Reaction** | Pauses the workflow until someone reacts to a specific message with an emoji |
| **Get Thread Messages**       | Retrieves all messages in a thread                                           |

<Tip>
  **Wait for Thread Reply** and **Wait for Message Reaction** are powerful for human-in-the-loop workflows. Post a question to a channel, wait for a team member to reply or react, and continue the workflow based on their response.
</Tip>

## Dynamic selections

When configuring Slack events in the workflow editor, channels and users are loaded dynamically from your Slack workspace. Select from dropdown lists rather than entering IDs manually.

## Subscription management

Slack triggers require an active subscription to receive events. Manage subscriptions from the **Subscriptions** tab on the Slack integration settings page.

## Example use case

An AI voice agent completes a call and extracts key details. The workflow posts a summary to a Slack channel using **Send Channel Message**, then uses **Wait for Message Reaction** to pause until a team member reacts with a checkmark. If approved, the workflow updates the TMS record automatically.

## Related

<CardGroup cols={3}>
  <Card title="Slack text agent" icon="slack" href="../../06-Text-Agents/07-Slack.md">
    Build conversational Slack agents that handle the full back-and-forth automatically.
  </Card>

  <Card title="Microsoft Teams" icon="users" href="04-Microsoft-Teams.md">
    Microsoft Teams messaging integration.
  </Card>

  <Card title="Workflows" icon="diagram-project" href="../../02-Workflows/01-Workflows-Overview.md">
    Learn how to build workflows with Slack actions.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/slack
