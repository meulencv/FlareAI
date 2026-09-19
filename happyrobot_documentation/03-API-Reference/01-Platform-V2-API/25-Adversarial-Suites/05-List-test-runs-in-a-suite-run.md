---
title: "List test runs in a suite run"
description: "All individual adversarial test results within this suite run."
---

# List test runs in a suite run

> All individual adversarial test results within this suite run.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /adversarial-suites/runs/{suite_run_id}/test-runs
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
  /adversarial-suites/runs/{suite_run_id}/test-runs:
    get:
      tags:
        - Adversarial Suites
      summary: List test runs in a suite run
      description: All individual adversarial test results within this suite run.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: suite_run_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  test_runs:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        test_name:
                          type: string
                        status:
                          type: string
                        audit_remarks:
                          type: array
                          items:
                            type: object
                            properties:
                              northstar_id:
                                type: string
                              grade:
                                type: string
                                enum:
                                  - passed
                                  - failed
                                  - not_applicable
                              correction:
                                type: string
                              correction_reason:
                                type: string
                              model:
                                type: string
                            required:
                              - northstar_id
                              - grade
                              - correction_reason
                              - model
                            additionalProperties: false
                        started_at:
                          nullable: true
                          type: string
                        completed_at:
                          nullable: true
                          type: string
                        created_at:
                          type: string
                      required:
                        - id
                        - test_name
                        - status
                        - audit_remarks
                        - started_at
                        - completed_at
                        - created_at
                      additionalProperties: false
                required:
                  - test_runs
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

Fuente original: https://docs.happyrobot.ai/api-reference/adversarial-suites/list-test-runs-in-a-suite-run
