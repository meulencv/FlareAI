---
title: "Webhook"
description: "Send and receive HTTP requests in workflows"
---

# Webhook

> Send and receive HTTP requests in workflows

The Webhook node lets your workflow send HTTP requests to external APIs and receive incoming webhooks from other systems. Use it to call REST APIs, submit form data, fetch remote resources, or trigger workflows from external events.

## HTTP methods

### Incoming Webhook

Receive HTTP requests from external systems to trigger or interact with your workflow. When configured, HappyRobot generates a unique URL that external services can call.

**Configuration:**

* **Webhook URL** — Auto-generated unique URL for receiving requests
* **Security** — Optional authentication requirements for incoming requests

### GET

Fetch data from an external API or resource.

**Configuration:**

* **URL** — The endpoint to request (supports variables — type `@` to insert dynamic values)
* **Query parameters** — Key-value pairs appended to the URL
* **Headers** — Custom HTTP headers
* **Body** — An optional request payload (see [Body modes](#body-modes) below). Most GET requests don't need one.
* **Authentication** — See [Authentication](#authentication) below

<Warning>
  Some APIs accept a body on GET requests, but gateways, servers, and proxies may ignore or drop it. If the target endpoint requires a payload, prefer POST.
</Warning>

### POST

Send data to an external API.

**Configuration:**

* **URL** — The endpoint to send data to (supports variables)
* **Headers** — Custom HTTP headers
* **Body** — The request payload (see [Body modes](#body-modes) below)
* **Content type** — The format of the request body
* **Authentication** — See [Authentication](#authentication) below
* **Error handling** — See [Error handling](#error-handling) below

### PUT

Replace a resource on an external API. Configuration is the same as POST.

### PATCH

Partially update a resource on an external API. Configuration is the same as POST.

### DELETE

Delete a resource on an external API. Configuration is the same as POST — you can send a request body, custom headers, query parameters, and authentication. Use the body when the target API expects a payload to identify or qualify the resource being deleted.

## Authentication

Configure how the webhook authenticates with the target API.

| Method           | Description                                               |
| ---------------- | --------------------------------------------------------- |
| **None**         | No authentication                                         |
| **API Key**      | Send an API key as a header or query parameter            |
| **Bearer Token** | Send a token in the `Authorization: Bearer` header        |
| **Basic Auth**   | Send username and password with HTTP Basic authentication |
| **OAuth2**       | Use OAuth2 client credentials flow                        |

All authentication values support variables — type `@` to insert credentials stored in [environment variables](../16-Account-and-Settings/08-Environment-Variables.md).

### Client certificates (mTLS)

For endpoints that require mutual TLS, attach a **Client Certificate (mTLS)** credential to the node. The certificate is presented during the TLS handshake, so it works alongside any of the authentication methods above — pick **None** if the certificate is the only thing the endpoint checks.

<Steps>
  <Step title="Create the credential">
    Go to **Settings > Integrations**, open **OAuth 2.0**, and add a **Client Certificate (mTLS)** credential. Paste the client certificate and private key as PEM, plus a CA certificate if the endpoint is signed by a private authority. See [Client certificates (mTLS)](../15-Integrations/02-Credentials.md#client-certificates-mtls).
  </Step>

  <Step title="Select it on the node">
    In the Webhook node's request settings, open the **Client certificate (mTLS)** selector and pick the credential. Leave it on **No client certificate** for endpoints that don't need one, or reference a variable when the certificate differs per run.
  </Step>
</Steps>

<Tip>
  The selector is independent of the authentication method, so a certificate can accompany **None**, **Bearer Token**, **OAuth2**, or any other method. Use the selector's clear control to remove a certificate; clearing it is saved explicitly, so the node stops presenting one on its next run.
</Tip>

## Body modes

For requests that send a body — POST, PUT, PATCH, DELETE, and optionally GET — choose how to define the request body:

* **Builder** — Visual key-value editor. Add fields by name and value, with variable support on each field. Best for simple payloads.
* **Raw** — A free-form text area for writing the full request body. Use this for complex JSON structures, nested objects, or non-JSON formats.

Picking `multipart/form-data` as the content type replaces both with a parts list — see [Multipart form data](#multipart-form-data).

## Content types

| Content Type                        | Use for                                                                              |
| ----------------------------------- | ------------------------------------------------------------------------------------ |
| `application/json`                  | JSON payloads (most common)                                                          |
| `application/x-www-form-urlencoded` | Form submissions                                                                     |
| `application/xml`                   | XML payloads                                                                         |
| `text/plain`                        | Unstructured text bodies                                                             |
| `multipart/form-data`               | File uploads and mixed form fields (see [Multipart form data](#multipart-form-data)) |
| `none`                              | No request body                                                                      |

### XML bodies

Selecting `application/xml` switches the body editor to raw text with XML syntax highlighting. The body is sent exactly as written — no JSON parsing, no JSON validation errors, and no **Format** button. Type `@` to insert a [variable](../02-Workflows/07-Variables.md) anywhere in the markup, including inside an element or an attribute value:

```xml theme={null}
<LoadStatus>
  <LoadId>@trigger.load_id</LoadId>
  <PickupTime>@extract_pickup.pickup_time</PickupTime>
</LoadStatus>
```

<Note>
  Because the body is passed through verbatim, HappyRobot doesn't check that your XML is well-formed. Make sure tags are balanced and any variable that lands inside markup resolves to a value the target API can parse.
</Note>

### Multipart form data

Selecting `multipart/form-data` replaces the body editor with a list of **fields**. Each field becomes one part of the request, sent in the order you list them, and the raw body is ignored. Use this for endpoints that expect an upload — sending a recording, a generated PDF, or a caller's attachment alongside regular form values.

Add a field, give it a name, and choose its type:

| Type     | What is sent                                                                                                                                            |
| -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Text** | The field's value as a plain form field. This is the default when no type is chosen.                                                                    |
| **File** | The file the value points to, uploaded as a file part. The value is an artifact ID or a file [variable](../02-Workflows/07-Variables.md) — type `@` to insert one. |

A file field whose value resolves to a list of artifacts sends one file part per artifact, so several files can share a single field name. You can also repeat the same field name across fields when the API expects repeated keys.

Each field has its own enable toggle, so you can leave an optional part configured but switched off. The node won't save until every enabled field has a name and every file field has a file reference.

<Tip>
  A file field expects a reference, not the file's contents. Upstream nodes that produce files — a [File operations](08-File-Operations.md) node, an email attachment, or an artifact captured during a call — expose that reference through the `@` variable picker.
</Tip>

## Capturing response headers

By default, a Webhook node exposes the response status and body to downstream nodes. To also make specific response headers available, open the node's **Settings** and enable **Response headers to capture**, then add the header names you want. Captured headers become available to downstream nodes through the `@` variable picker, the same way you reference the response body.

* Add up to **10** headers per node. Header names are case-insensitive and must be valid HTTP header tokens.
* Only the headers you name are captured — everything else in the response is ignored.

<Warning>
  Response headers may contain credentials, API keys, or other sensitive information. Captured headers are stored with the workflow run output and are available to downstream nodes, so capture only the headers you need.
</Warning>

## Error handling

* **Ignore 5XX errors** — When enabled, the workflow continues even if the API returns a server error (500-599). When disabled, 5XX responses cause the node to fail.
* **XSS protection** — Toggle to enable cross-site scripting protection on incoming data.

## Example

After a voice agent extracts load details, the Webhook node sends a POST request to a TMS API with the structured data as a JSON body, using a Bearer token stored in environment variables for authentication.

<Tip>
  Store API keys and tokens as [environment variables](../16-Account-and-Settings/08-Environment-Variables.md) and reference them with `@` in the authentication fields. Never hardcode credentials in webhook configurations.
</Tip>

## Related

<CardGroup cols={2}>
  <Card title="Integrations" icon="plug" href="../15-Integrations/01-Integrations-Overview.md">
    Pre-built integrations that don't require manual webhook setup.
  </Card>

  <Card title="Custom Code" icon="code" href="05-Custom-Code.md">
    Transform data before or after webhook requests.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/webhook
