---
title: "Create a Twin workflow dump table"
description: "Creates a Twin table plus a dump config that maps workflow run values into its columns. Unlike POST /twin/tables (a bare table), the server resolves the workflow's variable catalog and binds each column to a variable, so completed runs populate the table automatically. Captures every variable by def…"
---

# Create a Twin workflow dump table

> Creates a Twin table plus a dump config that maps workflow run values into its columns. Unlike POST /twin/tables (a bare table), the server resolves the workflow's variable catalog and binds each column to a variable, so completed runs populate the table automatically. Captures every variable by default; use `include` for a subset and `pk` to choose the primary key.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /twin/dump
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
  /twin/dump:
    post:
      tags:
        - Twin
      summary: Create a Twin workflow dump table
      description: >-
        Creates a Twin table plus a dump config that maps workflow run values
        into its columns. Unlike POST /twin/tables (a bare table), the server
        resolves the workflow's variable catalog and binds each column to a
        variable, so completed runs populate the table automatically. Captures
        every variable by default; use `include` for a subset and `pk` to choose
        the primary key.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                workflowId:
                  type: string
                  minLength: 1
                  description: Workflow (use case) UUID or slug to dump runs from
                tableName:
                  type: string
                  minLength: 1
                include:
                  description: >-
                    Subset of variables to capture (by name or
                    group_id.variable_id). Omit to capture every variable the
                    workflow produces.
                  type: array
                  items:
                    type: string
                    minLength: 1
                pk:
                  description: >-
                    Variable to use as the primary key (by name or
                    group_id.variable_id). Omit to add a synthetic run_id
                    primary key.
                  type: string
                  minLength: 1
              required:
                - workflowId
                - tableName
        required: true
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  success:
                    type: boolean
                    enum:
                      - true
                  config:
                    type: object
                    properties:
                      id:
                        type: string
                      org_id:
                        type: string
                      twin_instance_id:
                        type: string
                      use_case_id:
                        type: string
                      table_name:
                        type: string
                      column_mappings:
                        type: array
                        items:
                          type: object
                          properties:
                            name:
                              type: string
                            type:
                              type: string
                              enum:
                                - int8
                                - text
                                - boolean
                                - timestamp
                                - uuid
                                - jsonb
                                - float8
                            variableRef:
                              type: array
                              items:
                                description: >-
                                  !IMPORTANT: This schema describes one
                                  Paragraph object. When the containing field is
                                  an array of this schema, send a flat
                                  Paragraph[] array. Do not send a bare
                                  Paragraph object. Only send Paragraph[][] when
                                  the containing field is explicitly an array of
                                  arrays. Paragraph object schema: {type:
                                  'paragraph', children: Array<{text: string} |
                                  {type: 'variable', children: [{text: ''}],
                                  group_id: string, variable_id: string}>}
                            isPrimary:
                              type: boolean
                          required:
                            - name
                            - type
                            - variableRef
                            - isPrimary
                          additionalProperties: false
                      status:
                        type: string
                      created_at:
                        type: string
                        format: date-time
                      updated_at:
                        type: string
                        format: date-time
                    required:
                      - id
                      - org_id
                      - twin_instance_id
                      - use_case_id
                      - table_name
                      - column_mappings
                      - status
                      - created_at
                      - updated_at
                    additionalProperties: false
                required:
                  - success
                  - config
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

Fuente original: https://docs.happyrobot.ai/api-reference/twin/create-a-twin-workflow-dump-table
