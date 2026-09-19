---
title: "[Legacy] List runs"
description: "Lists runs for a use case. **Deprecated**: prefer GET /workflows/:workflow_id/runs instead."
---

# [Legacy] List runs

> Lists runs for a use case. **Deprecated**: prefer GET /workflows/:workflow_id/runs instead.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /runs/
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
  /runs/:
    get:
      tags:
        - Runs
      summary: '[Legacy] List runs'
      description: >-
        Lists runs for a use case. **Deprecated**: prefer GET
        /workflows/:workflow_id/runs instead.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: query
          name: use_case_id
          required: true
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
                            - scheduled
                            - running
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
      deprecated: true
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

Fuente original: https://docs.happyrobot.ai/api-reference/runs/[legacy]-list-runs
