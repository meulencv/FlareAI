---
title: "Remove phone number from a workflow"
description: "Removes a phone number from a specific workflow and version. The version must not be live."
---

# Remove phone number from a workflow

> Removes a phone number from a specific workflow and version. The version must not be live.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /phone-numbers/remove-from-workflow
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
  /phone-numbers/remove-from-workflow:
    post:
      tags:
        - Phone Numbers
      summary: Remove phone number from a workflow
      description: >-
        Removes a phone number from a specific workflow and version. The version
        must not be live.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: phone_number_id
          required: true
          description: Phone number ID (Twilio SID or Telnyx ID)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                workflow_slug:
                  type: string
                  minLength: 1
                version_slug:
                  type: string
                  minLength: 1
              required:
                - workflow_slug
                - version_slug
        required: true
      responses:
        '200':
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/remove-phone-number-from-a-workflow
