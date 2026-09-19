---
title: "Get chat session history"
description: "Retrieves message history for a chat session. Useful for page reloads or reconnects."
---

# Get chat session history

> Retrieves message history for a chat session. Useful for page reloads or reconnects.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /chat/sessions/{id}/history
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
  /chat/sessions/{id}/history:
    get:
      tags:
        - Chat
      summary: Get chat session history
      description: >-
        Retrieves message history for a chat session. Useful for page reloads or
        reconnects.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  session_id:
                    type: string
                  status:
                    type: string
                  started_at:
                    type: string
                  last_activity:
                    type: string
                  messages:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        role:
                          type: string
                        content:
                          type: string
                        timestamp:
                          type: string
                        metadata:
                          type: object
                          additionalProperties: {}
                        artifacts:
                          type: array
                          items:
                            type: object
                            properties:
                              media_id:
                                type: string
                              filename:
                                type: string
                              mime_type:
                                type: string
                              file_size:
                                type: number
                              presigned_url:
                                type: string
                            required:
                              - media_id
                              - filename
                              - mime_type
                            additionalProperties: false
                      required:
                        - id
                        - role
                        - content
                        - timestamp
                      additionalProperties: false
                  metadata:
                    type: object
                    additionalProperties: {}
                required:
                  - session_id
                  - status
                  - started_at
                  - last_activity
                  - messages
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

Fuente original: https://docs.happyrobot.ai/api-reference/chat/get-chat-session-history
