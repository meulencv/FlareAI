---
title: "Duplicate an app"
description: "Creates a copy of a managed custom app, including source code and custom environment variables."
---

# Duplicate an app

> Creates a copy of a managed custom app, including source code and custom environment variables.

This is a long-running request and may take a while before responding.

- **name** — Optional. Display name for the new app. Defaults to `'{original name} Copy'`.
- **description** — Optional. Defaults to the source app description.
- **tag_ids** — Optional. Tags to assign on the new app.

Platform-managed environment variables are regenerated for the new app. Service credentials are **not** copied and must be reconfigured. Only managed Next.js apps can be duplicated.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /apps/{app_slug}/duplicate
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
  /apps/{app_slug}/duplicate:
    post:
      tags:
        - Apps
      summary: Duplicate an app
      description: >-
        Creates a copy of a managed custom app, including source code and custom
        environment variables.


        This is a long-running request and may take a while before responding.


        - **name** — Optional. Display name for the new app. Defaults to
        `'{original name} Copy'`.

        - **description** — Optional. Defaults to the source app description.

        - **tag_ids** — Optional. Tags to assign on the new app.


        Platform-managed environment variables are regenerated for the new app.
        Service credentials are **not** copied and must be reconfigured. Only
        managed Next.js apps can be duplicated.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: app_slug
          required: true
          description: Slug of the source app to duplicate
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  description: >-
                    Display name for the new app. When omitted, defaults to
                    '{original app name} Copy'.
                  type: string
                  minLength: 1
                  maxLength: 256
                description:
                  description: >-
                    Description for the new app. When omitted, defaults to the
                    source app description.
                  type: string
                tag_ids:
                  description: >-
                    Tag IDs to assign to the duplicated app in the current
                    organization.
                  type: array
                  items:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
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
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  org_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  name:
                    type: string
                  slug:
                    type: string
                  description:
                    nullable: true
                    type: string
                  public_url:
                    nullable: true
                    type: string
                  tag_ids:
                    type: array
                    items:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  created_at:
                    type: string
                  updated_at:
                    type: string
                required:
                  - id
                  - org_id
                  - name
                  - slug
                  - description
                  - public_url
                  - tag_ids
                  - created_at
                  - updated_at
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

Fuente original: https://docs.happyrobot.ai/api-reference/apps/duplicate-an-app
