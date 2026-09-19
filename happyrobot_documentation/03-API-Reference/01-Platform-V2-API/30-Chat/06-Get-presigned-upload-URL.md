---
title: "Get presigned upload URL"
description: "Returns a presigned S3 URL for direct file upload from the browser. After uploading, call POST /chat/upload/complete to register the artifact."
---

# Get presigned upload URL

> Returns a presigned S3 URL for direct file upload from the browser. After uploading, call POST /chat/upload/complete to register the artifact.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /chat/upload/presigned
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
  /chat/upload/presigned:
    get:
      tags:
        - Chat
      summary: Get presigned upload URL
      description: >-
        Returns a presigned S3 URL for direct file upload from the browser.
        After uploading, call POST /chat/upload/complete to register the
        artifact.
      parameters:
        - schema:
            type: string
          in: query
          name: filename
          required: true
        - schema:
            type: string
          in: query
          name: mime_type
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
                  upload_url:
                    type: string
                  s3_uri:
                    type: string
                  max_file_size:
                    type: number
                required:
                  - artifact_id
                  - upload_url
                  - s3_uri
                  - max_file_size
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

Fuente original: https://docs.happyrobot.ai/api-reference/chat/get-presigned-upload-url
