---
title: "Create a northstar folder for a prompt node"
description: "Create a folder for organizing this prompt node's northstars. File northstars into it via folder_id on create or update."
---

# Create a northstar folder for a prompt node

> Create a folder for organizing this prompt node's northstars. File northstars into it via folder_id on create or update.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /nodes/{node_id}/northstars/folders
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
  /nodes/{node_id}/northstars/folders:
    post:
      tags:
        - Northstars
      summary: Create a northstar folder for a prompt node
      description: >-
        Create a folder for organizing this prompt node's northstars. File
        northstars into it via folder_id on create or update.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: node_id
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  type: string
                  minLength: 1
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
                  folder:
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                    required:
                      - id
                      - name
                    additionalProperties: false
                required:
                  - folder
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

Fuente original: https://docs.happyrobot.ai/api-reference/northstars/create-a-northstar-folder-for-a-prompt-node
