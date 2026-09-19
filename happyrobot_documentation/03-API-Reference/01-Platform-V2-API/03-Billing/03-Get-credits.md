---
title: "Get credits"
description: "Returns the authenticated organization's billable credit consumption by workflow for an inclusive date range, grouped daily, weekly, or monthly. Each row includes the period, full folder path, workflow identity, total credits, and the same L1 → L2 → L3 component breakdown shown in Settings → Usage,…"
---

# Get credits

> Returns the authenticated organization's billable credit consumption by workflow for an inclusive date range, grouped daily, weekly, or monthly. Each row includes the period, full folder path, workflow identity, total credits, and the same L1 → L2 → L3 component breakdown shown in Settings → Usage, including credits, volume, and volume unit. LLM subcomponents also include customer-visible token usage by model, split into input, cache input, cache write, and output tokens. LLM usage includes BYOK calls even when they consume zero HappyRobot credits. Organization-level consumption that is not attributable to a workflow — shown as "Platform & Services" in Settings → Usage — is returned as a row with an empty workflow_id, an empty workflow_name, and an empty folder_path. It is only included for callers with workspace-level usage or billing access, and cannot be selected or excluded through the filters below. Filter by any of the top three folder levels, workflow name, or exact workflow ID. Filters across fields use AND logic; multiple values within one field use OR logic.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /billing/usage/credits
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
  /billing/usage/credits:
    get:
      tags:
        - Billing
      summary: Get credits
      description: >-
        Returns the authenticated organization's billable credit consumption by
        workflow for an inclusive date range, grouped daily, weekly, or monthly.
        Each row includes the period, full folder path, workflow identity, total
        credits, and the same L1 → L2 → L3 component breakdown shown in Settings
        → Usage, including credits, volume, and volume unit. LLM subcomponents
        also include customer-visible token usage by model, split into input,
        cache input, cache write, and output tokens. LLM usage includes BYOK
        calls even when they consume zero HappyRobot credits. Organization-level
        consumption that is not attributable to a workflow — shown as "Platform
        & Services" in Settings → Usage — is returned as a row with an empty
        workflow_id, an empty workflow_name, and an empty folder_path. It is
        only included for callers with workspace-level usage or billing access,
        and cannot be selected or excluded through the filters below. Filter by
        any of the top three folder levels, workflow name, or exact workflow ID.
        Filters across fields use AND logic; multiple values within one field
        use OR logic.
      parameters:
        - schema:
            type: string
            pattern: ^\d{4}-\d{2}-\d{2}$
          in: query
          name: start_date
          required: true
        - schema:
            type: string
            pattern: ^\d{4}-\d{2}-\d{2}$
          in: query
          name: end_date
          required: true
        - schema:
            default: daily
            type: string
            enum:
              - daily
              - weekly
              - monthly
          in: query
          name: granularity
          required: false
        - schema:
            anyOf:
              - type: string
              - type: array
                items:
                  type: string
          in: query
          name: filter_by_folder_1
          required: false
        - schema:
            anyOf:
              - type: string
              - type: array
                items:
                  type: string
          in: query
          name: filter_by_folder_2
          required: false
        - schema:
            anyOf:
              - type: string
              - type: array
                items:
                  type: string
          in: query
          name: filter_by_folder_3
          required: false
        - schema:
            anyOf:
              - type: string
              - type: array
                items:
                  type: string
          in: query
          name: filter_by_workflow
          required: false
        - schema:
            anyOf:
              - type: string
              - type: array
                items:
                  type: string
          in: query
          name: filter_by_workflow_id
          required: false
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  workspace_name:
                    type: string
                  start_date:
                    type: string
                  end_date:
                    type: string
                  granularity:
                    type: string
                  unit:
                    type: string
                    enum:
                      - credits
                  data:
                    type: array
                    items:
                      type: object
                      properties:
                        period:
                          type: string
                        folder_path:
                          type: array
                          items:
                            type: string
                        workflow_id:
                          type: string
                        workflow_name:
                          type: string
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
                                    volume:
                                      type: number
                                    volume_unit:
                                      type: string
                                    usage:
                                      type: array
                                      items:
                                        type: object
                                        properties:
                                          model:
                                            type: string
                                          input_tokens:
                                            type: integer
                                            minimum: 0
                                            maximum: 9007199254740991
                                          cache_input_tokens:
                                            type: integer
                                            minimum: 0
                                            maximum: 9007199254740991
                                          cache_write_tokens:
                                            type: integer
                                            minimum: 0
                                            maximum: 9007199254740991
                                          output_tokens:
                                            type: integer
                                            minimum: 0
                                            maximum: 9007199254740991
                                        required:
                                          - model
                                          - input_tokens
                                          - cache_input_tokens
                                          - cache_write_tokens
                                          - output_tokens
                                        additionalProperties: false
                                    subcomponents:
                                      type: array
                                      items:
                                        type: object
                                        properties:
                                          name:
                                            type: string
                                          credits:
                                            type: number
                                          volume:
                                            type: number
                                          volume_unit:
                                            type: string
                                          usage:
                                            type: array
                                            items:
                                              type: object
                                              properties:
                                                model:
                                                  type: string
                                                input_tokens:
                                                  type: integer
                                                  minimum: 0
                                                  maximum: 9007199254740991
                                                cache_input_tokens:
                                                  type: integer
                                                  minimum: 0
                                                  maximum: 9007199254740991
                                                cache_write_tokens:
                                                  type: integer
                                                  minimum: 0
                                                  maximum: 9007199254740991
                                                output_tokens:
                                                  type: integer
                                                  minimum: 0
                                                  maximum: 9007199254740991
                                              required:
                                                - model
                                                - input_tokens
                                                - cache_input_tokens
                                                - cache_write_tokens
                                                - output_tokens
                                              additionalProperties: false
                                        required:
                                          - name
                                          - credits
                                          - volume
                                          - volume_unit
                                        additionalProperties: false
                                  required:
                                    - name
                                    - credits
                                    - volume
                                    - volume_unit
                                  additionalProperties: false
                            required:
                              - category
                              - credits
                              - subcomponents
                            additionalProperties: false
                        total_credits:
                          type: number
                      required:
                        - period
                        - folder_path
                        - workflow_id
                        - workflow_name
                        - components
                        - total_credits
                      additionalProperties: false
                required:
                  - workspace_name
                  - start_date
                  - end_date
                  - granularity
                  - unit
                  - data
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
        '503':
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

Fuente original: https://docs.happyrobot.ai/api-reference/billing/get-credits
