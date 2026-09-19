---
title: "Create message flag"
description: "Creates a new flag (issue) on a specific message. The flag is linked to the message and its parent run."
---

# Create message flag

> Creates a new flag (issue) on a specific message. The flag is linked to the message and its parent run.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /messages/{message_id}/flags
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
  /messages/{message_id}/flags:
    post:
      tags:
        - Messages
      summary: Create message flag
      description: >-
        Creates a new flag (issue) on a specific message. The flag is linked to
        the message and its parent run.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: message_id
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                type:
                  default: message
                  description: The type of issue to create
                  type: string
                  enum:
                    - transcriber
                    - message
                    - tool_call
                    - run
                    - interruption
                priority:
                  default: medium
                  description: Priority level of the flag
                  type: string
                  enum:
                    - low
                    - medium
                    - high
                correction:
                  description: Correction text explaining what went wrong
                  type: string
                correction_reason:
                  description: Reason or category for the correction
                  type: string
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  status:
                    type: string
                  priority:
                    type: string
                  type:
                    type: string
                  correction:
                    nullable: true
                    type: string
                  correction_reason:
                    nullable: true
                    type: string
                  created_at:
                    type: string
                  updated_at:
                    type: string
                required:
                  - id
                  - status
                  - priority
                  - type
                  - correction
                  - correction_reason
                  - created_at
                  - updated_at
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
                  message:
                    type: string
                  statusCode:
                    type: integer
                    minimum: -9007199254740991
                    maximum: 9007199254740991
                  details: {}
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
                  message:
                    type: string
                  statusCode:
                    type: integer
                    minimum: -9007199254740991
                    maximum: 9007199254740991
                  details: {}
                required:
                  - error
                additionalProperties: false
        '500':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  message:
                    type: string
                  statusCode:
                    type: integer
                    minimum: -9007199254740991
                    maximum: 9007199254740991
                  details: {}
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

Fuente original: https://docs.happyrobot.ai/api-reference/messages/create-message-flag
