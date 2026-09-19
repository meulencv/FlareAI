---
title: "Google Maps"
description: "Geographic utilities for your workflows"
---

# Google Maps

> Geographic utilities for your workflows

The Google Maps integration provides geographic utilities for your workflows — calculate driving distances, look up time zones, and convert addresses to coordinates. Use these actions to add location intelligence to your automation.

## Authentication

Google Maps uses a dialog-based configuration flow.

<Steps>
  <Step title="Enable the Google Maps integration">
    Go to **Settings > Integrations** and enable **Google Maps**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and follow the configuration dialog to enter your Google Maps API key.
  </Step>

  <Step title="Verify the connection">
    The credential will appear as **Active** once configured.
  </Step>
</Steps>

## Available events

### Actions

| Event               | Description                                                                      |
| ------------------- | -------------------------------------------------------------------------------- |
| **Distance Matrix** | Calculates travel distance and time between origins and destinations             |
| **Timezone**        | Looks up the timezone for a given location                                       |
| **Geocoding**       | Converts addresses to geographic coordinates (latitude/longitude) and vice versa |

## Example use case

A carrier calls about a load. The voice agent extracts the pickup and delivery addresses, uses **Distance Matrix** to calculate the driving distance and estimated transit time, and uses **Timezone** to determine the delivery location's time zone — ensuring the quoted delivery window accounts for time zone differences.

<Tip>
  Combine **Geocoding** with **Distance Matrix** to calculate distances when you only have street addresses. First geocode the addresses to coordinates, then compute the distance.
</Tip>

## Related

<CardGroup cols={2}>
  <Card title="Snowflake" icon="snowflake" href="02-Snowflake.md">
    Query data from Snowflake data warehouse.
  </Card>

  <Card title="Workflows" icon="diagram-project" href="../../02-Workflows/01-Workflows-Overview.md">
    Learn how to build workflows with data actions.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/google-maps
