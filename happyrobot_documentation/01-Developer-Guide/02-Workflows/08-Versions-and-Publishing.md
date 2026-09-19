---
title: "Versions and Publishing"
description: "Managing workflow versions and publishing changes"
---

# Versions and Publishing

> Managing workflow versions and publishing changes

Versions let you iterate on workflows safely. Make changes to a draft, publish when ready, and roll back to any previous version if something goes wrong. Every published version is a complete snapshot of your workflow configuration.

## How versions work

Each workflow maintains a version history. You work on an unlocked draft version, making changes freely. When you publish, HappyRobot locks the current configuration into a numbered version and activates it for the selected environment.

* **Draft** — Your current working copy. Editable, auto-saved, not yet live.
* **Published version** — A locked snapshot. Immutable once published.
* **Active version** — The published version currently running in a given environment. Each environment (development, staging, production) can have a different active version.

## Creating a version

<Steps>
  <Step title="Make changes to your workflow">
    Edit nodes, update configurations, add or remove steps. All changes auto-save to the current draft — no manual save needed.
  </Step>

  <Step title="Review your changes">
    Before publishing, review the workflow in the editor to make sure everything looks right. Trigger a test run to verify your changes work as expected.
  </Step>

  <Step title="Publish">
    When you're ready, click **Publish** to create a new version. Select the target environment and submit. Depending on your organization's approval settings, the version may go live immediately or require approval first.
  </Step>
</Steps>

## Publishing and approvals

When you publish, HappyRobot creates a **publish request** for the target environment. Depending on your organization's approval settings, the request follows one of two paths:

### Direct publish

If approval is not required for the target environment, the version is published and activated immediately. New triggers will execute using the published version right away.

### Approval required

If your organization requires approval for the target environment (e.g., production), the publish request enters a review flow:

<Steps>
  <Step title="Submit publish request">
    Click **Publish** and select the target environment. The request is created with a `pending` status.
  </Step>

  <Step title="Owner reviews and approves">
    An organization owner reviews the publish request and either approves or rejects it. Approved requests move to `approved` status.
  </Step>

  <Step title="Publish from approved request">
    Once approved, the version can be published to the target environment. It becomes the active version immediately.
  </Step>
</Steps>

<Info>
  Approval requirements are configured per environment. For example, you might allow direct publishing to development and staging but require approval for production. Configure this in **Settings > Workflow Settings**.
</Info>

You can also configure whether workflows with validation issues (missing configurations, incomplete nodes) are allowed to be published. See **Settings > Workflow Settings** for these options.

### Unreviewed tool results

A version can't be published while one of its active tools still has an unreviewed [Tool Call Result](../04-Tools/03-Tool-Call-Result.md). The tool appears in the publish blockers with the reason *Tool Call Result has not been opened yet*, and the tool node shows a red warning glyph in the editor.

Open the tool's **View Tool Call Result** panel once — or generate its schemas, or change field visibility — and the block clears. A copied tool needs its own review; tools created before the review flow existed never block publishing.

## Version history

Every version action is recorded in the version history panel. The changelog tracks:

* **Publishes** — When a version was published and to which environment
* **Unpublishes** — When a version was taken offline
* **Unlocks** — When a locked version was unlocked for editing
* **Forks** — When a new draft was created from an existing version
* **Workflow updates** — Configuration changes within a version

You can view the changelog in the versions sidebar of the workflow editor.

## Rolling back

If a published version has issues, you can roll back to any previous version instantly.

<Steps>
  <Step title="Open version history">
    Navigate to the version history panel in the workflow editor.
  </Step>

  <Step title="Select a version">
    Choose the version you want to restore. Review its configuration to confirm it's the right one.
  </Step>

  <Step title="Restore the version">
    Click **Restore** to make the selected version the active version. The workflow immediately starts using the restored configuration for new runs.
  </Step>
</Steps>

A rollback restores the full workflow configuration — node settings, connections, variables, and conditions. It does not affect runs that are already in progress.

<Warning>
  Runs that started before the rollback will continue using the version they were initiated with. Only new runs will use the restored version.
</Warning>

## Locking and unlocking

Published versions are locked by default — they cannot be edited. This protects the integrity of your version history.

If you need to make changes to a previously published version, you can unlock it to create a new draft based on that version. The original published version remains unchanged in the history.

<Info>
  Unlocking a version creates a new draft copy. The published version is never modified — your version history stays intact.
</Info>

## Workflow engine version (v2 and v3)

Each workflow version independently tracks which engine it runs on — v2 or v3. You can upgrade individual versions to v3 without affecting other versions in the same workflow.

<Warning>
  **Workflow engine v2 publishing was retired on July 10, 2026.** New v2 versions can no longer be published or promoted on any surface — the editor, the API, the SDK, and MCP; you must [upgrade a version to v3](#upgrading-a-version-to-v3) before publishing it. Existing published v2 versions stay live and continue running until you explicitly unpublish them, and v2 drafts remain editable. Contact HappyRobot if anything blocks the migration.
</Warning>

### Upgrading a version to v3

<Steps>
  <Step title="Fork the version you want to upgrade">
    In the version history panel, fork a published v2 version to create a new draft. The fork starts on v2 so existing behavior is preserved.
  </Step>

  <Step title="Upgrade the draft to v3">
    Open the draft in the editor. A banner will appear if the draft is still on v2. Click **Upgrade to v3** in the banner or the version options menu.

    During upgrade, any parallel or sequential action groups are automatically converted to explicit loop nodes. Review the converted nodes before publishing.

    The upgrade dialog also offers a **Preserve legacy child run behaviors** toggle (off by default). Leave it off to use native in-graph loops. Turn it on only if your workflow relies on the legacy behavior of spawning a separate [child run](../03-Core-Nodes/10-Loops.md#child-runs) per list item — this keeps the legacy trigger fan-out and marks migrated loops to run each item as a child run.
  </Step>

  <Step title="Test in staging">
    Publish the upgraded version to your staging environment first. Verify that runs behave correctly before promoting to production.
  </Step>

  <Step title="Publish to production when ready">
    Once testing is complete, publish the v3 version to production. Other versions in the same workflow remain on their existing engine — upgrading one version does not affect any other.
  </Step>
</Steps>

### Engine behavior by version

|                                     | v2                | v3                                     |
| ----------------------------------- | ----------------- | -------------------------------------- |
| Parallel / sequential action groups | Built-in          | Converted to loop nodes on upgrade     |
| Branch merges                       | Not supported     | Supported                              |
| Experiments                         | Not supported     | Supported                              |
| Fork inheritance                    | Fork starts on v2 | Fork inherits engine of source version |

### Downgrading a version

To downgrade a v3 version back to v2, unpublish it first, then click **Downgrade** in the version options. Only unpublished versions can be downgraded, and the downgrade only affects that version — other versions are not changed.

<Warning>
  Downgrading converts the version back to v2 but does not automatically reverse the loop-node conversion that happened during upgrade. Review your nodes after downgrading. Because [v2 publishing is retired](#workflow-engine-version-v2-and-v3), a downgraded v2 version cannot be published again — upgrade it back to v3 before publishing.
</Warning>

---

Fuente original: https://docs.happyrobot.ai/workflows/versions-and-publishing
