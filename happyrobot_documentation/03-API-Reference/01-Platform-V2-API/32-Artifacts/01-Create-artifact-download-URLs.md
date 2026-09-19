---
title: "Create artifact download URLs"
description: "Returns fresh presigned URLs after verifying each artifact against its server-authored message and the caller's workflow permissions."
---

# Create artifact download URLs

> Returns fresh presigned URLs after verifying each artifact against its server-authored message and the caller's workflow permissions.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /artifacts/download-urls
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
  /artifacts/download-urls:
    post:
      tags:
        - Artifacts
      summary: Create artifact download URLs
      description: >-
        Returns fresh presigned URLs after verifying each artifact against its
        server-authored message and the caller's workflow permissions.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                artifacts:
                  minItems: 1
                  maxItems: 20
                  type: array
                  items:
                    type: object
                    properties:
                      message_id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                      s3_key:
                        type: string
                        minLength: 1
                    required:
                      - message_id
                      - s3_key
                expires_in:
                  type: integer
                  minimum: 60
                  maximum: 604800
              required:
                - artifacts
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
                        message_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                      required:
                        - s3_key
                        - presigned_url
                        - error
                        - message_id
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

Fuente original: https://docs.happyrobot.ai/api-reference/artifacts/create-artifact-download-urls
