---
title: "Get test suitesruns"
---

# Get test suitesruns



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /test-suites/runs/{run_id}
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
  /test-suites/runs/{run_id}:
    get:
      tags:
        - Test Suites
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: run_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  run:
                    type: object
                    properties:
                      id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                      suite_id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                      status:
                        type: string
                      total_tests:
                        type: integer
                        minimum: -2147483648
                        maximum: 2147483647
                      completed_tests:
                        type: integer
                        minimum: -2147483648
                        maximum: 2147483647
                      passed_tests:
                        type: integer
                        minimum: -2147483648
                        maximum: 2147483647
                      failed_tests:
                        type: integer
                        minimum: -2147483648
                        maximum: 2147483647
                      workflow_id:
                        nullable: true
                        type: string
                      version_id:
                        nullable: true
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
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
                      created_at:
                        type: string
                        format: date-time
                        pattern: >-
                          ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
                      version_name:
                        nullable: true
                        type: string
                      version_number:
                        nullable: true
                        type: number
                    required:
                      - id
                      - suite_id
                      - status
                      - total_tests
                      - completed_tests
                      - passed_tests
                      - failed_tests
                      - workflow_id
                      - version_id
                      - started_at
                      - completed_at
                      - created_at
                      - version_name
                      - version_number
                    additionalProperties: false
                  results:
                    type: array
                    items:
                      type: object
                      properties:
                        kind:
                          type: string
                          enum:
                            - custom
                            - adversarial
                            - e2e
                        id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        test_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        name:
                          type: string
                        status:
                          type: string
                        passed:
                          nullable: true
                          type: boolean
                        error:
                          nullable: true
                          type: string
                        created_at:
                          type: string
                          format: date-time
                          pattern: >-
                            ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
                        target_run_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        result_state:
                          nullable: true
                          type: string
                          enum:
                            - waiting
                            - generating
                            - audit_failed
                            - passed
                            - failed
                            - inconclusive
                      required:
                        - kind
                        - id
                        - test_id
                        - name
                        - status
                        - passed
                        - error
                        - created_at
                        - target_run_id
                        - result_state
                      additionalProperties: false
                required:
                  - run
                  - results
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

Fuente original: https://docs.happyrobot.ai/api-reference/test-suites/get-test-suitesruns
