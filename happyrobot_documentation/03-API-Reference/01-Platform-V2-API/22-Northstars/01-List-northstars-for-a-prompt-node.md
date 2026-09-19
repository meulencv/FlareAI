---
title: "List northstars for a prompt node"
description: "Returns all northstars for a prompt node along with AI generation and coverage assessment statuses."
---

# List northstars for a prompt node

> Returns all northstars for a prompt node along with AI generation and coverage assessment statuses.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /nodes/{node_id}/northstars
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
  /nodes/{node_id}/northstars:
    get:
      tags:
        - Northstars
      summary: List northstars for a prompt node
      description: >-
        Returns all northstars for a prompt node along with AI generation and
        coverage assessment statuses.
      parameters:
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
                        name:
                          type: string
                        description:
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        category:
                          type: string
                        category_config:
                          nullable: true
                        enabled:
                          type: boolean
                        priority:
                          type: string
                        positive_examples:
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        negative_examples:
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        node_ids:
                          nullable: true
                          type: array
                          items:
                            type: string
                        agent_id:
                          nullable: true
                          type: string
                        org_id:
                          type: string
                        workflow_id:
                          nullable: true
                          type: string
                        version_id:
                          nullable: true
                          type: string
                        prompt_node_id:
                          nullable: true
                          type: string
                        prompt_component_id:
                          nullable: true
                          type: string
                        folder_id:
                          nullable: true
                          type: string
                        regenerated_from_northstar_id:
                          nullable: true
                          type: string
                        is_deleted:
                          type: boolean
                        created_at:
                          type: string
                        updated_at:
                          type: string
                        user_feedback:
                          nullable: true
                          type: object
                          properties:
                            id:
                              type: string
                            northstar_id:
                              type: string
                            correctness:
                              type: number
                            feedback:
                              nullable: true
                              type: string
                            created_at:
                              type: string
                            created_by:
                              nullable: true
                              type: string
                            created_by_api_key:
                              nullable: true
                              type: string
                          required:
                            - id
                            - northstar_id
                            - correctness
                            - created_at
                          additionalProperties: false
                      required:
                        - id
                        - name
                        - description
                        - category
                        - category_config
                        - enabled
                        - priority
                        - positive_examples
                        - negative_examples
                        - node_ids
                        - agent_id
                        - org_id
                        - workflow_id
                        - version_id
                        - prompt_node_id
                        - prompt_component_id
                        - folder_id
                        - regenerated_from_northstar_id
                        - is_deleted
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
                  generation_status:
                    nullable: true
                    type: string
                    enum:
                      - in_progress
                      - completed
                      - error
                  coverage_assessment_status:
                    nullable: true
                    type: string
                    enum:
                      - in_progress
                      - completed
                      - error
                required:
                  - data
                  - folders
                  - generation_status
                  - coverage_assessment_status
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

Fuente original: https://docs.happyrobot.ai/api-reference/northstars/list-northstars-for-a-prompt-node
