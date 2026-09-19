# Workflows

Ruta en la web: API Reference › Platform V2 API › Workflows

14 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [List workflows](01-List-workflows.md) | Returns paginated workflows for the authenticated organization. Each workflow includes its latest version info (live production version preferred, otherwise most recent). Supports searching by name and filtering by folder. |
| 2 | [Create a workflow](02-Create-a-workflow.md) | Creates a new workflow in the authenticated organization. Supports three creation modes: |
| 3 | [Get a workflow](03-Get-a-workflow.md) | Returns a single workflow by UUID or slug, including its latest version info (live production version preferred, otherwise most recent). |
| 4 | [Delete a workflow](04-Delete-a-workflow.md) | Soft-deletes a workflow by UUID or slug. The workflow must not have any live versions — unpublish all versions before deleting. |
| 5 | [Update a workflow](05-Update-a-workflow.md) | Updates workflow metadata and settings. Accepts a workflow UUID or slug as the path parameter. Set `folder_id` to `null` to move the workflow to the root level. Use `settings` to update configuration such as webhooks, out-of-office hours, approval process, data retention, and audits. This endpoint d… |
| 6 | [List workflow versions](06-List-workflow-versions.md) | Returns paginated versions for a workflow. Supports searching by version number or version name. |
| 7 | [List workflow templates](07-List-workflow-templates.md) | Returns a paginated list of available workflow templates. Each template includes a description and the inputs it accepts (marked as required or optional). Use a template's name in the `from_template.template` field when creating a workflow. |
| 8 | [Duplicate a workflow](08-Duplicate-a-workflow.md) | Creates a copy of a workflow including all its nodes and configurations. The duplicated workflow is created as a new unpublished workflow with version number 1. If the source uses workflow engine v2, the duplicate remains an editable v2 draft and cannot be published through the public API until upgr… |
| 9 | [Publish a workflow](09-Publish-a-workflow.md) | Publishes the latest version of the specified workflow to make it live. Before publishing, all action nodes are checked for test errors and untested status. If untested nodes exist (with no errors), a synchronous test-all is triggered first. If any node has test errors, the publish is blocked and er… |
| 10 | [Unpublish a workflow](10-Unpublish-a-workflow.md) | Finds the currently live version for the workflow and unpublishes it. The version is taken offline and unlocked for editing. Returns 400 if no version is currently live. Accepts a workflow UUID or slug as the path parameter. |
| 11 | [List workflow runs](11-List-workflow-runs.md) | Returns paginated runs for a workflow. Supports filtering by status, date ranges, and annotation. |
| 12 | [Trigger a workflow run](12-Trigger-a-workflow-run.md) | Starts a new run for a workflow by proxying to the hooks service. Accepts either a JSON body with payload/environment fields, or a multipart/form-data request with a file and optional form fields (pass environment as a query param for multipart). Supports targeting different environments (production… |
| 13 | [List workflow sessions](13-List-workflow-sessions.md) | Returns paginated sessions for a workflow across all runs, ordered by timestamp. |
| 14 | [Cancel active workflow runs](14-Cancel-active-workflow-runs.md) | Cancels all current and queued runs for the workflow. By default, the currently live workflow version is also unpublished. Set unpublish_workflow to false to keep the workflow published after cancellation. Accepts a workflow UUID or slug as the path parameter. |

---

[← Volver](../README.md)
