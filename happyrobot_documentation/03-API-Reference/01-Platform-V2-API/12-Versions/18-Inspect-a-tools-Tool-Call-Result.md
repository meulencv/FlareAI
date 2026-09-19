---
title: "Inspect a tool's Tool Call Result"
description: "Returns the current Tool Call Result and acks the tool."
---

# Inspect a tool's Tool Call Result

> Returns the current Tool Call Result and acks the tool.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /versions/{version_id}/tools/{tool_id}/tool-call-result/inspect
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
  /versions/{version_id}/tools/{tool_id}/tool-call-result/inspect:
    post:
      tags:
        - Versions
      summary: Inspect a tool's Tool Call Result
      description: Returns the current Tool Call Result and acks the tool.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: version_id
          required: true
          description: Version UUID or slug
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: tool_id
          required: true
          description: Tool node UUID
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: object
                    properties:
                      tool_id:
                        type: string
                      tool_name:
                        type: string
                      ack_state:
                        nullable: true
                        type: string
                        enum:
                          - unack
                          - ack
                      has_untested_nodes:
                        type: boolean
                      nodes:
                        type: array
                        items:
                          type: object
                          properties:
                            node_id:
                              type: string
                            persistent_id:
                              type: string
                            name:
                              type: string
                            state:
                              type: string
                              enum:
                                - incomplete
                                - untested
                                - valid
                            reason:
                              type: string
                            is_list:
                              type: boolean
                            output_schema:
                              nullable: true
                              type: object
                              additionalProperties: {}
                            error:
                              nullable: true
                              type: string
                            fields:
                              type: array
                              items:
                                type: object
                                properties:
                                  path:
                                    type: string
                                  exposed:
                                    type: boolean
                                required:
                                  - path
                                  - exposed
                                additionalProperties: false
                          required:
                            - node_id
                            - persistent_id
                            - name
                            - state
                            - is_list
                            - output_schema
                            - error
                            - fields
                          additionalProperties: false
                      preview:
                        type: object
                        properties:
                          steps:
                            type: array
                            items:
                              type: object
                              properties:
                                node:
                                  type: string
                                output:
                                  type: object
                                  additionalProperties: {}
                              required:
                                - node
                                - output
                              additionalProperties: false
                        required:
                          - steps
                        additionalProperties: false
                      generated:
                        type: array
                        items:
                          type: object
                          properties:
                            node_id:
                              type: string
                            name:
                              type: string
                            ok:
                              type: boolean
                            error:
                              type: string
                          required:
                            - node_id
                            - name
                            - ok
                          additionalProperties: false
                      skipped_incomplete:
                        type: array
                        items:
                          type: object
                          properties:
                            node_id:
                              type: string
                            name:
                              type: string
                            reason:
                              type: string
                          required:
                            - node_id
                            - name
                          additionalProperties: false
                    required:
                      - tool_id
                      - tool_name
                      - ack_state
                      - has_untested_nodes
                      - nodes
                      - preview
                    additionalProperties: false
                required:
                  - data
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/inspect-a-tools-tool-call-result
