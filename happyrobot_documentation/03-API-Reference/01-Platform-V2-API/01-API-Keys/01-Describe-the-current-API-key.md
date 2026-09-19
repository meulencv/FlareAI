---
title: "Describe the current API key"
description: "Returns metadata for the API key used in the Authorization header."
---

# Describe the current API key

> Returns metadata for the API key used in the Authorization header.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /api-key/describe
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
  /api-key/describe:
    get:
      tags:
        - API Keys
      summary: Describe the current API key
      description: Returns metadata for the API key used in the Authorization header.
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
                  orgId:
                    type: string
                  org_slug:
                    type: string
                  org_name:
                    type: string
                  name:
                    type: string
                  prefix:
                    type: string
                  lastFour:
                    type: string
                    minLength: 4
                    maxLength: 4
                  createdAt:
                    type: string
                  expiresAt:
                    nullable: true
                    type: string
                  lastUsedAt:
                    nullable: true
                    type: string
                  revokedAt:
                    nullable: true
                    type: string
                required:
                  - id
                  - orgId
                  - org_slug
                  - org_name
                  - name
                  - prefix
                  - lastFour
                  - createdAt
                  - expiresAt
                  - lastUsedAt
                  - revokedAt
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

Fuente original: https://docs.happyrobot.ai/api-reference/api-keys/describe-the-current-api-key
