---
title: "List audit remarks for a run"
description: "Returns all northstar audit remarks for a specific run, showing per-criterion pass/fail grades."
---

# List audit remarks for a run

> Returns all northstar audit remarks for a specific run, showing per-criterion pass/fail grades.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /runs/{run_id}/audits
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
  /runs/{run_id}/audits:
    get:
      tags:
        - Runs
      summary: List audit remarks for a run
      description: >-
        Returns all northstar audit remarks for a specific run, showing
        per-criterion pass/fail grades.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: run_id
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
                        northstar_name:
                          type: string
                        grade:
                          type: string
                          enum:
                            - passed
                            - failed
                            - not_applicable
                        correction:
                          nullable: true
                          type: string
                        correction_reason:
                          nullable: true
                          type: string
                        message_ids:
                          type: array
                          items:
                            type: string
                        status:
                          type: string
                          enum:
                            - open
                            - resolved
                            - dismissed
                      required:
                        - id
                        - northstar_name
                        - grade
                        - correction
                        - correction_reason
                        - message_ids
                        - status
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

Fuente original: https://docs.happyrobot.ai/api-reference/runs/list-audit-remarks-for-a-run
