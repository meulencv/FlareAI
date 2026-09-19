---
title: "Submit northstar feedback"
description: "Submit a correctness rating (-2 = strongly wrong, +2 = strongly correct). One entry per API key/user."
---

# Submit northstar feedback

> Submit a correctness rating (-2 = strongly wrong, +2 = strongly correct). One entry per API key/user.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /northstars/{northstar_id}/feedback
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
  /northstars/{northstar_id}/feedback:
    post:
      tags:
        - Northstars
      summary: Submit northstar feedback
      description: >-
        Submit a correctness rating (-2 = strongly wrong, +2 = strongly
        correct). One entry per API key/user.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: northstar_id
          required: true
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                correctness:
                  type: integer
                  minimum: -2
                  maximum: 2
                feedback:
                  type: string
                trigger_regeneration:
                  type: boolean
              required:
                - correctness
        required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  feedback:
                    type: object
                    properties:
                      id:
                        type: string
                      correctness:
                        type: number
                      feedback:
                        nullable: true
                        type: string
                      created_at:
                        type: string
                    required:
                      - id
                      - correctness
                      - created_at
                    additionalProperties: false
                required:
                  - feedback
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

Fuente original: https://docs.happyrobot.ai/api-reference/northstars/submit-northstar-feedback
