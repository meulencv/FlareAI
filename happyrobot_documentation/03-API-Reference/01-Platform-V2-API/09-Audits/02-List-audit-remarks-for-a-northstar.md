---
title: "List audit remarks for a northstar"
description: "Returns cursor-paginated audit remarks for a specific northstar criterion, optionally filtered by grade."
---

# List audit remarks for a northstar

> Returns cursor-paginated audit remarks for a specific northstar criterion, optionally filtered by grade.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}/audits/northstars/{northstar_id}/remarks
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
  /workflows/{workflow_id}/audits/northstars/{northstar_id}/remarks:
    get:
      tags:
        - Audits
      summary: List audit remarks for a northstar
      description: >-
        Returns cursor-paginated audit remarks for a specific northstar
        criterion, optionally filtered by grade.
      parameters:
        - schema:
            type: string
            enum:
              - passed
              - failed
              - not_applicable
          in: query
          name: grade
          required: false
        - schema:
            type: string
          in: query
          name: cursor
          required: false
        - schema:
            default: 25
            type: integer
            minimum: 1
            maximum: 100
          in: query
          name: limit
          required: false
        - schema:
            type: string
            minLength: 1
          in: path
          name: workflow_id
          required: true
          description: Workflow UUID or slug
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: northstar_id
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
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        run_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        timestamp:
                          type: string
                        run_url:
                          type: string
                        grade:
                          type: string
                          enum:
                            - passed
                            - failed
                            - not_applicable
                        passed:
                          nullable: true
                          type: boolean
                        message_ids:
                          type: array
                          items:
                            type: string
                        correction:
                          nullable: true
                          type: string
                        correction_reason:
                          nullable: true
                          type: string
                        org_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        is_e2e_test:
                          type: boolean
                        user_feedback:
                          nullable: true
                          type: object
                          properties:
                            polarity:
                              type: boolean
                            issue_attribution:
                              nullable: true
                              type: string
                          required:
                            - polarity
                            - issue_attribution
                          additionalProperties: false
                      required:
                        - id
                        - run_id
                        - timestamp
                        - run_url
                        - grade
                        - message_ids
                        - correction
                        - correction_reason
                        - org_id
                        - is_e2e_test
                      additionalProperties: false
                  next_cursor:
                    nullable: true
                    type: string
                  total:
                    type: number
                required:
                  - data
                  - next_cursor
                  - total
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

Fuente original: https://docs.happyrobot.ai/api-reference/audits/list-audit-remarks-for-a-northstar
