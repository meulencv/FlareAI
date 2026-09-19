---
title: "Post test suites"
---

# Post test suites



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /test-suites/
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
  /test-suites/:
    post:
      tags:
        - Test Suites
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                useCaseId:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                name:
                  type: string
                  minLength: 1
                  maxLength: 256
                description:
                  nullable: true
                  type: string
                origin:
                  default: manual
                  type: string
                  enum:
                    - manual
                    - ai_assisted
                generationConfig:
                  default: null
                  nullable: true
                  type: object
                  properties:
                    prompt:
                      type: string
                    count:
                      type: integer
                      minimum: 1
                      maximum: 10
                    kinds:
                      minItems: 1
                      type: array
                      items:
                        type: string
                        enum:
                          - custom
                          - e2e
                    targets:
                      type: array
                      items:
                        oneOf:
                          - type: object
                            properties:
                              kind:
                                type: string
                                enum:
                                  - custom
                              prompt_node_persistent_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                              judge_model:
                                type: string
                                minLength: 1
                            required:
                              - kind
                              - prompt_node_persistent_id
                            additionalProperties: false
                          - type: object
                            properties:
                              kind:
                                type: string
                                enum:
                                  - e2e
                              agent_node_persistent_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                              template_scenario_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                              model:
                                type: string
                                minLength: 1
                              timeout_seconds:
                                type: integer
                                minimum: 30
                                maximum: 3600
                            required:
                              - kind
                            additionalProperties: false
                    source_version_id:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    e2e_settings:
                      type: object
                      properties:
                        adversarial_model:
                          type: string
                          minLength: 1
                        target_environment:
                          type: string
                          enum:
                            - development
                            - staging
                            - production
                        timeout_seconds:
                          type: integer
                          minimum: 30
                          maximum: 3600
                        max_adversary_messages:
                          type: integer
                          minimum: 1
                          maximum: 100
                      required:
                        - adversarial_model
                        - target_environment
                        - timeout_seconds
                        - max_adversary_messages
                      additionalProperties: false
                  additionalProperties: false
                coverageScope:
                  default:
                    mode: all
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
                          type: array
                          items:
                            type: string
                      required:
                        - mode
                        - categories
                      additionalProperties: false
                    - type: object
                      properties:
                        mode:
                          type: string
                          enum:
                            - selected
                        northstar_ids:
                          type: array
                          items:
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                      required:
                        - mode
                        - northstar_ids
                      additionalProperties: false
                folderId:
                  nullable: true
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                members:
                  default: []
                  type: array
                  items:
                    type: object
                    properties:
                      kind:
                        type: string
                        enum:
                          - custom
                          - e2e
                      id:
                        type: string
                        format: uuid
                        pattern: >-
                          ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                    required:
                      - kind
                      - id
              required:
                - useCaseId
                - name
        required: true
      responses:
        '201':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  suite:
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
                      use_case_id:
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
                      name:
                        type: string
                      description:
                        nullable: true
                        type: string
                      origin:
                        type: string
                      generation_config:
                        nullable: true
                        type: object
                        properties:
                          prompt:
                            type: string
                          count:
                            type: integer
                            minimum: 1
                            maximum: 100
                          kinds:
                            minItems: 1
                            type: array
                            items:
                              type: string
                              enum:
                                - custom
                                - e2e
                          targets:
                            type: array
                            items:
                              oneOf:
                                - type: object
                                  properties:
                                    kind:
                                      type: string
                                      enum:
                                        - custom
                                    prompt_node_persistent_id:
                                      type: string
                                      format: uuid
                                      pattern: >-
                                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                    judge_model:
                                      type: string
                                      minLength: 1
                                  required:
                                    - kind
                                    - prompt_node_persistent_id
                                  additionalProperties: false
                                - type: object
                                  properties:
                                    kind:
                                      type: string
                                      enum:
                                        - e2e
                                    agent_node_persistent_id:
                                      type: string
                                      format: uuid
                                      pattern: >-
                                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                    template_scenario_id:
                                      type: string
                                      format: uuid
                                      pattern: >-
                                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                    model:
                                      type: string
                                      minLength: 1
                                    timeout_seconds:
                                      type: integer
                                      minimum: 30
                                      maximum: 3600
                                  required:
                                    - kind
                                  additionalProperties: false
                          source_version_id:
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          e2e_settings:
                            type: object
                            properties:
                              adversarial_model:
                                type: string
                                minLength: 1
                              target_environment:
                                type: string
                                enum:
                                  - development
                                  - staging
                                  - production
                              timeout_seconds:
                                type: integer
                                minimum: 30
                                maximum: 3600
                              max_adversary_messages:
                                type: integer
                                minimum: 1
                                maximum: 100
                            required:
                              - adversarial_model
                              - target_environment
                              - timeout_seconds
                              - max_adversary_messages
                            additionalProperties: false
                        additionalProperties: false
                      coverage_scope:
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
                                type: array
                                items:
                                  type: string
                            required:
                              - mode
                              - categories
                            additionalProperties: false
                          - type: object
                            properties:
                              mode:
                                type: string
                                enum:
                                  - selected
                              northstar_ids:
                                type: array
                                items:
                                  type: string
                                  format: uuid
                                  pattern: >-
                                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                            required:
                              - mode
                              - northstar_ids
                            additionalProperties: false
                      is_deleted:
                        type: boolean
                      generation_status:
                        type: string
                      generation_error:
                        nullable: true
                        type: string
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
                      - use_case_id
                      - folder_id
                      - name
                      - description
                      - origin
                      - generation_config
                      - coverage_scope
                      - is_deleted
                      - generation_status
                      - generation_error
                      - created_by
                      - created_by_api_key
                      - created_by_entity
                      - created_at
                      - updated_at
                    additionalProperties: false
                required:
                  - suite
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

Fuente original: https://docs.happyrobot.ai/api-reference/test-suites/post-test-suites
