---
title: "Create a Twin table"
---

# Create a Twin table



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /twin/tables
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
  /twin/tables:
    post:
      tags:
        - Twin
      summary: Create a Twin table
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                tableName:
                  type: string
                columns:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      type:
                        type: string
                        enum:
                          - int8
                          - text
                          - boolean
                          - timestamp
                          - uuid
                          - jsonb
                          - float8
                      defaultValue:
                        nullable: true
                        type: string
                      isPrimary:
                        type: boolean
                      isNullable:
                        type: boolean
                      primaryKeyGeneration:
                        type: string
                        enum:
                          - auto
                          - manual
                    required:
                      - name
                      - type
                      - defaultValue
                      - isPrimary
              required:
                - tableName
                - columns
        required: true
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                required:
                  - success
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

Fuente original: https://docs.happyrobot.ai/api-reference/twin/create-a-twin-table
