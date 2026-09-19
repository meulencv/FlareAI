---
title: "Get usage details"
description: "Returns the authenticated organization's voice minutes, emails, and text messages grouped by workflow between the inclusive start and end datetimes. Filter by one or more workflow IDs using repeated use_case_id parameters or a comma-separated list; omit the filter to include all workflows."
---

# Get usage details

> Returns the authenticated organization's voice minutes, emails, and text messages grouped by workflow between the inclusive start and end datetimes. Filter by one or more workflow IDs using repeated use_case_id parameters or a comma-separated list; omit the filter to include all workflows.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /billing/usage/details
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
  /billing/usage/details:
    get:
      tags:
        - Billing
      summary: Get usage details
      description: >-
        Returns the authenticated organization's voice minutes, emails, and text
        messages grouped by workflow between the inclusive start and end
        datetimes. Filter by one or more workflow IDs using repeated use_case_id
        parameters or a comma-separated list; omit the filter to include all
        workflows.
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
        - schema:
            anyOf:
              - type: string
                minLength: 1
              - type: array
                items:
                  type: string
                  minLength: 1
          in: query
          name: use_case_id
          required: false
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
                  useCases:
                    type: array
                    items:
                      type: object
                      properties:
                        totalMinutes:
                          type: number
                        totalEmails:
                          type: number
                        totalText:
                          type: number
                        useCaseName:
                          type: string
                        useCaseId:
                          type: string
                      required:
                        - totalMinutes
                        - totalEmails
                        - totalText
                        - useCaseName
                        - useCaseId
                      additionalProperties: false
                required:
                  - customerId
                  - startDate
                  - endDate
                  - useCases
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

Fuente original: https://docs.happyrobot.ai/api-reference/billing/get-usage-details
