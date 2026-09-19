---
title: "Update a workflow"
description: "Updates workflow metadata and settings. Accepts a workflow UUID or slug as the path parameter. Set `folder_id` to `null` to move the workflow to the root level. Use `settings` to update configuration such as webhooks, out-of-office hours, approval process, data retention, and audits. This endpoint d…"
---

# Update a workflow

> Updates workflow metadata and settings. Accepts a workflow UUID or slug as the path parameter. Set `folder_id` to `null` to move the workflow to the root level. Use `settings` to update configuration such as webhooks, out-of-office hours, approval process, data retention, and audits. This endpoint does not modify versions or nodes.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json patch /workflows/{workflow_id}
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
  /workflows/{workflow_id}:
    patch:
      tags:
        - Workflows
      summary: Update a workflow
      description: >-
        Updates workflow metadata and settings. Accepts a workflow UUID or slug
        as the path parameter. Set `folder_id` to `null` to move the workflow to
        the root level. Use `settings` to update configuration such as webhooks,
        out-of-office hours, approval process, data retention, and audits. This
        endpoint does not modify versions or nodes.
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
                  type: string
                  minLength: 1
                icon:
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
                settings:
                  type: object
                  properties:
                    data_retention_days:
                      nullable: true
                      type: integer
                      minimum: -9007199254740991
                      maximum: 9007199254740991
                    audits_enabled:
                      type: boolean
                    audit_sampling_bps:
                      type: integer
                      minimum: 0
                      maximum: 10000
                    audit_conditions:
                      type: array
                      items:
                        type: object
                        properties:
                          id:
                            type: string
                          title:
                            type: string
                          ors:
                            type: array
                            items:
                              type: object
                              properties:
                                id:
                                  type: string
                                ands:
                                  type: array
                                  items:
                                    type: object
                                    properties:
                                      id:
                                        type: string
                                      field:
                                        type: object
                                        properties:
                                          group_id:
                                            type: string
                                          variable_id:
                                            type: string
                                        required:
                                          - group_id
                                          - variable_id
                                      condition:
                                        type: string
                                      value:
                                        type: array
                                        items:
                                          description: >-
                                            !IMPORTANT: This schema describes one
                                            Paragraph object. When the containing
                                            field is an array of this schema, send a
                                            flat Paragraph[] array. Do not send a
                                            bare Paragraph object. Only send
                                            Paragraph[][] when the containing field
                                            is explicitly an array of arrays.
                                            Paragraph object schema: {type:
                                            'paragraph', children: Array<{text:
                                            string} | {type: 'variable', children:
                                            [{text: ''}], group_id: string,
                                            variable_id: string}>}
                              required:
                                - ands
                          output:
                            type: array
                            items:
                              description: >-
                                !IMPORTANT: This schema describes one Paragraph
                                object. When the containing field is an array of
                                this schema, send a flat Paragraph[] array. Do
                                not send a bare Paragraph object. Only send
                                Paragraph[][] when the containing field is
                                explicitly an array of arrays. Paragraph object
                                schema: {type: 'paragraph', children:
                                Array<{text: string} | {type: 'variable',
                                children: [{text: ''}], group_id: string,
                                variable_id: string}>}
                    out_of_office_hours:
                      type: object
                      additionalProperties:
                        type: object
                        properties:
                          timezone:
                            type: string
                            minLength: 1
                          weekly_schedule:
                            minItems: 7
                            maxItems: 7
                            type: array
                            items:
                              nullable: true
                              type: array
                              items:
                                nullable: true
                                type: object
                                properties:
                                  start:
                                    type: string
                                    pattern: ^(([0-1][0-9]|2[0-3]):[0-5][0-9]|24:00)$
                                  end:
                                    type: string
                                    pattern: ^(([0-1][0-9]|2[0-3]):[0-5][0-9]|24:00)$
                                required:
                                  - start
                                  - end
                          off_days:
                            type: object
                            additionalProperties:
                              type: array
                              items:
                                type: object
                                properties:
                                  start:
                                    type: string
                                    pattern: ^(([0-1][0-9]|2[0-3]):[0-5][0-9]|24:00)$
                                  end:
                                    type: string
                                    pattern: ^(([0-1][0-9]|2[0-3]):[0-5][0-9]|24:00)$
                                required:
                                  - start
                                  - end
                        required:
                          - timezone
                          - weekly_schedule
                    webhooks:
                      type: array
                      items:
                        type: object
                        properties:
                          url:
                            type: string
                            format: uri
                          headers:
                            type: object
                            additionalProperties:
                              type: string
                        required:
                          - url
                    workflow_approval_process_settings:
                      type: object
                      properties:
                        environments:
                          type: object
                          properties:
                            production:
                              type: boolean
                            staging:
                              type: boolean
                            development:
                              type: boolean
                          required:
                            - production
                            - staging
                            - development
                      required:
                        - environments
                    deployment:
                      description: '@internal'
                      type: object
                      properties:
                        owner:
                          nullable: true
                          type: string
                          maxLength: 256
                        pod_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        category_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        stage_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        description:
                          nullable: true
                          type: string
                        linked_workflow_ids:
                          nullable: true
                          type: array
                          items:
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
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
                required:
                  - id
                  - org_id
                  - name
                  - slug
                  - tag_ids
                  - timestamp
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/update-a-workflow
