---
title: "Delete a workflow folder"
description: "Deletes a workflow folder by UUID or slug. Workflows inside the folder are moved to the folder specified by `move_to`, or to the parent folder if `move_to` is omitted. Sub-folders are also moved to the same destination."
---

# Delete a workflow folder

> Deletes a workflow folder by UUID or slug. Workflows inside the folder are moved to the folder specified by `move_to`, or to the parent folder if `move_to` is omitted. Sub-folders are also moved to the same destination.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json delete /workflow-folders/{folder_id}
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
  /workflow-folders/{folder_id}:
    delete:
      tags:
        - Workflow Folders
      summary: Delete a workflow folder
      description: >-
        Deletes a workflow folder by UUID or slug. Workflows inside the folder
        are moved to the folder specified by `move_to`, or to the parent folder
        if `move_to` is omitted. Sub-folders are also moved to the same
        destination.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: folder_id
          required: true
          description: Folder UUID or slug
      requestBody:
        content:
          application/json:
            schema:
              nullable: true
              type: object
              properties:
                move_to:
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                  description: >-
                    Folder ID to move the contained workflows to. If omitted,
                    workflows are moved to the parent folder (one level up).
      responses:
        '204':
          description: Folder deleted
          content:
            application/json:
              schema:
                description: Folder deleted
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflow-folders/delete-a-workflow-folder
