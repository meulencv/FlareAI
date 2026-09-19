---
title: "Get config schema for an event"
description: "Returns the configuration schema for an event, including field types, required fields, defaults, and available options. Use this to inspect what an event expects before creating a node."
---

# Get config schema for an event

> Returns the configuration schema for an event, including field types, required fields, defaults, and available options. Use this to inspect what an event expects before creating a node.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /events/{event_id}/config-schema
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
  /events/{event_id}/config-schema:
    get:
      tags:
        - Events
      summary: Get config schema for an event
      description: >-
        Returns the configuration schema for an event, including field types,
        required fields, defaults, and available options. Use this to inspect
        what an event expects before creating a node.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
          in: query
          name: use_case_id
          required: false
          description: >-
            Workflow UUID this event is being configured for. Credentials are
            scoped to a workflow's tags, so pass it to see only the credentials
            that workflow may use.
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
          in: path
          name: event_id
          required: true
          description: The event ID
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
                    properties:
                      event_id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                      event_name:
                        type: string
                      fields:
                        type: array
                        items: e522fd6b-68e7-4164-ab64-32bc6b266a32
                      defaults:
                        nullable: true
                        type: object
                        additionalProperties: {}
                      available_options:
                        nullable: true
                        type: object
                        properties:
                          models:
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
                              required:
                                - id
                                - name
                              additionalProperties: false
                          phone_numbers:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                name:
                                  type: string
                                number:
                                  type: string
                              required:
                                - id
                                - name
                                - number
                              additionalProperties: false
                          voices:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                name:
                                  type: string
                                language:
                                  type: string
                                gender:
                                  type: string
                              required:
                                - id
                                - name
                                - language
                                - gender
                              additionalProperties: false
                          languages:
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
                          credentials:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                title:
                                  type: string
                              required:
                                - id
                                - title
                              additionalProperties: false
                        additionalProperties: false
                    required:
                      - event_id
                      - event_name
                      - fields
                      - defaults
                      - available_options
                    additionalProperties: false
                required:
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

Fuente original: https://docs.happyrobot.ai/api-reference/events/get-config-schema-for-an-event
