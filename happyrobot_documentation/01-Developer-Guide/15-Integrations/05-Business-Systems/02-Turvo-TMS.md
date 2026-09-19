---
title: "Turvo TMS"
description: "Integrate with Turvo TMS"
---

# Turvo TMS

> Integrate with Turvo TMS

The Turvo integration connects your workflows to the Turvo transportation management system. Search for carriers, query loads, and look up shipments by reference number.

## Authentication

Turvo uses form-based credentials with your Turvo API account.

<Steps>
  <Step title="Enable the Turvo integration">
    Go to **Settings > Integrations** and enable **Turvo**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    * **Username** — your Turvo account email address
    * **Password** — your Turvo account password (minimum 3 characters)
    * **API Key** — your Turvo API key (40 characters)
  </Step>

  <Step title="Verify the connection">
    The credential will validate automatically and appear as **Active**.
  </Step>
</Steps>

## Available events

### Actions

| Event                      | Description                                       |
| -------------------------- | ------------------------------------------------- |
| **Find Carrier**           | Searches for carriers matching specified criteria |
| **Find Loads**             | Searches for available loads                      |
| **Find Load by Reference** | Looks up a specific load by its reference number  |

## Example use case

A carrier calls in about a specific shipment. The voice agent extracts the reference number from the conversation, uses **Find Load by Reference** to look up the load details in Turvo, and confirms the pickup time and location with the caller.

## Related

<CardGroup cols={2}>
  <Card title="McLeod TMS" icon="truck" href="01-McLeod-TMS.md">
    McLeod LoadMaster TMS integration.
  </Card>

  <Card title="TPro" icon="truck" href="04-TPro.md">
    TPro TMS integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/turvo-tms
