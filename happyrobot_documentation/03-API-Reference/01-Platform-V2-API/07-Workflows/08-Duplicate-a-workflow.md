---
title: "Duplicate a workflow"
description: "Creates a copy of a workflow including all its nodes and configurations. The duplicated workflow is created as a new unpublished workflow with version number 1. If the source uses workflow engine v2, the duplicate remains an editable v2 draft and cannot be published through the public API until upgr…"
---

# Duplicate a workflow

> Creates a copy of a workflow including all its nodes and configurations. The duplicated workflow is created as a new unpublished workflow with version number 1. If the source uses workflow engine v2, the duplicate remains an editable v2 draft and cannot be published through the public API until upgraded to v3. The existing published v2 source remains live and continues running until explicitly unpublished.

- **name** — Optional. Display name for the new workflow. Defaults to `'{original name} Copy'`.
- **version_id** — Optional. The specific version to duplicate. Defaults to the latest version of the source workflow.
- **org_id** — Optional. Target organization for the copy. Defaults to the API key's organization. Cross-org duplication requires access to both organizations.

Sensitive configurations (e.g. phone numbers, SIP trunks) are cleared during duplication and must be reconfigured.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /workflows/{workflow_id}/duplicate
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
  /workflows/{workflow_id}/duplicate:
    post:
      tags:
        - Workflows
      summary: Duplicate a workflow
      description: >-
        Creates a copy of a workflow including all its nodes and configurations.
        The duplicated workflow is created as a new unpublished workflow with
        version number 1. If the source uses workflow engine v2, the duplicate
        remains an editable v2 draft and cannot be published through the public
        API until upgraded to v3. The existing published v2 source remains live
        and continues running until explicitly unpublished.


        - **name** — Optional. Display name for the new workflow. Defaults to
        `'{original name} Copy'`.

        - **version_id** — Optional. The specific version to duplicate. Defaults
        to the latest version of the source workflow.

        - **org_id** — Optional. Target organization for the copy. Defaults to
        the API key's organization. Cross-org duplication requires access to
        both organizations.


        Sensitive configurations (e.g. phone numbers, SIP trunks) are cleared
        during duplication and must be reconfigured.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: workflow_id
          required: true
          description: Workflow UUID or slug
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                name:
                  description: >-
                    Display name for the new workflow. When omitted, defaults to
                    '{original workflow name} Copy'.
                  type: string
                  minLength: 1
                org_id:
                  description: >-
                    Target organization ID for the duplicated workflow. Defaults
                    to the organization of the API key. Cross-org duplication
                    requires access to both organizations.
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                version_id:
                  description: >-
                    The version to duplicate. When omitted, defaults to the
                    latest version of the source workflow.
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                wait_for_test_all:
                  default: false
                  description: >-
                    When true, block until the post-duplication test-all
                    finishes and return per-node results in `test_all_results`.
                    When false (default), test-all is fired in the background
                    and the response returns immediately.
                  type: boolean
      responses:
        '201':
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
                  name:
                    type: string
                  slug:
                    type: string
                  icon:
                    nullable: true
                    type: string
                  folder_id:
                    nullable: true
                    type: string
                    format: uuid
                    pattern: >-
                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  tag_ids:
                    type: array
                    items:
                      type: string
                      format: uuid
                      pattern: >-
                        ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  timestamp:
                    type: string
                  version:
                    nullable: true
                    type: object
                    properties:
                      id:
                        type: string
                      name:
                        type: string
                      slug:
                        type: string
                      version_number:
                        nullable: true
                        type: number
                      is_published:
                        type: boolean
                      is_live:
                        type: boolean
                      environment:
                        type: string
                      workflow_version:
                        description: >-
                          Workflow engine version for this version: 2 = legacy,
                          3 = explicit-edges engine (loop/path/loop_break nodes
                          available).
                        type: number
                      published_at:
                        nullable: true
                        type: string
                      timestamp:
                        type: string
                    required:
                      - id
                      - name
                      - slug
                      - is_published
                      - is_live
                      - timestamp
                    additionalProperties: false
                  warnings:
                    type: array
                    items:
                      type: string
                  test_all_results:
                    type: array
                    items:
                      type: object
                      properties:
                        node_id:
                          type: string
                        persistent_id:
                          type: string
                        name:
                          type: string
                        status:
                          type: string
                          enum:
                            - success
                            - failed
                            - skipped
                        error:
                          type: string
                      required:
                        - node_id
                        - persistent_id
                        - name
                        - status
                      additionalProperties: false
                required:
                  - id
                  - org_id
                  - name
                  - slug
                  - tag_ids
                  - timestamp
                  - version
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/duplicate-a-workflow
