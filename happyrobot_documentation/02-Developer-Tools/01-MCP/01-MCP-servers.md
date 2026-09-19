---
title: "MCP servers"
description: "Connect to HappyRobot from AI coding assistants, Claude Desktop, or your own services"
---

# MCP servers

> Connect to HappyRobot from AI coding assistants, Claude Desktop, or your own services

The HappyRobot MCP servers let you manage workflows, query databases, and automate platform operations from any MCP-compatible client. They use **Streamable HTTP transport** with **OAuth 2.1 authentication** — no API keys or Node.js required on your machine.

<Note>
  This section covers the HappyRobot MCP servers for **developer tools** and **service-to-service** integrations. If you want to use external MCP servers as **tools inside your workflows**, see [MCP Tools](../../01-Developer-Guide/04-Tools/05-MCP-Tools.md) and [MCP Server Setup](../../01-Developer-Guide/04-Tools/06-MCP-Server-Setup.md).
</Note>

## Available servers

HappyRobot provides multiple MCP servers, each scoped to a different area. You can connect to them individually or use a combined endpoint:

| Server        | URL path         | Description                                                     |
| ------------- | ---------------- | --------------------------------------------------------------- |
| **All tools** | `/mcp`           | All workflow + Twin database tools combined                     |
| **Frontal**   | `/frontal/mcp`   | Build and edit workflows through conversation                   |
| **Workflows** | `/workflows/mcp` | Workflow management, integrations, testing, and evaluation      |
| **Twin**      | `/twin/mcp`      | Twin database schema exploration, queries, and table management |

<Tip>
  We recommend connecting only the servers you need. Scoping to a specific server reduces noise for the LLM, helps it pick the right tool faster, and consumes fewer tokens per request.
</Tip>

For the full list of tools available on each server, see:

<CardGroup cols={2}>
  <Card title="Workflows" icon="sitemap" href="03-Workflows-MCP.md">
    Workflow management, integrations, versions, testing, and evaluation tools.
  </Card>

  <Card title="Twin database" icon="database" href="04-Twin-MCP.md">
    Schema exploration, SQL queries, and table management tools.
  </Card>
</CardGroup>

## Clusters

The MCP servers are available in both US and EU regions. Append the server path to the base URL for your cluster:

| Cluster          | Base URL                                |
| ---------------- | --------------------------------------- |
| **US** (default) | `https://mcp.platform.happyrobot.ai`    |
| **EU**           | `https://mcp.platform.eu.happyrobot.ai` |

Use the base URL that matches your organization's cluster. If you're unsure, you're most likely on US.

## Installation

<Tabs>
  <Tab title="Claude Code">
    Run the following command in your terminal:

    ```bash theme={null}
    # Frontal — build and edit workflows through conversation
    claude mcp add --transport http happyrobot-frontal https://mcp.platform.happyrobot.ai/frontal/mcp

    # Workflows only (recommended)
    claude mcp add --transport http happyrobot-workflows https://mcp.platform.happyrobot.ai/workflows/mcp

    # Twin database only
    claude mcp add --transport http happyrobot-twin https://mcp.platform.happyrobot.ai/twin/mcp

    # All tools combined
    claude mcp add --transport http happyrobot https://mcp.platform.happyrobot.ai/mcp
    ```

    For the **EU cluster**, replace `mcp.platform.happyrobot.ai` with `mcp.platform.eu.happyrobot.ai`.

    <Warning>
      After adding the server, run `/mcp` in Claude Code, select the server, and click **Authenticate** to complete the OAuth setup. Tools are not available until authentication is complete.
    </Warning>
  </Tab>

  <Tab title="Codex CLI">
    Run the following command in your terminal:

    ```bash theme={null}
    # Frontal — build and edit workflows through conversation
    codex mcp add happyrobot-frontal --url https://mcp.platform.happyrobot.ai/frontal/mcp

    # Workflows only (recommended)
    codex mcp add happyrobot-workflows --url https://mcp.platform.happyrobot.ai/workflows/mcp

    # Twin database only
    codex mcp add happyrobot-twin --url https://mcp.platform.happyrobot.ai/twin/mcp

    # All tools combined
    codex mcp add happyrobot --url https://mcp.platform.happyrobot.ai/mcp
    ```

    For the **EU cluster**, replace `mcp.platform.happyrobot.ai` with `mcp.platform.eu.happyrobot.ai`.

    <Warning>
      After adding the server, run `codex mcp login happyrobot-workflows` to complete the OAuth setup. If you add a different server name, pass that name to `codex mcp login` instead. Tools are not available until authentication is complete.
    </Warning>
  </Tab>

  <Tab title="Codex app">
    Open [Codex](https://chatgpt.com/codex), then open **Settings → Integrations & MCP**.

    Add the server you want to use:

    | Server                      | Name                   | URL                                                |
    | --------------------------- | ---------------------- | -------------------------------------------------- |
    | **Frontal**                 | `happyrobot-frontal`   | `https://mcp.platform.happyrobot.ai/frontal/mcp`   |
    | **Workflows** (recommended) | `happyrobot-workflows` | `https://mcp.platform.happyrobot.ai/workflows/mcp` |
    | **Twin database**           | `happyrobot-twin`      | `https://mcp.platform.happyrobot.ai/twin/mcp`      |
    | **All tools**               | `happyrobot`           | `https://mcp.platform.happyrobot.ai/mcp`           |

    For the **EU cluster**, replace `mcp.platform.happyrobot.ai` with `mcp.platform.eu.happyrobot.ai`.

    <Warning>
      If prompted, complete the OAuth flow before using the tools. Codex shares MCP settings across the Codex app, CLI, and IDE extension, so servers added here are available in those clients too.
    </Warning>
  </Tab>

  <Tab title="Claude Desktop">
    Download the installer for your cluster and server:

    <Card title="Download HappyRobot Workflows (US)" icon="download" href="https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-workflows.mcpb">
      Downloads a `.mcpb` file that configures Claude Desktop automatically.
    </Card>

    <Accordion title="Other download options">
      **US cluster:**

      | Server            | Download                                                                                                    |
      | ----------------- | ----------------------------------------------------------------------------------------------------------- |
      | **Workflows**     | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-workflows.mcpb) |
      | **Twin database** | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-twin.mcpb)      |
      | **All tools**     | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-us-all.mcpb)       |

      **EU cluster:**

      | Server            | Download                                                                                                    |
      | ----------------- | ----------------------------------------------------------------------------------------------------------- |
      | **Workflows**     | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-eu-workflows.mcpb) |
      | **Twin database** | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-eu-twin.mcpb)      |
      | **All tools**     | [Download](https://pub-2609fcff26dd40a79f7954d7be8c58a2.r2.dev/assets/mcp/happyrobot-mcp-eu-all.mcpb)       |
    </Accordion>

    Open the downloaded `.mcpb` file — Claude Desktop will launch and prompt you to install.

    When you first use a HappyRobot tool, Claude Desktop will open your browser to authenticate.
  </Tab>

  <Tab title="Cursor">
    Add the following to `~/.cursor/mcp.json` (global) or `.cursor/mcp.json` (project-level):

    ```json theme={null}
    {
      "mcpServers": {
        "happyrobot-workflows": {
          "url": "https://mcp.platform.happyrobot.ai/workflows/mcp"
        }
      }
    }
    ```

    For the **EU cluster**, replace `mcp.platform.happyrobot.ai` with `mcp.platform.eu.happyrobot.ai`.

    <Warning>
      Open Cursor's MCP settings and log in to the HappyRobot server to complete the OAuth setup. Tools are not available until authentication is complete. Cursor authorizes through its own `cursor://` callback, which HappyRobot trusts by default — no workspace approval is needed.
    </Warning>
  </Tab>

  <Tab title="VS Code (Copilot)">
    Add the following to `.vscode/mcp.json` in your project:

    ```json theme={null}
    {
      "servers": {
        "happyrobot-workflows": {
          "url": "https://mcp.platform.happyrobot.ai/workflows/mcp"
        }
      }
    }
    ```
  </Tab>
</Tabs>

## Authentication

### User authentication (OAuth 2.1)

When connecting from a coding assistant or Claude Desktop, the MCP server uses **OAuth 2.1** for authentication. No API keys are needed.

On first connection, you'll be redirected to the HappyRobot platform to:

1. **Log in** with your existing account
2. **Select one or more workspaces** you want the MCP client to access — check each workspace in the list, or use **Select all**. Workspaces are grouped by parent organization, with independent workspaces listed separately.
3. **Authorize** the connection

Access tokens are valid for 24 hours and refresh automatically. You only need to authenticate once — your session stays active until you explicitly revoke it.

#### Authorizing multiple workspaces

A single connection can be authorized for more than one workspace. When you select multiple workspaces, every tool call must name which workspace it runs in by passing a required **`org`** parameter set to the workspace slug — there is no implicit "active" workspace. Single-workspace connections don't take this parameter.

Call the **`get_connection_info`** tool at any time to list the workspaces the connection is authorized for and their slugs.

### Service-to-service authentication

For programmatic access — connecting from your own backend, a CI/CD pipeline, or integrating the MCP into another platform — use the **client credentials** grant. This exchanges an existing org API key for a short-lived JWT, with no browser or user interaction required.

<Steps>
  <Step title="Generate an API key">
    Go to [Settings → API Keys](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md) and create an org-level API key for the workspace you want the MCP to access.
  </Step>

  <Step title="Request an access token">
    Call the token endpoint with your API key:

    ```bash theme={null}
    curl -X POST https://platform.happyrobot.ai/api/mcp/token \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "grant_type=client_credentials&client_secret=sk_live_your_api_key"
    ```

    You can also pass the API key with HTTP **Basic auth** instead of in the body — useful for platforms (such as Workato) that expect `client_secret_basic`. Send the credentials as `client_id:client_secret`, base64-encoded, in the `Authorization` header. The `client_id` can be any placeholder; only the secret is validated.

    ```bash theme={null}
    curl -X POST https://platform.happyrobot.ai/api/mcp/token \
      -H "Authorization: Basic $(echo -n 'client:sk_live_your_api_key' | base64)" \
      -H "Content-Type: application/x-www-form-urlencoded" \
      -d "grant_type=client_credentials"
    ```

    Response:

    ```json theme={null}
    {
      "access_token": "eyJ...",
      "token_type": "Bearer",
      "expires_in": 86400,
      "scope": "mcp:full"
    }
    ```
  </Step>

  <Step title="Call the MCP server">
    Use the access token as a Bearer token in your MCP requests:

    ```bash theme={null}
    curl -X POST https://mcp.platform.happyrobot.ai/workflows/mcp \
      -H "Authorization: Bearer eyJ..." \
      -H "Content-Type: application/json" \
      -d '{ ... }'
    ```

    When the token expires (after 24 hours), request a new one using the same API key. No refresh token is needed.
  </Step>
</Steps>

### External MCP hosts (Workato and other OAuth platforms)

Some platforms — such as [Workato](https://www.workato.com) — connect to the HappyRobot MCP server through their own OAuth 2.0 connector, proxying it behind their product. These clients use the standard **authorization code** grant (with PKCE) and a fixed, non-localhost redirect (callback) URI, and they refresh access tokens automatically.

Because the redirect URI is external (not `localhost`), a workspace **owner must approve it first**. This is a one-time setup; after it's connected, no further interaction is needed.

<Steps>
  <Step title="Approve the host's redirect URI">
    In the workspace you want the host to access, go to **Settings → MCP Clients** and add the host's OAuth callback URL. For Workato this is:

    ```
    https://www.workato.com/oauth/callback
    ```

    Only `https://` URIs are accepted, and they are matched exactly.
  </Step>

  <Step title="Configure the connector">
    Point the host's OAuth 2.0 connector at the HappyRobot endpoints:

    | Field                           | Value                                             |
    | ------------------------------- | ------------------------------------------------- |
    | Authorization URL               | `https://platform.happyrobot.ai/mcp/authorize`    |
    | Token URL                       | `https://platform.happyrobot.ai/api/mcp/token`    |
    | Registration URL (if requested) | `https://platform.happyrobot.ai/api/mcp/register` |
    | Redirect / callback URL         | `https://www.workato.com/oauth/callback`          |
    | PKCE                            | `S256`                                            |

    For the **EU cluster**, replace `platform.happyrobot.ai` with `platform.eu.happyrobot.ai`.
  </Step>

  <Step title="Connect">
    Start the connection from the host. You'll be sent to HappyRobot once to log in, **select one or more workspaces**, and approve — then the host stores a refresh token and renews access tokens on its own. If you select more than one workspace, the client must pass the `org` parameter on each tool call (see [Authorizing multiple workspaces](#authorizing-multiple-workspaces)).
  </Step>
</Steps>

<Note>
  Local MCP clients don't need this step. Loopback (`localhost`) callbacks, Cursor's native `cursor://` callback, and Claude's hosted callback are trusted by default — only other external redirect URIs require workspace approval under **Settings → MCP Clients**.
</Note>

## Troubleshooting

### "needs authentication" in Claude Code or Codex

After adding the MCP server, tools are not visible until you authenticate. In Claude Code, run `/mcp`, select the HappyRobot server, and click **Authenticate**. In the Codex app, open **Settings → Integrations & MCP** and complete the OAuth prompt. In Codex CLI, run `codex mcp login happyrobot-workflows` or replace `happyrobot-workflows` with the server name you added. This opens your browser for the OAuth flow.

### Cursor stays logged out after authorizing

Cursor's OAuth callback uses the `cursor://` scheme, which the browser hands back to the desktop app. If the HappyRobot authorization page finishes but Cursor still shows the server as needing login, allow your browser to open Cursor when it prompts, then retry the login from Cursor's MCP settings. You don't need to add `cursor://anysphere.cursor-mcp` under **Settings → MCP Clients** — it's trusted by default.

### Authentication fails

If the OAuth flow fails or the browser doesn't open:

1. Make sure you're logged in to the [HappyRobot platform](https://platform.happyrobot.ai)
2. Check that your account has access to at least one workspace
3. Try removing and re-adding the MCP server

### Claude Desktop extension disconnects

If the `.mcpb` extension shows "Server disconnected" after working initially, this is a known issue with the `mcp-remote` bridge used by extensions. To fix it:

1. Delete the cached tokens: `rm -rf ~/.mcp-auth/`
2. Quit Claude Desktop fully (Cmd+Q / Ctrl+Q)
3. Reopen Claude Desktop — the extension will prompt you to re-authenticate

To avoid this issue entirely, switch to the **Connector** method (see Installation → Claude Desktop (Connector) above), which connects directly without `mcp-remote`.

### Service-to-service token returns 401

* Verify the API key is valid and not revoked at [Settings → API Keys](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md)
* Ensure `grant_type` is exactly `client_credentials`
* Check you're using the correct cluster token endpoint

### "This redirect URI is not approved for this organization"

An external host's callback URL must be allow-listed before you can authorize it. A workspace owner needs to add it (exact `https://` match) under **Settings → MCP Clients**. The same cause explains a missing workspace in the picker during the authorization step — only workspaces that have approved the redirect URI are shown.

## Related

<CardGroup cols={3}>
  <Card title="Workflows tools" icon="sitemap" href="03-Workflows-MCP.md">
    Full list of workflow management tools and prompts.
  </Card>

  <Card title="Twin tools" icon="database" href="04-Twin-MCP.md">
    Full list of Twin database tools and limits.
  </Card>

  <Card title="Claude Desktop" icon="desktop" href="../../01-Developer-Guide/01-Get-Started/05-Claude-Desktop.md">
    One-click installer for Claude Desktop.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/developer-tools/mcp
