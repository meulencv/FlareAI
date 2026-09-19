---
title: "List custom eval runs"
---

# List custom eval runs



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /custom-evals/{eval_id}/runs
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
  /custom-evals/{eval_id}/runs:
    get:
      tags:
        - Custom Evals
      summary: List custom eval runs
      parameters:
        - schema:
            default: 20
            type: integer
            exclusiveMinimum: true
            maximum: 100
          in: query
          name: limit
          required: false
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: eval_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  runs:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        custom_test_id:
                          type: string
                        input_messages:
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        output_messages:
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        actual_tool_calls:
                          nullable: true
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        passed:
                          nullable: true
                          type: boolean
                        judge_reasoning:
                          nullable: true
                          type: string
                        tool_calls_matched:
                          nullable: true
                          type: boolean
                        version_id:
                          nullable: true
                          type: string
                        version_name:
                          nullable: true
                          type: string
                        version_number:
                          nullable: true
                          type: number
                        created_at:
                          type: string
                      required:
                        - id
                        - custom_test_id
                        - input_messages
                        - output_messages
                        - actual_tool_calls
                        - passed
                        - version_id
                        - created_at
                      additionalProperties: false
                required:
                  - runs
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

Fuente original: https://docs.happyrobot.ai/api-reference/custom-evals/list-custom-eval-runs
