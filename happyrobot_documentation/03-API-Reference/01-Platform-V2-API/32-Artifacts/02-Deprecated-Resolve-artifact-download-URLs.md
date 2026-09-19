---
title: "[Deprecated] Resolve artifact download URLs"
description: "This endpoint is deprecated and is scheduled to stop working on October 15, 2026 at 12:00 UTC. Migrate to POST /artifacts/download-urls and provide each artifact's message_id."
---

# [Deprecated] Resolve artifact download URLs

> This endpoint is deprecated and is scheduled to stop working on October 15, 2026 at 12:00 UTC. Migrate to POST /artifacts/download-urls and provide each artifact's message_id.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /artifacts/resolve
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
  /artifacts/resolve:
    post:
      tags:
        - Artifacts
      summary: '[Deprecated] Resolve artifact download URLs'
      description: >-
        This endpoint is deprecated and is scheduled to stop working on October
        15, 2026 at 12:00 UTC. Migrate to POST /artifacts/download-urls and
        provide each artifact's message_id.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                s3_keys:
                  minItems: 1
                  maxItems: 500
                  type: array
                  items:
                    type: string
                    minLength: 1
                expires_in:
                  type: integer
                  minimum: 60
                  maximum: 604800
              required:
                - s3_keys
        required: true
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
                        s3_key:
                          type: string
                        presigned_url:
                          nullable: true
                          type: string
                        error:
                          nullable: true
                          type: string
                      required:
                        - s3_key
                        - presigned_url
                        - error
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
        '410':
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

Fuente original: https://docs.happyrobot.ai/api-reference/artifacts/[deprecated]-resolve-artifact-download-urls
