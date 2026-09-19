---
title: "Publish a workflow"
description: "Publishes the latest version of the specified workflow to make it live. Before publishing, all action nodes are checked for test errors and untested status. If untested nodes exist (with no errors), a synchronous test-all is triggered first. If any node has test errors, the publish is blocked and er…"
---

# Publish a workflow

> Publishes the latest version of the specified workflow to make it live. Before publishing, all action nodes are checked for test errors and untested status. If untested nodes exist (with no errors), a synchronous test-all is triggered first. If any node has test errors, the publish is blocked and errors are returned. Workflow engine v2 versions cannot be published through the public API. Existing published v2 versions remain live and continue running until explicitly unpublished; this endpoint does not stop them.

For an eligible v3 target, returns an error if the workflow already has a live version. After the target passes readiness checks, use the unpublish endpoint to take the current version offline, then retry the publish request. Accepts a workflow UUID or slug as the path parameter.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /workflows/{workflow_id}/publish
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
  /workflows/{workflow_id}/publish:
    post:
      tags:
        - Workflows
      summary: Publish a workflow
      description: >-
        Publishes the latest version of the specified workflow to make it live.
        Before publishing, all action nodes are checked for test errors and
        untested status. If untested nodes exist (with no errors), a synchronous
        test-all is triggered first. If any node has test errors, the publish is
        blocked and errors are returned. Workflow engine v2 versions cannot be
        published through the public API. Existing published v2 versions remain
        live and continue running until explicitly unpublished; this endpoint
        does not stop them.


        For an eligible v3 target, returns an error if the workflow already has
        a live version. After the target passes readiness checks, use the
        unpublish endpoint to take the current version offline, then retry the
        publish request. Accepts a workflow UUID or slug as the path parameter.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: workflow_id
          required: true
          description: Workflow UUID or slug
      requestBody:
        content:
          application/json:
            schema:
              nullable: true
              type: object
              properties:
                environment:
                  default: production
                  description: Target environment for publishing
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
                  id:
                    type: string
                  is_published:
                    type: boolean
                  is_live:
                    type: boolean
                  environment:
                    type: string
                  missing_variables:
                    description: >-
                      Variable references that could not be resolved against
                      upstream nodes. Informational — does not block publishing.
                    type: array
                    items:
                      type: object
                      properties:
                        node_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          description: The node containing the broken reference
                        node_name:
                          nullable: true
                          description: Display name of the node
                          type: string
                        missing_variables:
                          type: array
                          items:
                            type: object
                            properties:
                              group_id:
                                type: string
                                description: >-
                                  The referenced variable group ID
                                  (persistent_id of the source node)
                              variable_id:
                                type: string
                                description: The referenced variable ID within the group
                            required:
                              - group_id
                              - variable_id
                            additionalProperties: false
                          description: Variable references that could not be resolved
                      required:
                        - node_id
                        - node_name
                        - missing_variables
                      additionalProperties: false
                required:
                  - id
                  - is_published
                  - is_live
                  - environment
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
                    type: number
                  errors:
                    type: array
                    items:
                      type: object
                      properties:
                        node_id:
                          type: string
                        name:
                          nullable: true
                          type: string
                        error:
                          type: string
                      required:
                        - node_id
                        - name
                        - error
                      additionalProperties: false
                  missing_variables:
                    description: >-
                      Variable references that could not be resolved against
                      upstream nodes.
                    type: array
                    items:
                      type: object
                      properties:
                        node_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          description: The node containing the broken reference
                        node_name:
                          nullable: true
                          description: Display name of the node
                          type: string
                        missing_variables:
                          type: array
                          items:
                            type: object
                            properties:
                              group_id:
                                type: string
                                description: >-
                                  The referenced variable group ID
                                  (persistent_id of the source node)
                              variable_id:
                                type: string
                                description: The referenced variable ID within the group
                            required:
                              - group_id
                              - variable_id
                            additionalProperties: false
                          description: Variable references that could not be resolved
                      required:
                        - node_id
                        - node_name
                        - missing_variables
                      additionalProperties: false
                required:
                  - error
                  - message
                  - statusCode
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/publish-a-workflow
