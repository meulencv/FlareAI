---
title: "Get e2e scenarios runs"
---

# Get e2e scenarios runs



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /e2e-scenarios/{scenario_id}/runs
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
  /e2e-scenarios/{scenario_id}/runs:
    get:
      tags:
        - E2E Scenarios
      parameters:
        - schema:
            type: integer
            minimum: 1
            maximum: 100
          in: query
          name: limit
          required: false
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: scenario_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  runs:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        scenario_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        suite_run_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        target_version_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        target_run_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        status:
                          type: string
                          maxLength: 32
                        error_code:
                          nullable: true
                          type: string
                          maxLength: 64
                        error_message:
                          nullable: true
                          type: string
                        created_by:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        created_at:
                          type: string
                          format: date-time
                          pattern: >-
                            ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
                        updated_at:
                          type: string
                          format: date-time
                          pattern: >-
                            ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
                        started_at:
                          nullable: true
                          type: string
                          format: date-time
                          pattern: >-
                            ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
                        completed_at:
                          nullable: true
                          type: string
                          format: date-time
                          pattern: >-
                            ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
                        legacy_run_id:
                          type: string
                        target_version_name:
                          nullable: true
                          type: string
                        target_version_number:
                          nullable: true
                          type: number
                        target_version_is_live:
                          nullable: true
                          type: boolean
                        target_run_status:
                          nullable: true
                          type: string
                        result_state:
                          type: string
                          enum:
                            - waiting
                            - generating
                            - audit_failed
                            - failed
                            - passed
                            - inconclusive
                        audit_status:
                          nullable: true
                          type: string
                        audit_remarks:
                          type: array
                          items:
                            type: object
                            properties:
                              id:
                                type: string
                              northstar_id:
                                type: string
                              northstar_name:
                                type: string
                              grade:
                                nullable: true
                                type: string
                                enum:
                                  - passed
                                  - failed
                                  - not_applicable
                              correction:
                                nullable: true
                                type: string
                              correction_reason:
                                nullable: true
                                type: string
                            required:
                              - id
                              - northstar_id
                              - northstar_name
                              - grade
                              - correction
                              - correction_reason
                            additionalProperties: false
                      required:
                        - id
                        - scenario_id
                        - suite_run_id
                        - target_version_id
                        - target_run_id
                        - status
                        - error_code
                        - error_message
                        - created_by
                        - created_at
                        - updated_at
                        - started_at
                        - completed_at
                        - target_version_name
                        - target_version_number
                        - target_version_is_live
                        - target_run_status
                        - result_state
                        - audit_status
                        - audit_remarks
                      additionalProperties: false
                required:
                  - runs
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

Fuente original: https://docs.happyrobot.ai/api-reference/e2e-scenarios/get-e2e-scenarios-runs
