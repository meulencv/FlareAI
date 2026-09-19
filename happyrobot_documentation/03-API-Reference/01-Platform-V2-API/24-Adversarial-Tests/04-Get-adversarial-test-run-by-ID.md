---
title: "Get adversarial test run by ID"
description: "Full status and audit remarks for a single test run."
---

# Get adversarial test run by ID

> Full status and audit remarks for a single test run.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /adversarial-tests/runs/{run_id}
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
  /adversarial-tests/runs/{run_id}:
    get:
      tags:
        - Adversarial Tests
      summary: Get adversarial test run by ID
      description: Full status and audit remarks for a single test run.
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
                  run:
                    type: object
                    properties:
                      id:
                        type: string
                      adversarial_test_id:
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
                      version_id:
                        nullable: true
                        type: string
                      version_name:
                        nullable: true
                        type: string
                      version_number:
                        nullable: true
                        type: number
                      created_at:
                        type: string
                    required:
                      - id
                      - adversarial_test_id
                      - status
                      - audit_remarks
                      - started_at
                      - completed_at
                      - created_at
                    additionalProperties: false
                required:
                  - run
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

Fuente original: https://docs.happyrobot.ai/api-reference/adversarial-tests/get-adversarial-test-run-by-id
