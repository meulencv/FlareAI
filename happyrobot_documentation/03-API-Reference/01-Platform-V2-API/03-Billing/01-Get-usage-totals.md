---
title: "Get usage totals"
description: "Returns the authenticated organization's total voice minutes, emails, and text messages between the inclusive start and end datetimes. Use Get usage details for the same usage grouped by workflow."
---

# Get usage totals

> Returns the authenticated organization's total voice minutes, emails, and text messages between the inclusive start and end datetimes. Use Get usage details for the same usage grouped by workflow.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /billing/usage/totals
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
  /billing/usage/totals:
    get:
      tags:
        - Billing
      summary: Get usage totals
      description: >-
        Returns the authenticated organization's total voice minutes, emails,
        and text messages between the inclusive start and end datetimes. Use Get
        usage details for the same usage grouped by workflow.
      parameters:
        - schema:
            type: string
            format: date-time
            pattern: >-
              ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z|([+-](?:[01]\d|2[0-3]):[0-5]\d)))$
          in: query
          name: start
          required: true
        - schema:
            type: string
            format: date-time
            pattern: >-
              ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z|([+-](?:[01]\d|2[0-3]):[0-5]\d)))$
          in: query
          name: end
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  customerId:
                    type: string
                  startDate:
                    type: string
                  endDate:
                    type: string
                  usage:
                    type: object
                    properties:
                      totalMinutes:
                        type: number
                      totalEmails:
                        type: number
                      totalText:
                        type: number
                    required:
                      - totalMinutes
                      - totalEmails
                      - totalText
                    additionalProperties: false
                required:
                  - customerId
                  - startDate
                  - endDate
                  - usage
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
        '403':
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

Fuente original: https://docs.happyrobot.ai/api-reference/billing/get-usage-totals
