---
title: "Extract custom eval from a run"
description: "Build a custom eval from an existing run. Auto-extracts messages, variables, and suggests a name."
---

# Extract custom eval from a run

> Build a custom eval from an existing run. Auto-extracts messages, variables, and suggests a name.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /nodes/{node_id}/custom-evals/extract-from-run
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
  /nodes/{node_id}/custom-evals/extract-from-run:
    post:
      tags:
        - Custom Evals
      summary: Extract custom eval from a run
      description: >-
        Build a custom eval from an existing run. Auto-extracts messages,
        variables, and suggests a name.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: node_id
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                run_id:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                message_id:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
              required:
                - run_id
                - message_id
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  messages:
                    type: array
                    items:
                      type: object
                      additionalProperties: {}
                  variables:
                    type: object
                    additionalProperties: {}
                  suggested_name:
                    type: string
                  source_run_id:
                    type: string
                  navigation_info:
                    type: object
                    properties:
                      prompt_node_id:
                        type: string
                      workflow_id:
                        type: string
                    required:
                      - prompt_node_id
                      - workflow_id
                    additionalProperties: false
                required:
                  - messages
                  - variables
                  - suggested_name
                  - source_run_id
                  - navigation_info
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

Fuente original: https://docs.happyrobot.ai/api-reference/custom-evals/extract-custom-eval-from-a-run
