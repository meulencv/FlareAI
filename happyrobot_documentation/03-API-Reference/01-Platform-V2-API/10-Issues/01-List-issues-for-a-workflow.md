---
title: "List issues for a workflow"
description: "Returns paginated quality issues (flags) for a workflow, optionally filtered by status or source."
---

# List issues for a workflow

> Returns paginated quality issues (flags) for a workflow, optionally filtered by status or source.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}/issues
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
  /workflows/{workflow_id}/issues:
    get:
      tags:
        - Issues
      summary: List issues for a workflow
      description: >-
        Returns paginated quality issues (flags) for a workflow, optionally
        filtered by status or source.
      parameters:
        - schema:
            default: 1
            type: integer
            minimum: 1
            maximum: 9007199254740991
          in: query
          name: page
          required: false
        - schema:
            default: 50
            type: integer
            minimum: 1
            maximum: 200
          in: query
          name: page_size
          required: false
        - schema:
            type: string
            enum:
              - open
              - approved
              - rejected
              - closed
          in: query
          name: status
          required: false
        - schema:
            type: string
            enum:
              - manual
              - auto
          in: query
          name: source
          required: false
        - schema:
            type: string
            minLength: 1
          in: path
          name: workflow_id
          required: true
          description: Workflow UUID or slug
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
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        run_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        session_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        message_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        type:
                          type: string
                        priority:
                          type: string
                        status:
                          type: string
                        source:
                          type: string
                        description:
                          nullable: true
                          type: string
                        correction:
                          nullable: true
                          type: string
                        correction_reason:
                          nullable: true
                          type: string
                        metric_key:
                          nullable: true
                          type: string
                        metric_value:
                          nullable: true
                          type: number
                        threshold_value:
                          nullable: true
                          type: number
                        version_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        created_at:
                          type: string
                        updated_at:
                          type: string
                      required:
                        - id
                        - run_id
                        - session_id
                        - message_id
                        - type
                        - priority
                        - status
                        - source
                        - description
                        - correction
                        - correction_reason
                        - metric_key
                        - metric_value
                        - threshold_value
                        - version_id
                        - created_at
                        - updated_at
                      additionalProperties: false
                  pagination:
                    type: object
                    properties:
                      page:
                        type: number
                      page_size:
                        type: number
                      total_pages:
                        type: number
                      total_records:
                        type: number
                      has_next_page:
                        type: boolean
                      has_previous_page:
                        type: boolean
                    required:
                      - page
                      - page_size
                      - total_pages
                      - total_records
                      - has_next_page
                      - has_previous_page
                    additionalProperties: false
                required:
                  - data
                  - pagination
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

Fuente original: https://docs.happyrobot.ai/api-reference/issues/list-issues-for-a-workflow
