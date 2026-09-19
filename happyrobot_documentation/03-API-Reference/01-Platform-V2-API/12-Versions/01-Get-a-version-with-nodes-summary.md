---
title: "Get a version with nodes summary"
description: "Returns a single version by UUID or slug with metadata, node count, node counts by type, and the list of events (action node types) used."
---

# Get a version with nodes summary

> Returns a single version by UUID or slug with metadata, node count, node counts by type, and the list of events (action node types) used.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /versions/{version_id}/
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
  /versions/{version_id}/:
    get:
      tags:
        - Versions
      summary: Get a version with nodes summary
      description: >-
        Returns a single version by UUID or slug with metadata, node count, node
        counts by type, and the list of events (action node types) used.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: version_id
          required: true
          description: Version UUID or slug
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
                  name:
                    type: string
                  slug:
                    type: string
                  workflow_slug:
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
                  workflow_version:
                    type: number
                  published_at:
                    nullable: true
                    type: string
                  timestamp:
                    type: string
                  node_count:
                    type: number
                  node_counts_by_type:
                    type: object
                    additionalProperties:
                      type: number
                  events:
                    type: array
                    items:
                      type: object
                      properties:
                        event_id:
                          type: string
                        name:
                          type: string
                      required:
                        - event_id
                        - name
                      additionalProperties: false
                  changelog:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        type:
                          type: string
                        description:
                          nullable: true
                          type: string
                        created_at:
                          type: string
                        created_by:
                          nullable: true
                          type: object
                          properties:
                            type:
                              type: string
                              enum:
                                - user
                                - api_key
                            name:
                              nullable: true
                              type: string
                          required:
                            - type
                            - name
                          additionalProperties: false
                      required:
                        - id
                        - type
                        - description
                        - created_at
                        - created_by
                      additionalProperties: false
                required:
                  - id
                  - name
                  - slug
                  - is_published
                  - is_live
                  - timestamp
                  - node_count
                  - node_counts_by_type
                  - events
                  - changelog
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/get-a-version-with-nodes-summary
