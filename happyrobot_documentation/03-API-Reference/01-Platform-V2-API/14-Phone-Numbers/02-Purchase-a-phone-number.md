---
title: "Purchase a phone number"
description: "Purchases a new phone number from Twilio or Telnyx. For toll-free numbers (US/CA only), also submits toll-free verification. Rate limited to one purchase every 10 minutes per organization. Send force=true in the body to bypass this limit (use with caution — each number has a recurring monthly cost)."
---

# Purchase a phone number

> Purchases a new phone number from Twilio or Telnyx. For toll-free numbers (US/CA only), also submits toll-free verification. Rate limited to one purchase every 10 minutes per organization. Send force=true in the body to bypass this limit (use with caution — each number has a recurring monthly cost).



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /phone-numbers/
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
    post:
      tags:
        - Phone Numbers
      summary: Purchase a phone number
      description: >-
        Purchases a new phone number from Twilio or Telnyx. For toll-free
        numbers (US/CA only), also submits toll-free verification. Rate limited
        to one purchase every 10 minutes per organization. Send force=true in
        the body to bypass this limit (use with caution — each number has a
        recurring monthly cost).
      requestBody:
        content:
          application/json:
            schema:
              oneOf:
                - type: object
                  properties:
                    name:
                      type: string
                      minLength: 1
                    area_code:
                      type: string
                    number_type:
                      type: string
                      enum:
                        - regular
                        - toll_free
                    provider:
                      type: string
                      enum:
                        - twilio
                    country_code:
                      default: US
                      type: string
                      minLength: 2
                      maxLength: 2
                    phone_number_type:
                      type: string
                      enum:
                        - local
                        - toll_free
                        - national
                        - mobile
                    bundle_id:
                      nullable: true
                      type: string
                    address_sid:
                      nullable: true
                      type: string
                    business_profile_application_id:
                      description: >-
                        Approved Twilio Compliance Business Profile application
                        ID. Only used when provider is twilio; US Twilio numbers
                        without one cannot call US destinations until a Business
                        Profile is assigned.
                      nullable: true
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    force:
                      description: >-
                        Set to true to bypass the 10-minute rate limit between
                        phone number purchases. Use with caution: each phone
                        number incurs a recurring monthly cost.
                      type: boolean
                    tag_ids:
                      description: >-
                        Tag IDs to assign to the purchased number. Under
                        tag-based access scopes, a tag-restricted principal must
                        supply at least one tag within their own scope — an
                        untagged purchase is otherwise invisible to them.
                        Full-access principals may omit this.
                      type: array
                      items:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    sms_url:
                      type: string
                    sms_method:
                      default: POST
                      type: string
                      enum:
                        - POST
                        - GET
                    sms_fallback_url:
                      type: string
                    sms_fallback_method:
                      default: POST
                      type: string
                      enum:
                        - POST
                        - GET
                    business_name:
                      type: string
                    business_website:
                      type: string
                    business_address_line_1:
                      type: string
                    business_address_line_2:
                      type: string
                    business_city:
                      type: string
                    business_state:
                      type: string
                    business_postal_code:
                      type: string
                    business_country:
                      default: US
                      type: string
                    business_type:
                      type: string
                      enum:
                        - PRIVATE_PROFIT
                        - PUBLIC_PROFIT
                        - SOLE_PROPRIETOR
                        - NON_PROFIT
                        - GOVERNMENT
                    business_registration_number:
                      type: string
                    business_registration_authority:
                      type: string
                      enum:
                        - EIN
                        - CBN
                        - CRN
                        - PROVINCIAL_NUMBER
                        - VAT
                        - ACN
                        - ABN
                        - BRN
                        - SIREN
                        - SIRET
                        - NZBN
                        - USt-IdNr
                        - CIF
                        - NIF
                        - CNPJ
                        - UID
                        - NEQ
                        - OTHER
                    business_registration_country:
                      type: string
                      minLength: 2
                      maxLength: 2
                    contact_first_name:
                      type: string
                    contact_last_name:
                      type: string
                    contact_email:
                      type: string
                    contact_phone:
                      type: string
                    notification_email:
                      type: string
                    message_volume:
                      type: string
                    use_categories:
                      type: array
                      items:
                        type: string
                    workflow_summary:
                      type: string
                    production_message_sample:
                      type: string
                    opt_in_type:
                      type: string
                      enum:
                        - VERBAL
                        - WEB_FORM
                        - PAPER_FORM
                        - VIA_TEXT
                        - MOBILE_QR_CODE
                        - IMPORT
                        - IMPORT_PLEASE_REPLACE
                    opt_in_image_url:
                      type: string
                    additional_information:
                      type: string
                  required:
                    - name
                    - number_type
                    - provider
                    - phone_number_type
                - type: object
                  properties:
                    name:
                      type: string
                      minLength: 1
                    area_code:
                      type: string
                    number_type:
                      type: string
                      enum:
                        - regular
                        - toll_free
                    provider:
                      type: string
                      enum:
                        - telnyx
                    country_code:
                      default: US
                      type: string
                      minLength: 2
                      maxLength: 2
                    phone_number_type:
                      type: string
                      enum:
                        - local
                        - toll_free
                        - national
                        - mobile
                    bundle_id:
                      nullable: true
                      type: string
                    address_sid:
                      nullable: true
                      type: string
                    business_profile_application_id:
                      description: >-
                        Approved Twilio Compliance Business Profile application
                        ID. Only used when provider is twilio; US Twilio numbers
                        without one cannot call US destinations until a Business
                        Profile is assigned.
                      nullable: true
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    force:
                      description: >-
                        Set to true to bypass the 10-minute rate limit between
                        phone number purchases. Use with caution: each phone
                        number incurs a recurring monthly cost.
                      type: boolean
                    tag_ids:
                      description: >-
                        Tag IDs to assign to the purchased number. Under
                        tag-based access scopes, a tag-restricted principal must
                        supply at least one tag within their own scope — an
                        untagged purchase is otherwise invisible to them.
                        Full-access principals may omit this.
                      type: array
                      items:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  required:
                    - name
                    - number_type
                    - provider
                    - phone_number_type
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  message:
                    type: string
                  verification_failed:
                    type: boolean
                  setup_price:
                    type: number
                  recurring_price:
                    type: number
                required:
                  - message
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
        '429':
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/purchase-a-phone-number
