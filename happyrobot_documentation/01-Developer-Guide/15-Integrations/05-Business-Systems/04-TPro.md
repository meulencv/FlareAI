---
title: "TPro"
description: "Integrate with TPro TMS"
---

# TPro

> Integrate with TPro TMS

The TPro integration connects your workflows to the TPro transportation management system. Search for carriers and loads, look up shipments by reference or lane, and log carrier options.

## Authentication

TPro uses a dialog-based configuration flow.

<Steps>
  <Step title="Enable the TPro integration">
    Go to **Settings > Integrations** and enable **TPro**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and follow the configuration dialog to set up your TPro connection.
  </Step>

  <Step title="Verify the connection">
    The credential will appear as **Active** once configured.
  </Step>
</Steps>

## Available events

### Actions

| Event                        | Description                                                  |
| ---------------------------- | ------------------------------------------------------------ |
| **Find Carrier**             | Searches for carriers matching specified criteria            |
| **Find E-Load by Reference** | Looks up an electronic load by its reference number          |
| **Find Load by Lane**        | Searches for loads matching origin/destination lane criteria |
| **Find Load by Reference**   | Looks up a specific load by its reference number             |
| **Log Email Option**         | Records a carrier option via email notification              |
| **Log Option**               | Records a carrier option or note against a load              |

## Example use case

A carrier calls about available loads on a specific lane. The voice agent uses **Find Load by Lane** to search for matching shipments, presents the options to the carrier, and uses **Log Option** to record the carrier's interest and rate.

## Related

<CardGroup cols={2}>
  <Card title="McLeod TMS" icon="truck" href="01-McLeod-TMS.md">
    McLeod LoadMaster TMS integration.
  </Card>

  <Card title="3PL" icon="warehouse" href="05-3PL.md">
    3PL Warehouse Manager integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/tpro
