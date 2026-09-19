---
title: "Submit toll-free verification"
description: "Submits a toll-free verification request for a phone number. Requires business_name, notification_email, and sms_url."
---

# Submit toll-free verification

> Submits a toll-free verification request for a phone number. Requires business_name, notification_email, and sms_url.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /phone-numbers/tollfree-verification
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
  /phone-numbers/tollfree-verification:
    post:
      tags:
        - Phone Numbers
      summary: Submit toll-free verification
      description: >-
        Submits a toll-free verification request for a phone number. Requires
        business_name, notification_email, and sms_url.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: phone_number_id
          required: true
          description: Phone number ID (Twilio SID or Telnyx ID)
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                business_name:
                  type: string
                  minLength: 1
                notification_email:
                  type: string
                  minLength: 1
                  format: email
                  pattern: >-
                    ^(?!\.)(?!.*\.\.)([A-Za-z0-9_'+\-\.]*)[A-Za-z0-9_+-]@([A-Za-z0-9][A-Za-z0-9\-]*\.)+[A-Za-z]{2,}$
                sms_url:
                  type: string
                  minLength: 1
                  format: uri
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
                compliance_action:
                  type: string
                  enum:
                    - ordering
                    - porting
                bundle_id:
                  nullable: true
                  type: string
                address_sid:
                  nullable: true
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
                business_website:
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
                contact_first_name:
                  type: string
                contact_last_name:
                  type: string
                contact_email:
                  type: string
                contact_phone:
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
                - business_name
                - notification_email
                - sms_url
                - phone_number_type
        required: true
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/submit-toll-free-verification
