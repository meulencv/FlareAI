---
title: "Organization"
description: "Manage your organization settings"
---

# Organization

> Manage your organization settings

Organization settings control how your HappyRobot organization is configured, who can join automatically, how failures are handled, and whether workflows require approval before publishing.

## General settings

Navigate to **Settings > General** to manage your organization's basic information.

* **Organization name** — the display name for your organization (editable)
* **Organization image** — a URL for your organization's logo or avatar
* **Organization ID** — a read-only identifier you can copy for use in API integrations
* **Industries** — select the industries your organization operates in; this determines which integrations are available to you

## Domains

The **Domains** section lets you add approved email domains so that users with matching email addresses can join your organization automatically — no invitation required.

<Steps>
  <Step title="Navigate to Domains">
    Go to **Settings > Domains**.
  </Step>

  <Step title="Add a domain">
    Enter the domain (e.g., `company.com`, not `@company.com`) and click **Add**.
  </Step>

  <Step title="Manage domains">
    Search, view, and delete domains from the list.
  </Step>
</Steps>

<Warning>
  Users with an email address matching an approved domain will gain instant access to your organization. Only add domains that belong to your company.
</Warning>

Common email providers (Gmail, Outlook, Yahoo, Hotmail, iCloud, AOL, ProtonMail, Yandex, etc.) are blocked and cannot be added as approved domains.

## Data retention

Under **Advanced Settings** in the General tab, you can set a retention policy for the whole workspace. Workflow data — transcripts, recordings, node outputs — is deleted after the configured period.

| Setting                        | Description                                                                                  |
| ------------------------------ | -------------------------------------------------------------------------------------------- |
| **Workspace Data Retention**   | Toggle on to delete workflow data in this workspace after a fixed period.                    |
| **Workspace Retention Period** | **7 days**, **14 days**, **30 days**, **60 days**, **90 days**, **180 days**, or **1 year**. |

### How workspace and workflow policies interact

A workflow can set its own, shorter retention period in [workflow settings](10-Workflow-Settings.md#data-retention), but it can't keep data longer than the workspace policy:

* Periods longer than the workspace policy are not offered in the workflow's picker.
* A workflow that already had a longer period shows it as **exceeds workspace limit** and can't be saved with that value.
* When both are set, the shorter of the two applies.

### Reviewing affected workflows

When you shorten the workspace period, the warning below the field links to an **Affected Workflows** dialog listing every workflow whose data would start being deleted sooner, along with each one's own retention policy (or **Not defined**). Saving then asks you to confirm, since the next cleanup may delete data that is currently retained.

<Warning>
  Shortening a retention period is not reversible for data that has already been deleted. Review the affected workflows before confirming.
</Warning>

<Note>
  Through the [API](https://docs.happyrobot.ai/api-reference/overview), a `data_retention_days` value on workflow create or update is rejected with a 400 error when it exceeds the workspace policy.
</Note>

## API key retention

Also under **Advanced Settings** in the General tab, you can require every [API key](06-API-Keys.md) in the workspace to expire after a fixed period.

| Setting                      | Description                                                         |
| ---------------------------- | ------------------------------------------------------------------- |
| **Enable API Key Retention** | Toggle on to require API keys in this organization to expire.       |
| **Maximum Key Age**          | **30 days**, **60 days**, **90 days**, **180 days**, or **1 year**. |

The limit applies to organization keys, personal keys, and keys that already exist. A key's effective expiry is the earlier of its own expiration and its creation date plus this limit. With the policy on, **Never** is no longer offered when creating a key, and the expiration picker only lists periods at or below the limit.

### Reviewing affected keys

When you enable or shorten the policy, a warning below the field counts the existing keys whose expiry would move earlier. Click **See affected keys** for the **Affected API Keys** dialog listing each key with its **current effective expiry** and **new effective expiry**; keys already past the new limit show **Immediately**. Saving then asks you to confirm.

<Warning>
  Keys already past the new limit are revoked within the hour, and revocation is irreversible. Any integration using one stops authenticating — rotate it before you apply the policy.
</Warning>

Changing this policy requires the **Update API key policy** action, which is a full-workspace action. See [Custom Roles](03-Custom-Roles.md).

## Disaster recovery

Configure a default fallback phone number for inbound voice workflows. If an inbound workflow encounters a failure, calls will be forwarded to this number instead of being dropped.

* Enter a phone number in **E.164 format** (e.g., `+1234567890`)
* This setting applies to all inbound voice workflows in your organization
* Individual workflows can override this number on their inbound trigger node

## Workflow approval process

Control whether workflows in your organization require approval before being published to specific environments.

You can toggle approval requirements independently for each environment:

| Environment     | Effect when enabled                                         |
| --------------- | ----------------------------------------------------------- |
| **Production**  | Workflows must be approved before publishing to production  |
| **Staging**     | Workflows must be approved before publishing to staging     |
| **Development** | Workflows must be approved before publishing to development |

Organization-level approval settings cascade to all workflows. Individual workflows can add stricter requirements but cannot remove enforcement set at the organization level.

<Note>
  Disabling approval for an environment that has open publish requests will close those pending requests. You will be asked to confirm before this happens.
</Note>

## Next steps

<CardGroup cols={3}>
  <Card title="Team Members and Roles" icon="users" href="02-Members-and-Access.md">
    Invite members and manage role-based access.
  </Card>

  <Card title="API Keys" icon="key" href="06-API-Keys.md">
    Generate keys for the HappyRobot API.
  </Card>

  <Card title="Environment Variables" icon="code" href="08-Environment-Variables.md">
    Configure variables across environments.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/organization
