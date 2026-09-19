---
title: "List version nodes"
description: "Returns all workflow nodes belonging to the specified version. The version can be identified by its UUID or slug."
---

# List version nodes

> Returns all workflow nodes belonging to the specified version. The version can be identified by its UUID or slug.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /versions/{version_id}/nodes
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
  /versions/{version_id}/nodes:
    get:
      tags:
        - Versions
      summary: List version nodes
      description: >-
        Returns all workflow nodes belonging to the specified version. The
        version can be identified by its UUID or slug.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: version_id
          required: true
          description: Version UUID or slug
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
                      oneOf:
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - action
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                            event_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                            integration_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                            trigger_interval:
                              nullable: true
                              type: string
                            multi_event_behavior:
                              nullable: true
                              type: string
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - prompt
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                            prompt:
                              nullable: true
                            prompt_md:
                              nullable: true
                              type: string
                            initial_message:
                              nullable: true
                            initial_message_uninterruptible:
                              type: boolean
                            initial_message_delay_ms:
                              type: integer
                              minimum: -9007199254740991
                              maximum: 9007199254740991
                            model:
                              nullable: true
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - tool
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                            function:
                              nullable: true
                              type: object
                              additionalProperties: {}
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - condition
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                            type_of_condition:
                              nullable: true
                              type: string
                            order:
                              nullable: true
                              type: number
                            conditions:
                              nullable: true
                              type: array
                              items: {}
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - module-change
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - path
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - loop
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - loop_break
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - loop_end
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                        - type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            persistent_id:
                              nullable: true
                              type: string
                            version_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            workflow_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            org_id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            parent_id:
                              nullable: true
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            type:
                              type: string
                              enum:
                                - cron
                            name:
                              nullable: true
                              type: string
                            sort_index:
                              nullable: true
                              type: number
                            is_complete:
                              nullable: true
                              type: boolean
                            configuration:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            node_output:
                              nullable: true
                              type: object
                              properties:
                                id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                node_id:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                type:
                                  nullable: true
                                  type: string
                                data:
                                  nullable: true
                                  type: object
                                  additionalProperties: {}
                                timestamp:
                                  type: string
                              required:
                                - id
                                - node_id
                                - timestamp
                              additionalProperties: false
                            timestamp:
                              type: string
                          required:
                            - id
                            - version_id
                            - workflow_id
                            - org_id
                            - type
                            - timestamp
                          additionalProperties: false
                required:
                  - data
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/list-version-nodes
