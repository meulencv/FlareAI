---
title: "List authorized organizations"
description: "Returns the organizations this MCP token is authorized to act on."
---

# List authorized organizations

> Returns the organizations this MCP token is authorized to act on.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /mcp/authorized-orgs
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
  /mcp/authorized-orgs:
    get:
      tags:
        - MCP Servers
      summary: List authorized organizations
      description: Returns the organizations this MCP token is authorized to act on.
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: object
                    properties:
                      orgs:
                        type: array
                        items:
                          type: object
                          properties:
                            id:
                              type: string
                              format: uuid
                              pattern: >-
                                ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            slug:
                              type: string
                            name:
                              type: string
                          required:
                            - id
                            - slug
                            - name
                          additionalProperties: false
                    required:
                      - orgs
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

Fuente original: https://docs.happyrobot.ai/api-reference/mcp-servers/list-authorized-organizations
