# Chat

Ruta en la web: API Reference › Platform V2 API › Chat

7 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [Create a chat client token](01-Create-a-chat-client-token.md) | Generates a scoped JWT for browser-side chat operations. Call this from your backend with your API key, then pass the token to the frontend. |
| 2 | [Create a chat session](02-Create-a-chat-session.md) | Creates a new chat session for the workflow scoped in the client token. |
| 3 | [Send a chat message](03-Send-a-chat-message.md) | Sends a user message to the chat session. The AI response will arrive via WebSocket. |
| 4 | [Close a chat session](04-Close-a-chat-session.md) | Ends the chat session, stopping the AI agent. The session cannot be resumed after this call. |
| 5 | [Get chat session history](05-Get-chat-session-history.md) | Retrieves message history for a chat session. Useful for page reloads or reconnects. |
| 6 | [Get presigned upload URL](06-Get-presigned-upload-URL.md) | Returns a presigned S3 URL for direct file upload from the browser. After uploading, call POST /chat/upload/complete to register the artifact. |
| 7 | [Complete file upload](07-Complete-file-upload.md) | Registers an uploaded artifact after direct S3 upload. Call this after uploading the file to the presigned URL. |

---

[← Volver](../README.md)
