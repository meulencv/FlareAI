---
title: "Add a member to the current organization"
description: "Adds a member to the authenticated organization by email. Internal users are added immediately; everyone else receives an email invitation to accept. Role must be editor or viewer (owners cannot be assigned via the API); defaults to viewer."
---

# Add a member to the current organization

> Adds a member to the authenticated organization by email. Internal users are added immediately; everyone else receives an email invitation to accept. Role must be editor or viewer (owners cannot be assigned via the API); defaults to viewer.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /org/members/
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
    post:
      tags:
        - Organization
      summary: Add a member to the current organization
      description: >-
        Adds a member to the authenticated organization by email. Internal users
        are added immediately; everyone else receives an email invitation to
        accept. Role must be editor or viewer (owners cannot be assigned via the
        API); defaults to viewer.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                email:
                  type: string
                  format: email
                  pattern: >-
                    ^(?!\.)(?!.*\.\.)([A-Za-z0-9_'+\-\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\-]*\.)+[A-Za-z]{2,}$
                role:
                  default: viewer
                  type: string
                  enum:
                    - editor
                    - viewer
              required:
                - email
        required: true
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: object
                    properties:
                      org_id:
                        type: string
                      email:
                        type: string
                      role:
                        type: string
                        enum:
                          - editor
                          - viewer
                      status:
                        type: string
                        enum:
                          - member
                          - invited
                    required:
                      - org_id
                      - email
                      - role
                      - status
                    additionalProperties: false
                required:
                  - data
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
        '429':
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

Fuente original: https://docs.happyrobot.ai/api-reference/organization/add-a-member-to-the-current-organization
