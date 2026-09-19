---
title: "Complete file upload"
description: "Registers an uploaded artifact after direct S3 upload. Call this after uploading the file to the presigned URL."
---

# Complete file upload

> Registers an uploaded artifact after direct S3 upload. Call this after uploading the file to the presigned URL.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /chat/upload/complete
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
  /chat/upload/complete:
    post:
      tags:
        - Chat
      summary: Complete file upload
      description: >-
        Registers an uploaded artifact after direct S3 upload. Call this after
        uploading the file to the presigned URL.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                artifact_id:
                  type: string
                s3_uri:
                  type: string
                filename:
                  type: string
                mime_type:
                  type: string
                size_bytes:
                  type: number
                  minimum: 0
                  exclusiveMinimum: true
              required:
                - artifact_id
                - s3_uri
                - filename
                - mime_type
                - size_bytes
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  artifact_id:
                    type: string
                  status:
                    type: string
                required:
                  - artifact_id
                  - status
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
                  statusCode:
                    type: number
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
                  statusCode:
                    type: number
                required:
                  - error
                additionalProperties: false
        '413':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  statusCode:
                    type: number
                required:
                  - error
                additionalProperties: false
        '502':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  statusCode:
                    type: number
                required:
                  - error
                additionalProperties: false
        '503':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
                  statusCode:
                    type: number
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

Fuente original: https://docs.happyrobot.ai/api-reference/chat/complete-file-upload
