---
title: "Update a version"
description: "Updates version metadata (name and/or description). Accepts a version UUID or slug as the path parameter."
---

# Update a version

> Updates version metadata (name and/or description). Accepts a version UUID or slug as the path parameter.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json patch /versions/{version_id}/
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
    patch:
      tags:
        - Versions
      summary: Update a version
      description: >-
        Updates version metadata (name and/or description). Accepts a version
        UUID or slug as the path parameter.
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
              type: object
              properties:
                name:
                  description: Version display name
                  type: string
                  minLength: 1
                  maxLength: 256
                description:
                  description: Version description
                  type: string
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
                  description:
                    nullable: true
                    type: string
                required:
                  - id
                  - name
                  - slug
                  - is_published
                  - is_live
                  - timestamp
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/update-a-version
