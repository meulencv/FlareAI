---
title: "Workflows Overview"
description: "Introduction to HappyRobot workflows"
---

# Workflows Overview

> Introduction to HappyRobot workflows

Workflows are the automation engine behind HappyRobot. Each workflow is a visual, directed graph of nodes — triggers, AI agents, integration actions, conditions, and more — that execute in sequence when an event fires. You build them in a drag-and-drop editor with no code required.

## What you can build

<CardGroup cols={2}>
  <Card title="Inbound call handling" icon="phone-arrow-down-left">
    Phone call arrives, AI agent answers, extracts shipment details, updates your TMS, and sends a summary email — all automatically.
  </Card>

  <Card title="Outbound campaigns" icon="phone-arrow-up-right">
    API trigger initiates an outbound call. If the customer doesn't answer, the workflow retries with configurable delays and logs the result.
  </Card>

  <Card title="Email automation" icon="envelope">
    Incoming email triggers AI extraction of key data, updates a spreadsheet, and sends a formatted reply — no human intervention.
  </Card>

  <Card title="Multi-channel support" icon="messages">
    WhatsApp message arrives, AI classifies intent, and routes the conversation to a voice agent or text agent based on the result.
  </Card>
</CardGroup>

## How workflows work

<Steps>
  <Step title="Trigger fires">
    Every workflow starts with a trigger — a webhook call, incoming phone call, email, SMS, or a recurring schedule. The trigger captures input data and kicks off the run.
  </Step>

  <Step title="Nodes execute in sequence">
    The workflow engine walks through the graph, executing each node in order. Action nodes call integrations, prompt nodes run AI conversations, and condition nodes branch the path based on data.
  </Step>

  <Step title="Data flows between nodes">
    Each node can reference outputs from previous nodes using template variables. Data passes forward automatically, so a phone number extracted in one step can be used in the next.
  </Step>

  <Step title="Run completes with full audit trail">
    When the workflow finishes, HappyRobot records everything — node outputs, transcripts, recordings, duration, and status. You can review any run in detail from the Runs tab.
  </Step>
</Steps>

## Workflow editor

The workflow editor is where you design automation visually. Add nodes by clicking the **+** button, drag to reorder, and configure each node in the side panel. The canvas shows the full execution flow at a glance, making it easy to understand and modify complex logic.

## Key features

<CardGroup cols={2}>
  <Card title="Branching and conditions" icon="code-branch">
    Route execution down different paths based on data values, AI classifications, or custom logic.
  </Card>

  <Card title="Variables and dynamic data" icon="brackets-curly">
    Pass data between nodes with template variables. Reference trigger inputs, node outputs, and environment variables anywhere.
  </Card>

  <Card title="Versioning and rollback" icon="clock-rotate-left">
    Every publish creates a version snapshot. Roll back to any previous version instantly if something goes wrong.
  </Card>

  <Card title="Multi-environment deployment" icon="server">
    Deploy independently to development, staging, and production. Test changes with real data before going live.
  </Card>

  <Card title="40+ integration actions" icon="plug">
    Connect to Gmail, Slack, Snowflake, TMS systems, Google Sheets, and more — all available as workflow nodes.
  </Card>

  <Card title="Full run history" icon="list-check">
    Every execution is recorded with node-level outputs, transcripts, recordings, and timing data.
  </Card>
</CardGroup>

## Next steps

<CardGroup cols={3}>
  <Card title="Create a workflow" icon="plus" href="02-Creating-a-Workflow.md">
    Step-by-step guide to building your first workflow.
  </Card>

  <Card title="Node types" icon="shapes" href="04-Node-Types.md">
    Learn about action, prompt, tool, condition, loop, and module change nodes.
  </Card>

  <Card title="Triggers" icon="bolt" href="05-Triggers.md">
    Explore all the ways to start a workflow.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/workflows/overview
