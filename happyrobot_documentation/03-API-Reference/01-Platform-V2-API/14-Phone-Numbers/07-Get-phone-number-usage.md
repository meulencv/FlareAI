---
title: "Get phone number usage"
description: "Returns usage information for a phone number across all workflows and versions."
---

# Get phone number usage

> Returns usage information for a phone number across all workflows and versions.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /phone-numbers/usage
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
  /phone-numbers/usage:
    get:
      tags:
        - Phone Numbers
      summary: Get phone number usage
      description: >-
        Returns usage information for a phone number across all workflows and
        versions.
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
                type: array
                items:
                  type: object
                  properties:
                    workflow:
                      type: object
                      properties:
                        name:
                          type: string
                        slug:
                          type: string
                      required:
                        - name
                        - slug
                      additionalProperties: false
                    version:
                      type: object
                      properties:
                        name:
                          type: string
                        version_number:
                          nullable: true
                          type: number
                        environment:
                          type: string
                        slug:
                          type: string
                      required:
                        - name
                        - version_number
                        - environment
                        - slug
                      additionalProperties: false
                    event:
                      type: object
                      properties:
                        name:
                          type: string
                      required:
                        - name
                      additionalProperties: false
                    status:
                      type: string
                      enum:
                        - draft
                        - locked
                        - live
                  required:
                    - workflow
                    - version
                    - event
                    - status
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/get-phone-number-usage
