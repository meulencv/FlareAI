---
title: "Tools Overview"
description: "Introduction to tools in HappyRobot"
---

# Tools Overview

> Introduction to tools in HappyRobot

Tools are functions attached to prompt nodes (voice and text agents) that the AI agent can invoke mid-conversation. When a tool is triggered, the agent pauses the conversation, executes the tool's logic, and uses the result to continue — enabling lookups, actions, and integrations without leaving the call or chat.

## Use cases

<CardGroup cols={3}>
  <Card title="Look up data" icon="magnifying-glass">
    Query a TMS, CRM, or database to retrieve real-time information during a conversation.
  </Card>

  <Card title="Trigger actions" icon="bolt">
    Send emails, create records, or call webhooks based on what the caller or user says.
  </Card>

  <Card title="Transfer calls" icon="phone-arrow-right">
    Navigate phone trees, press DTMF digits, or escalate to a human agent.
  </Card>
</CardGroup>

## How tools work

When an agent decides to use a tool, the following happens:

1. The agent identifies which tool to call and fills in the required parameters from the conversation context.
2. The platform executes the tool — running any child action nodes (webhooks, integrations, custom code) attached to it.
3. The exposed fields of each node's output are returned to the agent, which incorporates them into the ongoing conversation. You control which fields are exposed — see [Tool Call Result](03-Tool-Call-Result.md).

<Info>
  Tools can have child action nodes nested beneath them in the workflow editor. These child nodes run when the tool is invoked and their output is passed back to the agent. See [Creating Tools](02-Creating-Tools.md) for details.
</Info>

Use the [Tool Call Result](03-Tool-Call-Result.md) panel to preview that payload and pick which fields the agent is allowed to see.

## Tool types

<CardGroup cols={3}>
  <Card title="Custom tools" icon="wrench" href="02-Creating-Tools.md">
    Build your own tools with custom parameters, messages, and child action nodes.
  </Card>

  <Card title="Built-in tools" icon="cube" href="04-Built-in-Tools.md">
    Default tools that come with voice and text agents — hangup, voicemail, escalation, and more.
  </Card>

  <Card title="MCP tools" icon="plug" href="05-MCP-Tools.md">
    Import tools from external Model Context Protocol servers.
  </Card>
</CardGroup>

## Controlling what the agent receives

Each tool has a **Tool Call Result** panel that previews the payload the agent gets back after the tool's child nodes run, and lets you expose or hide individual fields. Hidden fields stay out of the agent's context but remain visible in run details and available as variables to downstream nodes.

A new tool — including one you copy, duplicate, or import — blocks publishing until you open its Tool Call Result once. See [Tool Call Result](03-Tool-Call-Result.md).

## Adding a tool

<Steps>
  <Step title="Open a prompt node">
    In the workflow editor, select the voice or text agent prompt node you want to add tools to.
  </Step>

  <Step title="Add a tool">
    Click the **+** button below the agent node and select **Tool**. A new tool node appears as a child of the prompt node.
  </Step>

  <Step title="Configure the tool">
    Give the tool a name, description, parameters, and message behavior. Optionally add child action nodes that execute when the tool is called.
  </Step>
</Steps>

## Related

<CardGroup cols={3}>
  <Card title="Tool Call Result" icon="eye" href="03-Tool-Call-Result.md">
    Preview and choose the payload your tools return to the agent.
  </Card>

  <Card title="Node Types" icon="diagram-project" href="../02-Workflows/04-Node-Types.md">
    Learn about all node types available in workflows.
  </Card>

  <Card title="Voice Agents" icon="microphone" href="../05-Voice-Agents/01-Voice-Agents-Overview.md">
    Build AI-powered voice agents for inbound and outbound calls.
  </Card>

  <Card title="Tool Call Result" icon="eye" href="03-Tool-Call-Result.md">
    Review what a tool returns to the agent and control field visibility.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/tools/overview
