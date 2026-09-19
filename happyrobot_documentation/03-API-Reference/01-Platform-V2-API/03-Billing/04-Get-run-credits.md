---
title: "Get run credits"
description: "Returns credit consumption for a single run, broken down with the same L1 -> L2 -> L3 component taxonomy as Get credits (category -> subcomponents). Scoped to the authenticated organization via API key."
---

# Get run credits

> Returns credit consumption for a single run, broken down with the same L1 -> L2 -> L3 component taxonomy as Get credits (category -> subcomponents). Scoped to the authenticated organization via API key.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /billing/usage/runs/{run_id}
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
  /billing/usage/runs/{run_id}:
    get:
      tags:
        - Billing
      summary: Get run credits
      description: >-
        Returns credit consumption for a single run, broken down with the same
        L1 -> L2 -> L3 component taxonomy as Get credits (category ->
        subcomponents). Scoped to the authenticated organization via API key.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: run_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  run_id:
                    type: string
                  workflow_id:
                    type: string
                  unit:
                    type: string
                    enum:
                      - credits
                  total_credits:
                    type: number
                  components:
                    type: array
                    items:
                      type: object
                      properties:
                        category:
                          type: string
                        credits:
                          type: number
                        subcomponents:
                          type: array
                          items:
                            type: object
                            properties:
                              name:
                                type: string
                              credits:
                                type: number
                              subcomponents:
                                type: array
                                items:
                                  type: object
                                  properties:
                                    name:
                                      type: string
                                    credits:
                                      type: number
                                  required:
                                    - name
                                    - credits
                                  additionalProperties: false
                            required:
                              - name
                              - credits
                            additionalProperties: false
                      required:
                        - category
                        - credits
                        - subcomponents
                      additionalProperties: false
                required:
                  - run_id
                  - workflow_id
                  - unit
                  - total_credits
                  - components
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
        '404':
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

Fuente original: https://docs.happyrobot.ai/api-reference/billing/get-run-credits
