---
title: "Publish a version"
description: "Publishes the specified version to make it live. Before publishing, node configuration completeness is validated. If untested nodes exist, a synchronous test-all is triggered automatically. Test errors do not block publishing (matching UI behavior) but are returned as informational warnings in the `…"
---

# Publish a version

> Publishes the specified version to make it live. Before publishing, node configuration completeness is validated. If untested nodes exist, a synchronous test-all is triggered automatically. Test errors do not block publishing (matching UI behavior) but are returned as informational warnings in the `test_errors` field. Workflow engine v2 versions cannot be published through the public API. Existing published v2 versions remain live and continue running until explicitly unpublished; this endpoint does not stop them.

For an eligible v3 target, either `unpublish_version_id` or `force: true` must be provided when a live version exists. Use `unpublish_version_id` to explicitly specify the live version to replace. Use `force: true` to automatically unpublish whatever version is currently live.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /versions/{version_id}/publish
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
  /versions/{version_id}/publish:
    post:
      tags:
        - Versions
      summary: Publish a version
      description: >-
        Publishes the specified version to make it live. Before publishing, node
        configuration completeness is validated. If untested nodes exist, a
        synchronous test-all is triggered automatically. Test errors do not
        block publishing (matching UI behavior) but are returned as
        informational warnings in the `test_errors` field. Workflow engine v2
        versions cannot be published through the public API. Existing published
        v2 versions remain live and continue running until explicitly
        unpublished; this endpoint does not stop them.


        For an eligible v3 target, either `unpublish_version_id` or `force:
        true` must be provided when a live version exists. Use
        `unpublish_version_id` to explicitly specify the live version to
        replace. Use `force: true` to automatically unpublish whatever version
        is currently live.
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
              nullable: true
              type: object
              properties:
                unpublish_version_id:
                  description: >-
                    ID of the currently live version to unpublish before
                    publishing this one. Required when the workflow already has
                    a live version, unless force is true.
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                environment:
                  default: production
                  description: Target environment for publishing
                  type: string
                  enum:
                    - production
                    - staging
                    - development
                force:
                  default: false
                  description: >-
                    When true, automatically unpublishes any currently live
                    version without requiring unpublish_version_id.
                  type: boolean
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
                  test_errors:
                    description: >-
                      Nodes with test errors at time of publishing.
                      Informational — does not block publishing (matches UI
                      behavior).
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/publish-a-version
