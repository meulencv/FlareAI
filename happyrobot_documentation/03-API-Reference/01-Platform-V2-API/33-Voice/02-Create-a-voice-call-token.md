---
title: "Create a voice call token"
description: "Generates a LiveKit token for browser-side voice calls with AI agents. Call this from your backend with your API key, then pass the token to the frontend. Use workflow_id to start a new call, or session_id to silently listen to an in-progress call. Set should_takeover to true to take over the call i…"
---

# Create a voice call token

> Generates a LiveKit token for browser-side voice calls with AI agents. Call this from your backend with your API key, then pass the token to the frontend. Use workflow_id to start a new call, or session_id to silently listen to an in-progress call. Set should_takeover to true to take over the call instead.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /voice/tokens/
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
  /voice/tokens/:
    post:
      tags:
        - Voice
      summary: Create a voice call token
      description: >-
        Generates a LiveKit token for browser-side voice calls with AI agents.
        Call this from your backend with your API key, then pass the token to
        the frontend. Use workflow_id to start a new call, or session_id to
        silently listen to an in-progress call. Set should_takeover to true to
        take over the call instead.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                workflow_id:
                  description: >-
                    Workflow UUID or slug to scope the token to. Starts a new
                    call. Mutually exclusive with session_id.
                  type: string
                  minLength: 1
                session_id:
                  description: >-
                    ID of an in-progress session to join. Generates a token for
                    the session's existing LiveKit room. Mutually exclusive with
                    workflow_id.
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                should_takeover:
                  default: false
                  description: >-
                    When false, joins a session as a hidden, subscribe-only
                    observer and keeps the AI agent active. When true, takes
                    over the call and the AI agent drops. Only valid with
                    session_id.
                  type: boolean
                data:
                  description: >-
                    Payload data to pass to the voice agent as participant
                    attributes (workflow_id only)
                  type: object
                  additionalProperties: {}
                env:
                  default: production
                  description: Environment to use for version resolution (workflow_id only)
                  type: string
                  enum:
                    - production
                    - staging
                    - development
                ttl_seconds:
                  default: 21600
                  description: >-
                    LiveKit token lifetime in seconds. Defaults to 21600 (6
                    hours) to match LiveKit's default. Min 60s, max 24h. The
                    browser must (re)connect before this expires; LiveKit does
                    not refresh tokens on an active call.
                  type: integer
                  minimum: 60
                  maximum: 86400
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  url:
                    type: string
                    description: LiveKit WebSocket URL
                  token:
                    type: string
                    description: LiveKit access token
                  room_name:
                    type: string
                    description: LiveKit room name
                  run_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    description: Run ID for tracking
                required:
                  - url
                  - token
                  - room_name
                  - run_id
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
        '409':
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

Fuente original: https://docs.happyrobot.ai/api-reference/voice/create-a-voice-call-token
