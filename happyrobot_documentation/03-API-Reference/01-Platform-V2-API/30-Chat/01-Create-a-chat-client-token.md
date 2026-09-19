---
title: "Create a chat client token"
description: "Generates a scoped JWT for browser-side chat operations. Call this from your backend with your API key, then pass the token to the frontend."
---

# Create a chat client token

> Generates a scoped JWT for browser-side chat operations. Call this from your backend with your API key, then pass the token to the frontend.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /chat/tokens/
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
  /chat/tokens/:
    post:
      tags:
        - Chat
      summary: Create a chat client token
      description: >-
        Generates a scoped JWT for browser-side chat operations. Call this from
        your backend with your API key, then pass the token to the frontend.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                workflow_id:
                  type: string
                  minLength: 1
                  description: Workflow UUID or slug to scope the token to
                data:
                  description: Payload data to pass to the chat agent as trigger variables
                  type: object
                  additionalProperties: {}
                env:
                  default: production
                  description: Environment to use for session initialization
                  type: string
                  enum:
                    - production
                    - staging
                    - development
                ttl_seconds:
                  default: 3600
                  description: >-
                    Token lifetime in seconds. Defaults to 3600 (1 hour). Min
                    60s, max 24h.
                  type: integer
                  minimum: 60
                  maximum: 86400
              required:
                - workflow_id
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  token:
                    type: string
                  expires_at:
                    type: string
                    description: ISO 8601 timestamp
                required:
                  - token
                  - expires_at
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
        '404':
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
        '500':
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

Fuente original: https://docs.happyrobot.ai/api-reference/chat/create-a-chat-client-token
