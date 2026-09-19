---
title: "Stream session messages (SSE)"
description: "Opens a Server-Sent Events stream for a single session. Optionally backfills the most recent messages. The stream emits `message` events in real-time and closes when the session ends."
---

# Stream session messages (SSE)

> Opens a Server-Sent Events stream for a single session. Optionally backfills the most recent messages. The stream emits `message` events in real-time and closes when the session ends.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /sessions/{session_id}/stream
openapi: 3.0.3
info:
  title: Happyrobot Public API
  description: Public API endpoints for Happyrobot
  version: 0.1.1
servers:
  - url: https://platform.happyrobot.ai/api/v2
security:
  - bearerAuth: []
paths:
  /sessions/{session_id}/stream:
    get:
      tags:
        - Sessions
      summary: Stream session messages (SSE)
      description: >-
        Opens a Server-Sent Events stream for a single session. Optionally
        backfills the most recent messages. The stream emits `message` events in
        real-time and closes when the session ends.
      parameters:
        - schema:
            default: 0
            type: integer
            minimum: 0
            maximum: 1000
          in: query
          name: backfillLimit
          required: false
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: session_id
          required: true
      responses:
        '404':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                required:
                  - message
                additionalProperties: false
      security:
        - bearerAuth: []
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: Opaque

````

---

Fuente original: https://docs.happyrobot.ai/api-reference/sessions/stream-session-messages-sse
