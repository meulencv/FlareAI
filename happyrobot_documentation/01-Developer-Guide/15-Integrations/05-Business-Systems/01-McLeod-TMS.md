---
title: "McLeod TMS"
description: "Integrate with McLeod LoadMaster TMS"
---

# McLeod TMS

> Integrate with McLeod LoadMaster TMS

The McLeod integration connects your workflows to McLeod LoadMaster, one of the most widely used transportation management systems. Query loads, find carriers, update locations, track shipments, and log options — all directly from your workflow nodes.

## Authentication

McLeod uses form-based credentials with your LoadMaster API connection details.

<Steps>
  <Step title="Enable the McLeod integration">
    Go to **Settings > Integrations** and enable **McLeod**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    * **Base URL** — your McLeod LoadMaster API endpoint URL
    * **Token Type** — select `Bearer`, `Token`, or `Basic` depending on your authentication method
    * **Token** — your API token or credentials (optional, depending on setup)
    * **Company ID** — your McLeod company identifier (optional)
  </Step>

  <Step title="Save and verify">
    Save the credential and verify it appears as **Active**.
  </Step>
</Steps>

## Available events

### Triggers

| Event                    | Description                                             |
| ------------------------ | ------------------------------------------------------- |
| **Get Tendered Loads**   | Fires when new tendered loads are available             |
| **Get In Transit Loads** | Fires when in-transit load status updates are available |

### Actions

| Event                             | Description                                                      |
| --------------------------------- | ---------------------------------------------------------------- |
| **Find Load by Reference**        | Looks up a specific load by its reference number                 |
| **Find Loads by Lane**            | Searches for loads matching origin/destination lane criteria     |
| **Update Location**               | Updates the current location of a shipment                       |
| **Log Option**                    | Records a carrier option or note against a load                  |
| **Find Carrier**                  | Searches for carriers matching specified criteria                |
| **Verify Carrier and Find Loads** | Verifies a carrier's eligibility and searches for matching loads |
| **Load Tracking**                 | Retrieves tracking information for a load                        |
| **Custom Endpoint**               | Calls a custom McLeod API endpoint with configurable parameters  |

<Tip>
  The **Custom Endpoint** action is useful when you need to access McLeod API functionality not covered by the built-in actions. Specify the endpoint path, HTTP method, and request body to call any McLeod API.
</Tip>

## Example use case

An inbound call arrives from a carrier. The voice agent extracts the reference number, uses **Find Load by Reference** to look up the shipment, confirms the details with the caller, and uses **Log Option** to record the carrier's rate. The workflow then sends a summary to Slack.

## Related

<CardGroup cols={2}>
  <Card title="Turvo TMS" icon="truck" href="02-Turvo-TMS.md">
    Turvo TMS integration.
  </Card>

  <Card title="Broker App" icon="building" href="07-Broker-App.md">
    HappyRobot's broker platform integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/mcleod-tms
