---
title: "Update a SIP trunk"
description: "Updates a SIP trunk by ID."
---

# Update a SIP trunk

> Updates a SIP trunk by ID.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json put /sip-trunks/{id}
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
  /sip-trunks/{id}:
    put:
      tags:
        - SIP Trunks
      summary: Update a SIP trunk
      description: Updates a SIP trunk by ID.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: id
          required: true
          description: SIP trunk ID
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                number:
                  type: string
                  minLength: 1
                  pattern: ^\+\d+$
                name:
                  type: string
                  minLength: 1
                address:
                  type: string
                transport:
                  default: udp
                  type: string
                  enum:
                    - udp
                    - tcp
                    - tls
                auth_username:
                  type: string
                auth_password:
                  type: string
                allowed_addresses:
                  type: array
                  items:
                    type: string
                    minLength: 1
                    pattern: >-
                      ^(?:(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)\.){3}(?:25[0-5]|2[0-4]\d|1\d\d|[1-9]?\d)(?:\/(?:3[0-2]|[12]\d|[1-9]))?$
                attributes_to_headers:
                  type: object
                  additionalProperties:
                    type: string
                    minLength: 1
                    pattern: ^[!#$%&'*+\-.^_`|~0-9A-Za-z]+$
                provider:
                  type: string
                  enum:
                    - twilio
                    - telnyx
                    - custom
                direction:
                  default: both
                  type: string
                  enum:
                    - inbound
                    - outbound
                    - both
                tag_ids:
                  type: array
                  items:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                force:
                  description: >-
                    Set to true to bypass the 10-minute rate limit between SIP
                    trunk creations. Use with caution: each SIP trunk incurs a
                    recurring monthly cost.
                  type: boolean
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
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  org_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  number:
                    type: string
                  inbound_trunk_id:
                    nullable: true
                    type: string
                  outbound_trunk_id:
                    nullable: true
                    type: string
                  name:
                    type: string
                  created_at:
                    type: string
                  updated_at:
                    type: string
                required:
                  - id
                  - org_id
                  - number
                  - inbound_trunk_id
                  - outbound_trunk_id
                  - name
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

Fuente original: https://docs.happyrobot.ai/api-reference/sip-trunks/update-a-sip-trunk
