---
title: "List adversarial tests for a node"
---

# List adversarial tests for a node



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /nodes/{node_id}/adversarial-tests
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
  /nodes/{node_id}/adversarial-tests:
    get:
      tags:
        - Adversarial Tests
      summary: List adversarial tests for a node
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: query
          name: version_id
          required: false
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: node_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
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
                        suite_id:
                          nullable: true
                          type: string
                        folder_id:
                          nullable: true
                          type: string
                        name:
                          type: string
                        description:
                          nullable: true
                          type: string
                        is_deleted:
                          type: boolean
                        adversarial_prompt:
                          type: string
                        adversarial_model:
                          type: string
                        variables:
                          type: object
                          additionalProperties: {}
                        template_variables:
                          nullable: true
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        graph_path:
                          nullable: true
                          type: array
                          items:
                            type: string
                        timeout_seconds:
                          type: number
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
                        - description
                        - is_deleted
                        - adversarial_prompt
                        - adversarial_model
                        - variables
                        - timeout_seconds
                        - scope_mode
                        - scoped_categories
                        - created_by
                        - created_at
                        - updated_at
                      additionalProperties: false
                  folders:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        name:
                          type: string
                      required:
                        - id
                        - name
                      additionalProperties: false
                required:
                  - data
                  - folders
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

Fuente original: https://docs.happyrobot.ai/api-reference/adversarial-tests/list-adversarial-tests-for-a-node
