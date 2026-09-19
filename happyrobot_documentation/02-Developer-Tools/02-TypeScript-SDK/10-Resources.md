---
title: "Resources"
description: "Manage contacts, knowledge bases, variables, MCP servers, apps, billing, voices, and API keys"
---

# Resources

> Manage contacts, knowledge bases, variables, MCP servers, apps, billing, voices, and API keys

Access platform resources like contacts, knowledge bases, apps, and billing data through dedicated sub-clients.

## Contacts

Look up contacts and view their interaction history. Use this to search for contacts by name, resolve them by phone number or email, and retrieve their call/message history.

| Method                       | HTTP                             | Description                                |
| ---------------------------- | -------------------------------- | ------------------------------------------ |
| `list(query?)`               | `GET /contacts`                  | List contacts (cursor-paginated)           |
| `resolve(query)`             | `GET /contacts/resolve`          | Look up a contact by phone number or email |
| `get(contactId)`             | `GET /contacts/:id`              | Get contact by ID                          |
| `getInteractions(contactId)` | `GET /contacts/:id/interactions` | Get call/message history for a contact     |
| `getMemories(contactId)`     | `GET /contacts/:id/memories`     | Get AI memories for a contact              |

```ts theme={null}
const { data } = await client.contacts.list({ search: "John" });
const contact = await client.contacts.resolve({ phone_number: "+14155551234" });
const contact = await client.contacts.get("contact-id");
const interactions = await client.contacts.getInteractions("contact-id");
const memories = await client.contacts.getMemories("contact-id");
```

***

## Knowledge bases

Manage knowledge base documents for agent RAG. Use this to upload files, trigger processing, and manage knowledge bases that your agents reference during conversations.

| Method                      | HTTP                                         | Description                         |
| --------------------------- | -------------------------------------------- | ----------------------------------- |
| `list()`                    | `GET /knowledge-bases`                       | List all knowledge bases            |
| `create(body)`              | `POST /knowledge-bases`                      | Create a new knowledge base         |
| `listFiles(kbId)`           | `GET /knowledge-bases/:id/files`             | List documents in a knowledge base  |
| `getUploadUrls(kbId, body)` | `POST /knowledge-bases/:id/upload-urls`      | Get pre-signed S3 upload URLs       |
| `triggerChunking(kbId)`     | `POST /knowledge-bases/:id/trigger-chunking` | Start document processing/chunking  |
| `deleteFile(kbId, fileId)`  | `DELETE /knowledge-bases/:id/files/:fileId`  | Delete a file from a knowledge base |
| `delete(kbId)`              | `DELETE /knowledge-bases/:id`                | Delete a knowledge base             |

```ts theme={null}
const kbs = await client.knowledgeBases.list();

// Create a knowledge base
const kb = await client.knowledgeBases.create({ name: "Support Docs", description: "Customer support articles" });

const files = await client.knowledgeBases.listFiles("kb-id");

// Upload a file
const urls = await client.knowledgeBases.getUploadUrls("kb-id", {
  files: [{ name: "doc.pdf", content_type: "application/pdf" }],
});
// ... upload to the pre-signed URL ...
await client.knowledgeBases.triggerChunking("kb-id");

await client.knowledgeBases.deleteFile("kb-id", "file-id");
await client.knowledgeBases.delete("kb-id");
```

***

## Variables

Workflow-scoped variables for dynamic configuration. Use these to store key-value pairs that your workflow nodes can reference at runtime.

| Method                                 | HTTP                                    | Description                   |
| -------------------------------------- | --------------------------------------- | ----------------------------- |
| `list(workflowId, query?)`             | `GET /workflows/:wId/variables`         | List variables for a workflow |
| `create(workflowId, body)`             | `POST /workflows/:wId/variables`        | Create a variable             |
| `update(workflowId, variableId, body)` | `PATCH /workflows/:wId/variables/:vId`  | Update a variable             |
| `delete(workflowId, variableId)`       | `DELETE /workflows/:wId/variables/:vId` | Delete a variable             |

```ts theme={null}
const { data } = await client.variables.list("workflow-id");
await client.variables.create("workflow-id", { name: "MY_VAR", value: "hello" });
await client.variables.update("workflow-id", "variable-id", { value: "world" });
await client.variables.delete("workflow-id", "variable-id");
```

***

## MCP servers

Register and manage MCP servers. Use this to connect external tool servers that your agents can invoke during conversations.

| Method           | HTTP                    | Description                         |
| ---------------- | ----------------------- | ----------------------------------- |
| `list(query?)`   | `GET /mcp`              | List MCP servers (paginated)        |
| `create(body)`   | `POST /mcp`             | Register a new MCP server           |
| `refresh(mcpId)` | `POST /mcp/:id/refresh` | Re-discover tools for an MCP server |

```ts theme={null}
const { data } = await client.mcp.list();
await client.mcp.create({ name: "My MCP", url: "https://..." });
await client.mcp.refresh("mcp-id");
```

***

## Apps

Duplicate managed [apps](../../01-Developer-Guide/07-Apps/01-Apps-Overview.md) programmatically. Use this to spin up a copy of an existing app — including its source code and custom environment variables — from your own code or automation.

| Method                      | HTTP                             | Description                     |
| --------------------------- | -------------------------------- | ------------------------------- |
| `duplicate(appSlug, body?)` | `POST /apps/:app_slug/duplicate` | Duplicate a managed Next.js app |

```ts theme={null}
// Duplicate an app, keeping the source app's defaults
const copy = await client.apps.duplicate("carrier-portal-a1b2c");

// Or override the name, description, and tags for the copy
const named = await client.apps.duplicate("carrier-portal-a1b2c", {
  name: "Carrier Portal (Staging)",
  description: "Staging copy of the carrier portal",
  tag_ids: ["tag-id-1", "tag-id-2"],
});
console.log(named.slug, named.public_url);
```

| Field         | Type       | Description                                                                   |
| ------------- | ---------- | ----------------------------------------------------------------------------- |
| `name`        | `string`   | Optional. Display name for the new app. Defaults to `"{original name} Copy"`. |
| `description` | `string`   | Optional. Defaults to the source app's description.                           |
| `tag_ids`     | `string[]` | Optional. Tags to assign to the duplicated app.                               |

The response is the new app: `id`, `org_id`, `name`, `slug`, `description`, `public_url`, `tag_ids`, `created_at`, and `updated_at`.

<Note>
  Duplication is a long-running request — provisioning the copy's repository and deployment can take a while before the response returns. Your custom environment variables are copied, but platform-managed values are regenerated and service credentials must be reconfigured. Only managed Next.js apps can be duplicated.
</Note>

***

## Billing

Query billing usage and credit consumption. Use this to retrieve itemized line items, aggregated totals for a date range, or the credit breakdown for a single run.

| Method                 | HTTP                               | Description                                                  |
| ---------------------- | ---------------------------------- | ------------------------------------------------------------ |
| `getDetails(query)`    | `GET /billing/usage/details`       | Voice minutes, emails, and text messages grouped by workflow |
| `getTotals(query)`     | `GET /billing/usage/totals`        | The same usage aggregated across the organization            |
| `getRunCredits(runId)` | `GET /billing/usage/runs/{run_id}` | Credit consumption for one run                               |

```ts theme={null}
const details = await client.billing.getDetails({
  start: "2024-01-01",
  end: "2024-01-31",
});
const totals = await client.billing.getTotals({
  start: "2024-01-01",
  end: "2024-01-31",
});

// What one run cost, by category and subcomponent
const runCredits = await client.billing.getRunCredits(
  "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
);
```

`getRunCredits` returns `total_credits` for the run plus a `components` breakdown using the same category → subcomponent taxonomy as the credits shown in **Settings > Usage**, so a run's cost can be attributed to voice, LLM, and other components. See [Credits for a single run](../../01-Developer-Guide/16-Account-and-Settings/09-Usage-and-Billing.md#credits-for-a-single-run) for the response shape.

***

## Voices

List the text-to-speech voices available to your workspace. Use this to resolve a voice ID before writing it into a voice agent's configuration.

| Method         | HTTP          | Description                                            |
| -------------- | ------------- | ------------------------------------------------------ |
| `list(query?)` | `GET /voices` | List available voices, optionally filtered by language |

```ts theme={null}
// Every voice available to the workspace
const voices = await client.voice.list();

// Only voices that support a specific locale
const british = await client.voice.list({ language: "en-GB" });

for (const voice of british) {
  console.log(voice.id, voice.name, voice.locales);
}
```

`language` accepts a prefix such as `en` to match every accent of that language, or a locale such as `en-GB` to match one locale. Each voice's `id` is the value used in a workflow's `agent.voices` configuration. See [Voices](../../01-Developer-Guide/14-Assets/04-Voices.md#listing-voices-with-the-api) for the full response shape.

Token creation for browser-side calls lives on the same sub-client — see the [voice call tutorial](04-Voice-call-tutorial.md).

***

## API key

Introspect the current API key. Use this to verify which key is active and retrieve its associated metadata.

| Method       | HTTP                    | Description                                          |
| ------------ | ----------------------- | ---------------------------------------------------- |
| `describe()` | `GET /api-key/describe` | Introspect the current API key (ID, name, org, etc.) |

```ts theme={null}
const info = await client.apiKey.describe();
console.log(info); // { id, name, org_id, ... }
```

---

Fuente original: https://docs.happyrobot.ai/developer-tools/sdk/resources
