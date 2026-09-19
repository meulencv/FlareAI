---
title: "Claude Desktop"
description: "Use Claude Desktop to build and manage HappyRobot workflows conversationally"
---

# Claude Desktop

> Use Claude Desktop to build and manage HappyRobot workflows conversationally

Claude Desktop can connect directly to HappyRobot, letting you build workflows, configure agents, and run tests through conversation — no code or terminal required.

## Install

<Steps>
  <Step title="Download the installer">
    Click the button below to download the HappyRobot Workflows installer for Claude Desktop.

    <Card title="Download HappyRobot Workflows (US)" icon="download" href="https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-workflows.mcpb">
      Downloads a `.mcpb` file that configures Claude Desktop automatically.
    </Card>

    <Accordion title="Other download options">
      HappyRobot offers multiple MCP servers scoped to different areas. We recommend installing only the ones you need — fewer tools means less noise for the LLM, faster tool selection, and lower token usage.

      **US cluster:**

      | Server            | Description                                            | Download                                                                                                    |
      | ----------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
      | **Workflows**     | Workflow management, integrations, testing, evaluation | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-workflows.mcpb) |
      | **Twin database** | Schema exploration, SQL queries, table management      | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-twin.mcpb)      |
      | **All tools**     | Everything combined                                    | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-all.mcpb)       |

      **EU cluster:**

      | Server            | Description                                            | Download                                                                                                    |
      | ----------------- | ------------------------------------------------------ | ----------------------------------------------------------------------------------------------------------- |
      | **Workflows**     | Workflow management, integrations, testing, evaluation | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-eu-workflows.mcpb) |
      | **Twin database** | Schema exploration, SQL queries, table management      | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-eu-twin.mcpb)      |
      | **All tools**     | Everything combined                                    | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-eu-all.mcpb)       |

      <Note>
        Use the cluster that matches your organization. If you're unsure, you're most likely on US.
      </Note>
    </Accordion>
  </Step>

  <Step title="Open the file">
    Open the downloaded `.mcpb` file. This will automatically launch Claude Desktop.
  </Step>

  <Step title="Click Install">
    Claude Desktop will show the HappyRobot MCP extension. Click **Install** to add it.
  </Step>

  <Step title="Authenticate">
    When you first use a HappyRobot tool, Claude Desktop will open your browser to authenticate. Log in with your HappyRobot account, select the workspace you want to connect to, and click **Authorize**.

    Access tokens refresh automatically — you only need to authenticate once.
  </Step>
</Steps>

<Accordion title="Troubleshooting: Extension shows 'Server disconnected'">
  If the extension disconnects after working initially, clear the cached authentication tokens and restart:

  1. Run `rm -rf ~/.mcp-auth/` in your terminal
  2. Quit Claude Desktop fully (Cmd+Q / Ctrl+Q)
  3. Reopen Claude Desktop — the extension will prompt you to re-authenticate
</Accordion>

## What you can do

Once connected, you can ask Claude to:

* **List and inspect workflows** — browse your organization's workflows and review their configuration
* **Create and edit workflows** — add nodes, update prompts, configure triggers, and wire up integrations
* **Test workflows** — trigger test runs and review the results, transcripts, and recordings
* **Manage versions** — publish, fork, and roll back workflow versions
* **Search integrations** — find available integrations and their events

## Next steps

<CardGroup cols={2}>
  <Card title="Platform overview" icon="map" href="02-Platform-overview.md">
    Learn how workflows, agents, and integrations fit together.
  </Card>

  <Card title="Full MCP tools reference" icon="wrench" href="../../02-Developer-Tools/01-MCP/01-MCP-servers.md">
    See every available tool, configuration option, and troubleshooting tip.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/claude-desktop
