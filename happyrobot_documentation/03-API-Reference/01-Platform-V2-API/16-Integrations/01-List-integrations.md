---
title: "List integrations"
description: "Returns available integrations with optional events and credentials. Delegated providers (CRM, HRIS, ATS, etc.) are expanded into individual entries. Supports filtering by category, provider, and search. Paginated (default: 20 per page)."
---

# List integrations

> Returns available integrations with optional events and credentials. Delegated providers (CRM, HRIS, ATS, etc.) are expanded into individual entries. Supports filtering by category, provider, and search. Paginated (default: 20 per page).



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /integrations/
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
  /integrations/:
    get:
      tags:
        - Integrations
      summary: List integrations
      description: >-
        Returns available integrations with optional events and credentials.
        Delegated providers (CRM, HRIS, ATS, etc.) are expanded into individual
        entries. Supports filtering by category, provider, and search. Paginated
        (default: 20 per page).
      parameters:
        - schema:
            type: string
          in: query
          name: search
          required: false
        - schema:
            type: string
          in: query
          name: category
          required: false
          description: >-
            Filter by category. Works for both internal groups (e.g.
            'Communications', 'Data') and delegated categories (e.g. 'crm',
            'hris', 'ats'). Case-insensitive.
        - schema:
            type: string
          in: query
          name: provider
          required: false
          description: >-
            Filter by provider slug. Works for both internal integrations (e.g.
            'gmail', 'slack') and delegated providers (e.g. 'hubspot',
            'workday').
        - schema:
            type: string
            enum:
              - 'true'
              - 'false'
          in: query
          name: include_events
          required: false
          description: 'If true, include events per integration (default: false)'
        - schema:
            type: string
            enum:
              - 'true'
              - 'false'
          in: query
          name: include_credentials
          required: false
          description: >-
            If true, include the organization's connected credentials per
            integration (default: false)
        - schema:
            type: string
            enum:
              - 'true'
              - 'false'
          in: query
          name: include_config_schema
          required: false
          description: >-
            If true, include config_schema per event. Only effective when
            include_events=true (default: false)
        - schema:
            default: 1
            type: integer
            minimum: 1
            maximum: 9007199254740991
          in: query
          name: page
          required: false
        - schema:
            default: 20
            type: integer
            minimum: 1
            maximum: 100
          in: query
          name: page_size
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
                                  Non-null for delegated provider events (e.g.
                                  'crm', 'hris'). When present, the node
                                  configuration must include
                                  _merge_provider_slug.
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
                  pagination:
                    type: object
                    properties:
                      page:
                        type: number
                      page_size:
                        type: number
                      total_pages:
                        type: number
                      total_records:
                        type: number
                      has_next_page:
                        type: boolean
                      has_previous_page:
                        type: boolean
                    required:
                      - page
                      - page_size
                      - total_pages
                      - total_records
                      - has_next_page
                      - has_previous_page
                    additionalProperties: false
                required:
                  - data
                  - pagination
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

Fuente original: https://docs.happyrobot.ai/api-reference/integrations/list-integrations
