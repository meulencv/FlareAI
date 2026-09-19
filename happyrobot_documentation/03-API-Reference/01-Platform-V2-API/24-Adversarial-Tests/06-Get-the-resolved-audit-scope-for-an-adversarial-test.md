---
title: "Get the resolved audit scope for an adversarial test"
description: "Returns the northstar categories that BEA will grade against when this test runs. Generated tests inherit the suite's scope; standalone tests carry their own. Use this to display 'currently grading against tags: [...]' without re-implementing the resolution."
---

# Get the resolved audit scope for an adversarial test

> Returns the northstar categories that BEA will grade against when this test runs. Generated tests inherit the suite's scope; standalone tests carry their own. Use this to display 'currently grading against tags: [...]' without re-implementing the resolution.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /adversarial-tests/{test_id}/effective-scope
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
  /adversarial-tests/{test_id}/effective-scope:
    get:
      tags:
        - Adversarial Tests
      summary: Get the resolved audit scope for an adversarial test
      description: >-
        Returns the northstar categories that BEA will grade against when this
        test runs. Generated tests inherit the suite's scope; standalone tests
        carry their own. Use this to display 'currently grading against tags:
        [...]' without re-implementing the resolution.
      parameters:
        - schema:
            type: string
            format: uuid
            pattern: >-
              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
          in: path
          name: test_id
          required: true
      responses:
        '200':
          description: Default Response
          content:
            application/json:
              schema:
                type: object
                properties:
                  mode:
                    type: string
                    enum:
                      - all
                      - by_category
                  categories:
                    type: array
                    items:
                      type: string
                      enum:
                        - notes
                        - style
                        - contradiction
                        - tool
                        - sequential
                  source:
                    type: string
                    enum:
                      - test
                      - suite
                      - default
                required:
                  - mode
                  - categories
                  - source
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
        '403':
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

Fuente original: https://docs.happyrobot.ai/api-reference/adversarial-tests/get-the-resolved-audit-scope-for-an-adversarial-test
