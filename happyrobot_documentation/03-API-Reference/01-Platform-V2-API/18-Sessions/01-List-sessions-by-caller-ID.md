---
title: "List sessions by caller ID"
description: "Returns paginated sessions whose caller phone number matches caller_id, ordered by timestamp. Optionally filter by session timestamp with start_date and/or end_date (ISO 8601). Resolves the phone number to a contact, so a session is only returned if it produced a communication event. Use the session…"
---

# List sessions by caller ID

> Returns paginated sessions whose caller phone number matches caller_id, ordered by timestamp. Optionally filter by session timestamp with start_date and/or end_date (ISO 8601). Resolves the phone number to a contact, so a session is only returned if it produced a communication event. Use the session id with GET /sessions/{session_id}/messages to fetch the transcript.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /sessions/
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
  /sessions/:
    get:
      tags:
        - Sessions
      summary: List sessions by caller ID
      description: >-
        Returns paginated sessions whose caller phone number matches caller_id,
        ordered by timestamp. Optionally filter by session timestamp with
        start_date and/or end_date (ISO 8601). Resolves the phone number to a
        contact, so a session is only returned if it produced a communication
        event. Use the session id with GET /sessions/{session_id}/messages to
        fetch the transcript.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: query
          name: caller_id
          required: true
        - schema:
            anyOf:
              - type: string
                format: date-time
                pattern: >-
                  ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
              - type: string
                enum:
                  - ''
          in: query
          name: start_date
          required: false
        - schema:
            anyOf:
              - type: string
                format: date-time
                pattern: >-
                  ^(?:(?:\d\d[2468][048]|\d\d[13579][26]|\d\d0[48]|[02468][048]00|[13579][26]00)-02-29|\d{4}-(?:(?:0[13578]|1[02])-(?:0[1-9]|[12]\d|3[01])|(?:0[469]|11)-(?:0[1-9]|[12]\d|30)|(?:02)-(?:0[1-9]|1\d|2[0-8])))T(?:(?:[01]\d|2[0-3]):[0-5]\d(?::[0-5]\d(?:\.\d+)?)?(?:Z))$
              - type: string
                enum:
                  - ''
          in: query
          name: end_date
          required: false
        - schema:
            default: 1
            type: integer
            minimum: 1
            maximum: 9007199254740991
          in: query
          name: page
          required: false
        - schema:
            default: 50
            type: integer
            minimum: 1
            maximum: 100
          in: query
          name: page_size
          required: false
        - schema:
            default: desc
            type: string
            enum:
              - asc
              - desc
          in: query
          name: sort
          required: false
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
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
                        use_case_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        version_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        run_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        user_number:
                          type: string
                        status:
                          type: string
                        type:
                          type: string
                        duration:
                          nullable: true
                          type: integer
                          minimum: -9007199254740991
                          maximum: 9007199254740991
                        timestamp:
                          type: string
                        call_connected_at:
                          nullable: true
                          type: string
                        sip_code:
                          nullable: true
                          type: string
                        sip_reason:
                          nullable: true
                          type: string
                        failure_reason:
                          nullable: true
                          type: string
                        llm_model:
                          nullable: true
                          type: string
                        stt_model:
                          nullable: true
                          type: string
                        tts_model:
                          nullable: true
                          type: string
                        voice_id:
                          nullable: true
                          type: string
                        languages:
                          nullable: true
                          type: array
                          items:
                            type: string
                      required:
                        - id
                        - org_id
                        - use_case_id
                        - version_id
                        - run_id
                        - user_number
                        - status
                        - type
                        - duration
                        - timestamp
                        - call_connected_at
                        - sip_code
                        - sip_reason
                        - failure_reason
                        - llm_model
                        - stt_model
                        - tts_model
                        - voice_id
                        - languages
                      additionalProperties: false
                  pagination:
                    type: object
                    properties:
                      page:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      page_size:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      total_pages:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      total_records:
                        type: integer
                        minimum: -9007199254740991
                        maximum: 9007199254740991
                      has_next_page:
                        type: boolean
                      has_previous_page:
                        type: boolean
                    required:
                      - page
                      - page_size
                      - total_pages
                      - total_records
                      - has_next_page
                      - has_previous_page
                    additionalProperties: false
                required:
                  - data
                  - pagination
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

Fuente original: https://docs.happyrobot.ai/api-reference/sessions/list-sessions-by-caller-id
