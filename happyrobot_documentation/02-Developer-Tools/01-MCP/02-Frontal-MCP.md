---
title: "Frontal MCP"
description: "Build and edit workflows through conversation from your own MCP client"
---

# Frontal MCP

> Build and edit workflows through conversation from your own MCP client

The Frontal MCP server brings the same capabilities as the [Frontal AI assistant](../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md) in the app — building and editing workflows through conversation — to any MCP client. It's available at the `/frontal/mcp` path.

For installation, authentication, and service-to-service setup, see the [MCP servers overview](01-MCP-servers.md).

<Note>
  The Frontal MCP is the actively developed replacement for the [Workflows MCP](03-Workflows-MCP.md), which is now in maintenance mode. New capabilities land here first.
</Note>

## What you can do

Frontal reads your workflow structure and applies reviewable edits, the same way it does inside the editor:

* **Make workflow edits** — "Rewrite the prompt in the first AI Generate node to be more concise", "Add a Slack notification node after the final AI node", "Merge these two branches into one."
* **Ask questions about your workflow** — "What does the first branch do?", "Which nodes are connected to the webhook trigger?", "Why might the extraction node return empty results?"
* **Get recommendations** — "How should I handle the case where the extracted email is missing?", "Is there a more efficient way to structure this branching logic?"
* **Manage tests and quality** — "Create an adversarial test where the caller disputes the rate", "Group these tests into a suite and run it against version 12", "Which northstar audits failed on this workflow?" Frontal MCP carries the `manage_test_suites`, `manage_e2e_scenarios`, `manage_custom_evals`, `manage_northstars`, and `view_audit_remarks` tools, which replace the retired adversarial tools of the [Workflows MCP](03-Workflows-MCP.md).

Every edit is applied as a reviewable operation, so you can inspect, undo, or revert Frontal's changes.

## Plan mode and Build mode

Like the in-app assistant, Frontal supports two modes for applying changes:

| Mode      | Behavior                                                                                                                                                             |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Plan**  | Frontal proposes a plan before applying any changes. Review it, then approve or reject. Use this for significant changes where you want to see the full scope first. |
| **Build** | Frontal applies edits directly, one operation at a time. Use this for smaller, incremental changes.                                                                  |

## Related

<CardGroup cols={3}>
  <Card title="MCP servers overview" icon="server" href="01-MCP-servers.md">
    Installation, authentication, and service-to-service setup.
  </Card>

  <Card title="Frontal AI assistant" icon="wand-2" href="../../01-Developer-Guide/02-Workflows/03-Frontal-AI-assistant.md">
    The in-app assistant Frontal MCP is built on.
  </Card>

  <Card title="Workflows tools" icon="sitemap" href="03-Workflows-MCP.md">
    The maintenance-mode server Frontal MCP replaces.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/developer-tools/mcp-frontal
