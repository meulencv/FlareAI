---
title: "Execute SQL on Twin database"
---

# Execute SQL on Twin database



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /twin/sql
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
  /twin/sql:
    post:
      tags:
        - Twin
      summary: Execute SQL on Twin database
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                sql:
                  type: string
              required:
                - sql
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  command:
                    type: string
                  rowCount:
                    nullable: true
                    type: number
                  fields:
                    type: array
                    items:
                      type: object
                      properties:
                        name:
                          type: string
                        dataTypeId:
                          type: number
                      required:
                        - name
                        - dataTypeId
                      additionalProperties: false
                  rows:
                    type: array
                    items:
                      type: object
                      additionalProperties: {}
                  truncated:
                    type: boolean
                  truncationReason:
                    nullable: true
                    type: string
                    enum:
                      - row_cap
                      - response_size_cap
                  limits:
                    type: object
                    properties:
                      maxRows:
                        type: number
                      maxResponseBytes:
                        type: number
                    required:
                      - maxRows
                      - maxResponseBytes
                    additionalProperties: false
                  returnedRows:
                    type: number
                  schemaCacheReloadAttempted:
                    type: boolean
                  schemaCacheReloaded:
                    type: boolean
                required:
                  - command
                  - rowCount
                  - fields
                  - rows
                  - truncated
                  - truncationReason
                  - limits
                  - returnedRows
                  - schemaCacheReloadAttempted
                  - schemaCacheReloaded
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

Fuente original: https://docs.happyrobot.ai/api-reference/twin/execute-sql-on-twin-database
