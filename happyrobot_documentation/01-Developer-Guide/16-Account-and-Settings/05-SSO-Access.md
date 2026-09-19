---
title: "SSO Access"
description: "Configure SSO login and resolve identity-provider groups into access grants"
---

# SSO Access

> Configure SSO login and resolve identity-provider groups into access grants

Single Sign-On (SSO) can authenticate users and, optionally, make identity-provider groups authoritative for their HappyRobot access.

These are separate controls:

| Control                                    | Purpose                                                                                        |
| ------------------------------------------ | ---------------------------------------------------------------------------------------------- |
| **Enable SSO Login**                       | Lets users sign in through your identity provider. Contact HappyRobot Support to configure it. |
| **Resolve incoming group names as grants** | Converts supported IdP group names into HappyRobot roles and access scopes.                    |

Enabling SSO login alone does not decide which workflows or settings a user can access.

## Authorization modes

| Mode                     | Custom roles      | Scope Tags | Current recommendation                |
| ------------------------ | ----------------- | ---------- | ------------------------------------- |
| Manual HR-managed access | Yes               | Yes        | Use for access managed in HappyRobot. |
| **HR SSO Grants**        | Yes               | Yes        | Use for access managed in your IdP.   |
| Legacy SSO RBAC          | System roles only | No         | Deprecated; migrate to HR SSO Grants. |

Legacy SSO RBAC may still appear for organizations already using it. It uses a different policy and legacy `HR_...` group format. New HR SSO Grant names use `HR:` and are ignored by legacy mode.

## Resolve group names as grants

You need permission to update workspace or parent-organization settings.

<Steps>
  <Step title="Configure SSO login">
    Contact HappyRobot Support from **Settings > SSO Access** to connect your identity provider.
  </Step>

  <Step title="Model access in HappyRobot">
    Create the required [custom roles](03-Custom-Roles.md), [Scope Tags](04-Scope-Tags.md), and test member grants.
  </Step>

  <Step title="Generate group names">
    Use the **HR SSO Grants > Grant Builder** tab. Select a role and either the full workspace or a Scope Tag expression, then copy the generated name.
  </Step>

  <Step title="Create and assign IdP groups">
    Create groups with those exact names in your identity provider and assign users to them.
  </Step>

  <Step title="Enable resolution">
    Under **Settings > General > Access Control**, turn on **Resolve incoming group names as grants** and choose how to reconcile existing HappyRobot assignments.
  </Step>

  <Step title="Verify a login or sync">
    Confirm each test user receives the expected workspace membership and grants before migrating the rest of the organization.
  </Step>
</Steps>

### Reconcile existing access

When enabling resolution, choose one of these transitions:

* **Remove existing roles and grants immediately**: current HappyRobot assignments are revoked. Users regain access after their IdP groups are processed at login or sync.
* **Keep roles until next login**: current assignments remain until each user's next SSO reconciliation, then the IdP groups replace them.

<Warning>
  After resolution is enabled, the relevant IdP groups are authoritative. Removing a user's last valid grant group for a workspace or parent organization removes their access to that target.
</Warning>

Disabling resolution stops future group-name reconciliation. It does not automatically delete the grants already materialized in HappyRobot; review and manage those assignments from the Members page.

## Build IdP group names

Always copy names from the Grant Builder when possible. It uses role slugs, typed tags, canonical ordering, and the correct workspace or parent-organization slug.

The **New Role** and **New Tag** shortcuts appear when you have `role.create` or `tag.manage`, respectively. If Tags as access scopes is off, the builder offers full-scope grants and links you to enable the feature for tag-scoped grants.

### Saved builder rows

Builder rows are stored on the workspace or parent organization, not in your browser. Every row you add, edit, or remove is saved as you make the change, so the set of group names your organization has modeled is the same for every administrator and survives switching machines.

Two consequences are worth knowing:

* Editing rows requires `workspace.settings.update` (or `parent-org.settings.update`). With view-only settings access you can read the rows and copy names but not change them.
* A tag referenced by a builder row cannot be deleted until the row is changed or removed. Deleting the tag would silently change the group name the row encodes, so HappyRobot blocks it and the delete dialog reports how many builder rows still use the tag. The same applies to deleting a tag type.

Builder rows are configuration only — they describe group names, they never grant access on their own.

### Full-workspace access

```text theme={null}
HR:wsp:<workspace-slug>:<role-slug>
```

Example:

```text theme={null}
HR:wsp:acme-support:editor
```

### One Scope Tag

```text theme={null}
HR:wsp:<workspace-slug>:<tag-type>:<tag-value>:<role-slug>
```

Example:

```text theme={null}
HR:wsp:acme-support:Region:LATAM:workflow-author
```

A one-tag grant includes descendants of that tag.

### Compound Scope Tags

```text theme={null}
HR:wsp:<workspace-slug>:compound:[<tag-type>:<tag-value>,<tag-type>:<tag-value>]:<role-slug>
```

Example:

```text theme={null}
HR:wsp:acme-support:compound:[Region:LATAM,Team:Support]:workflow-author
```

Every tag in the brackets is required. Assign several separate group names when the user should match any of several scopes.

### Parent-organization access

Replace `wsp` with `po` and use the parent-organization slug:

```text theme={null}
HR:po:acme:owner
HR:po:acme:Region:LATAM:workflow-author
```

A full-parent grant covers all current and future child workspaces. Parent tag grants depend on a shared, parent-managed tag vocabulary.

## Reuse an existing IdP group name

You don't have to create HappyRobot's canonical `HR:` groups in your identity provider. Each grant you configure in the Grant Builder can carry one **alias** — a group name your IdP already sends — that resolves to the same role and scope.

<Steps>
  <Step title="Configure the grant">
    Add the grant in **HR SSO Grants > Grant Builder** and pick its role and scope as usual. The canonical `HR:` name appears beneath it.
  </Step>

  <Step title="Add the alias">
    Click **Add custom alias** under the generated name, then select or type the IdP group name. The picker suggests your parent organization's existing **Policies** and the **Legacy group names** from legacy SSO RBAC, and you can enter any other name instead.
  </Step>

  <Step title="Save it">
    Confirm with the check button. The alias appears as a second row under the grant, with buttons to copy, edit, or remove it.
  </Step>
</Steps>

An alias can contain at most 256 characters. Removing an alias leaves the grant in place; removing the grant removes its alias too. A grant has at most one alias — configure a second grant if two IdP group names should map to the same role and scope.

At login or directory sync, a claimed group name that matches an alias is treated exactly like its canonical `HR:` name, so aliased and canonical groups can be mixed during a migration.

<Warning>
  Alias matching is exact and does not use the `HR:` prefix, so a name that is short or generic — `admins`, for example — is easy to collide with. Prefer names that already identify the workspace or role.
</Warning>

## Group-name rules

* Use the generated `HR:` prefix. The `wsp` and `po` namespace identifies the target type.
* The role slug is always the final segment.
* A group name can contain at most 256 characters.
* Workspace, parent, role, tag-type, and tag-value segments cannot contain `:`, `,`, `[` or `]`.
* `compound` is reserved for multi-tag scopes.
* Only typed tags can be encoded.
* The target, role, tag type, and tag value must already exist when the claim is processed.
* Use one full-scope group per target. Multiple full-scope roles are ambiguous because only one full-scope grant can be stored.
* Do not use resource-type segments. Only full, one-tag, and compound-tag formats are supported.

Role slugs are matched exactly. Tag type and tag value matching is case-insensitive, but preserving the generated casing makes IdP configuration easier to audit.

## Preview the groups existing members need

Open **HR SSO Grants > Workspace Member Groups** or **Parent Org Member Groups**. The page shows the canonical groups that reproduce each member's current HappyRobot grants, separated into:

* Full workspace or parent-organization access
* Tag-scoped access

Rows are rendered exactly as in the Grant Builder, so a name you read here matches a name you generate there. A section is hidden when the member has no grants of that kind, and members with no grants at all — or a suspended role — are left out of the list.

Use this view to stage a migration in your IdP before enabling resolution. Viewing it requires access to the corresponding Members page. If you lack that permission, HappyRobot displays the exact member action you need to request from an administrator.

## Reconciliation behavior

At SSO login or directory sync, HappyRobot:

1. Selects grant-shaped group claims for each workspace or parent target.
2. Resolves the target slug, role slug, and any typed Scope Tags.
3. Creates or updates the target membership for an existing HappyRobot user.
4. Replaces that target's grants with the valid groups in the latest claim set.
5. Removes target access when the user's last relevant grant group disappears.

Claims are reconciled independently per target. Groups from multiple connected directories are aggregated so one directory does not revoke a grant still asserted by another.

Invalid group names are ignored while other valid claims for the same target still apply. Common causes are an invalid format, an unknown target, an archived role, a renamed or deleted tag, or a name longer than 256 characters.

<Warning>
  For a target that still exists, if none of its claimed groups resolves to a valid role-and-scope grant, HappyRobot clears that target's access. Validate generated names and test with a limited group before a broad rollout.
</Warning>

## Parent inheritance

Enabling group-name resolution at a parent organization makes it effective for its child workspaces. A child cannot override an inherited enabled setting.

Parent-managed roles and parent-managed Scope Tags determine which catalog is used when parent group names are resolved. Role ownership and tag ownership are independent; confirm both before generating parent-level group names.

## Required permissions

* Viewing the workspace page requires `workspace.settings.view`; changing its toggle requires `workspace.settings.update`.
* Parent equivalents are `parent-org.settings.view` and `parent-org.settings.update`.
* Workspace Member Groups requires `workspace.member.view`.
* Parent Org Member Groups requires `parent-org.member.manage`.
* Creating shortcuts depend on `role.create` and `tag.manage`.

## Migrate from legacy SSO RBAC

Legacy SSO RBAC and HR SSO Grants cannot control the same organization at the same time.

### Stage the new model before the cutover

While legacy SSO RBAC is still active, you can build the replacement model in advance. The Roles, Tags, and SSO Access pages show a **Legacy SSO RBAC is still active** banner and let you create and edit tags, custom roles, and HR SSO grants. Those definitions are saved but have no effect on access, and they become active when legacy SSO RBAC is turned off.

While staging:

* The Grant Builder offers tag scopes even though Tags as access scopes is off, so you can generate the group names your IdP will need.
* Custom roles appear in the grant and alias pickers.
* The **Resolve incoming group names as grants** toggle and the parent **Tags as access scopes** setting stay hidden — they're part of the cutover, not the staging.

### Cut over

1. Recreate required access with system or custom roles and Scope Tags.
2. Use the Member Groups view to generate the new canonical `HR:` group names.
3. Create and assign those groups in your identity provider.
4. Contact HappyRobot Support to coordinate the legacy-mode change.
5. Enable **Resolve incoming group names as grants** with the appropriate reconciliation option.
6. Verify a test cohort, then remove legacy `HR_...` groups.

## Operational checklist

* Keep at least one full-workspace Owner outside a narrow tag scope.
* Treat role and tag slugs/names as an IdP interface once groups are deployed.
* Use the builder again after any role, workspace, parent, or tag change.
* Test untagged resources; tag-only users cannot access them.
* Test a removed group as carefully as an added group.
* Review members after disabling resolution because materialized grants remain.

<CardGroup cols={3}>
  <Card title="Members and Access" icon="users" href="02-Members-and-Access.md">
    Review the grants that SSO will reproduce.
  </Card>

  <Card title="Custom Roles" icon="shield" href="03-Custom-Roles.md">
    Define the action sets used in IdP groups.
  </Card>

  <Card title="Scope Tags" icon="tags" href="04-Scope-Tags.md">
    Define the resource boundaries used in scoped groups.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/sso-access
