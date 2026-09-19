---
title: "Microsoft Teams"
description: "Send messages and monitor channels in Microsoft Teams"
---

# Microsoft Teams

> Send messages and monitor channels in Microsoft Teams

The Microsoft Teams integration lets your workflows send messages to Teams channels and users, monitor channels for new messages, wait for replies, and run dedicated [Teams text agents](../../06-Text-Agents/06-Microsoft-Teams.md) for full back-and-forth conversations — all through the Microsoft Graph API and the Microsoft Bot Framework.

## Setup

Setting up Microsoft Teams is a one-time process per Microsoft 365 tenant. Your IT administrator uploads the HappyRobot bot app package, grants admin consent for the requested permissions, distributes the bot to users, and creates a credential in HappyRobot.

### Prerequisites

* A Microsoft 365 subscription with Teams enabled.
* An IT administrator with access to the **Microsoft Teams Admin Center** (admin.teams.microsoft.com).
* The HappyRobot bot app package (a `.zip` file provided by your HappyRobot account team — the bot is **not** listed on the Microsoft Teams Marketplace).

### Step 1: Upload the HappyRobot bot

<Steps>
  <Step title="Get the bot app package">
    HappyRobot provides the Teams app package as a `.zip` file. Contact your account team to receive it.
  </Step>

  <Step title="Upload the app">
    In the **Microsoft Teams Admin Center**, go to **Teams apps > Manage apps**, click **Upload new app > Upload**, and select the `.zip` file. The app then appears in your organization's app catalog.
  </Step>

  <Step title="Grant admin consent">
    Review the requested permissions (see [Permissions](#permissions) below) and click **Grant admin consent**. After consent is granted, the app appears under **Built for your org** in the Teams app store.
  </Step>
</Steps>

### Step 2: Distribute the bot to users

Choose how the bot reaches end users:

* **Self-service** — Users install the bot themselves from the Teams app store under **Built for your org**.
* **Admin-deployed** — Use Teams Admin Center app setup policies to push the app to all users or specific groups automatically.
* **Automatic for outbound** — When you send an outbound message to a user who hasn't installed the bot, HappyRobot installs it for them on the fly (this requires the `TeamsAppInstallation.ReadWriteSelfForUser.All` permission listed below).

### Step 3: Add the bot to channels and group chats

For each conversation where the agent should operate:

* **Direct messages** — No setup needed. Once a user has the bot installed, they can message it directly from their chat list.
* **Channels** — Type `@HappyRobot` in the channel; Teams will prompt you to add the bot. Confirm to make the bot a member.
* **Group chats** — Type `@HappyRobot` in the chat; Teams will prompt you to add the bot. Confirm to add it to the conversation.

### Step 4: Create a Microsoft Teams credential

The credential authorizes HappyRobot's API access to your Microsoft 365 tenant for user and channel lookups (separate from the bot's own message-handling capabilities).

<Steps>
  <Step title="Enable the Microsoft Teams integration">
    In HappyRobot, go to **Settings > Integrations** and enable **Microsoft Teams**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and select **Microsoft Teams**. You'll be redirected to Microsoft's authorization page.
  </Step>

  <Step title="Sign in and approve">
    Sign in with a Microsoft 365 admin account and approve the requested permissions.
  </Step>

  <Step title="Verify the connection">
    After redirecting back, the credential appears as **Active**.
  </Step>
</Steps>

## Permissions

The HappyRobot bot requests the following permissions during admin consent. Your Microsoft 365 administrator handles this — you don't need to configure these yourself. The Microsoft Teams Admin Center will display the full list during the consent flow.

### What the bot can do

| Capability                       | What it means                                                                                         |
| -------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Send and receive messages        | Read messages directed to the bot and reply in DMs, group chats, and channels where it has been added |
| Look up users                    | Find users by email or display name to send them messages                                             |
| Create group chats               | Spin up new group chats for outbound multi-party messages                                             |
| Install itself for users         | Deliver outbound messages to users who haven't manually installed the bot                             |
| Read chat members                | See who is in a group chat the bot is part of                                                         |
| Read basic team and channel info | Identify the right team and channel when routing messages                                             |
| Read channel messages            | Receive notifications when messages are posted in monitored channels                                  |

### What the bot cannot do

| Restriction                      | Details                                                                                               |
| -------------------------------- | ----------------------------------------------------------------------------------------------------- |
| Read messages everywhere         | Only sees messages in conversations where it's a participant — it cannot snoop on other conversations |
| Access files                     | Cannot read, upload, or manage files in Teams or SharePoint                                           |
| Modify channels or teams         | Cannot create, rename, or delete channels or teams                                                    |
| Access email or calendar         | Operates only within Teams chat — no Outlook access                                                   |
| See private channels it isn't in | Only accesses channels it has been explicitly added to                                                |
| Delete or edit messages          | Cannot modify any messages, including its own                                                         |

### User and directory permissions

Used to find people in your organization so the bot can send them messages.

| Permission             | Type        | Admin consent | Why it's needed                                                                                 |
| ---------------------- | ----------- | ------------- | ----------------------------------------------------------------------------------------------- |
| **User.Read.All**      | Application | Yes           | Looks up Teams users by email or display name when configuring outbound messages.               |
| **User.Read.All**      | Delegated   | Yes           | Verifies user identities during the credential setup flow.                                      |
| **Directory.Read.All** | Application | Yes           | Confirms users belong to your organization — paired with `User.Read.All` for directory queries. |
| **Directory.Read.All** | Delegated   | Yes           | Same as above, used during credential setup.                                                    |
| **openid**             | Delegated   | No            | Standard sign-in scope. Verifies the identity of the person authorizing the connection.         |
| **profile**            | Delegated   | No            | Reads basic profile info (name, email) of the installer during credential setup.                |
| **offline\_access**    | Delegated   | No            | Maintains the connection without requiring re-authorization on every API call.                  |

### Chat permissions

Used to participate in conversations, verify chat status, and create new group chats.

| Permission             | Type        | Admin consent | Why it's needed                                                                                                       |
| ---------------------- | ----------- | ------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Chat.Create**        | Application | Yes           | Creates new group chats for outbound multi-party messaging. Without this, outbound group chats do not work.           |
| **Chat.Create**        | Delegated   | No            | Same capability used during delegated authorization (e.g., when a user sets up a group chat through the platform UI). |
| **Chat.Read.All**      | Application | Yes           | Verifies that an existing group chat still exists before sending — auto-recreates the chat if it was deleted.         |
| **Chat.Read**          | Delegated   | No            | Finds existing 1:1 conversations to avoid creating duplicate DM threads.                                              |
| **Chat.ReadWrite**     | Delegated   | No            | Confirms group chat membership during setup flows.                                                                    |
| **Chat.ReadWrite.All** | Delegated   | Yes           | Manages chat operations that span the organization (e.g., admin configuring the bot across many group chats).         |

### Channel message permissions

Used to monitor and participate in team channel conversations.

| Permission                  | Type        | Admin consent | Why it's needed                                                                                                           |
| --------------------------- | ----------- | ------------- | ------------------------------------------------------------------------------------------------------------------------- |
| **ChannelMessage.Read.All** | Application | Yes           | Receives notifications when new messages are posted in monitored channels. Without this, the bot cannot monitor channels. |
| **ChannelMessage.Read.All** | Delegated   | Yes           | Same capability, used during delegated channel-monitoring setup through the platform UI.                                  |

### Channel and team permissions

Used to understand your organization's team and channel structure.

| Permission                | Type        | Admin consent | Why it's needed                                                                                          |
| ------------------------- | ----------- | ------------- | -------------------------------------------------------------------------------------------------------- |
| **Channel.ReadBasic.All** | Delegated   | No            | Reads channel names and descriptions when configuring the bot for a specific channel.                    |
| **Team.ReadBasic.All**    | Application | Yes           | Identifies the correct team for outbound channel messaging and lists available teams in setup dropdowns. |
| **Team.ReadBasic.All**    | Delegated   | No            | Same as above, used during the setup flow when browsing teams in the platform UI.                        |
| **Group.Read.All**        | Application | Yes           | Resolves the underlying Microsoft 365 Group that backs each Team — required for some team lookups.       |
| **Group.Read.All**        | Delegated   | Yes           | Same as above, used during setup and configuration.                                                      |
| **TeamMember.Read.All**   | Delegated   | Yes           | Verifies team membership before posting in a channel.                                                    |

### Bot installation permissions

Used to install the bot proactively so it can message users and participate in chats it hasn't been manually added to. These permissions are scoped to the HappyRobot app only — they cannot install other apps.

| Permission                                                  | Type        | Admin consent | Why it's needed                                                                                                                                                |
| ----------------------------------------------------------- | ----------- | ------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **TeamsAppInstallation.ReadWriteSelfForUser.All**           | Application | Yes           | Auto-installs the bot for outbound recipients who haven't installed it yet, so the message can be delivered.                                                   |
| **TeamsAppInstallation.ReadWriteSelfForChat.All**           | Application | Yes           | Installs the bot into newly created group chats so it can send and receive messages there.                                                                     |
| **TeamsAppInstallation.ReadWriteAndConsentSelfForChat.All** | Application | Yes           | Activates the bot's ability to receive messages in a group chat as part of the install — combines installation and activation in a single, more reliable step. |

### How permissions work in practice

| Scenario                                           | Permissions used                                                                                                                                                                  |
| -------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| User sends a DM to the bot                         | Receives via Bot Framework; replies via Bot Framework (no Graph permission needed for DMs)                                                                                        |
| User @mentions the bot in a channel                | `ChannelMessage.Read.All` to receive the notification; reply goes through the Bot Framework                                                                                       |
| Outbound DM to a user who hasn't installed the bot | `User.Read.All` (lookup) + `TeamsAppInstallation.ReadWriteSelfForUser.All` (auto-install) + Bot Framework (send)                                                                  |
| Outbound group chat with three users               | `User.Read.All` (lookup each user) + `Chat.Create` (new chat) + `TeamsAppInstallation.ReadWriteAndConsentSelfForChat.All` (install + activate bot in chat) + Bot Framework (send) |
| Bot monitors a channel for messages                | `ChannelMessage.Read.All` (subscribe to updates); reply via Bot Framework                                                                                                         |

### Data privacy

The bot only accesses data it needs to function:

* It reads messages **only** in conversations where it is a participant.
* It looks up users **only** when configured to message someone.
* It does not scan, index, or store messages from conversations it isn't part of.
* All message data is processed in accordance with HappyRobot's data handling policies.

## Available events

### Triggers

| Event                   | Description                                                     |
| ----------------------- | --------------------------------------------------------------- |
| **New Channel Message** | Fires when a new message is posted in a monitored Teams channel |

### Actions

| Event                             | Description                                                    |
| --------------------------------- | -------------------------------------------------------------- |
| **Send Channel Message**          | Posts a message to a Teams channel                             |
| **Send Direct Message**           | Sends a direct message to a Teams user                         |
| **Wait for Thread Reply**         | Pauses the workflow until someone replies to a specific thread |
| **Wait for Direct Message Reply** | Pauses the workflow until someone replies to a direct message  |
| **Get Thread Messages**           | Retrieves all messages in a thread                             |

#### Gracefully handle send errors

The **Send Channel Message** and **Send Direct Message** actions have a **Gracefully handle send errors** toggle. When it's enabled, a failed send doesn't fail the node — the error is returned as structured node output and the workflow continues to the next step. Leave it off (the default) to have send failures stop the run so they surface immediately. Enable it when a Teams notification is best-effort and you'd rather the workflow keep going than halt on a delivery problem.

## Dynamic selections

When configuring Teams events in the workflow editor, teams, channels, and users are loaded dynamically from your Microsoft Teams organization. Select from dropdown lists rather than entering IDs manually.

## Subscription management

The **New Channel Message** trigger (used by individual workflow nodes, not the Teams text agent) requires an active subscription to receive events via Microsoft Graph webhooks. Manage subscriptions from the **Subscriptions** tab on the Microsoft Teams integration settings page.

<Note>
  The Teams text agent does not use Microsoft Graph subscriptions — it receives messages through the Bot Framework once the bot is installed. There's nothing to renew and no per-channel setup required for text agents.
</Note>

## Example use case

A workflow monitors a Teams channel for new messages from customers. When a message arrives, **AI Classify** determines the intent. If it's a load status inquiry, the workflow queries the TMS and posts a **Send Channel Message** reply with the current status. If escalation is needed, it sends a **Send Direct Message** to the assigned account manager.

## Related

<CardGroup cols={3}>
  <Card title="Teams text agent" icon="users" href="../../06-Text-Agents/06-Microsoft-Teams.md">
    Build conversational Teams agents that handle the full back-and-forth automatically.
  </Card>

  <Card title="Slack" icon="slack" href="03-Slack.md">
    Slack messaging integration.
  </Card>

  <Card title="Credentials" icon="key" href="../02-Credentials.md">
    Learn about credential types and management.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/microsoft-teams
