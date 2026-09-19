---
title: "Create a northstar for a prompt node"
description: "Create a new northstar evaluation criterion for this prompt node."
---

# Create a northstar for a prompt node

> Create a new northstar evaluation criterion for this prompt node.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /nodes/{node_id}/northstars
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
    post:
      tags:
        - Northstars
      summary: Create a northstar for a prompt node
      description: Create a new northstar evaluation criterion for this prompt node.
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
                name:
                  type: string
                  minLength: 1
                description:
                  type: array
                  items:
                    type: object
                    additionalProperties: {}
                category:
                  type: string
                  enum:
                    - notes
                    - style
                    - tool
                    - sequential
                version_id:
                  type: string
                  minLength: 1
                  description: Version UUID or slug
                priority:
                  type: string
                  enum:
                    - low
                    - medium
                    - high
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
                category_config:
                  type: object
                  properties:
                    current_stage:
                      type: string
                      minLength: 1
                    prerequisite_stage:
                      type: string
                      minLength: 1
                  required:
                    - current_stage
                    - prerequisite_stage
                folder_id:
                  nullable: true
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
              required:
                - name
                - description
                - category
                - version_id
        required: true
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  northstar:
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
                required:
                  - northstar
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

Fuente original: https://docs.happyrobot.ai/api-reference/northstars/create-a-northstar-for-a-prompt-node
