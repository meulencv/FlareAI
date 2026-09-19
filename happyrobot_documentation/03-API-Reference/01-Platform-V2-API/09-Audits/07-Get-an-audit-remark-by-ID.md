---
title: "Get an audit remark by ID"
description: "Returns a single behavioral audit remark, including its northstar criterion, grade, correction, evaluated messages, and status."
---

# Get an audit remark by ID

> Returns a single behavioral audit remark, including its northstar criterion, grade, correction, evaluated messages, and status.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /audit-remarks/{audit_remark_id}
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
  /audit-remarks/{audit_remark_id}:
    get:
      tags:
        - Audits
      summary: Get an audit remark by ID
      description: >-
        Returns a single behavioral audit remark, including its northstar
        criterion, grade, correction, evaluated messages, and status.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: audit_remark_id
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
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  run_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  run_url:
                    type: string
                  timestamp:
                    type: string
                  updated_at:
                    type: string
                  grade:
                    type: string
                    enum:
                      - passed
                      - failed
                      - not_applicable
                  passed:
                    nullable: true
                    type: boolean
                  status:
                    type: string
                    enum:
                      - open
                      - resolved
                      - dismissed
                  category:
                    type: string
                  northstar_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  northstar_name:
                    type: string
                  use_case_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  node_id:
                    nullable: true
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  message_ids:
                    type: array
                    items:
                      type: string
                  messages:
                    type: array
                    items:
                      type: object
                      properties:
                        role:
                          type: string
                        content:
                          type: string
                      required:
                        - role
                        - content
                      additionalProperties: false
                  correction:
                    nullable: true
                    type: string
                  correction_reason:
                    nullable: true
                    type: string
                  org_id:
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  is_e2e_test:
                    type: boolean
                  user_feedback:
                    nullable: true
                    type: object
                    properties:
                      polarity:
                        type: boolean
                      issue_attribution:
                        nullable: true
                        type: string
                    required:
                      - polarity
                      - issue_attribution
                    additionalProperties: false
                required:
                  - id
                  - run_id
                  - run_url
                  - timestamp
                  - updated_at
                  - grade
                  - status
                  - category
                  - northstar_id
                  - northstar_name
                  - use_case_id
                  - node_id
                  - message_ids
                  - messages
                  - correction
                  - correction_reason
                  - org_id
                  - is_e2e_test
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

Fuente original: https://docs.happyrobot.ai/api-reference/audits/get-an-audit-remark-by-id
