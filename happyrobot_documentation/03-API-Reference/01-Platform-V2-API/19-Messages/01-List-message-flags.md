---
title: "List message flags"
description: "Returns paginated flags (issues) for a specific message, ordered by creation date."
---

# List message flags

> Returns paginated flags (issues) for a specific message, ordered by creation date.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /messages/{message_id}/flags
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
    get:
      tags:
        - Messages
      summary: List message flags
      description: >-
        Returns paginated flags (issues) for a specific message, ordered by
        creation date.
      parameters:
        - schema:
            default: 1
            type: integer
            minimum: 1
            maximum: 9007199254740991
          in: query
          name: page
          required: false
        - schema:
            default: 50
            type: integer
            minimum: 1
            maximum: 100
          in: query
          name: page_size
          required: false
        - schema:
            default: desc
            type: string
            enum:
              - asc
              - desc
          in: query
          name: sort
          required: false
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: message_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
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
                  pagination:
                    type: object
                    properties:
                      page:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      page_size:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      total_pages:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      total_records:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      has_next_page:
                        type: boolean
                      has_previous_page:
                        type: boolean
                    required:
                      - page
                      - page_size
                      - total_pages
                      - total_records
                      - has_next_page
                      - has_previous_page
                    additionalProperties: false
                required:
                  - data
                  - pagination
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

Fuente original: https://docs.happyrobot.ai/api-reference/messages/list-message-flags
