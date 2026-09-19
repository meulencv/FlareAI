---
title: "List prompt issues"
description: "Returns prompt quality issues for all prompt nodes in the specified version. Issues are generated asynchronously by the platform's prompt analysis system. Each prompt node includes its current prompt text, issue generation status, and any open (non-rejected) issues with recommendations."
---

# List prompt issues

> Returns prompt quality issues for all prompt nodes in the specified version. Issues are generated asynchronously by the platform's prompt analysis system. Each prompt node includes its current prompt text, issue generation status, and any open (non-rejected) issues with recommendations.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /versions/{version_id}/prompt-issues
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
  /versions/{version_id}/prompt-issues:
    get:
      tags:
        - Versions
      summary: List prompt issues
      description: >-
        Returns prompt quality issues for all prompt nodes in the specified
        version. Issues are generated asynchronously by the platform's prompt
        analysis system. Each prompt node includes its current prompt text,
        issue generation status, and any open (non-rejected) issues with
        recommendations.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: version_id
          required: true
          description: Version UUID or slug
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
                        node_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        node_name:
                          nullable: true
                          type: string
                        prompt_md:
                          nullable: true
                          type: string
                        initial_message:
                          nullable: true
                        issue_generation_status:
                          nullable: true
                          type: string
                        issues:
                          type: array
                          items:
                            type: object
                            properties:
                              id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                              issue_type:
                                type: string
                              recommendation:
                                type: string
                              status:
                                type: string
                            required:
                              - id
                              - issue_type
                              - recommendation
                              - status
                            additionalProperties: false
                      required:
                        - node_id
                        - node_name
                        - prompt_md
                        - initial_message
                        - issue_generation_status
                        - issues
                      additionalProperties: false
                required:
                  - data
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/list-prompt-issues
