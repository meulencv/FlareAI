---
title: "Get Twin database schema"
---

# Get Twin database schema



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /twin/schema
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
  /twin/schema:
    get:
      tags:
        - Twin
      summary: Get Twin database schema
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    name:
                      type: string
                    kind:
                      type: string
                      enum:
                        - table
                        - view
                    columns:
                      type: array
                      items:
                        type: object
                        properties:
                          name:
                            type: string
                          type:
                            type: string
                          isPrimary:
                            type: boolean
                        required:
                          - name
                          - type
                          - isPrimary
                        additionalProperties: false
                  required:
                    - name
                    - kind
                    - columns
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

Fuente original: https://docs.happyrobot.ai/api-reference/twin/get-twin-database-schema
