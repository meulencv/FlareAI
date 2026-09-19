---
title: "Get Twin table data"
---

# Get Twin table data



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /twin/tables/{tableName}
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
  /twin/tables/{tableName}:
    get:
      tags:
        - Twin
      summary: Get Twin table data
      parameters:
        - schema:
            default: 50
            type: integer
            minimum: 1
            maximum: 500
          in: query
          name: limit
          required: false
        - schema:
            default: 0
            type: integer
            minimum: 0
            maximum: 9007199254740991
          in: query
          name: offset
          required: false
        - schema:
            type: string
          in: path
          name: tableName
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  tableName:
                    type: string
                  kind:
                    type: string
                    enum:
                      - table
                      - view
                  rows:
                    type: array
                    items:
                      type: object
                      additionalProperties: {}
                  total:
                    type: number
                required:
                  - tableName
                  - kind
                  - rows
                  - total
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

Fuente original: https://docs.happyrobot.ai/api-reference/twin/get-twin-table-data
