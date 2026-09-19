---
title: "Publish an immediate signal"
description: "Publishes a signal to internal signal service. payload.org_id is always derived from API key org. Built-in keys (org., usecase., session.) are allowed for targeting active sessions."
---

# Publish an immediate signal

> Publishes a signal to internal signal service. payload.org_id is always derived from API key org. Built-in keys (org., usecase., session.) are allowed for targeting active sessions.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /signals/
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
  /signals/:
    post:
      tags:
        - Signals
      summary: Publish an immediate signal
      description: >-
        Publishes a signal to internal signal service. payload.org_id is always
        derived from API key org. Built-in keys (org., usecase., session.) are
        allowed for targeting active sessions.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                key:
                  type: string
                  minLength: 1
                  maxLength: 256
                  pattern: ^[a-zA-Z0-9_\-.*#]+(?:\.[a-zA-Z0-9_\-.*#]+)*$
                keys:
                  minItems: 1
                  type: array
                  items:
                    type: string
                    minLength: 1
                    maxLength: 256
                    pattern: ^[a-zA-Z0-9_\-.*#]+(?:\.[a-zA-Z0-9_\-.*#]+)*$
                env:
                  type: string
                  enum:
                    - production
                    - staging
                    - development
                payload:
                  type: object
                  additionalProperties: {}
                metadata:
                  type: object
                  additionalProperties: {}
              required:
                - payload
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  dispatch_id:
                    type: string
                  signal_id:
                    type: string
                  status:
                    type: string
                  published_at:
                    type: string
                  keys:
                    type: array
                    items:
                      type: string
                  signals:
                    type: array
                    items:
                      type: object
                      properties:
                        signal_id:
                          type: string
                        key:
                          type: string
                        status:
                          type: string
                      required:
                        - signal_id
                        - key
                        - status
                      additionalProperties: false
                required:
                  - status
                  - published_at
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
        '502':
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

Fuente original: https://docs.happyrobot.ai/api-reference/signals/publish-an-immediate-signal
