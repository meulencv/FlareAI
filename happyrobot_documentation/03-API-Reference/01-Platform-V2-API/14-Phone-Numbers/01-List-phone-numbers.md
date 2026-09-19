---
title: "List phone numbers"
description: "Returns all phone numbers for the authenticated organization, including Twilio, Telnyx, and SIP trunk numbers with caller ID information."
---

# List phone numbers

> Returns all phone numbers for the authenticated organization, including Twilio, Telnyx, and SIP trunk numbers with caller ID information.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /phone-numbers/
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
  /phone-numbers/:
    get:
      tags:
        - Phone Numbers
      summary: List phone numbers
      description: >-
        Returns all phone numbers for the authenticated organization, including
        Twilio, Telnyx, and SIP trunk numbers with caller ID information.
      parameters:
        - schema:
            type: string
          in: query
          name: restrict
          required: false
          description: >-
            Comma-separated filter values: INBOUND, OUTBOUND_WITH_CALLBACK,
            OUTBOUND_WITH_CALLBACK_STAGING, OUTBOUND_WITH_CALLBACK_DEVELOPMENT,
            ALL
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: array
                items:
                  oneOf:
                    - type: object
                      properties:
                        id:
                          type: string
                        name:
                          nullable: true
                          type: string
                        number:
                          type: string
                        caller_id:
                          type: string
                          enum:
                            - us
                            - them
                        toll_free_verification:
                          type: object
                          properties:
                            status:
                              type: string
                          additionalProperties: false
                        type:
                          type: string
                          enum:
                            - twilio
                        has_sip_trunk_in_preferred_region:
                          type: boolean
                        sip_trunk_status:
                          type: string
                          enum:
                            - valid
                            - invalid
                            - none
                      required:
                        - id
                        - name
                        - number
                        - caller_id
                        - type
                        - has_sip_trunk_in_preferred_region
                        - sip_trunk_status
                      additionalProperties: false
                    - type: object
                      properties:
                        id:
                          type: string
                        name:
                          nullable: true
                          type: string
                        number:
                          type: string
                        caller_id:
                          type: string
                          enum:
                            - us
                            - them
                        toll_free_verification:
                          type: object
                          properties:
                            status:
                              type: string
                          additionalProperties: false
                        type:
                          type: string
                          enum:
                            - telnyx
                      required:
                        - id
                        - name
                        - number
                        - caller_id
                        - type
                      additionalProperties: false
                    - type: object
                      properties:
                        id:
                          type: string
                        name:
                          nullable: true
                          type: string
                        number:
                          type: string
                        caller_id:
                          type: string
                          enum:
                            - us
                            - them
                        toll_free_verification:
                          type: object
                          properties:
                            status:
                              type: string
                          additionalProperties: false
                        type:
                          type: string
                          enum:
                            - sip
                        inbound_trunk_id:
                          nullable: true
                          type: string
                        outbound_trunk_id:
                          nullable: true
                          type: string
                        org_id:
                          type: string
                        created_at:
                          type: string
                        updated_at:
                          type: string
                      required:
                        - id
                        - name
                        - number
                        - caller_id
                        - type
                        - inbound_trunk_id
                        - outbound_trunk_id
                        - org_id
                        - created_at
                        - updated_at
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/list-phone-numbers
