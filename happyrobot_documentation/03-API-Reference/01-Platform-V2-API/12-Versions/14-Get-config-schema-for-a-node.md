---
title: "Get config schema for a node"
description: "Returns the configuration schema for the node's event, including field types, required fields, current values, defaults, and validation status. Only works for action nodes (nodes with an event_id)."
---

# Get config schema for a node

> Returns the configuration schema for the node's event, including field types, required fields, current values, defaults, and validation status. Only works for action nodes (nodes with an event_id).



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /versions/{version_id}/nodes/{node_id}/config-schema
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
  /versions/{version_id}/nodes/{node_id}/config-schema:
    get:
      tags:
        - Versions
      summary: Get config schema for a node
      description: >-
        Returns the configuration schema for the node's event, including field
        types, required fields, current values, defaults, and validation status.
        Only works for action nodes (nodes with an event_id).
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
          in: path
          name: node_id
          required: true
          description: The UUID of the node
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
                      event_id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                      event_name:
                        type: string
                      fields:
                        type: array
                        items: e522fd6b-68e7-4164-ab64-32bc6b266a32
                      current_values:
                        nullable: true
                        type: object
                        additionalProperties: {}
                      defaults:
                        nullable: true
                        type: object
                        additionalProperties: {}
                      validation:
                        type: object
                        properties:
                          is_valid:
                            type: boolean
                          issues:
                            type: array
                            items:
                              type: object
                              properties:
                                field:
                                  type: string
                                message:
                                  type: string
                              required:
                                - message
                              additionalProperties: false
                        required:
                          - is_valid
                          - issues
                        additionalProperties: false
                      available_options:
                        nullable: true
                        type: object
                        properties:
                          models:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                name:
                                  type: string
                                description:
                                  type: string
                              required:
                                - id
                                - name
                              additionalProperties: false
                          phone_numbers:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                name:
                                  type: string
                                number:
                                  type: string
                              required:
                                - id
                                - name
                                - number
                              additionalProperties: false
                          voices:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                name:
                                  type: string
                                language:
                                  type: string
                                gender:
                                  type: string
                              required:
                                - id
                                - name
                                - language
                                - gender
                              additionalProperties: false
                          languages:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                name:
                                  type: string
                              required:
                                - id
                                - name
                              additionalProperties: false
                          credentials:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                title:
                                  type: string
                              required:
                                - id
                                - title
                              additionalProperties: false
                        additionalProperties: false
                    required:
                      - event_id
                      - event_name
                      - fields
                      - current_values
                      - defaults
                      - validation
                      - available_options
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/get-config-schema-for-a-node
