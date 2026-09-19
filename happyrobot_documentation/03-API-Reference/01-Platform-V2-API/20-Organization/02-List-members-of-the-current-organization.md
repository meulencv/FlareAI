---
title: "List members of the current organization"
description: "Returns members of the authenticated organization, including public profile information and each member's workspace-wide role. The role is null when a member only has scoped access."
---

# List members of the current organization

> Returns members of the authenticated organization, including public profile information and each member's workspace-wide role. The role is null when a member only has scoped access.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /org/members/
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
  /org/members/:
    get:
      tags:
        - Organization
      summary: List members of the current organization
      description: >-
        Returns members of the authenticated organization, including public
        profile information and each member's workspace-wide role. The role is
        null when a member only has scoped access.
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
                        user_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        email:
                          type: string
                          format: email
                          pattern: >-
                            ^(?!\.)(?!.*\.\.)([A-Za-z0-9_'+\-\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\-]*\.)+[A-Za-z]{2,}$
                        first_name:
                          nullable: true
                          type: string
                        last_name:
                          nullable: true
                          type: string
                        image_url:
                          nullable: true
                          type: string
                        role:
                          nullable: true
                          type: string
                      required:
                        - user_id
                        - email
                        - first_name
                        - last_name
                        - image_url
                        - role
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

Fuente original: https://docs.happyrobot.ai/api-reference/organization/list-members-of-the-current-organization
