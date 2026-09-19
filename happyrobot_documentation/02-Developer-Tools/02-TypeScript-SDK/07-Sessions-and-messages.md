---
title: "Sessions and messages"
description: "Read session details, fetch messages, and stream live conversation events with the TypeScript SDK"
---

# Sessions and messages

> Read session details, fetch messages, and stream live conversation events with the TypeScript SDK

Read session data, manage message-level quality flags, and stream live conversation events.

## Sessions

Session details and message retrieval. Use this to fetch session metadata and paginated message history for any completed or active session.

| Method                           | HTTP                         | Description                          |
| -------------------------------- | ---------------------------- | ------------------------------------ |
| `list(query)`                    | `GET /sessions`              | List sessions by caller phone number |
| `get(sessionId)`                 | `GET /sessions/:id`          | Get session details                  |
| `getMessages(sessionId, query?)` | `GET /sessions/:id/messages` | Get paginated messages for a session |
| `stream(sessionId, query?)`      | `GET /sessions/:id/stream`   | Open SSE stream of session messages  |

```ts theme={null}
const session = await client.sessions.get("session-id");
const { data: messages } = await client.sessions.getMessages("session-id");

for (const msg of messages) {
  console.log(`[${msg.role}] ${msg.content}`);
}
```

### List sessions by caller

Look up sessions by the caller's phone number. Pass `caller_id` as an E.164 phone number; the results are paginated and ordered by timestamp. Use each returned session id with `getMessages()` to fetch the transcript.

```ts theme={null}
const { data: sessions } = await client.sessions.list({
  caller_id: "+15551234567",
  start_date: "2026-07-01T00:00:00Z", // optional, ISO 8601
  end_date: "2026-07-03T00:00:00Z", // optional, ISO 8601
  page: 1, // optional, default 1
  page_size: 50, // optional, default 50, max 100
});

for (const session of sessions) {
  const { data: messages } = await client.sessions.getMessages(session.id);
  console.log(session.id, messages.length, "messages");
}
```

| Parameter    | Type     | Description                                                                 |
| ------------ | -------- | --------------------------------------------------------------------------- |
| `caller_id`  | `string` | Required. The caller's phone number, normalized to E.164 for an exact match |
| `start_date` | `string` | Optional. Only return sessions on or after this ISO 8601 timestamp          |
| `end_date`   | `string` | Optional. Only return sessions on or before this ISO 8601 timestamp         |
| `page`       | `number` | Optional. Page number (default `1`)                                         |
| `page_size`  | `number` | Optional. Results per page (default `50`, max `100`)                        |

<Note>
  A session is resolved through the caller's [contact](../../01-Developer-Guide/13-Contacts/01-Contacts-Overview.md) record, so it's only returned if it produced a communication event. The endpoint returns `404` when no sessions match the caller.
</Note>

<Warning>
  **Breaking change:** `getMessages()` no longer returns embedded presigned download URLs inside message artifacts. Artifact objects now contain only `s3_key` and `status` fields. To obtain download URLs, use `client.artifacts.resolve()` — see below.
</Warning>

***

## Artifacts

Resolve presigned download URLs for message artifacts. Artifact URLs are not embedded in message responses and must be fetched on demand using this endpoint.

| Method          | HTTP                      | Description                                                 |
| --------------- | ------------------------- | ----------------------------------------------------------- |
| `resolve(body)` | `POST /artifacts/resolve` | Resolve presigned download URLs for up to 500 artifact keys |

### Request

```ts theme={null}
const result = await client.artifacts.resolve({
  s3_keys: ["artifacts/org-123/session-456/recording.mp3"],
  expires_in: 3600, // optional, seconds; range 60–604800 (default: 3600)
});

for (const item of result.data) {
  if (item.presigned_url) {
    console.log("Download:", item.presigned_url);
  } else {
    console.error("Failed to resolve", item.s3_key, item.error);
  }
}
```

### Response

Each item in `data` corresponds to one input `s3_key`:

| Field           | Type             | Description                                            |
| --------------- | ---------------- | ------------------------------------------------------ |
| `s3_key`        | `string`         | The artifact key from the message                      |
| `presigned_url` | `string \| null` | Temporary download URL, valid for `expires_in` seconds |
| `error`         | `string \| null` | Error message if the URL could not be resolved         |

<Tip>
  Presigned URLs are temporary. Resolve them close to when they'll be used, and do not cache them for longer than the `expires_in` window.
</Tip>

***

## Messages

Quality flags on individual messages. Use this to list existing flags or create new ones to mark specific messages as incorrect or problematic.

| Method                         | HTTP                       | Description                        |
| ------------------------------ | -------------------------- | ---------------------------------- |
| `listFlags(messageId, query?)` | `GET /messages/:id/flags`  | List quality flags for a message   |
| `createFlag(messageId, body)`  | `POST /messages/:id/flags` | Create a quality flag on a message |

```ts theme={null}
const { data } = await client.messages.listFlags("message-id");
await client.messages.createFlag("message-id", {
  type: "incorrect",
  note: "Agent gave wrong pricing info",
});
```

***

## SSE streaming

Open a real-time server-sent events stream for any active session. The stream emits events as the conversation progresses and closes when the session ends.

### Event types

| Event           | Description                                                                 |
| --------------- | --------------------------------------------------------------------------- |
| `message`       | A new message was added to the conversation. Includes `role` and `content`. |
| `session_ended` | The session has ended. Close the stream after receiving this event.         |

### Example

```ts theme={null}
const stream = await client.sessions.stream("session-id");

for await (const event of stream) {
  switch (event.event) {
    case "message":
      console.log(`[${event.data.role}] ${event.data.content}`);
      break;
    case "session_ended":
      console.log("Session ended");
      break;
  }
}
```

<Tip>
  SSE streaming is useful for building real-time dashboards or live transcription UIs. Combine it with `triggerAndWait` to trigger a call and stream its messages as they arrive.
</Tip>

---

Fuente original: https://docs.happyrobot.ai/developer-tools/sdk/sessions-and-messages
