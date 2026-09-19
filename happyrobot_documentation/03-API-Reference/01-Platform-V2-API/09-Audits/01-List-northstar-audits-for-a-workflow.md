---
title: "List northstar audits for a workflow"
description: "Returns paginated northstar audit results for a workflow, showing pass/fail rates per behavioral criterion."
---

# List northstar audits for a workflow

> Returns paginated northstar audit results for a workflow, showing pass/fail rates per behavioral criterion.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}/audits/northstars
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
  /workflows/{workflow_id}/audits/northstars:
    get:
      tags:
        - Audits
      summary: List northstar audits for a workflow
      description: >-
        Returns paginated northstar audit results for a workflow, showing
        pass/fail rates per behavioral criterion.
      parameters:
        - schema:
            type: string
          in: query
          name: from_date
          required: false
        - schema:
            type: string
          in: query
          name: to_date
          required: false
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
          in: query
          name: enabled
          required: false
        - schema:
            type: string
          in: query
          name: search
          required: false
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
                        northstar_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        northstar_name:
                          type: string
                        description:
                          type: array
                          items:
                            type: object
                            additionalProperties: {}
                        category:
                          nullable: true
                          type: string
                        use_case_name:
                          type: string
                        use_case_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        workflow_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        pass_count:
                          type: number
                        fail_count:
                          type: number
                        na_count:
                          type: number
                        total_count:
                          type: number
                        pass_rate:
                          nullable: true
                          type: number
                        latest_failure:
                          nullable: true
                          type: string
                        latest_occurrence:
                          type: string
                        enabled:
                          type: boolean
                        version_id:
                          type: string
                        version_number:
                          nullable: true
                          type: number
                        version_name:
                          nullable: true
                          type: string
                      required:
                        - northstar_id
                        - northstar_name
                        - description
                        - category
                        - use_case_name
                        - use_case_id
                        - workflow_id
                        - pass_count
                        - fail_count
                        - na_count
                        - total_count
                        - pass_rate
                        - latest_failure
                        - latest_occurrence
                        - enabled
                        - version_id
                        - version_number
                        - version_name
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

Fuente original: https://docs.happyrobot.ai/api-reference/audits/list-northstar-audits-for-a-workflow
