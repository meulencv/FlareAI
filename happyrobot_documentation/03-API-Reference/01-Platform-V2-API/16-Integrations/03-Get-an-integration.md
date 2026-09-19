---
title: "Get an integration"
description: "Returns a single integration by ID, including its events and the organization's connected credentials. Supports both native integration UUIDs and delegated provider composite IDs (e.g. {uuid}--{provider_slug})."
---

# Get an integration

> Returns a single integration by ID, including its events and the organization's connected credentials. Supports both native integration UUIDs and delegated provider composite IDs (e.g. {uuid}--{provider_slug}).



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /integrations/{integrationId}
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
  /integrations/{integrationId}:
    get:
      tags:
        - Integrations
      summary: Get an integration
      description: >-
        Returns a single integration by ID, including its events and the
        organization's connected credentials. Supports both native integration
        UUIDs and delegated provider composite IDs (e.g.
        {uuid}--{provider_slug}).
      parameters:
        - schema:
            type: string
          in: path
          name: integrationId
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  id:
                    type: string
                  name:
                    type: string
                  group:
                    type: string
                  icon:
                    type: string
                  description:
                    type: string
                  docs_url:
                    type: string
                  website_url:
                    type: string
                  is_top:
                    type: boolean
                  requires_credentials:
                    type: boolean
                  agent_specific:
                    type: boolean
                  events:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                        name:
                          type: string
                        integration_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                        type:
                          type: integer
                          minimum: -9007199254740991
                          maximum: 9007199254740991
                          description: 0 = trigger, 1 = action
                        description:
                          type: string
                        is_instant:
                          type: boolean
                        has_cron_trigger:
                          type: boolean
                        coming_soon:
                          type: boolean
                        config_schema:
                          nullable: true
                          type: array
                          items: ea78b2e6-58ae-4dda-9e9a-e4b00bfe3b32
                        delegated_category:
                          description: >-
                            Non-null for delegated provider events (e.g. 'crm',
                            'hris'). When present, the node configuration must
                            include _merge_provider_slug.
                          nullable: true
                          type: string
                      required:
                        - id
                        - name
                        - integration_id
                        - type
                        - description
                        - is_instant
                        - has_cron_trigger
                        - coming_soon
                      additionalProperties: false
                  credentials:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        integration_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                        title:
                          type: string
                        timestamp:
                          type: string
                      required:
                        - id
                        - integration_id
                        - title
                        - timestamp
                      additionalProperties: false
                  credential_config:
                    nullable: true
                    type: object
                    properties:
                      credential_types:
                        type: array
                        items:
                          type: object
                          properties:
                            type:
                              type: string
                            display_name:
                              type: string
                            description:
                              type: string
                            flow:
                              type: string
                              enum:
                                - oauth
                                - form
                            fields:
                              type: array
                              items:
                                type: object
                                properties:
                                  name:
                                    type: string
                                  label:
                                    type: string
                                  type:
                                    type: string
                                    enum:
                                      - string
                                      - password
                                      - email
                                      - number
                                      - boolean
                                      - select
                                  required:
                                    type: boolean
                                  description:
                                    type: string
                                  options:
                                    type: array
                                    items:
                                      type: string
                                required:
                                  - name
                                  - label
                                  - type
                                  - required
                                additionalProperties: false
                          required:
                            - type
                            - display_name
                            - description
                            - flow
                            - fields
                          additionalProperties: false
                      default_credential_type:
                        type: string
                    required:
                      - credential_types
                      - default_credential_type
                    additionalProperties: false
                required:
                  - id
                  - name
                  - group
                  - icon
                  - description
                  - docs_url
                  - website_url
                  - is_top
                  - requires_credentials
                  - agent_specific
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

Fuente original: https://docs.happyrobot.ai/api-reference/integrations/get-an-integration
