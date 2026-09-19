---
title: "API Keys"
description: "Generate and manage API keys for the HappyRobot API"
---

# API Keys

> Generate and manage API keys for the HappyRobot API

API keys authenticate requests to the HappyRobot API. There are two types: **organization keys** (shared across your org) and **personal keys** (tied to an individual user).

## Organization API keys

Organization-level API keys authenticate requests on behalf of your entire organization.

* Navigate to **Settings > API Keys** to manage organization keys
* You can have up to **10 active keys** at a time
* Keys are displayed as a prefix plus the last 4 characters (e.g., `hr_...a1b2`)
* Each key shows a **last used** timestamp so you can identify stale keys, and an **Expires** date
* Use the **Active** and **Revoked** tabs to switch between current and deactivated keys

<Steps>
  <Step title="Create a key">
    Click **Create API Key**, name it, choose its access grants, and set an **Expiration**. The full key is displayed once — copy it immediately.
  </Step>

  <Step title="Store it securely">
    Save the key in a secure location (e.g., a secrets manager or password vault).
  </Step>

  <Step title="Edit or revoke it later">
    Open the **⋯** menu on any active key and choose **Edit** to change its name or access, or **Revoke** to permanently deactivate it.
  </Step>
</Steps>

<Warning>
  Your API key is only shown once at creation. If you lose it, you will need to create a new key.
</Warning>

## Access grants for organization keys

An organization API key carries its own **role and scope grants**, the same way a [team member](02-Members-and-Access.md) does. What a request can do is decided by the grants on the key, not by whoever created it.

* Each grant pairs a role with a scope: the **full workspace**, or one or more [Scope Tags](04-Scope-Tags.md)
* A key needs at least one grant. New keys start with **Viewer** on the full workspace
* Multiple grants combine, so you can give a key Viewer everywhere plus Editor on `Region: LATAM`
* Tag grants are selectable only while **Tags as access scopes** is enabled for the workspace. Grants that fall inactive are flagged in the edit dialog so you can remove them
* Give integrations the narrowest role that still works. A key scoped to a role and a tag can only read and change resources inside that boundary

To change grants on an existing key, open the **⋯** menu next to it and choose **Edit**. The key value itself never changes, so callers keep working while you tighten or widen its access.

<Note>
  Organization keys created before access grants existed were given **Owner** on the full workspace, which matches the workspace-wide access they had previously. Review them and narrow them where a service only needs part of the workspace.
</Note>

Because the key is the principal, it gets no HappyRobot-staff bypass and no parent-organization fallback — it can only reach the workspace it belongs to. Revoking a key removes its grants with it.

<Info>
  Workspaces that resolve permissions from an identity provider manage key access through [SSO grants](05-SSO-Access.md) instead. In those workspaces the create and edit dialogs report that manual access grants require HR-managed RBAC, and keys keep their existing workspace-wide access.
</Info>

## Expiration

Each organization key gets an expiration when it's created. The options are **30 days**, **60 days**, **90 days**, **180 days**, **1 year**, and — unless your organization restricts key age — **Never**.

The **Expires** column in the key table shows what applies to each key:

| Value                  | Meaning                                                                                                 |
| ---------------------- | ------------------------------------------------------------------------------------------------------- |
| A date                 | The key stops working on that date.                                                                     |
| **Never**              | The key doesn't expire. Only possible while no organization maximum key age is set.                     |
| **Pending revocation** | The key is already past its expiry and is revoked on the next cleanup pass, which runs within the hour. |

An expired key is revoked, not restored — create a new key and update whatever was using the old one.

<Tip>
  Pick the shortest expiration your integration can live with, and set a calendar reminder ahead of the date. Rotating a key is a matter of creating the replacement, switching the caller over, and revoking the old key.
</Tip>

### Organization maximum key age

An owner can cap how long any key in the organization stays valid under **Settings > General**. See [API key retention](01-Organization.md#api-key-retention) for how to configure it.

When a maximum key age is set:

* **Never** disappears from the expiration picker, and only periods up to the cap are offered.
* Personal keys and organization keys are both bound by the cap.
* Existing keys are re-evaluated against it, so a key created before the policy can expire sooner than its own expiry date — the **Expires** column always shows whichever comes first.
* The limit is the default selection for new keys.
* API requests asking for a longer expiry than the policy allows are rejected with a `400` error.

### Key access is bounded by your own

A key can't be given access you don't hold yourself. Creating, updating, or revoking a key is rejected when the key's grants — their scope, or the actions in the roles you assign — exceed your own permissions, and the error appears next to the access editor so you can adjust the grant. A key created without explicit grants requests full-workspace Owner access, so it is subject to the same check. See [You can only grant access you hold](02-Members-and-Access.md#you-can-only-grant-access-you-hold).

## Personal API keys

Each user can create **1 personal API key**. Personal keys are tied to your individual user account, not the organization.

* Navigate to your **user settings** to manage your personal key
* The key is displayed as a prefix plus the last 4 characters, along with its expiry date when it has one
* A personal key follows the organization's maximum key age — there's no per-key expiration to choose
* You can revoke your existing key and create a new one in a single action
* Personal keys have no grants of their own — they inherit the roles and scopes of the user they belong to, so their access changes whenever yours does

## What a key can access

API requests are authorized with the same permission model as the platform UI, so which endpoints a key can call — and which records those endpoints return — depends on the grants behind it:

| Key type             | Access                                                                                                                                                                                                                                                                                                                                                   |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Organization key** | Whatever its own [access grants](#access-grants-for-organization-keys) allow — a role paired with the full workspace or a set of [Scope Tags](04-Scope-Tags.md). New keys start at **Viewer** on the full workspace; keys that predate access grants were backfilled to **Owner**. A key can never reach another workspace or a parent organization. |
| **Personal key**     | Exactly what its owner can do in the UI: their [role](02-Members-and-Access.md), their [custom role](03-Custom-Roles.md) actions, and their [Scope Tag](04-Scope-Tags.md) boundaries. Change the member's grants and the key's reach changes with them.                                                                                  |

This applies across the API — workflows, runs, sessions, contacts, integrations, signals, quality issues, Twin, voices, and organization details — and to the run stream: a key subscribed to run updates only receives runs it is allowed to view.

Requests that fall outside a key's permissions return `403 Forbidden`, and requests for a specific record the key cannot view return `404 Not Found` so the API doesn't reveal that the record exists. See [Error handling](https://docs.happyrobot.ai/api-reference/error-handling).

<Tip>
  Scope an organization key to the narrowest role and tags a service actually needs, and use **Edit** to adjust it later without rotating the key. Reach for a personal key only when an integration should track one person's access — for example a script that should stop working when that member's grants are revoked.
</Tip>

Personal keys don't have an expiration picker. They inherit the organization's maximum key age, and don't expire when no policy is set.

## Who can manage keys

Managing organization keys requires the **API key management** action on your role. That action is bounded by your own access: you cannot create a key, change a key's grants, or revoke a key that carries access you don't have yourself. See [Delegation limits](03-Custom-Roles.md#delegation-limits).

Any member of a workspace can create their own personal key — it inherits the permissions of their account.

## Using API keys

Include your API key in API requests to authenticate. See the [Authentication](https://docs.happyrobot.ai/api-reference/authentication) documentation for the full details on how to format your requests.

`GET /api-key/describe` reports the calling key's own metadata, including `expiresAt` — already reduced to the organization's maximum key age when one is set. Poll it from your integration if you want to warn before a key lapses.

## Bring your own LLM keys

The **⋮** menu next to **Create API Key** opens **Bring your own keys**, where you register your organization's own OpenAI, Anthropic, or Gemini credentials so model usage is billed to your provider account instead of HappyRobot's. These are provider credentials, not HappyRobot API keys — see [Bring your own keys](07-Bring-your-own-keys.md).

## Next steps

<CardGroup cols={2}>
  <Card title="API Reference" icon="book" href="https://docs.happyrobot.ai/api-reference/overview">
    Explore the full HappyRobot API.
  </Card>

  <Card title="Authentication" icon="lock" href="https://docs.happyrobot.ai/api-reference/authentication">
    Learn how to authenticate API requests.
  </Card>

  <Card title="Bring your own keys" icon="vault" href="07-Bring-your-own-keys.md">
    Use your own LLM provider credentials.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/api-keys
