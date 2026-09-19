---
title: "Validate toll-free numbers for TextAgent"
description: "Validates toll-free phone numbers for use with TextAgent SMS. Outbound numbers are always valid. Inbound numbers are blocked if a live inbound TextAgent already uses them."
---

# Validate toll-free numbers for TextAgent

> Validates toll-free phone numbers for use with TextAgent SMS. Outbound numbers are always valid. Inbound numbers are blocked if a live inbound TextAgent already uses them.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /phone-numbers/validate-toll-free-numbers
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
  /phone-numbers/validate-toll-free-numbers:
    post:
      tags:
        - Phone Numbers
      summary: Validate toll-free numbers for TextAgent
      description: >-
        Validates toll-free phone numbers for use with TextAgent SMS. Outbound
        numbers are always valid. Inbound numbers are blocked if a live inbound
        TextAgent already uses them.
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                phone_numbers:
                  minItems: 1
                  type: array
                  items:
                    type: string
                message_direction:
                  type: string
                  enum:
                    - inbound
                    - outbound
              required:
                - phone_numbers
                - message_direction
        required: true
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
                    phone_number:
                      type: string
                    is_valid:
                      type: boolean
                    reason:
                      type: string
                    conflict_info:
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
                            id:
                              type: string
                          required:
                            - name
                            - id
                          additionalProperties: false
                        status:
                          type: string
                          enum:
                            - draft
                            - locked
                            - live
                        phone_number:
                          type: string
                        channel:
                          type: string
                          enum:
                            - sms
                        message_direction:
                          type: string
                          enum:
                            - inbound
                            - outbound
                        provider:
                          type: string
                          enum:
                            - use_existing_toll_free
                      required:
                        - workflow
                        - version
                        - event
                        - status
                        - phone_number
                        - channel
                        - message_direction
                        - provider
                      additionalProperties: false
                  required:
                    - phone_number
                    - is_valid
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/validate-toll-free-numbers-for-textagent
