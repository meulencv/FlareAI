---
title: "Cancel active workflow runs"
description: "Cancels all current and queued runs for the workflow. By default, the currently live workflow version is also unpublished. Set unpublish_workflow to false to keep the workflow published after cancellation. Accepts a workflow UUID or slug as the path parameter."
---

# Cancel active workflow runs

> Cancels all current and queued runs for the workflow. By default, the currently live workflow version is also unpublished. Set unpublish_workflow to false to keep the workflow published after cancellation. Accepts a workflow UUID or slug as the path parameter.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /workflows/{workflow_id}/cancel-runs
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
  /workflows/{workflow_id}/cancel-runs:
    post:
      tags:
        - Workflows
      summary: Cancel active workflow runs
      description: >-
        Cancels all current and queued runs for the workflow. By default, the
        currently live workflow version is also unpublished. Set
        unpublish_workflow to false to keep the workflow published after
        cancellation. Accepts a workflow UUID or slug as the path parameter.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: workflow_id
          required: true
          description: Workflow UUID or slug
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                unpublish_workflow:
                  type: boolean
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  workflow_toggle_result:
                    nullable: true
                    type: object
                    properties:
                      success:
                        type: boolean
                      unpublished_version_id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                      message:
                        type: string
                      error:
                        type: string
                    required:
                      - success
                    additionalProperties: false
                required:
                  - status
                  - workflow_toggle_result
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
        '403':
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
        '502':
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/cancel-active-workflow-runs
