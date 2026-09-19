---
title: "Get an adversarial suite by ID"
description: "Returns the suite and the mermaid workflow graph if already generated."
---

# Get an adversarial suite by ID

> Returns the suite and the mermaid workflow graph if already generated.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /adversarial-suites/{suite_id}
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
  /adversarial-suites/{suite_id}:
    get:
      tags:
        - Adversarial Suites
      summary: Get an adversarial suite by ID
      description: Returns the suite and the mermaid workflow graph if already generated.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: suite_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  suite:
                    type: object
                    properties:
                      id:
                        type: string
                      org_id:
                        type: string
                      workflow_id:
                        type: string
                      agent_node_id:
                        type: string
                      agent_node_persistent_id:
                        type: string
                      folder_id:
                        nullable: true
                        type: string
                      name:
                        type: string
                      is_deleted:
                        type: boolean
                      adversarial_model:
                        type: string
                      timeout_seconds:
                        type: number
                      generation_prompt:
                        type: string
                      generation_count:
                        type: number
                      generation_status:
                        type: string
                      generation_error:
                        nullable: true
                        type: string
                      scope_mode:
                        type: string
                        enum:
                          - all
                          - by_category
                      scoped_categories:
                        nullable: true
                        type: array
                        items:
                          type: string
                          enum:
                            - notes
                            - style
                            - contradiction
                            - tool
                            - sequential
                      created_by:
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
                      - agent_node_id
                      - agent_node_persistent_id
                      - name
                      - is_deleted
                      - adversarial_model
                      - timeout_seconds
                      - generation_prompt
                      - generation_count
                      - generation_status
                      - scope_mode
                      - scoped_categories
                      - created_by
                      - created_at
                      - updated_at
                    additionalProperties: false
                  workflow_graph_mermaid:
                    nullable: true
                    type: string
                required:
                  - suite
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

Fuente original: https://docs.happyrobot.ai/api-reference/adversarial-suites/get-an-adversarial-suite-by-id
