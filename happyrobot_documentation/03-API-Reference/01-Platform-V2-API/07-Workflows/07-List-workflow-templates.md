---
title: "List workflow templates"
description: "Returns a paginated list of available workflow templates. Each template includes a description and the inputs it accepts (marked as required or optional). Use a template's name in the `from_template.template` field when creating a workflow."
---

# List workflow templates

> Returns a paginated list of available workflow templates. Each template includes a description and the inputs it accepts (marked as required or optional). Use a template's name in the `from_template.template` field when creating a workflow.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /workflows/templates
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
  /workflows/templates:
    get:
      tags:
        - Workflows
      summary: List workflow templates
      description: >-
        Returns a paginated list of available workflow templates. Each template
        includes a description and the inputs it accepts (marked as required or
        optional). Use a template's name in the `from_template.template` field
        when creating a workflow.
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
            type: string
          in: query
          name: search
          required: false
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
                        template:
                          type: string
                        description:
                          type: string
                        inputs:
                          type: array
                          items:
                            type: object
                            properties:
                              name:
                                type: string
                              type:
                                type: string
                              required:
                                type: boolean
                              description:
                                type: string
                              options:
                                type: array
                                items:
                                  type: string
                              default:
                                type: string
                            required:
                              - name
                              - type
                              - required
                              - description
                            additionalProperties: false
                      required:
                        - template
                        - description
                        - inputs
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/list-workflow-templates
