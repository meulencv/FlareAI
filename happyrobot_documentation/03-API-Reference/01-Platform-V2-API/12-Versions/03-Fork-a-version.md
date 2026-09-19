---
title: "Fork a version"
description: "Creates a new version by copying all nodes from the specified version. The new version gets the next available version number and is unlocked/unpublished. If the source uses workflow engine v2, the fork remains an editable v2 draft and cannot be published through the public API until upgraded to v3.…"
---

# Fork a version

> Creates a new version by copying all nodes from the specified version. The new version gets the next available version number and is unlocked/unpublished. If the source uses workflow engine v2, the fork remains an editable v2 draft and cannot be published through the public API until upgraded to v3. Any existing published v2 version remains live and continues running until explicitly unpublished. Accepts a version UUID or slug as the path parameter.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /versions/{version_id}/fork
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
  /versions/{version_id}/fork:
    post:
      tags:
        - Versions
      summary: Fork a version
      description: >-
        Creates a new version by copying all nodes from the specified version.
        The new version gets the next available version number and is
        unlocked/unpublished. If the source uses workflow engine v2, the fork
        remains an editable v2 draft and cannot be published through the public
        API until upgraded to v3. Any existing published v2 version remains live
        and continues running until explicitly unpublished. Accepts a version
        UUID or slug as the path parameter.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: version_id
          required: true
          description: Version UUID or slug
      responses:
        '201':
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
                  source_version_id:
                    nullable: true
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  warnings:
                    type: array
                    items:
                      type: string
                required:
                  - id
                  - name
                  - slug
                  - is_published
                  - is_live
                  - timestamp
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/fork-a-version
