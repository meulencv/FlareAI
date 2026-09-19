---
title: "Patch test suites members"
---

# Patch test suites members



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json patch /test-suites/{suite_id}/members
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
  /test-suites/{suite_id}/members:
    patch:
      tags:
        - Test Suites
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: suite_id
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                members:
                  type: array
                  items:
                    type: object
                    properties:
                      kind:
                        type: string
                        enum:
                          - custom
                          - e2e
                      id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    required:
                      - kind
                      - id
                detach:
                  default: false
                  type: boolean
              required:
                - members
        required: true
      responses:
        '200':
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

Fuente original: https://docs.happyrobot.ai/api-reference/test-suites/patch-test-suites-members
