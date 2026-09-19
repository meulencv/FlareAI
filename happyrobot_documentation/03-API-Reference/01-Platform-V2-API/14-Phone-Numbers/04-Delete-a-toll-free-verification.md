---
title: "Delete a toll-free verification"
description: "Deletes a toll-free verification request by its SID."
---

# Delete a toll-free verification

> Deletes a toll-free verification request by its SID.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json delete /phone-numbers/tollfree-verification/{verification_sid}
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
  /phone-numbers/tollfree-verification/{verification_sid}:
    delete:
      tags:
        - Phone Numbers
      summary: Delete a toll-free verification
      description: Deletes a toll-free verification request by its SID.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: verification_sid
          required: true
          description: Toll-free verification SID
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/delete-a-toll-free-verification
