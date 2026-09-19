---
title: "Schedule a delayed signal"
description: "Schedules a delayed signal in internal signal service. payload.org_id is always derived from API key org."
---

# Schedule a delayed signal

> Schedules a delayed signal in internal signal service. payload.org_id is always derived from API key org.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /signals/scheduled-signals
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
  /signals/scheduled-signals:
    post:
      tags:
        - Signals
      summary: Schedule a delayed signal
      description: >-
        Schedules a delayed signal in internal signal service. payload.org_id is
        always derived from API key org.
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
                env:
                  type: string
                  enum:
                    - production
                    - staging
                    - development
                payload:
                  type: object
                  additionalProperties: {}
                delay_seconds:
                  type: integer
                  exclusiveMinimum: true
                  maximum: 9007199254740991
                metadata:
                  type: object
                  additionalProperties: {}
              required:
                - key
                - payload
                - delay_seconds
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  scheduled_signal_id:
                    type: string
                  status:
                    type: string
                  deliver_at:
                    type: string
                required:
                  - scheduled_signal_id
                  - status
                  - deliver_at
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

Fuente original: https://docs.happyrobot.ai/api-reference/signals/schedule-a-delayed-signal
