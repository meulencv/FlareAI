---
title: "Post knowledge bases upload urls"
description: "Step 1 of the file upload flow. Creates file records in the database and returns presigned object-storage URLs (valid for 3 minutes). Upload each file using uploadUrl and send uploadHeaders when present, then call POST /:kbId/trigger-chunking with the returned fileIds to start processing."
---

# Post knowledge bases upload urls

> Step 1 of the file upload flow. Creates file records in the database and returns presigned object-storage URLs (valid for 3 minutes). Upload each file using uploadUrl and send uploadHeaders when present, then call POST /:kbId/trigger-chunking with the returned fileIds to start processing.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /knowledge-bases/{kbId}/upload-urls
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
  /knowledge-bases/{kbId}/upload-urls:
    post:
      tags:
        - Knowledge Bases
      description: >-
        Step 1 of the file upload flow. Creates file records in the database and
        returns presigned object-storage URLs (valid for 3 minutes). Upload each
        file using uploadUrl and send uploadHeaders when present, then call POST
        /:kbId/trigger-chunking with the returned fileIds to start processing.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: kbId
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                files:
                  type: array
                  items:
                    type: object
                    properties:
                      fileName:
                        type: string
                        minLength: 1
                      contentType:
                        type: string
                        minLength: 1
                      contentLength:
                        type: number
                        minimum: 0
                        exclusiveMinimum: true
                    required:
                      - fileName
                      - contentType
                      - contentLength
              required:
                - files
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  files:
                    type: array
                    items:
                      type: object
                      properties:
                        fileId:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        fileName:
                          type: string
                        uploadUrl:
                          type: string
                          format: uri
                        uploadHeaders:
                          type: object
                          additionalProperties:
                            type: string
                      required:
                        - fileId
                        - fileName
                        - uploadUrl
                      additionalProperties: false
                required:
                  - files
                additionalProperties: false
        '400':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                required:
                  - message
                additionalProperties: false
        '401':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                required:
                  - message
                additionalProperties: false
        '403':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                required:
                  - message
                additionalProperties: false
        '404':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                required:
                  - message
                additionalProperties: false
        '409':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                required:
                  - message
                additionalProperties: false
        '500':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                required:
                  - message
                additionalProperties: false
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: Opaque

````

---

Fuente original: https://docs.happyrobot.ai/api-reference/knowledge-bases/post-knowledge-bases-upload-urls
