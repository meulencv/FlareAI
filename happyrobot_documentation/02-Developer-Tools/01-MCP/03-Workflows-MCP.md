---
title: "Workflows MCP"
description: "Available tools and prompts for the Workflows MCP server"
---

# Workflows MCP

> Available tools and prompts for the Workflows MCP server

<Note>
  **The Workflows MCP server is entering maintenance mode.** We're focusing new development on the **[Frontal MCP](02-Frontal-MCP.md)**, which brings the same capabilities as the Frontal AI assistant in the app — building and editing workflows through conversation — to your own tools.

  The Workflows MCP server remains available and supported, but new features will land in the Frontal MCP going forward. We recommend adopting it for new projects.
</Note>

The Workflows MCP server provides tools for managing workflows, integrations, testing, and evaluation. It's available at the `/workflows/mcp` path.

For installation, authentication, and service-to-service setup, see the [MCP servers overview](01-MCP-servers.md).

## Available tools

<AccordionGroup>
  <Accordion title="Core workflow management">
    | Tool                    | Description                                              |
    | ----------------------- | -------------------------------------------------------- |
    | `list_workflows`        | List all workflows in the organization                   |
    | `get_workflow_details`  | Get full details of a specific workflow                  |
    | `create_workflow`       | Create a new workflow from scratch                       |
    | `manage_workflow`       | Update, delete, duplicate, or cancel runs for a workflow |
    | `manage_versions`       | Fork, publish, unpublish, lock, and unlock versions      |
    | `update_workflow_nodes` | Add, update, or delete nodes in a version                |
    | `browse_workflows`      | Browse workflow folders                                  |
  </Accordion>

  <Accordion title="Integrations and configuration">
    | Tool                     | Description                                                  |
    | ------------------------ | ------------------------------------------------------------ |
    | `list_integrations`      | Search integrations, events, and fetch integration resources |
    | `manage_credentials`     | List and create credentials for integrations                 |
    | `manage_mcp_servers`     | List, create, and refresh MCP server connections             |
    | `manage_knowledge_bases` | Create, list, and delete knowledge bases; upload files       |
    | `manage_phone_numbers`   | List, purchase, update, and delete phone numbers             |
    | `manage_sip_trunks`      | List, create, update, and delete SIP trunks                  |
    | `manage_variables`       | CRUD workflow-scoped environment variables                   |
  </Accordion>

  <Accordion title="Node configuration">
    | Tool                      | Description                                     |
    | ------------------------- | ----------------------------------------------- |
    | `get_node_details`        | Get the full configuration of a specific node   |
    | `get_node_config_schema`  | Get the configuration schema for a node's event |
    | `get_available_variables` | Get upstream variables available to a node      |
  </Accordion>

  <Accordion title="Testing and quality">
    | Tool                  | Description                                                                                          |
    | --------------------- | ---------------------------------------------------------------------------------------------------- |
    | `trigger_run`         | Trigger a workflow run with optional payload                                                         |
    | `test_workflow`       | Test workflow versions (run all node tests or test single nodes)                                     |
    | `monitor_runs`        | List runs, view sessions, recordings, and manage annotations                                         |
    | `fix_broken_vars`     | Diagnose and fix broken variable references                                                          |
    | `fix_prompt_issues`   | Fetch prompt quality issues and get recommendations                                                  |
    | `manage_northstars`   | Manage northstar success criteria for evaluating prompt nodes                                        |
    | `manage_audits`       | Read behavioral audit remarks — per-run, per-northstar pass/fail grades with corrections (read-only) |
    | `manage_custom_evals` | Manage custom eval tests (expected responses, tool calls)                                            |
  </Accordion>
</AccordionGroup>

<Note>
  Buying a number with `manage_phone_numbers` requires `provider`, `name`, and `phone_number_type` (`local`, `toll_free`, `national`, or `mobile`). There is no default for `phone_number_type` — the assistant asks you which type you want before purchasing, since availability depends on the country and provider.

  <Note>
    The `manage_adversarial_tests` and `manage_adversarial_suites` tools have been retired from this server. Manage [adversarial tests](../../01-Developer-Guide/11-Quality-and-Evaluation/07-Adversarial-tests.md) and [test suites](../../01-Developer-Guide/11-Quality-and-Evaluation/08-Test-suites.md) through the [Frontal MCP](02-Frontal-MCP.md) (`manage_e2e_scenarios` and `manage_test_suites`) or the [Platform API](../02-TypeScript-SDK/11-Quality-and-testing.md#test-suites).
  </Note>
</Note>

## Prompts

The Workflows server includes built-in prompts that load HappyRobot platform knowledge into your assistant's context:

| Prompt                | Coverage                                                                     |
| --------------------- | ---------------------------------------------------------------------------- |
| **Variable guide**    | Variable reference syntax, output patterns by node type, common mistakes     |
| **Node types**        | What each node type does, config fields, outputs, pitfalls                   |
| **Workflow patterns** | Tool sequencing, when to use which tools, version management                 |
| **Eval guide**        | How northstars, custom evals, and adversarial tests layer together           |
| **Platform setup**    | Integration/credential discovery, phone numbers, SIP trunks, MCP connections |

<Tip>
  These prompts are especially useful when starting a new project. Load the platform overview prompt first to give your assistant full context on how HappyRobot works before building workflows.
</Tip>

## Related

<CardGroup cols={3}>
  <Card title="MCP servers overview" icon="server" href="01-MCP-servers.md">
    Installation, authentication, and service-to-service setup.
  </Card>

  <Card title="Twin tools" icon="database" href="04-Twin-MCP.md">
    Twin database schema exploration and query tools.
  </Card>

  <Card title="Claude Desktop" icon="desktop" href="../../01-Developer-Guide/01-Get-Started/05-Claude-Desktop.md">
    One-click installer for Claude Desktop.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/developer-tools/mcp-workflows
