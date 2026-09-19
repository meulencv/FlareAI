---
title: "Broker App"
description: "Use the HappyRobot Broker App integration"
---

# Broker App

> Use the HappyRobot Broker App integration

The Broker App integration connects your workflows to HappyRobot's own freight brokerage platform. It provides the most comprehensive set of freight operations — carrier search, load management, rate negotiation tracking, analytics, and more.

## Authentication

The Broker App integration connects directly to your HappyRobot Broker App instance. No external credentials are required — the integration is available once enabled.

<Steps>
  <Step title="Enable the Broker App integration">
    Go to **Settings > Integrations** and enable **Broker App**.
  </Step>

  <Step title="Start using it in workflows">
    Add Broker App events to your workflow nodes. The integration connects to your organization's Broker App data automatically.
  </Step>
</Steps>

## Available events

### Actions

| Event                               | Description                                                                            |
| ----------------------------------- | -------------------------------------------------------------------------------------- |
| **Find Carrier**                    | Searches for carriers matching specified criteria                                      |
| **Find Load by Reference**          | Looks up a specific load by its reference number                                       |
| **Find Loads**                      | Searches for available loads                                                           |
| **Log Option**                      | Records a carrier option or note against a load                                        |
| **Verify Carrier and Search Loads** | Verifies a carrier's eligibility and searches for matching loads in a single operation |
| **Log Email Option**                | Records a carrier option via email notification                                        |
| **Update Lowest Agreed Rate**       | Updates the lowest agreed rate for a load                                              |
| **Get Interest on Load**            | Retrieves carrier interest and bids on a load                                          |
| **Update Carrier Status**           | Updates a carrier's status on a load                                                   |
| **Carrier Sales Evals**             | Runs carrier sales evaluation metrics                                                  |
| **Tracking Evals**                  | Runs tracking evaluation metrics                                                       |
| **OCS Evals**                       | Runs OCS (Order Control System) evaluation metrics                                     |
| **Log Capacity**                    | Records carrier capacity information                                                   |
| **Track and Trace Analytics**       | Retrieves track-and-trace analytics data                                               |

## Example use case

An inbound carrier call triggers a workflow. The voice agent uses **Verify Carrier and Search Loads** to confirm the carrier's authority and find matching loads simultaneously. After the carrier selects a load, **Log Option** records their rate, and **Update Carrier Status** marks them as interested. The workflow then sends a confirmation email via Gmail.

## Related

<CardGroup cols={2}>
  <Card title="McLeod TMS" icon="truck" href="01-McLeod-TMS.md">
    McLeod LoadMaster TMS integration.
  </Card>

  <Card title="Custom TMS" icon="gear" href="06-Custom-TMS.md">
    Connect to unsupported TMS systems.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/broker-app
