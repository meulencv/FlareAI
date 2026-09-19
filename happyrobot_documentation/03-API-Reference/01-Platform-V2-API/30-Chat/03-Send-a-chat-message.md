---
title: "Send a chat message"
description: "Sends a user message to the chat session. The AI response will arrive via WebSocket."
---

# Send a chat message

> Sends a user message to the chat session. The AI response will arrive via WebSocket.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /chat/sessions/{id}/messages
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
  /chat/sessions/{id}/messages:
    post:
      tags:
        - Chat
      summary: Send a chat message
      description: >-
        Sends a user message to the chat session. The AI response will arrive
        via WebSocket.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: id
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                content:
                  type: string
                  description: Message text content
                artifacts:
                  description: Attached file references
                  type: array
                  items:
                    type: object
                    properties:
                      type:
                        default: raw
                        type: string
                      media_id:
                        type: string
                      s3_key:
                        type: string
                      mime_type:
                        type: string
                      presigned_url:
                        type: string
                      filename:
                        type: string
                      size_bytes:
                        type: number
                      artifact_text:
                        type: string
                    required:
                      - media_id
                      - mime_type
              required:
                - content
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: object
                    properties:
                      id:
                        type: string
                      session_id:
                        type: string
                      content:
                        type: string
                      role:
                        type: string
                      created_at:
                        type: string
                    required:
                      - id
                      - session_id
                      - content
                      - role
                      - created_at
                    additionalProperties: false
                required:
                  - message
                additionalProperties: false
        '401':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  statusCode:
                    type: number
                required:
                  - error
                additionalProperties: false
        '403':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  statusCode:
                    type: number
                required:
                  - error
                additionalProperties: false
        '404':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  statusCode:
                    type: number
                required:
                  - error
                additionalProperties: false
        '502':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  statusCode:
                    type: number
                required:
                  - error
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

Fuente original: https://docs.happyrobot.ai/api-reference/chat/send-a-chat-message
