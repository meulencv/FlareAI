---
title: "Free up a phone number"
description: "Removes a phone number from all workflows it is assigned to. The phone number must not be used in any live version."
---

# Free up a phone number

> Removes a phone number from all workflows it is assigned to. The phone number must not be used in any live version.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /phone-numbers/free-up-number
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
  /phone-numbers/free-up-number:
    post:
      tags:
        - Phone Numbers
      summary: Free up a phone number
      description: >-
        Removes a phone number from all workflows it is assigned to. The phone
        number must not be used in any live version.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: phone_number_id
          required: true
          description: Phone number ID (Twilio SID or Telnyx ID)
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/free-up-a-phone-number
