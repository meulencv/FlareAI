---
title: "Get a workflow"
description: "Returns a single workflow by UUID or slug, including its latest version info (live production version preferred, otherwise most recent)."
---

# Get a workflow

> Returns a single workflow by UUID or slug, including its latest version info (live production version preferred, otherwise most recent).



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}
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
  /workflows/{workflow_id}:
    get:
      tags:
        - Workflows
      summary: Get a workflow
      description: >-
        Returns a single workflow by UUID or slug, including its latest version
        info (live production version preferred, otherwise most recent).
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
                  name:
                    type: string
                  slug:
                    type: string
                  icon:
                    nullable: true
                    type: string
                  folder_id:
                    nullable: true
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  tag_ids:
                    type: array
                    items:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  data_retention_days:
                    nullable: true
                    type: number
                  timestamp:
                    type: string
                  latest_version:
                    nullable: true
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                      slug:
                        type: string
                      version_number:
                        nullable: true
                        type: number
                      is_published:
                        type: boolean
                      is_live:
                        type: boolean
                      environment:
                        type: string
                      workflow_version:
                        description: >-
                          Workflow engine version for this version: 2 = legacy,
                          3 = explicit-edges engine (loop/path/loop_break nodes
                          available).
                        type: number
                      published_at:
                        nullable: true
                        type: string
                      timestamp:
                        type: string
                    required:
                      - id
                      - name
                      - slug
                      - is_published
                      - is_live
                      - timestamp
                    additionalProperties: false
                  live_version:
                    nullable: true
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                      slug:
                        type: string
                      version_number:
                        nullable: true
                        type: number
                      is_published:
                        type: boolean
                      is_live:
                        type: boolean
                      environment:
                        type: string
                      workflow_version:
                        description: >-
                          Workflow engine version for this version: 2 = legacy,
                          3 = explicit-edges engine (loop/path/loop_break nodes
                          available).
                        type: number
                      published_at:
                        nullable: true
                        type: string
                      timestamp:
                        type: string
                    required:
                      - id
                      - name
                      - slug
                      - is_published
                      - is_live
                      - timestamp
                    additionalProperties: false
                required:
                  - id
                  - org_id
                  - name
                  - slug
                  - tag_ids
                  - timestamp
                  - latest_version
                  - live_version
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/get-a-workflow
