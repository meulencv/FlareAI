---
title: "List integration categories with providers"
description: "Returns a unified map of categories to their available providers. Includes both internal integration groups (Communications, Data, etc.) and delegated provider categories (CRM, HRIS, ATS, etc.)."
---

# List integration categories with providers

> Returns a unified map of categories to their available providers. Includes both internal integration groups (Communications, Data, etc.) and delegated provider categories (CRM, HRIS, ATS, etc.).



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /integrations/categories
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
  /integrations/categories:
    get:
      tags:
        - Integrations
      summary: List integration categories with providers
      description: >-
        Returns a unified map of categories to their available providers.
        Includes both internal integration groups (Communications, Data, etc.)
        and delegated provider categories (CRM, HRIS, ATS, etc.).
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: object
                    additionalProperties:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: string
                          name:
                            type: string
                          slug:
                            type: string
                          icon:
                            nullable: true
                            type: string
                        required:
                          - id
                          - name
                          - slug
                          - icon
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

Fuente original: https://docs.happyrobot.ai/api-reference/integrations/list-integration-categories-with-providers
