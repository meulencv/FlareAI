---
title: "Kafka"
description: "Publish messages to Apache Kafka topics from a workflow"
---

# Kafka

> Publish messages to Apache Kafka topics from a workflow

The Kafka integration lets your workflows publish messages to topics on your own [Apache Kafka](https://kafka.apache.org) broker. Use it to stream workflow outcomes into your event pipeline — a completed call, an extracted load, a status change — so downstream consumers pick them up without polling HappyRobot.

<Note>
  Kafka connects to a broker you run. HappyRobot does not host a broker, so you need network access from HappyRobot to your bootstrap servers.
</Note>

## Authentication

Kafka uses form-based credentials with your broker connection details.

<Steps>
  <Step title="Enable the Kafka integration">
    Go to **Settings > Integrations** and enable **Kafka**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    | Field                                    | Description                                                                                                                       |
    | ---------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------- |
    | **Bootstrap Servers**                    | Comma-separated `host:port` list for your brokers (for example, `broker-1.example.com:9093,broker-2.example.com:9093`). Required. |
    | **Authentication**                       | **SASL/PLAIN** (username and password) or **None**. Defaults to SASL/PLAIN.                                                       |
    | **Username**                             | SASL username. Required when authentication is SASL/PLAIN.                                                                        |
    | **Password**                             | SASL password. Required when authentication is SASL/PLAIN.                                                                        |
    | **TLS Encryption**                       | Use an encrypted connection to the broker. On by default and recommended.                                                         |
    | **CA Certificate (PEM)**                 | Optional. Paste the PEM certificate chain when your broker uses a private or self-signed certificate authority.                   |
    | **Skip TLS Verification**                | Accepts any broker certificate. Insecure — only use it while testing.                                                             |
    | **Schema Registry URL**                  | Optional. Required to publish Avro in Confluent wire format.                                                                      |
    | **Schema Registry Username**             | Optional. Defaults to the SASL username.                                                                                          |
    | **Schema Registry Password**             | Optional. Defaults to the SASL password.                                                                                          |
    | **Schema Registry CA Certificate (PEM)** | Optional. Defaults to the broker CA certificate.                                                                                  |
  </Step>

  <Step title="Verify the connection">
    Save the credential and verify it appears as **Active**.
  </Step>
</Steps>

<Warning>
  Leave **Skip TLS Verification** off in production. With it enabled, HappyRobot accepts any certificate the broker presents, which removes the protection TLS is there to provide.
</Warning>

## Available events

### Actions

| Event       | Description                           |
| ----------- | ------------------------------------- |
| **Publish** | Publishes a message to a Kafka topic. |

## Publish

Add a **Kafka > Publish** action node anywhere in a workflow and configure:

| Field                | Description                                                                                                                                              |
| -------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Kafka Credential** | The credential to publish with. Required. Supports [variables](../../02-Workflows/07-Variables.md), so the target broker can be chosen at runtime.                     |
| **Topic**            | The topic to publish to. Required. Supports variables — the topic name can come entirely from an upstream variable. Whitespace-only topics are rejected. |
| **Payload**          | The message value written to the topic. Required. Use JSON or plain text, with variables anywhere in the value.                                          |
| **Message Key**      | Optional partition key. Messages that share a key land on the same partition, which preserves their relative order.                                      |
| **Headers**          | Optional record headers sent with the message, such as CloudEvents attributes. Each header is a key/value pair, and values support variables.            |
| **Value Format**     | How the payload is serialized — **JSON** or **Avro**. See [Value format and Avro](#value-format-and-avro).                                               |
| **Schema Subject**   | Optional. The schema registry subject to resolve when the value format is Avro. Defaults to `<topic>-value`.                                             |

The node fails if the credential, topic, or payload is missing, and each publish has a 30-second timeout.

### Value format and Avro

**JSON** sends the payload as written. **Avro** resolves the subject's registered schema from your schema registry and publishes the message in Confluent wire format, so consumers that expect a schema ID prefix can read it.

To publish Avro:

1. Set **Schema Registry URL** on the Kafka credential. The registry username, password, and CA certificate fall back to the broker's SASL credentials and CA certificate when left blank.
2. Register the value schema for the subject you're publishing to.
3. Set **Value Format** to **Avro** on the Publish node, and set **Schema Subject** if the subject isn't `<topic>-value`.

The **Payload** stays JSON in the editor — it's encoded against the registered schema at publish time, so the payload's fields have to match that schema.

## Example use case

After a voice agent finishes a carrier check call, an **AI Extract** node pulls the confirmed pickup time and reference number out of the transcript. A **Kafka > Publish** node then writes a JSON payload to `loads.status.v1` with the carrier's MC number as the message key, so every event for a carrier stays ordered on one partition and your TMS consumer updates the load without calling back into HappyRobot.

```json Payload theme={null}
{
  "load_id": "@trigger.load_id",
  "mc_number": "@trigger.mc_number",
  "pickup_time": "@extract_pickup.pickup_time",
  "source": "happyrobot"
}
```

<Tip>
  Publish a stable, versioned topic name (such as `loads.status.v1`) rather than one derived from workflow names. That keeps consumers working when you rename or duplicate the workflow.
</Tip>

## Related

<CardGroup cols={2}>
  <Card title="Redis" icon="database" href="03-Redis.md">
    Read and write key-value data for caching and shared state.
  </Card>

  <Card title="Webhook" icon="webhook" href="../../03-Core-Nodes/06-Webhook.md">
    Send an HTTP request when the target system has no broker.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/kafka
