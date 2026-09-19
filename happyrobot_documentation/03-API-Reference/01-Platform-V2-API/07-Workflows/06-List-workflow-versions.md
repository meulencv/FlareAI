---
title: "List workflow versions"
description: "Returns paginated versions for a workflow. Supports searching by version number or version name."
---

# List workflow versions

> Returns paginated versions for a workflow. Supports searching by version number or version name.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}/versions
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
  /workflows/{workflow_id}/versions:
    get:
      tags:
        - Workflows
      summary: List workflow versions
      description: >-
        Returns paginated versions for a workflow. Supports searching by version
        number or version name.
      parameters:
        - schema:
            default: 1
            type: integer
            minimum: 1
            maximum: 9007199254740991
          in: query
          name: page
          required: false
        - schema:
            default: 50
            type: integer
            minimum: 1
            maximum: 100
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
          in: query
          name: search
          required: false
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
                  data:
                    type: array
                    items:
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
                            Workflow engine version for this version: 2 =
                            legacy, 3 = explicit-edges engine
                            (loop/path/loop_break nodes available).
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
                  pagination:
                    type: object
                    properties:
                      page:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      page_size:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      total_pages:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      total_records:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      has_next_page:
                        type: boolean
                      has_previous_page:
                        type: boolean
                    required:
                      - page
                      - page_size
                      - total_pages
                      - total_records
                      - has_next_page
                      - has_previous_page
                    additionalProperties: false
                required:
                  - data
                  - pagination
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/list-workflow-versions
