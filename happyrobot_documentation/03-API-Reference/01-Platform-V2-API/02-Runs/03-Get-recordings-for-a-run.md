---
title: "Get recordings for a run"
description: "Returns signed URLs for call recordings associated with a run. Optionally filter by session_id."
---

# Get recordings for a run

> Returns signed URLs for call recordings associated with a run. Optionally filter by session_id.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /runs/{run_id}/recordings
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
  /runs/{run_id}/recordings:
    get:
      tags:
        - Runs
      summary: Get recordings for a run
      description: >-
        Returns signed URLs for call recordings associated with a run.
        Optionally filter by session_id.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: query
          name: session_id
          required: false
        - schema:
            default: 1
            type: integer
            minimum: 1
            maximum: 7
          in: query
          name: url_expires_in_days
          required: false
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: run_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  recordings:
                    type: array
                    items:
                      type: object
                      properties:
                        session_id:
                          type: string
                        url:
                          type: string
                      required:
                        - session_id
                        - url
                      additionalProperties: false
                required:
                  - recordings
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
        '500':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  error:
                    type: string
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

Fuente original: https://docs.happyrobot.ai/api-reference/runs/get-recordings-for-a-run
