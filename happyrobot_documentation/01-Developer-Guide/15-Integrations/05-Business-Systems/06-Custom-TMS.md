---
title: "Custom TMS"
description: "Connect to any TMS with a custom integration"
---

# Custom TMS

> Connect to any TMS with a custom integration

The Custom TMS integration lets you connect HappyRobot to transportation management systems that aren't covered by the built-in integrations (McLeod, Turvo, TPro, 3PL). It provides a standardized set of freight operations that can be mapped to your TMS's API.

## Authentication

Custom TMS uses a dialog-based configuration flow tailored to your specific TMS.

<Steps>
  <Step title="Enable the Custom TMS integration">
    Go to **Settings > Integrations** and enable **Custom TMS**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and follow the configuration dialog. The required fields depend on your TMS — typically API endpoints, authentication tokens, and account identifiers.
  </Step>

  <Step title="Verify the connection">
    The credential will appear as **Active** once configured.
  </Step>
</Steps>

## Available events

### Actions

| Event                      | Description                                       |
| -------------------------- | ------------------------------------------------- |
| **Find Loads**             | Searches for available loads in your TMS          |
| **Find Load by Reference** | Looks up a specific load by its reference number  |
| **Log Option**             | Records a carrier option or note against a load   |
| **Find Carrier**           | Searches for carriers matching specified criteria |

## When to use Custom TMS

Use the Custom TMS integration when:

* Your TMS doesn't have a dedicated HappyRobot integration
* You have a proprietary or in-house TMS system
* You need to connect to a TMS that uses a non-standard API

<Tip>
  If your TMS is not listed and you need deeper integration support, contact the HappyRobot team. Dedicated integrations can be built for commonly requested TMS systems through the [custom integrations](../01-Integrations-Overview.md) process.
</Tip>

## Example use case

A brokerage uses a proprietary TMS. They configure the Custom TMS integration with their API endpoint and authentication details. When carriers call, the voice agent can search for loads, check availability, and log carrier options — all mapped to the brokerage's custom system.

## Related

<CardGroup cols={2}>
  <Card title="McLeod TMS" icon="truck" href="01-McLeod-TMS.md">
    McLeod LoadMaster TMS integration.
  </Card>

  <Card title="Broker App" icon="building" href="07-Broker-App.md">
    HappyRobot's broker platform integration.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/custom-tms
