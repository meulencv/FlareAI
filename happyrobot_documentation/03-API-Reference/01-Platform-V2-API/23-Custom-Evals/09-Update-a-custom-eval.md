---
title: "Update a custom eval"
---

# Update a custom eval



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json patch /custom-evals/{eval_id}
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
  /custom-evals/{eval_id}:
    patch:
      tags:
        - Custom Evals
      summary: Update a custom eval
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: eval_id
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  minLength: 1
                description:
                  type: string
                test_messages:
                  type: array
                  items:
                    type: object
                    properties:
                      role:
                        type: string
                        enum:
                          - user
                          - assistant
                          - tool
                      content:
                        type: string
                      turn_index:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      tool_calls:
                        type: array
                        items:
                          type: object
                          properties:
                            function:
                              type: object
                              properties:
                                name:
                                  type: string
                                arguments:
                                  type: string
                              required:
                                - name
                                - arguments
                            id:
                              type: string
                          required:
                            - function
                      tool_call_id:
                        type: string
                    required:
                      - role
                      - content
                      - turn_index
                expected_response:
                  type: string
                judge_model:
                  nullable: true
                  type: string
                expected_tool_calls:
                  type: array
                  items:
                    type: object
                    properties:
                      name:
                        type: string
                      args_description:
                        type: object
                        additionalProperties:
                          type: string
                    required:
                      - name
                variables:
                  type: object
                  additionalProperties: {}
                eval_mode:
                  type: string
                  enum:
                    - custom
                    - northstar
                northstar_ids:
                  type: array
                  items:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                folder_id:
                  nullable: true
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  test:
                    type: object
                    properties:
                      id:
                        type: string
                      org_id:
                        type: string
                      workflow_id:
                        nullable: true
                        type: string
                      prompt_node_id:
                        type: string
                      prompt_node_persistent_id:
                        nullable: true
                        type: string
                      name:
                        type: string
                      description:
                        nullable: true
                        type: string
                      test_messages:
                        type: array
                        items:
                          type: object
                          additionalProperties: {}
                      expected_response:
                        nullable: true
                        type: string
                      judge_model:
                        nullable: true
                        type: string
                      expected_tool_calls:
                        nullable: true
                        type: array
                        items:
                          type: object
                          additionalProperties: {}
                      variables:
                        type: object
                        additionalProperties: {}
                      source_run_id:
                        nullable: true
                        type: string
                      is_deleted:
                        type: boolean
                      eval_mode:
                        type: string
                      examples:
                        type: array
                        items:
                          type: object
                          additionalProperties: {}
                      northstar_ids:
                        type: array
                        items:
                          type: string
                      folder_id:
                        nullable: true
                        type: string
                      created_at:
                        type: string
                      updated_at:
                        type: string
                    required:
                      - id
                      - org_id
                      - workflow_id
                      - prompt_node_id
                      - prompt_node_persistent_id
                      - name
                      - description
                      - test_messages
                      - expected_response
                      - judge_model
                      - expected_tool_calls
                      - variables
                      - source_run_id
                      - is_deleted
                      - eval_mode
                      - examples
                      - northstar_ids
                      - folder_id
                      - created_at
                      - updated_at
                    additionalProperties: false
                required:
                  - test
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

Fuente original: https://docs.happyrobot.ai/api-reference/custom-evals/update-a-custom-eval
