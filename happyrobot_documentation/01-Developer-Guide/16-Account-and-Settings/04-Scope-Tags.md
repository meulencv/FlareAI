---
title: "Scope Tags"
description: "Organize resources and limit roles to matching tagged resources"
---

# Scope Tags

> Organize resources and limit roles to matching tagged resources

Scope Tags let you use the same role at different boundaries. For example, an operator can manage resources for `Region: LATAM` without receiving the same access to every resource in the workspace.

The access model is:

> **Role actions** apply when the member's grant scope matches the resource's Scope Tags.

## Set up Scope Tags

<Steps>
  <Step title="Create tag types">
    Go to **Settings > Tags**. Create vocabularies such as `Region`, `Team`, `Customer`, or `Environment`.
  </Step>

  <Step title="Create tags">
    Add values within each type, such as `Region: LATAM` or `Team: Support`. Tags can be nested into a hierarchy.
  </Step>

  <Step title="Tag resources">
    Assign Scope Tags to workflows, folders, phone numbers, apps, components, credentials, knowledge bases, and Twin tables.
  </Step>

  <Step title="Enable access scopes">
    Go to **Settings > General > Access Control** and enable **Tags as access scopes** (beta). Existing full-workspace grants remain unchanged.
  </Step>

  <Step title="Assign grants">
    On **Settings > Members**, combine a role with one tag, several tags, or the full workspace. [Organization API keys](06-API-Keys.md#access-grants-for-organization-keys) take the same kind of grants from **Settings > API Keys**.
  </Step>
</Steps>

<Info>
  Scope Tags can organize resources even while Tags as access scopes is off. The toggle controls whether tag-based member grants affect authorization.
</Info>

## Review tag coverage

On **Settings > Tags > All tags**, use **Show resources** to see which resources carry which tags without opening each resource. The toggle is available in workspaces that belong to a parent organization.

With it on:

* Every tag in the tree expands into the resources tagged with it, grouped by resource type.
* An **Untagged resources** section below the tree lists resources with no effective tag, grouped by type with a count per group. **Hide resources** collapses back to tags only.
* Resources are grouped by kind: workflows and workflow folders, phone numbers, node components, prompt components, integration credentials, knowledge bases, apps, and Twin. Each group header counts how many of its resources still have no tag.
* A tag badge with a solid background is **assigned directly**; an outlined badge is **inherited from the resource's workflow folder**.
* The search box covers resources as well as tags, matching resource names, resource types, and assigned tag names.

Only resources you can view appear. When a resource type can't be loaded — usually because your role can't view it — a warning tells you the list is incomplete.

### Assign tags by drag and drop

Drag a resource onto a tag to change its assignment. Dropping opens a small menu:

| Choice          | Result                                                                                                                                                |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Add**         | Adds the tag, keeping the resource's other tags. Disabled when the resource already has that tag.                                                     |
| **Move**        | Replaces the tag you dragged the resource out of with the drop target. Available only when you drag from a tag row and that tag is assigned directly. |
| **Replace all** | Removes every direct tag on the resource and leaves only the drop target.                                                                             |

Inherited tags — for example a tag a workflow gets from its folder — can't be moved or removed here. Change them on the resource that owns the assignment.

<Note>
  Twin appears in the view so you can see its coverage, but Twin tags can't be changed from here.
</Note>

## How matching works

Assume a resource has `Team: Support` and `Region: LATAM`.

| Grant                                                 | Result                                                       |
| ----------------------------------------------------- | ------------------------------------------------------------ |
| Full workspace                                        | Matches every resource, including untagged resources.        |
| One tag: `Team: Support`                              | Matches the tag and its descendants.                         |
| Compound: `Team: Support` **and** `Region: LATAM`     | Matches only when every listed tag is present.               |
| Two separate grants: `Team: Support`; `Region: LATAM` | Matches either grant. This is broader than a compound grant. |

The concise rule is:

* Tags inside one compound grant are **AND**.
* Separate grants are **OR**.
* Extra tags on a resource do not prevent a match.
* Untagged resources require a full-workspace grant.

### Hierarchies

A one-tag grant includes descendants. If `North America` contains `United States`, a grant on `North America` also matches a resource tagged `United States`.

Compound grants are literal. A compound grant on `Region: North America` and `Team: Support` does not match `Region: United States` unless the resource also carries the literal `North America` tag.

### Combining roles

Matching grants contribute their actions together. A member might have:

* **Viewer** across the full workspace.
* **Editor** on `Region: LATAM`.

They can view untagged and non-LATAM resources, while Editor actions are added only on matching LATAM resources.

## Workflow resource compatibility

Scope Tags also prevent a workflow from depending on a resource outside the workflow's boundary. A workflow can use a tagged resource only when it carries every tag assigned to that resource.

For example, a workflow tagged `Team: Support` and `Region: LATAM` can use a phone number tagged `Team: Support`. It cannot use a phone number tagged `Team: Sales`, or one with an additional tag missing from the workflow.

This comparison is literal; hierarchy does not expand tags. An untagged resource can be used only by an untagged workflow.

<Warning>
  User access and workflow compatibility answer different questions. A member's grant tags must be contained by the resource's tags; a dependency resource's tags must be contained by the workflow's tags.
</Warning>

## Who can hold a grant

| Principal            | Where grants are set    | Notes                                                                                                                                                                  |
| -------------------- | ----------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Member               | **Settings > Members**  | Combine roles and scopes per member.                                                                                                                                   |
| Pending invitation   | **Settings > Members**  | The grant applies as soon as the invitation is accepted.                                                                                                               |
| Organization API key | **Settings > API Keys** | The key is its own principal: requests are authorized by the grants on the key, not by the person who created it. No staff bypass and no parent-organization fallback. |

Personal API keys are not separate principals — they resolve to their owner's grants.

## Supported resources

Scope-based list and action enforcement currently covers:

* Workflows and workflow folders
* Phone numbers
* Apps
* Node and prompt components
* Credentials
* Knowledge bases
* Twin tables

<Note>
  A phone number is tagged once, as a number — not once per provider. Tags assigned from **Assets > Telephony > Manage tags** cover the number's Twilio, Telnyx, WhatsApp, and SIP connections together, so a WhatsApp number or a number with no SIP trunk can now be scoped like any other.
</Note>

Some workspace-wide libraries remain full-scope-only. If a resource does not offer a Scope Tag control, access to it is determined by the member's full-workspace actions.

## Tag and tag-type rules

* A tag type is a vocabulary; a tag is a value in that vocabulary.
* Tag and tag-type names can contain up to 256 characters.
* Names cannot contain `:`, `,`, `[` or `]` because those characters delimit SSO grant group names.
* `compound` is reserved as a tag-type name.
* Tag names are unique within the active vocabulary.
* Tags used by a member, pending invitation, or API key grant cannot be deleted until those grants are changed.
* Tags referenced by a saved [HR SSO Grant Builder](05-SSO-Access.md#saved-builder-rows) row cannot be deleted either. The delete dialog reports how many rows still use the tag, because deleting it would change the IdP group name those rows encode.
* Tag and tag-type renaming is disabled while group-name grant resolution is enabled, because names are part of the IdP contract.

## Disable Tags as access scopes

The toggle lives under **Settings > General > Access Control**. Disabling the feature does not delete tag definitions, resource assignments, or existing tag grants. Tag grants become inactive; full-workspace grants continue to apply.

HappyRobot blocks disabling if a member, pending invitation, or API key relies entirely on tag grants, and the confirmation tells you how many of each are affected. Give every affected principal a full-workspace grant first. If inactive tag grants exist, the member and API key editors can reveal them so they can be reviewed or removed.

## Scope Tags in parent organizations

Parent organizations control two independent settings:

### Where tags are managed

* **Tags managed by parent organization** provides one shared vocabulary across every child workspace. Manage it from the parent Tags page; child workspaces can browse it but cannot edit it.
* When disabled, each child workspace owns an independent vocabulary.

Changing ownership makes the outgoing vocabulary inactive and removes its assignments from resources. The change is blocked while members or pending invitations still reference the outgoing tags.

### Where access scopes are enabled

Enabling Tags as access scopes at the parent level enables it for every child workspace. The setting is inherited and cannot be disabled by a child while the parent setting remains on.

Direct parent-member tag grants are available only when the parent owns the shared tag vocabulary. Full-parent grants apply across all current and future child workspaces.

## Recommended rollout

1. Design a small, stable vocabulary around real access boundaries.
2. Tag resources before assigning tag-only members.
3. Start with a full-workspace Viewer grant plus narrow elevated grants.
4. Test untagged resources and workflow dependencies explicitly.
5. Use the [SSO Grant Builder](05-SSO-Access.md#build-idp-group-names) to generate IdP groups.
6. Remove broad grants only after the scoped behavior is verified.

<CardGroup cols={2}>
  <Card title="Custom Roles" icon="shield" href="03-Custom-Roles.md">
    Choose the actions that apply inside each scope.
  </Card>

  <Card title="SSO Access" icon="key" href="05-SSO-Access.md">
    Resolve IdP groups into role-and-scope grants.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/scope-tags
