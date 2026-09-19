---
title: "Add a custom signal key to node"
description: "Appends a custom signal key to the target node configuration in all environments."
---

# Add a custom signal key to node

> Appends a custom signal key to the target node configuration in all environments.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /signals/keys
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
  /signals/keys:
    post:
      tags:
        - Signals
      summary: Add a custom signal key to node
      description: >-
        Appends a custom signal key to the target node configuration in all
        environments.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                node_id:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                key:
                  type: string
                  minLength: 1
                  maxLength: 256
                  pattern: ^[a-zA-Z0-9_\-.*#]+(?:\.[a-zA-Z0-9_\-.*#]+)*$
              required:
                - node_id
                - key
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  node_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  keys:
                    type: array
                    items:
                      type: string
                required:
                  - node_id
                  - keys
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
        '502':
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

Fuente original: https://docs.happyrobot.ai/api-reference/signals/add-a-custom-signal-key-to-node
