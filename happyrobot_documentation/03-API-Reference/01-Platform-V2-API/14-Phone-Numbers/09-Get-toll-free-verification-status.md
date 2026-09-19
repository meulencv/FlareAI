---
title: "Get toll-free verification status"
description: "Returns toll-free verification status and submitted data for a phone number. Returns 204 when no verification exists."
---

# Get toll-free verification status

> Returns toll-free verification status and submitted data for a phone number. Returns 204 when no verification exists.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /phone-numbers/tollfree-verification
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
    get:
      tags:
        - Phone Numbers
      summary: Get toll-free verification status
      description: >-
        Returns toll-free verification status and submitted data for a phone
        number. Returns 204 when no verification exists.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: phone_number_id
          required: true
          description: Phone number ID (Twilio SID or Telnyx ID)
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                  sid:
                    type: string
                  business_name:
                    type: string
                  business_website:
                    type: string
                  notification_email:
                    type: string
                  tollfree_phone_number_sid:
                    type: string
                  business_street_address:
                    type: string
                  business_street_address_2:
                    type: string
                  business_city:
                    type: string
                  business_state_province:
                    type: string
                  business_postal_code:
                    type: string
                  business_country:
                    type: string
                  workflow_categories:
                    type: array
                    items:
                      type: string
                  workflow_summary:
                    type: string
                  message_volume:
                    type: string
                  business_contact_email:
                    type: string
                  business_contact_first_name:
                    type: string
                  business_contact_last_name:
                    type: string
                  business_contact_phone:
                    type: string
                  production_message_sample:
                    type: string
                  opt_in_type:
                    type: string
                  opt_in_image_urls:
                    type: array
                    items:
                      type: string
                  additional_information:
                    type: string
                  date_created:
                    type: string
                  date_updated:
                    type: string
                additionalProperties: false
        '204':
          description: No verification exists
          content:
            application/json:
              schema:
                description: No verification exists
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

Fuente original: https://docs.happyrobot.ai/api-reference/phone-numbers/get-toll-free-verification-status
