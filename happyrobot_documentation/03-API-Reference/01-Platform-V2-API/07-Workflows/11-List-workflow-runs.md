---
title: "List workflow runs"
description: "Returns paginated runs for a workflow. Supports filtering by status, date ranges, and annotation."
---

# List workflow runs

> Returns paginated runs for a workflow. Supports filtering by status, date ranges, and annotation.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}/runs
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
  /workflows/{workflow_id}/runs:
    get:
      tags:
        - Workflows
      summary: List workflow runs
      description: >-
        Returns paginated runs for a workflow. Supports filtering by status,
        date ranges, and annotation.
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
            default: 100
            type: integer
            minimum: 1
            maximum: 2000
          in: query
          name: page_size
          required: false
        - schema:
            default: desc
            type: string
            enum:
              - asc
              - desc
          in: query
          name: sort
          required: false
        - schema:
            type: string
            enum:
              - scheduled
              - running
              - completed
              - canceled
              - failed
          in: query
          name: status
          required: false
        - schema:
            anyOf:
              - type: string
                format: date-time
                pattern: >-
                  ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
              - type: string
                enum:
                  - ''
          in: query
          name: start_date
          required: false
        - schema:
            anyOf:
              - type: string
                format: date-time
                pattern: >-
                  ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
              - type: string
                enum:
                  - ''
          in: query
          name: end_date
          required: false
        - schema:
            anyOf:
              - type: string
                format: date-time
                pattern: >-
                  ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
              - type: string
                enum:
                  - ''
          in: query
          name: completed_start_date
          required: false
        - schema:
            anyOf:
              - type: string
                format: date-time
                pattern: >-
                  ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
              - type: string
                enum:
                  - ''
          in: query
          name: completed_end_date
          required: false
        - schema:
            type: string
            enum:
              - correct
              - incorrect
              - critical
          in: query
          name: annotation
          required: false
        - schema:
            type: string
            enum:
              - 'true'
              - 'false'
          in: query
          name: is_e2e_test
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
                        status:
                          type: string
                          enum:
                            - not_started
                            - scheduled
                            - running
                            - skipped
                            - succeeded
                            - completed
                            - canceled
                            - failed
                        org_id:
                          type: string
                        timestamp:
                          type: string
                        use_case_id:
                          type: string
                        version_id:
                          type: string
                        execution_environment:
                          nullable: true
                          type: string
                          enum:
                            - staging
                            - production
                            - development
                        annotation:
                          nullable: true
                          type: string
                          enum:
                            - correct
                            - incorrect
                            - critical
                        completed_at:
                          nullable: true
                          type: string
                        input_tokens:
                          nullable: true
                          type: integer
                          minimum: -9007199254740991
                          maximum: 9007199254740991
                        output_tokens:
                          nullable: true
                          type: integer
                          minimum: -9007199254740991
                          maximum: 9007199254740991
                        is_e2e_test:
                          type: boolean
                        data:
                          type: object
                          additionalProperties: {}
                      required:
                        - id
                        - status
                        - org_id
                        - timestamp
                        - use_case_id
                        - version_id
                        - execution_environment
                        - annotation
                        - completed_at
                        - input_tokens
                        - output_tokens
                        - is_e2e_test
                        - data
                      additionalProperties: false
                  pagination:
                    type: object
                    properties:
                      page:
                        type: integer
                        minimum: 1
                        maximum: 9007199254740991
                      pageSize:
                        type: integer
                        minimum: 1
                        maximum: 9007199254740991
                      totalPages:
                        type: integer
                        minimum: 0
                        maximum: 9007199254740991
                      totalRecords:
                        type: integer
                        minimum: 0
                        maximum: 9007199254740991
                      hasNextPage:
                        type: boolean
                      hasPreviousPage:
                        type: boolean
                    required:
                      - page
                      - pageSize
                      - totalPages
                      - totalRecords
                      - hasNextPage
                      - hasPreviousPage
                    additionalProperties: false
                required:
                  - data
                  - pagination
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/list-workflow-runs
