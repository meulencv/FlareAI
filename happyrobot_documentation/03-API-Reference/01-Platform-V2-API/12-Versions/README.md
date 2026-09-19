# Versions

Ruta en la web: API Reference › Platform V2 API › Versions

22 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [Get a version with nodes summary](01-Get-a-version-with-nodes-summary.md) | Returns a single version by UUID or slug with metadata, node count, node counts by type, and the list of events (action node types) used. |
| 2 | [Update a version](02-Update-a-version.md) | Updates version metadata (name and/or description). Accepts a version UUID or slug as the path parameter. |
| 3 | [Fork a version](03-Fork-a-version.md) | Creates a new version by copying all nodes from the specified version. The new version gets the next available version number and is unlocked/unpublished. If the source uses workflow engine v2, the fork remains an editable v2 draft and cannot be published through the public API until upgraded to v3.… |
| 4 | [Publish a version](04-Publish-a-version.md) | Publishes the specified version to make it live. Before publishing, node configuration completeness is validated. If untested nodes exist, a synchronous test-all is triggered automatically. Test errors do not block publishing (matching UI behavior) but are returned as informational warnings in the `… |
| 5 | [Lock a version](05-Lock-a-version.md) | Locks the specified version, preventing further edits to its nodes. Accepts a version UUID or slug as the path parameter. |
| 6 | [Unlock a version](06-Unlock-a-version.md) | Unlocks the specified version, allowing edits to its nodes. A version that is currently live cannot be unlocked — use unpublish instead. Accepts a version UUID or slug as the path parameter. |
| 7 | [Unpublish a version](07-Unpublish-a-version.md) | Unpublishes the version (takes it offline) and unlocks it for editing. The version will no longer be live and its published lock is removed, allowing further modifications. The version must currently be live. Accepts a version UUID or slug as the path parameter. |
| 8 | [List version nodes](08-List-version-nodes.md) | Returns all workflow nodes belonging to the specified version. The version can be identified by its UUID or slug. |
| 9 | [Add nodes to a version](09-Add-nodes-to-a-version.md) | Adds one or more nodes to the specified version. Nodes are processed sequentially in array order, so later nodes can reference earlier ones via `parent_node_index` (0-based index into this array) or existing DB nodes via `parent_node_id`. Each node must include a `type` discriminator: `"trigger"`, `… |
| 10 | [Get a single node](10-Get-a-single-node.md) | Returns the full details of a single node including its configuration. For webhook trigger nodes (INCOMING_HOOK or PREDEFINED_REQUEST), the response also includes production, staging, development, and test webhook URLs. |
| 11 | [Update a node](11-Update-a-node.md) | Updates the specified node. The request body must include a `type` discriminator matching the node type. Updatable fields depend on the type: - **trigger**: `name`, `configuration`, `webhook_payload` - **action**: `name`, `configuration`, `webhook_payload` - **agent**: `name`, `configuration`, `prom… |
| 12 | [Delete a node](12-Delete-a-node.md) | Deletes the specified node. For tool, condition, and paths-root nodes, owned child nodes are also cascade-deleted. For action, prompt, and module-change nodes, children are reparented to the deleted node's parent so the workflow chain is preserved. Agent nodes delete their internal children (prompt… |
| 13 | [List available variables for a node](13-List-available-variables-for-a-node.md) | Returns all variable groups available to the specified node, including system variables, environment variables, and upstream node outputs. |
| 14 | [Get config schema for a node](14-Get-config-schema-for-a-node.md) | Returns the configuration schema for the node's event, including field types, required fields, current values, defaults, and validation status. Only works for action nodes (nodes with an event_id). |
| 15 | [Set custom node output](15-Set-custom-node-output.md) | Sets a custom JSON object as the node's output for testing purposes. This upserts the node's generated output schema, marking the node as complete. Useful for defining output schemas on trigger nodes, webhooks, or any node where you want to manually specify the output shape without running the actua… |
| 16 | [Test a single node](16-Test-a-single-node.md) | Triggers a test run for a single node in the specified version. The node must have a complete configuration and the version must not be published. Returns the generated node output (schema) on success. |
| 17 | [Test all nodes in a version](17-Test-all-nodes-in-a-version.md) | Triggers a synchronous test-all run for every testable node in the specified version. Nodes are executed in dependency waves — independent nodes run in parallel. If a node fails, dependent nodes are skipped. The endpoint blocks until all nodes have been tested and returns per-node results. |
| 18 | [Inspect a tool's Tool Call Result](18-Inspect-a-tools-Tool-Call-Result.md) | Returns the current Tool Call Result and acks the tool. |
| 19 | [Sync a tool's Tool Call Result](19-Sync-a-tools-Tool-Call-Result.md) | Generates only untested or out-of-date testable nodes. |
| 20 | [Generate a tool's Tool Call Result](20-Generate-a-tools-Tool-Call-Result.md) | Generates every testable node. |
| 21 | [Set Tool Call Result visibility](21-Set-Tool-Call-Result-visibility.md) | Replaces the complete list of generated leaf fields one branch node exposes to the agent. |
| 22 | [List prompt issues](22-List-prompt-issues.md) | Returns prompt quality issues for all prompt nodes in the specified version. Issues are generated asynchronously by the platform's prompt analysis system. Each prompt node includes its current prompt text, issue generation status, and any open (non-rejected) issues with recommendations. |

---

[← Volver](../README.md)
