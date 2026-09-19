---
title: "Core Nodes Overview"
description: "Built-in workflow nodes that don't require a third-party integration"
---

# Core Nodes Overview

> Built-in workflow nodes that don't require a third-party integration

Core nodes are the built-in utility nodes available in every workflow. They handle common operations like AI processing, HTTP requests, scheduling, file handling, and branching logic — no external integration or credentials required.

## Available core nodes

<CardGroup cols={2}>
  <Card title="AI Extract" icon="wand-magic-sparkles" href="02-AI-Extract.md">
    Extract structured data from unstructured text using AI.
  </Card>

  <Card title="AI Classify" icon="tags" href="03-AI-Classify.md">
    Classify text into predefined categories using AI.
  </Card>

  <Card title="AI Generate" icon="sparkles" href="04-AI-Generate.md">
    Generate text content using AI.
  </Card>

  <Card title="Custom Code" icon="code" href="05-Custom-Code.md">
    Run Python code within your workflow.
  </Card>

  <Card title="Webhook" icon="globe" href="06-Webhook.md">
    Send and receive HTTP requests to external APIs.
  </Card>

  <Card title="Schedule" icon="clock" href="07-Schedule.md">
    Add delays and timing control to workflows.
  </Card>

  <Card title="File Operations" icon="file" href="08-File-Operations.md">
    Upload, parse, search, and extract text from files.
  </Card>

  <Card title="Conditionals" icon="code-branch" href="09-Conditionals.md">
    Add branching logic with paths and conditional outputs.
  </Card>

  <Card title="Loops" icon="arrows-rotate" href="10-Loops.md">
    Iterate over collections or repeat actions a fixed number of times.
  </Card>

  <Card title="Module Change" icon="arrow-right-arrow-left" href="11-Module-Change.md">
    Jump to a different module within a workflow.
  </Card>

  <Card title="Call Workflow" icon="share-nodes" href="12-Call-Workflow.md">
    Invoke another workflow and wait for its response.
  </Card>
</CardGroup>

## Adding a core node

<Steps>
  <Step title="Click the + button">
    In the workflow editor, click the **+** button between any two nodes or at the end of the flow.
  </Step>

  <Step title="Select the node type">
    Browse the node picker and select the core node you need. Core nodes are listed alongside integration nodes in the picker.
  </Step>

  <Step title="Configure the node">
    The configuration panel opens on the right. Fill in the required fields — most core nodes support [variables](../02-Workflows/07-Variables.md) using the `@` picker.
  </Step>
</Steps>

## Next steps

<CardGroup cols={2}>
  <Card title="Variables" icon="brackets-curly" href="../02-Workflows/07-Variables.md">
    Learn how to pass data between nodes using template variables.
  </Card>

  <Card title="Node Types" icon="shapes" href="../02-Workflows/04-Node-Types.md">
    Understand all node categories including action, prompt, tool, and condition nodes.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/overview
