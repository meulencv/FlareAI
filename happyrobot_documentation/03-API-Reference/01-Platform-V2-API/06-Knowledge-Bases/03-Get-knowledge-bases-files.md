---
title: "Get knowledge bases files"
description: "List all files in a knowledge base. Use this endpoint to check file processing status after triggering chunking via POST /:kbId/trigger-chunking."
---

# Get knowledge bases files

> List all files in a knowledge base. Use this endpoint to check file processing status after triggering chunking via POST /:kbId/trigger-chunking.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /knowledge-bases/{kbId}/files
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
  /knowledge-bases/{kbId}/files:
    get:
      tags:
        - Knowledge Bases
      description: >-
        List all files in a knowledge base. Use this endpoint to check file
        processing status after triggering chunking via POST
        /:kbId/trigger-chunking.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: kbId
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
                        id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        kb_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        file_size_in_bytes:
                          type: integer
                          minimum: -2147483648
                          maximum: 2147483647
                        org_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        external_uri:
                          type: string
                        name:
                          type: string
                          maxLength: 256
                        type:
                          type: string
                          maxLength: 256
                        uploaded_by:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        last_updated:
                          type: string
                          format: date-time
                        processing_status:
                          nullable: true
                          type: string
                          maxLength: 64
                        chunking_config:
                          nullable: true
                          anyOf:
                            - anyOf:
                                - type: string
                                - type: number
                                - type: boolean
                                - type: string
                                  nullable: true
                                  enum:
                                    - null
                            - type: object
                              additionalProperties: {}
                            - type: array
                              items: {}
                        summary:
                          nullable: true
                          type: string
                        summary_keywords:
                          nullable: true
                          type: array
                          items:
                            type: string
                        parsed_content:
                          nullable: true
                          type: string
                        source_url:
                          nullable: true
                          type: string
                        source_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        content_hash:
                          nullable: true
                          type: string
                        alchemist_elixir_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        created_at:
                          type: string
                          format: date-time
                        uploaded_by_email:
                          nullable: true
                          type: string
                      required:
                        - id
                        - kb_id
                        - file_size_in_bytes
                        - org_id
                        - external_uri
                        - name
                        - type
                        - uploaded_by
                        - last_updated
                        - processing_status
                        - chunking_config
                        - summary
                        - summary_keywords
                        - parsed_content
                        - source_url
                        - source_id
                        - content_hash
                        - alchemist_elixir_id
                        - created_at
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

Fuente original: https://docs.happyrobot.ai/api-reference/knowledge-bases/get-knowledge-bases-files
