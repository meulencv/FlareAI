# Sessions

Ruta en la web: API Reference › Platform V2 API › Sessions

4 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [List sessions by caller ID](01-List-sessions-by-caller-ID.md) | Returns paginated sessions whose caller phone number matches caller_id, ordered by timestamp. Optionally filter by session timestamp with start_date and/or end_date (ISO 8601). Resolves the phone number to a contact, so a session is only returned if it produced a communication event. Use the session… |
| 2 | [Stream session messages (SSE)](02-Stream-session-messages-SSE.md) | Opens a Server-Sent Events stream for a single session. Optionally backfills the most recent messages. The stream emits `message` events in real-time and closes when the session ends. |
| 3 | [Get session](03-Get-session.md) | Returns metadata for a single session. |
| 4 | [List session messages](04-List-session-messages.md) | Returns paginated messages for a session, ordered by timestamp. |

---

[← Volver](../README.md)
