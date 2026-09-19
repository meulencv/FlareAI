---
title: "Custom Roles"
description: "Create reusable roles from HappyRobot access actions"
---

# Custom Roles

> Create reusable roles from HappyRobot access actions

Roles define **what** a member can do. A custom role is a reusable collection of access actions that matches a job function, such as workflow author, reviewer, telephony operator, or billing administrator.

Use [Scope Tags](04-Scope-Tags.md) separately to decide **where** those actions apply.

## System and custom roles

|                  | System roles          | Custom roles                 |
| ---------------- | --------------------- | ---------------------------- |
| Examples         | Owner, Editor, Viewer | Roles you create             |
| Editable         | No                    | Yes                          |
| Duplicable       | Yes                   | Yes                          |
| Archivable       | No                    | Yes, when unassigned         |
| SSO group names  | Supported             | Supported with HR SSO Grants |
| Scope Tag grants | Supported             | Supported                    |

## Create a role

You need permission to create roles.

<Steps>
  <Step title="Open Roles">
    Go to **Settings > Roles** and select **New Role**.
  </Step>

  <Step title="Describe the role">
    Enter a name and an optional description. HappyRobot generates the stable role slug used in SSO group names.
  </Step>

  <Step title="Choose actions">
    Search or browse the action catalog and select at least one action. Actions are grouped by product area.
  </Step>

  <Step title="Review dependencies">
    Some actions require another action. HappyRobot selects and locks prerequisites automatically until every dependent action is removed.
  </Step>

  <Step title="Create the role">
    The role becomes available in member, invitation, and SSO grant builders.
  </Step>
</Steps>

Role names must contain 2–256 characters. Descriptions can contain up to 1,000 characters.

## Tag-scoped and full-scope-only actions

The role editor separates actions according to whether they can apply through a Scope Tag grant.

* **Tag-scoped actions** apply to matching resources, such as viewing or managing a workflow, credential, app, or knowledge base.
* **Full-scope-only actions** control the workspace or parent organization as a whole, such as organization-wide administration and settings.

If a role is assigned only through Scope Tags, its full-scope-only actions stay inactive. Give the member a full-workspace grant when they also need those actions.

<Warning>
  A tag-scoped **Owner** does not become a global workspace Owner. Owner-only administration and last-owner protection rely on a full-workspace or full-parent grant.
</Warning>

**API key management** is not full-scope-only. It can be held through a Scope Tag grant, and it is bounded by the grants the caller actually has — see [Delegation limits](#delegation-limits).

## Delegation limits

You cannot hand out access you don't hold yourself. HappyRobot enforces this on the server for every path that confers access, so the rule holds through the UI, the API, and Frontal alike:

| Action                                           | Limit                                                                                                                                                                                                                                                |
| ------------------------------------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Inviting a member, or changing a member's grants | Every role-and-scope grant you assign must be covered by your own grants: you need each of the role's actions everywhere the proposed scope reaches. Changing an existing member also requires that you can already delegate their *current* grants. |
| Creating or updating an API key, or revoking one | Same rule, applied to the key's grants. Revoking an organization key requires that you could have granted that key's access.                                                                                                                         |
| Creating or updating a role                      | Because editing a role changes every assignment of it, you need each action in the role across the whole scope that owns the role — a tagged branch is not enough. The error names the role and says it includes actions you do not have.            |

Scope coverage follows the Scope Tag rules in [How matching works](04-Scope-Tags.md#how-matching-works): a full-workspace grant covers everything, and a tag grant covers its tag and descendants. A grant you hold only on `Region: LATAM` cannot be used to give someone the same role across the workspace.

<Note>
  Suspended members are exempt from the current-grant check, so you can reactivate and re-scope a suspended member without first being able to delegate the access they had before.
</Note>

## Edit, duplicate, or archive a role

* **Edit** changes the role for every member and invitation that uses it. Custom roles only.
* **Duplicate** creates a starting point for a similar role. You can duplicate **Owner**, **Editor**, and **Viewer** as well as your own roles, so a new custom role can start from a system role's action list instead of an empty one. The copy is a normal custom role — editable, archivable, and independent of the system role it came from.
* **Archive** removes an unused custom role from assignment lists.

Duplicating needs permission to edit the role catalog. In a workspace whose roles are managed by its parent organization, the catalog is read-only and neither action is offered.

HappyRobot blocks archival while the role is assigned to any member or pending invitation, including Scope Tag grants. The impact dialog identifies affected assignments so you can replace them first.

<Tip>
  Prefer a few job-function roles over one role per person. Combine a reusable role with different scopes to vary access without duplicating its action list.
</Tip>

## Roles in parent organizations

A parent organization chooses where child-workspace role catalogs are managed:

* **Roles managed by parent organization**: define one shared catalog in the parent. Child workspaces inherit it and cannot edit it.
* **Roles managed by workspaces**: each child owns its catalog. The parent Roles page provides a workspace-by-workspace view.

This setting is independent from Scope Tag ownership. A parent can centralize roles while leaving tags local to each workspace, or the reverse.

<Warning>
  Changing role ownership replaces assignments that reference custom roles from the outgoing catalog with **Viewer**. Review the impact shown in the confirmation dialog before switching.
</Warning>

## Roles and SSO

Custom roles work with [HR SSO Grants](05-SSO-Access.md#resolve-group-names-as-grants). The canonical group name uses the role's slug as its final segment.

```text theme={null}
HR:wsp:acme-support:workflow-author
```

The slug is generated when the role is created and remains stable if you later edit its display name. Use the SSO Grant Builder to discover the current slug rather than constructing group names by hand.

Legacy SSO RBAC supports only the system roles. Organizations still using that mode must migrate to HR-managed roles and HR SSO Grants before assigning custom roles through SSO.

## Related permissions

Role access is controlled by separate view, create, update, and delete actions. A user may be able to assign an existing role without being able to change the role catalog.

<CardGroup cols={2}>
  <Card title="Members and Access" icon="users" href="02-Members-and-Access.md">
    Assign roles directly to members and invitations.
  </Card>

  <Card title="Scope Tags" icon="tags" href="04-Scope-Tags.md">
    Apply roles to subsets of resources.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/custom-roles
