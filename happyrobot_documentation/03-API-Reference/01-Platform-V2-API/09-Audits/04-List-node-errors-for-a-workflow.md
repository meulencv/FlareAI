---
title: "List node errors for a workflow"
description: "Returns paginated node execution errors for a workflow, grouped by node and error type."
---

# List node errors for a workflow

> Returns paginated node execution errors for a workflow, grouped by node and error type.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/{workflow_id}/audits/node-errors
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
  /workflows/{workflow_id}/audits/node-errors:
    get:
      tags:
        - Audits
      summary: List node errors for a workflow
      description: >-
        Returns paginated node execution errors for a workflow, grouped by node
        and error type.
      parameters:
        - schema:
            type: string
          in: query
          name: from_date
          required: false
        - schema:
            type: string
          in: query
          name: to_date
          required: false
        - schema:
            type: string
          in: query
          name: search
          required: false
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
            maximum: 200
          in: query
          name: page_size
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
                        node_id:
                          type: string
                        persistent_node_id:
                          type: string
                        error:
                          type: string
                        node_name:
                          type: string
                        use_case_name:
                          type: string
                        count:
                          type: number
                        latest_timestamp:
                          type: string
                        earliest_timestamp:
                          type: string
                      required:
                        - node_id
                        - persistent_node_id
                        - error
                        - node_name
                        - use_case_name
                        - count
                        - latest_timestamp
                        - earliest_timestamp
                      additionalProperties: false
                  pagination:
                    type: object
                    properties:
                      page:
                        type: number
                      page_size:
                        type: number
                      total_pages:
                        type: number
                      total_records:
                        type: number
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

Fuente original: https://docs.happyrobot.ai/api-reference/audits/list-node-errors-for-a-workflow
