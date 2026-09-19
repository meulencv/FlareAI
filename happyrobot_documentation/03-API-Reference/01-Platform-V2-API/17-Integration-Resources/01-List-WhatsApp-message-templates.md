---
title: "List WhatsApp message templates"
description: "Returns all approved WhatsApp message templates for the given credential and business account."
---

# List WhatsApp message templates

> Returns all approved WhatsApp message templates for the given credential and business account.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /integrations/whatsapp/message-templates
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
  /integrations/whatsapp/message-templates:
    get:
      tags:
        - Integration Resources
      summary: List WhatsApp message templates
      description: >-
        Returns all approved WhatsApp message templates for the given credential
        and business account.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: query
          name: credential_id
          required: true
        - schema:
            type: string
          in: query
          name: business_account_id
          required: false
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                        name:
                          type: string
                        description:
                          type: string
                        disabled:
                          type: boolean
                        metadata:
                          type: object
                          properties:
                            language:
                              type: string
                            category:
                              type: string
                            status:
                              type: string
                            components:
                              type: array
                              items: {}
                          required:
                            - language
                            - category
                            - status
                          additionalProperties: false
                      required:
                        - name
                      additionalProperties: false
                required:
                  - data
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

Fuente original: https://docs.happyrobot.ai/api-reference/integration-resources/list-whatsapp-message-templates
