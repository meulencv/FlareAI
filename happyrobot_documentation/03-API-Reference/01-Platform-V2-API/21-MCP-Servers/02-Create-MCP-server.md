---
title: "Create MCP server"
description: "Creates a new MCP server connection. Tests connectivity and discovers available tools before saving."
---

# Create MCP server

> Creates a new MCP server connection. Tests connectivity and discovers available tools before saving.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /mcp/
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
  /mcp/:
    post:
      tags:
        - MCP Servers
      summary: Create MCP server
      description: >-
        Creates a new MCP server connection. Tests connectivity and discovers
        available tools before saving.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                server_name:
                  type: string
                  minLength: 1
                server_url:
                  type: string
                  format: uri
                auth_type:
                  type: string
                  enum:
                    - none
                    - bearer
                    - api_key
                    - oauth2
                auth_token:
                  type: string
                oauth2_credential_id:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                staging_oauth2_credential_id:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                development_oauth2_credential_id:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                auth_header_name:
                  type: string
                staging_auth_header_name:
                  type: string
                development_auth_header_name:
                  type: string
                custom_headers:
                  type: object
                  additionalProperties:
                    type: string
                staging_custom_headers:
                  type: object
                  additionalProperties:
                    type: string
                development_custom_headers:
                  type: object
                  additionalProperties:
                    type: string
                staging_server_url:
                  anyOf:
                    - type: string
                      format: uri
                    - type: string
                      enum:
                        - ''
                staging_auth_token:
                  type: string
                development_server_url:
                  anyOf:
                    - type: string
                      format: uri
                    - type: string
                      enum:
                        - ''
                development_auth_token:
                  type: string
                title:
                  type: string
                tag_ids:
                  type: array
                  items:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
              required:
                - server_name
                - server_url
                - auth_type
        required: true
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  server_name:
                    type: string
                  server_url:
                    type: string
                  auth_type:
                    type: string
                    enum:
                      - none
                      - bearer
                      - api_key
                      - oauth2
                  oauth2_credential_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  staging_oauth2_credential_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  development_oauth2_credential_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  auth_header_name:
                    type: string
                  staging_auth_header_name:
                    type: string
                  development_auth_header_name:
                    type: string
                  custom_headers:
                    type: object
                    additionalProperties:
                      type: string
                  staging_custom_headers:
                    type: object
                    additionalProperties:
                      type: string
                  development_custom_headers:
                    type: object
                    additionalProperties:
                      type: string
                  staging_server_url:
                    type: string
                  development_server_url:
                    type: string
                  tools:
                    type: array
                    items:
                      type: object
                      properties:
                        name:
                          type: string
                        description:
                          type: string
                        input_schema: {}
                      required:
                        - name
                      additionalProperties: false
                  last_connected_at:
                    type: string
                  title:
                    type: string
                  timestamp:
                    type: string
                required:
                  - id
                  - server_name
                  - server_url
                  - auth_type
                  - tools
                  - last_connected_at
                  - title
                  - timestamp
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
        '403':
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

Fuente original: https://docs.happyrobot.ai/api-reference/mcp-servers/create-mcp-server
