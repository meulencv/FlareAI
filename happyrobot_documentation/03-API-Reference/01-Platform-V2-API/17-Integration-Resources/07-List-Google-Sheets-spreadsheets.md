---
title: "List Google Sheets spreadsheets"
description: "Returns Google Sheets spreadsheets accessible with the organization's credentials. Supports search and cursor-based pagination."
---

# List Google Sheets spreadsheets

> Returns Google Sheets spreadsheets accessible with the organization's credentials. Supports search and cursor-based pagination.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /integrations/google-sheets/spreadsheets
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
  /integrations/google-sheets/spreadsheets:
    get:
      tags:
        - Integration Resources
      summary: List Google Sheets spreadsheets
      description: >-
        Returns Google Sheets spreadsheets accessible with the organization's
        credentials. Supports search and cursor-based pagination.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: query
          name: credential_id
          required: false
        - schema:
            type: string
          in: query
          name: search
          required: false
        - schema:
            type: string
          in: query
          name: page_token
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
                      required:
                        - id
                        - name
                      additionalProperties: false
                  next_page_token:
                    type: string
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

Fuente original: https://docs.happyrobot.ai/api-reference/integration-resources/list-google-sheets-spreadsheets
