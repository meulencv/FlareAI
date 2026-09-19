---
title: "CXone"
description: "Integrate with NICE CXone contact center platform"
---

# CXone

> Integrate with NICE CXone contact center platform

The CXone integration connects your workflows to NICE CXone, a cloud contact center platform. Send call transcripts and interaction data from HappyRobot voice agents directly into CXone for unified reporting and quality management.

## Authentication

CXone uses a dialog-based configuration flow.

<Steps>
  <Step title="Enable the CXone integration">
    Go to **Settings > Integrations** and enable **CXone**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and follow the configuration dialog to set up your CXone connection details.
  </Step>

  <Step title="Verify the connection">
    The credential will appear as **Active** once configured.
  </Step>
</Steps>

## Available events

### Actions

| Event               | Description                                                           |
| ------------------- | --------------------------------------------------------------------- |
| **Send Transcript** | Sends a call transcript to CXone for recording and quality management |

## When to use CXone

Use the CXone integration when:

* Your contact center uses NICE CXone for quality management and reporting
* You want HappyRobot AI call transcripts to appear alongside human agent interactions in CXone
* You need unified analytics across AI and human-handled calls

## Example use case

An AI voice agent handles an inbound carrier call. After the call completes, the workflow uses **Send Transcript** to push the full conversation transcript to CXone, where supervisors can review it alongside human agent calls in a single quality management dashboard.

## Related

<CardGroup cols={2}>
  <Card title="Voice agents" icon="phone" href="../../05-Voice-Agents/01-Voice-Agents-Overview.md">
    Learn about AI voice agents.
  </Card>

  <Card title="Runs and monitoring" icon="list-check" href="../../09-Runs-and-Monitoring/01-Runs-Overview.md">
    Monitor workflow runs and transcripts.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/cxone
