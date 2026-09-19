---
title: "Create a realtime client token"
description: "Generates a scoped JWT for browser-side realtime connections."
---

# Create a realtime client token

> Generates a scoped JWT for browser-side realtime connections.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /realtime/tokens
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
  /realtime/tokens:
    post:
      tags:
        - Realtime
      summary: Create a realtime client token
      description: Generates a scoped JWT for browser-side realtime connections.
      requestBody:
        content:
          application/json:
            schema:
              oneOf:
                - type: object
                  properties:
                    channel:
                      type: string
                      enum:
                        - runs_firehose
                    use_case_id:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  required:
                    - channel
                    - use_case_id
                - type: object
                  properties:
                    channel:
                      type: string
                      enum:
                        - run_detail
                    run_id:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  required:
                    - channel
                    - run_id
                - type: object
                  properties:
                    channel:
                      type: string
                      enum:
                        - conversations_org
                  required:
                    - channel
                - type: object
                  properties:
                    channel:
                      type: string
                      enum:
                        - conversation_group
                    group_id:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  required:
                    - channel
                    - group_id
                - type: object
                  properties:
                    channel:
                      type: string
                      enum:
                        - adversarial_test
                    test_run_id:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  required:
                    - channel
                    - test_run_id
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                  expires_at:
                    type: string
                    format: date-time
                    pattern: >-
                      ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
                required:
                  - token
                  - expires_at
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

Fuente original: https://docs.happyrobot.ai/api-reference/realtime/create-a-realtime-client-token
