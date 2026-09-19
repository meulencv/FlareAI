---
title: "List contacts"
description: "Returns paginated contacts for the organization. Uses cursor-based pagination."
---

# List contacts

> Returns paginated contacts for the organization. Uses cursor-based pagination.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /contacts/
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
  /contacts/:
    get:
      tags:
        - Contacts
      summary: List contacts
      description: >-
        Returns paginated contacts for the organization. Uses cursor-based
        pagination.
      parameters:
        - schema:
            default: 50
            type: integer
            minimum: 1
            maximum: 100
          in: query
          name: limit
          required: false
        - schema:
            type: string
          in: query
          name: cursor
          required: false
        - schema:
            type: string
          in: query
          name: search
          required: false
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
                        type:
                          nullable: true
                          type: string
                        value:
                          type: string
                        contact_summary:
                          nullable: true
                          type: string
                        extracted_attributes:
                          type: object
                          additionalProperties:
                            anyOf:
                              - type: string
                              - type: array
                                items:
                                  type: string
                        created_at:
                          type: string
                        updated_at:
                          type: string
                        interactions_count:
                          type: object
                          additionalProperties:
                            type: number
                        tags:
                          type: array
                          items:
                            type: string
                        last_interaction_date:
                          nullable: true
                          type: string
                        has_blocked_workflows:
                          type: boolean
                      required:
                        - id
                        - type
                        - value
                        - contact_summary
                        - extracted_attributes
                        - created_at
                        - updated_at
                        - interactions_count
                        - tags
                        - has_blocked_workflows
                      additionalProperties: false
                  next_cursor:
                    nullable: true
                    type: string
                  has_more:
                    type: boolean
                required:
                  - data
                  - next_cursor
                  - has_more
                additionalProperties: false
        '400':
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

Fuente original: https://docs.happyrobot.ai/api-reference/contacts/list-contacts
