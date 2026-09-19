---
title: "Post knowledge bases"
description: "Create a new knowledge base for the organization."
---

# Post knowledge bases

> Create a new knowledge base for the organization.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /knowledge-bases/
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
  /knowledge-bases/:
    post:
      tags:
        - Knowledge Bases
      description: Create a new knowledge base for the organization.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  minLength: 1
                description:
                  type: string
                max_file_size_mb:
                  type: integer
                  minimum: 1
                  maximum: 1024
              required:
                - name
        required: true
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  knowledge_base:
                    type: object
                    properties:
                      id:
                        type: string
                      org_id:
                        type: string
                      name:
                        type: string
                      description:
                        nullable: true
                        type: string
                      max_file_size_mb:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      created_at:
                        type: string
                      updated_at:
                        type: string
                    required:
                      - id
                      - org_id
                      - name
                      - description
                      - max_file_size_mb
                      - created_at
                      - updated_at
                    additionalProperties: false
                required:
                  - knowledge_base
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
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: Opaque

````

---

Fuente original: https://docs.happyrobot.ai/api-reference/knowledge-bases/post-knowledge-bases
