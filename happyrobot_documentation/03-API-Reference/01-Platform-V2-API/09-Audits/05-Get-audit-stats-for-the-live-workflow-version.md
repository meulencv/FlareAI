---
title: "Get audit stats for the live workflow version"
description: "Returns aggregate audit statistics for the live (or most recently audited) version of a workflow."
---

# Get audit stats for the live workflow version

> Returns aggregate audit statistics for the live (or most recently audited) version of a workflow.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}/audits/stats
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
  /workflows/{workflow_id}/audits/stats:
    get:
      tags:
        - Audits
      summary: Get audit stats for the live workflow version
      description: >-
        Returns aggregate audit statistics for the live (or most recently
        audited) version of a workflow.
      parameters:
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
                  pass_rate_24h:
                    nullable: true
                    type: number
                  pass_count_24h:
                    type: number
                  total_count_24h:
                    type: number
                  average_run_score:
                    nullable: true
                    type: number
                  audited_run_count:
                    type: number
                  version_id:
                    nullable: true
                    type: string
                  version_number:
                    nullable: true
                    type: number
                  version_name:
                    nullable: true
                    type: string
                  is_live:
                    type: boolean
                required:
                  - pass_rate_24h
                  - pass_count_24h
                  - total_count_24h
                  - average_run_score
                  - audited_run_count
                  - version_id
                  - version_number
                  - version_name
                  - is_live
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

Fuente original: https://docs.happyrobot.ai/api-reference/audits/get-audit-stats-for-the-live-workflow-version
