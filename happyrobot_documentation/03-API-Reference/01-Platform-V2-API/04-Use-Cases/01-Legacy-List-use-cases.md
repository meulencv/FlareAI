---
title: "[Legacy] List use cases"
description: "Returns use cases for the authenticated org along with the live production version if available (or the most recent version as fallback). **Deprecated**: prefer GET /workflows instead."
---

# [Legacy] List use cases

> Returns use cases for the authenticated org along with the live production version if available (or the most recent version as fallback). **Deprecated**: prefer GET /workflows instead.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /use-cases/
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
  /use-cases/:
    get:
      tags:
        - Use Cases
      summary: '[Legacy] List use cases'
      description: >-
        Returns use cases for the authenticated org along with the live
        production version if available (or the most recent version as
        fallback). **Deprecated**: prefer GET /workflows instead.
      parameters:
        - schema:
            type: string
            enum:
              - 'true'
              - 'false'
          in: query
          name: is_deleted
          required: false
        - schema:
            type: string
            enum:
              - 'true'
              - 'false'
          in: query
          name: is_live
          required: false
        - schema:
            type: string
            enum:
              - 'true'
              - 'false'
          in: query
          name: is_published
          required: false
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: array
                items:
                  type: object
                  properties:
                    id:
                      type: string
                    org_id:
                      type: string
                    name:
                      type: string
                    slug:
                      type: string
                    icon:
                      nullable: true
                      type: string
                    folder_id:
                      nullable: true
                      type: string
                    tag_ids:
                      type: array
                      items:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    data_retention_days:
                      nullable: true
                      type: number
                    timestamp:
                      type: string
                    latest_version:
                      nullable: true
                      type: object
                      properties:
                        id:
                          type: string
                        name:
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
                        published_at:
                          nullable: true
                          type: string
                        timestamp:
                          type: string
                      required:
                        - id
                        - name
                        - is_published
                        - is_live
                        - timestamp
                      additionalProperties: false
                  required:
                    - id
                    - org_id
                    - name
                    - slug
                    - tag_ids
                    - timestamp
                    - latest_version
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
      deprecated: true
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

Fuente original: https://docs.happyrobot.ai/api-reference/use-cases/[legacy]-list-use-cases
