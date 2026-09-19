---
title: "Members and Access"
description: "Manage members, invitations, roles, and access grants"
---

# Members and Access

> Manage members, invitations, roles, and access grants

HappyRobot access is built from **grants**. Each grant combines a role with a scope:

* The **role** defines what the member can do.
* The **scope** defines where those actions apply.

```mermaid theme={null}
flowchart LR
  Member[Member or invitation] --> Grant[Access grant]
  Role[Role: what they can do] --> Grant
  Scope[Scope: where it applies] --> Grant
  Grant --> Access[Effective access]
  Tags[Scope Tags on resources] --> Access
```

A member can have a full-workspace grant, one or more Scope Tag grants, or both. When more than one grant matches a resource, HappyRobot combines the actions from the matching roles.

<Info>
  Scope Tag grants are available when **Tags as access scopes** is enabled. Until then, members receive full-workspace access and any existing tag grants remain inactive.
</Info>

## Grant types

| Scope               | What it covers                                                                              |
| ------------------- | ------------------------------------------------------------------------------------------- |
| Full workspace      | Every resource, including untagged resources, plus any workspace-level actions in the role. |
| One Scope Tag       | Resources carrying that tag or one of its descendants.                                      |
| Compound Scope Tags | Resources carrying every tag in the grant.                                                  |

Each row can use a different role. For example, a member can be a full-workspace Viewer and an Editor only for resources tagged `Region: LATAM`.

## System roles

Every workspace includes these system roles:

| Role       | Description                                                         |
| ---------- | ------------------------------------------------------------------- |
| **Owner**  | Full access to every available action.                              |
| **Editor** | Can create and manage day-to-day workspace resources.               |
| **Viewer** | Can view and use permitted resources without administrative access. |

System roles cannot be edited or archived. You can create [custom roles](03-Custom-Roles.md) when these defaults are too broad.

## Invite a member

You can invite one person or paste comma- or newline-separated email addresses to invite several people at once.

<Steps>
  <Step title="Open Members">
    Go to **Settings > Members** and select **Invite**.
  </Step>

  <Step title="Enter the email addresses">
    Review the preview for invalid addresses, existing members, or pending invitations.
  </Step>

  <Step title="Assign access">
    Select a role for full-workspace access. If Tags as access scopes is enabled, you can also add one or more role-and-tag grants.
  </Step>

  <Step title="Send the invitations">
    Each valid recipient receives an invitation. Pending invitations can be resent or revoked before acceptance.
  </Step>
</Steps>

The invitation keeps the selected grants. When the recipient accepts, HappyRobot transfers those grants to the new membership.

The **New Role** and **New Tag** shortcuts appear in the access editor only when you have permission to create roles or manage Scope Tags.

## You can only grant access you hold

Access is bounded by your own permissions. HappyRobot rejects an invitation or an access change — in the UI and through the API — when the grant you're assigning would exceed what you can do yourself:

* **Scope** — you must hold the inviting or updating permission everywhere the requested scope reaches. A member scoped to `Region: LATAM` can't grant full-workspace access, or access to a tag they don't cover.
* **Actions** — every action in the role you're assigning must be an action you hold across that same scope. You can't hand out a permission you don't have.

The denial says whether the scope or the role was the problem, and it's shown next to the access editor so you can adjust the grant. The same ceiling applies when creating, updating, or revoking [API keys](06-API-Keys.md).

## Manage a member

From **Settings > Members**, you can:

* Review every active member and pending invitation.
* Change a member's full-workspace and Scope Tag grants.
* Suspend a member without deleting their identity.
* Reactivate a suspended member and assign fresh access.
* Search by name or email.

HappyRobot prevents changes that would leave a workspace without a full-workspace Owner. A tag-scoped Owner is not a substitute: workspace administration and other full-scope-only actions require a full-workspace grant.

### You can only grant what you hold

Invitations and grant changes are bounded by your own access. To assign a role-and-scope grant, you need every action in that role everywhere the scope reaches — so an Editor scoped to `Region: LATAM` cannot invite someone as a full-workspace Editor. Editing an existing member additionally requires that you could have granted the access they already have. The check runs on the server, so it applies to the API and Frontal as well as the members page. See [Delegation limits](03-Custom-Roles.md#delegation-limits).

### When SSO resolves access

When **Resolve incoming group names as grants** is enabled, the identity provider becomes authoritative for role and scope assignments. Invitations and manual access editing are disabled. Update the user's groups in your identity provider, then let the next SSO login or directory sync reconcile their HappyRobot access.

See [SSO Access](05-SSO-Access.md) for group-name formats and reconciliation behavior.

## Manage members through the API

You can list, add, and remove members with an [API key](06-API-Keys.md) for the workspace.

### List members

`GET /org/members` returns the members of the authenticated organization. Listing requires the **view workspace members** action.

```bash cURL theme={null}
curl -X GET "https://platform.happyrobot.ai/api/v2/org/members" \
  -H "Authorization: Bearer hr_live_abc123def456"
```

```json theme={null}
{
  "data": [
    {
      "user_id": "6f1d2c8e-6f4b-4e2a-9c3d-9a1b2c3d4e5f",
      "email": "teammate@example.com",
      "first_name": "Ada",
      "last_name": "Lovelace",
      "image_url": null,
      "role": "editor"
    }
  ]
}
```

`role` is the member's workspace-wide role, and is `null` when they only hold [Scope Tag](04-Scope-Tags.md) grants.

### Add a member

`POST /org/members` currently supports a full-workspace `editor` or `viewer` system role. It defaults to `viewer`; it does not create custom-role or Scope Tag grants. Owners cannot be assigned through this endpoint.

```bash cURL theme={null}
curl -X POST "https://platform.happyrobot.ai/api/v2/org/members" \
  -H "Authorization: Bearer hr_live_abc123def456" \
  -H "Content-Type: application/json" \
  -d '{"email": "teammate@example.com", "role": "editor"}'
```

The response reports whether the user was added directly or invited:

```json theme={null}
{
  "data": {
    "org_id": "org_123",
    "email": "teammate@example.com",
    "role": "editor",
    "status": "invited"
  }
}
```

`status` is `member` when the user was added immediately or `invited` when they must accept an email invitation.

### Remove a member

`DELETE /org/members` removes a member by either `email` or `user_id`. Provide exactly one. Owners cannot be removed through this endpoint.

```bash cURL theme={null}
curl -X DELETE "https://platform.happyrobot.ai/api/v2/org/members?email=teammate@example.com" \
  -H "Authorization: Bearer hr_live_abc123def456"
```

See the [API reference](https://docs.happyrobot.ai/api-reference/overview) for complete request and response schemas.

## Email domains for automatic access

If your organization has approved email domains, users with matching addresses can join automatically without an invitation. See [Organization Settings](01-Organization.md#domains).

## Next steps

<CardGroup cols={3}>
  <Card title="Custom Roles" icon="shield" href="03-Custom-Roles.md">
    Define the exact actions available to each job function.
  </Card>

  <Card title="Scope Tags" icon="tags" href="04-Scope-Tags.md">
    Limit roles to matching tagged resources.
  </Card>

  <Card title="SSO Access" icon="key" href="05-SSO-Access.md">
    Resolve identity-provider groups into the same grants.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/team-members-and-roles
