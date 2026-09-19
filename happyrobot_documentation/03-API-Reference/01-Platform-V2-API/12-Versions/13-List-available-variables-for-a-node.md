---
title: "List available variables for a node"
description: "Returns all variable groups available to the specified node, including system variables, environment variables, and upstream node outputs."
---

# List available variables for a node

> Returns all variable groups available to the specified node, including system variables, environment variables, and upstream node outputs.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /versions/{version_id}/nodes/{node_id}/available-vars
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
  /versions/{version_id}/nodes/{node_id}/available-vars:
    get:
      tags:
        - Versions
      summary: List available variables for a node
      description: >-
        Returns all variable groups available to the specified node, including
        system variables, environment variables, and upstream node outputs.
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
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        event_id:
                          type: string
                        icon:
                          type: string
                        name:
                          type: string
                        is_complete:
                          type: boolean
                        is_list:
                          description: >-
                            Whether variables in this group resolve as arrays.
                            Loop body outputs set this when referenced outside
                            the loop; sequential and parallel loops both return
                            lists, including one-item lists for single-iteration
                            loops.
                          type: boolean
                        variables:
                          type: array
                          items:
                            type: object
                            properties:
                              id:
                                type: string
                              name:
                                type: string
                              type:
                                type: string
                                enum:
                                  - string
                                  - number
                                  - boolean
                                  - 'null'
                                  - object
                                  - array
                              value:
                                anyOf:
                                  - type: string
                                  - type: number
                                  - type: boolean
                                  - type: string
                                    nullable: true
                                    enum:
                                      - null
                            required:
                              - id
                              - name
                            additionalProperties: false
                        integration_name:
                          type: string
                      required:
                        - id
                        - name
                        - is_complete
                        - variables
                      additionalProperties: false
                required:
                  - data
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/list-available-variables-for-a-node
