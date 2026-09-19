---
title: "Get e2e scenarios"
---

# Get e2e scenarios



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /e2e-scenarios/
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
  /e2e-scenarios/:
    get:
      tags:
        - E2E Scenarios
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: query
          name: use_case_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  scenarios:
                    type: array
                    items:
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
                        target_use_case_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        target_agent_node_persistent_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        suite_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        folder_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        mode:
                          type: string
                          enum:
                            - ''
                            - whole_run
                            - agent_isolated
                        source_run_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        graph_path:
                          nullable: true
                          type: array
                          items:
                            type: string
                        graph_artifact_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        seeds:
                          nullable: true
                          type: array
                          items:
                            type: object
                            properties:
                              persistent_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                              input:
                                type: object
                                additionalProperties: {}
                              data: {}
                              node_name:
                                type: string
                              node_order:
                                type: integer
                                minimum: -9007199254740991
                                maximum: 9007199254740991
                              kind:
                                type: string
                                enum:
                                  - trigger
                                  - context
                              target_agent_persistent_ids:
                                type: array
                                items:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                              source_input:
                                type: object
                                additionalProperties: {}
                              source_data:
                                type: object
                                additionalProperties: {}
                            required:
                              - persistent_id
                              - data
                            additionalProperties: false
                        target_environment:
                          type: string
                          enum:
                            - staging
                            - production
                            - development
                        grading_scope:
                          oneOf:
                            - type: object
                              properties:
                                mode:
                                  type: string
                                  enum:
                                    - all
                              required:
                                - mode
                              additionalProperties: false
                            - type: object
                              properties:
                                mode:
                                  type: string
                                  enum:
                                    - by_category
                                categories:
                                  minItems: 1
                                  type: array
                                  items:
                                    type: string
                                    enum:
                                      - notes
                                      - style
                                      - contradiction
                                      - tool
                                      - sequential
                              required:
                                - mode
                                - categories
                              additionalProperties: false
                        name:
                          type: string
                        description:
                          nullable: true
                          type: string
                        adversarial_prompt:
                          type: string
                        adversarial_model:
                          type: string
                        opening_message:
                          nullable: true
                          type: string
                        variables:
                          anyOf:
                            - anyOf:
                                - type: string
                                - type: number
                                - type: boolean
                                - type: string
                                  nullable: true
                                  enum:
                                    - null
                            - type: object
                              additionalProperties: {}
                            - type: array
                              items: {}
                        max_adversary_messages:
                          type: integer
                          minimum: -2147483648
                          maximum: 2147483647
                        timeout_seconds:
                          type: integer
                          minimum: -2147483648
                          maximum: 2147483647
                        secondary_personas:
                          nullable: true
                          type: array
                          items:
                            type: object
                            properties:
                              agent_persistent_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                              prompt:
                                type: string
                                minLength: 1
                              model:
                                type: string
                                maxLength: 128
                              max_messages:
                                type: integer
                                minimum: 1
                                maximum: 100
                            required:
                              - agent_persistent_id
                              - prompt
                            additionalProperties: false
                        is_deleted:
                          type: boolean
                        created_by:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        created_by_api_key:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        created_by_entity:
                          nullable: true
                          type: string
                          enum:
                            - api_key
                            - user
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
                      required:
                        - id
                        - org_id
                        - target_use_case_id
                        - target_agent_node_persistent_id
                        - suite_id
                        - folder_id
                        - mode
                        - source_run_id
                        - graph_path
                        - graph_artifact_id
                        - seeds
                        - target_environment
                        - grading_scope
                        - name
                        - description
                        - adversarial_prompt
                        - adversarial_model
                        - opening_message
                        - variables
                        - max_adversary_messages
                        - timeout_seconds
                        - secondary_personas
                        - is_deleted
                        - created_by
                        - created_by_api_key
                        - created_by_entity
                        - created_at
                        - updated_at
                      additionalProperties: false
                required:
                  - scenarios
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

Fuente original: https://docs.happyrobot.ai/api-reference/e2e-scenarios/get-e2e-scenarios
