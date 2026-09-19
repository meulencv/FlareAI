---
title: "Get adversarial suite run by ID"
description: "Full status and aggregate counts for a suite run."
---

# Get adversarial suite run by ID

> Full status and aggregate counts for a suite run.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /adversarial-suites/runs/{suite_run_id}
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
  /adversarial-suites/runs/{suite_run_id}:
    get:
      tags:
        - Adversarial Suites
      summary: Get adversarial suite run by ID
      description: Full status and aggregate counts for a suite run.
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
                  run:
                    type: object
                    properties:
                      id:
                        type: string
                      suite_id:
                        type: string
                      status:
                        type: string
                      total_tests:
                        type: number
                      completed_tests:
                        type: number
                      passed_tests:
                        type: number
                      failed_tests:
                        type: number
                      workflow_id:
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
                      - suite_id
                      - status
                      - total_tests
                      - completed_tests
                      - passed_tests
                      - failed_tests
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

Fuente original: https://docs.happyrobot.ai/api-reference/adversarial-suites/get-adversarial-suite-run-by-id
