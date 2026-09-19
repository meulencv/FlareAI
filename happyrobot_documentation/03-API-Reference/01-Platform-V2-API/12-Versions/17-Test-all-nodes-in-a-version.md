---
title: "Test all nodes in a version"
description: "Triggers a synchronous test-all run for every testable node in the specified version. Nodes are executed in dependency waves — independent nodes run in parallel. If a node fails, dependent nodes are skipped. The endpoint blocks until all nodes have been tested and returns per-node results."
---

# Test all nodes in a version

> Triggers a synchronous test-all run for every testable node in the specified version. Nodes are executed in dependency waves — independent nodes run in parallel. If a node fails, dependent nodes are skipped. The endpoint blocks until all nodes have been tested and returns per-node results.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /versions/{version_id}/test-all
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
  /versions/{version_id}/test-all:
    post:
      tags:
        - Versions
      summary: Test all nodes in a version
      description: >-
        Triggers a synchronous test-all run for every testable node in the
        specified version. Nodes are executed in dependency waves — independent
        nodes run in parallel. If a node fails, dependent nodes are skipped. The
        endpoint blocks until all nodes have been tested and returns per-node
        results.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: version_id
          required: true
          description: Version UUID or slug
      requestBody:
        content:
          application/json:
            schema:
              default: {}
              nullable: true
              type: object
              properties:
                environment:
                  default: development
                  description: Environment to use for variable resolution
                  type: string
                  enum:
                    - production
                    - staging
                    - development
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  results:
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
                        status:
                          type: string
                          enum:
                            - success
                            - failed
                            - skipped
                        error:
                          type: string
                      required:
                        - node_id
                        - persistent_id
                        - name
                        - status
                      additionalProperties: false
                required:
                  - results
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/test-all-nodes-in-a-version
