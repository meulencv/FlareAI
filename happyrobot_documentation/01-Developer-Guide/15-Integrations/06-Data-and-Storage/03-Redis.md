---
title: "Redis"
description: "Use Redis for caching and key-value storage"
---

# Redis

> Use Redis for caching and key-value storage

The Redis integration lets your workflows read and write key-value data to a Redis instance. Use it for caching frequently accessed data, storing temporary state between workflow runs, or sharing data across workflows.

## Authentication

Redis uses form-based credentials with your Redis connection details.

<Steps>
  <Step title="Enable the Redis integration">
    Go to **Settings > Integrations** and enable **Redis**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    * **Host** — your Redis server hostname or IP address
    * **Port** — the Redis port (default: `6379`)
    * **Database** — the Redis database number to use
    * **Password** — your Redis password (optional, leave blank if no authentication is required)
    * **TLS** — toggle on if your Redis instance requires encrypted connections
  </Step>

  <Step title="Verify the connection">
    Save the credential and verify it appears as **Active**.
  </Step>
</Steps>

## Available events

### Actions

| Event           | Description                         |
| --------------- | ----------------------------------- |
| **Read Value**  | Retrieves a value by key from Redis |
| **Write Value** | Writes a key-value pair to Redis    |

## Example use case

During a carrier sales call, the voice agent uses **Read Value** to check if the carrier's MC number has been called recently (stored as a key with a TTL). If the key exists, the agent adjusts its approach based on the previous interaction context. After the call, **Write Value** stores the updated interaction data for future reference.

<Tip>
  Redis is ideal for storing temporary data that needs to be accessed quickly across multiple workflow runs — rate quotes, call state, deduplication flags, and more.
</Tip>

## Related

<CardGroup cols={2}>
  <Card title="Snowflake" icon="snowflake" href="02-Snowflake.md">
    Query data from Snowflake data warehouse.
  </Card>

  <Card title="Kafka" icon="database" href="04-Kafka.md">
    Publish messages to Apache Kafka topics.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/redis
