---
title: "Get run"
description: "Returns metadata for a single run. Use /runs/:run_id/nodes for node summaries, /runs/:run_id/outputs/:output_id for a full node output payload, /runs/:run_id/sessions for session data, and /runs/:run_id/flags for issues."
---

# Get run

> Returns metadata for a single run. Use /runs/:run_id/nodes for node summaries, /runs/:run_id/outputs/:output_id for a full node output payload, /runs/:run_id/sessions for session data, and /runs/:run_id/flags for issues.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /runs/{run_id}
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
  /runs/{run_id}:
    get:
      tags:
        - Runs
      summary: Get run
      description: >-
        Returns metadata for a single run. Use /runs/:run_id/nodes for node
        summaries, /runs/:run_id/outputs/:output_id for a full node output
        payload, /runs/:run_id/sessions for session data, and
        /runs/:run_id/flags for issues.
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
                  id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  org_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  workflow_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  version_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
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
                  annotation:
                    nullable: true
                    type: string
                    enum:
                      - correct
                      - incorrect
                      - critical
                  timestamp:
                    type: string
                  completed_at:
                    nullable: true
                    type: string
                  execution_environment:
                    nullable: true
                    type: string
                  is_e2e_test:
                    type: boolean
                required:
                  - id
                  - org_id
                  - workflow_id
                  - version_id
                  - status
                  - annotation
                  - timestamp
                  - completed_at
                  - execution_environment
                  - is_e2e_test
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

Fuente original: https://docs.happyrobot.ai/api-reference/runs/get-run
