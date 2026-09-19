---
title: "Create a workflow"
description: "Creates a new workflow in the authenticated organization. Supports three creation modes:"
---

# Create a workflow

> Creates a new workflow in the authenticated organization. Supports three creation modes:

1. **Plain** — Creates an empty workflow with an initial version.
2. **From template** — Use `from_template` to create a pre-configured workflow with trigger and agent nodes. Available templates: `voice-agent`, `inbound-voice-agent`, `whatsapp-agent`, `sms-agent`, `email-agent`, `chatbot-agent`. Credentials are auto-discovered from the organization.
3. **With version and nodes** — Use `version` to provide custom version metadata and an optional `nodes` array to define the workflow structure inline. The first node must be a `trigger`, subsequent nodes reference their parent via `parent_index`.

`from_template` and `version` are mutually exclusive.

Optionally, pass a `variables` array to create workflow-scoped environment variables alongside the workflow.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /workflows/
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
  /workflows/:
    post:
      tags:
        - Workflows
      summary: Create a workflow
      description: >-
        Creates a new workflow in the authenticated organization. Supports three
        creation modes:


        1. **Plain** — Creates an empty workflow with an initial version.

        2. **From template** — Use `from_template` to create a pre-configured
        workflow with trigger and agent nodes. Available templates:
        `voice-agent`, `inbound-voice-agent`, `whatsapp-agent`, `sms-agent`,
        `email-agent`, `chatbot-agent`. Credentials are auto-discovered from the
        organization.

        3. **With version and nodes** — Use `version` to provide custom version
        metadata and an optional `nodes` array to define the workflow structure
        inline. The first node must be a `trigger`, subsequent nodes reference
        their parent via `parent_index`.


        `from_template` and `version` are mutually exclusive.


        Optionally, pass a `variables` array to create workflow-scoped
        environment variables alongside the workflow.
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
                  default: robot
                  type: string
                folder_id:
                  nullable: true
                  type: string
                  format: uuid
                  pattern: >-
                    ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                tag_ids:
                  default: []
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
                from_template:
                  oneOf:
                    - type: object
                      properties:
                        template:
                          type: string
                          enum:
                            - voice-agent
                        inputs:
                          default: {}
                          type: object
                          properties:
                            agent_name:
                              description: Display name for the AI voice agent.
                              type: string
                            prompt:
                              description: Prompt node overrides.
                              type: object
                              properties:
                                prompt_md:
                                  description: Agent system prompt in markdown format.
                                  type: string
                                initial_message:
                                  description: >-
                                    The first message the agent says when the
                                    call/conversation starts.
                                  type: string
                                initial_message_uninterruptible:
                                  description: >-
                                    Whether the voice agent initial message is
                                    uninterruptible.
                                  type: boolean
                                model:
                                  description: >-
                                    LLM model selection as a TemplatedValue
                                    (e.g. { type: "static", static: { id:
                                    "gpt-4.1", name: "gpt-4.1" } }).
                                  type: object
                                  properties:
                                    type:
                                      type: string
                                      enum:
                                        - static
                                        - dynamic
                                    static:
                                      type: object
                                      properties:
                                        id:
                                          type: string
                                        name:
                                          type: string
                                        description:
                                          type: string
                                      required:
                                        - id
                                        - name
                                    dynamic:
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
                                    - type
                                initial_message_delay_ms:
                                  description: >-
                                    Milliseconds to wait before the agent speaks
                                    its initial message (0 means no delay).
                                    Caller speech ends the wait early.
                                  type: integer
                                  minimum: 0
                                  maximum: 10000
                      required:
                        - template
                    - type: object
                      properties:
                        template:
                          type: string
                          enum:
                            - inbound-voice-agent
                        inputs:
                          default: {}
                          type: object
                          properties:
                            agent_name:
                              description: Display name for the inbound voice agent.
                              type: string
                            prompt:
                              description: Prompt node overrides.
                              type: object
                              properties:
                                prompt_md:
                                  description: Agent system prompt in markdown format.
                                  type: string
                                initial_message:
                                  description: >-
                                    The first message the agent says when the
                                    call/conversation starts.
                                  type: string
                                initial_message_uninterruptible:
                                  description: >-
                                    Whether the voice agent initial message is
                                    uninterruptible.
                                  type: boolean
                                model:
                                  description: >-
                                    LLM model selection as a TemplatedValue
                                    (e.g. { type: "static", static: { id:
                                    "gpt-4.1", name: "gpt-4.1" } }).
                                  type: object
                                  properties:
                                    type:
                                      type: string
                                      enum:
                                        - static
                                        - dynamic
                                    static:
                                      type: object
                                      properties:
                                        id:
                                          type: string
                                        name:
                                          type: string
                                        description:
                                          type: string
                                      required:
                                        - id
                                        - name
                                    dynamic:
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
                                    - type
                                initial_message_delay_ms:
                                  description: >-
                                    Milliseconds to wait before the agent speaks
                                    its initial message (0 means no delay).
                                    Caller speech ends the wait early.
                                  type: integer
                                  minimum: 0
                                  maximum: 10000
                      required:
                        - template
                    - type: object
                      properties:
                        template:
                          type: string
                          enum:
                            - whatsapp-agent
                        inputs:
                          default: {}
                          type: object
                          properties:
                            agent_name:
                              description: Display name for the WhatsApp agent.
                              type: string
                            prompt:
                              description: Prompt node overrides.
                              type: object
                              properties:
                                prompt_md:
                                  description: Agent system prompt in markdown format.
                                  type: string
                                initial_message:
                                  description: >-
                                    The first message the agent says when the
                                    call/conversation starts.
                                  type: string
                                initial_message_uninterruptible:
                                  description: >-
                                    Whether the voice agent initial message is
                                    uninterruptible.
                                  type: boolean
                                model:
                                  description: >-
                                    LLM model selection as a TemplatedValue
                                    (e.g. { type: "static", static: { id:
                                    "gpt-4.1", name: "gpt-4.1" } }).
                                  type: object
                                  properties:
                                    type:
                                      type: string
                                      enum:
                                        - static
                                        - dynamic
                                    static:
                                      type: object
                                      properties:
                                        id:
                                          type: string
                                        name:
                                          type: string
                                        description:
                                          type: string
                                      required:
                                        - id
                                        - name
                                    dynamic:
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
                                    - type
                      required:
                        - template
                    - type: object
                      properties:
                        template:
                          type: string
                          enum:
                            - sms-agent
                        inputs:
                          default: {}
                          type: object
                          properties:
                            agent_name:
                              description: Display name for the SMS agent.
                              type: string
                            prompt:
                              description: Prompt node overrides.
                              type: object
                              properties:
                                prompt_md:
                                  description: Agent system prompt in markdown format.
                                  type: string
                                initial_message:
                                  description: >-
                                    The first message the agent says when the
                                    call/conversation starts.
                                  type: string
                                initial_message_uninterruptible:
                                  description: >-
                                    Whether the voice agent initial message is
                                    uninterruptible.
                                  type: boolean
                                model:
                                  description: >-
                                    LLM model selection as a TemplatedValue
                                    (e.g. { type: "static", static: { id:
                                    "gpt-4.1", name: "gpt-4.1" } }).
                                  type: object
                                  properties:
                                    type:
                                      type: string
                                      enum:
                                        - static
                                        - dynamic
                                    static:
                                      type: object
                                      properties:
                                        id:
                                          type: string
                                        name:
                                          type: string
                                        description:
                                          type: string
                                      required:
                                        - id
                                        - name
                                    dynamic:
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
                                    - type
                      required:
                        - template
                    - type: object
                      properties:
                        template:
                          type: string
                          enum:
                            - email-agent
                        inputs:
                          default: {}
                          type: object
                          properties:
                            agent_name:
                              description: Display name for the Email agent.
                              type: string
                            email_to:
                              description: Default recipient email address.
                              type: string
                            prompt:
                              description: Prompt node overrides.
                              type: object
                              properties:
                                prompt_md:
                                  description: Agent system prompt in markdown format.
                                  type: string
                                initial_message:
                                  description: >-
                                    The first message the agent says when the
                                    call/conversation starts.
                                  type: string
                                initial_message_uninterruptible:
                                  description: >-
                                    Whether the voice agent initial message is
                                    uninterruptible.
                                  type: boolean
                                model:
                                  description: >-
                                    LLM model selection as a TemplatedValue
                                    (e.g. { type: "static", static: { id:
                                    "gpt-4.1", name: "gpt-4.1" } }).
                                  type: object
                                  properties:
                                    type:
                                      type: string
                                      enum:
                                        - static
                                        - dynamic
                                    static:
                                      type: object
                                      properties:
                                        id:
                                          type: string
                                        name:
                                          type: string
                                        description:
                                          type: string
                                      required:
                                        - id
                                        - name
                                    dynamic:
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
                                    - type
                      required:
                        - template
                    - type: object
                      properties:
                        template:
                          type: string
                          enum:
                            - chatbot-agent
                        inputs:
                          default: {}
                          type: object
                          properties:
                            agent_name:
                              description: Display name for the chatbot agent.
                              type: string
                            prompt:
                              description: Prompt node overrides.
                              type: object
                              properties:
                                prompt_md:
                                  description: Agent system prompt in markdown format.
                                  type: string
                                initial_message:
                                  description: >-
                                    The first message the agent says when the
                                    call/conversation starts.
                                  type: string
                                initial_message_uninterruptible:
                                  description: >-
                                    Whether the voice agent initial message is
                                    uninterruptible.
                                  type: boolean
                                model:
                                  description: >-
                                    LLM model selection as a TemplatedValue
                                    (e.g. { type: "static", static: { id:
                                    "gpt-4.1", name: "gpt-4.1" } }).
                                  type: object
                                  properties:
                                    type:
                                      type: string
                                      enum:
                                        - static
                                        - dynamic
                                    static:
                                      type: object
                                      properties:
                                        id:
                                          type: string
                                        name:
                                          type: string
                                        description:
                                          type: string
                                      required:
                                        - id
                                        - name
                                    dynamic:
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
                                    - type
                      required:
                        - template
                variables:
                  description: >-
                    Optional list of workflow-scoped variables to create
                    alongside the workflow.
                  maxItems: 100
                  type: array
                  items:
                    type: object
                    properties:
                      key:
                        type: string
                        minLength: 1
                      value_production:
                        type: string
                      value_staging:
                        type: string
                      value_development:
                        type: string
                      is_hidden_in_ui:
                        default: false
                        type: boolean
                    required:
                      - key
                      - value_production
                      - value_staging
                      - value_development
                version:
                  type: object
                  properties:
                    name:
                      type: string
                    description:
                      type: string
                    nodes:
                      description: >-
                        Ordered list of nodes to create. The first node must be
                        a trigger.
                      minItems: 1
                      maxItems: 50
                      type: array
                      items:
                        oneOf:
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - trigger
                              event_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                                description: The trigger event ID
                              name:
                                description: Display name override
                                type: string
                              configuration:
                                description: Trigger-specific configuration (JSONB)
                                type: object
                                additionalProperties: {}
                              webhook_payload:
                                description: >-
                                  Expected payload for webhook nodes. When
                                  provided, this is saved as the node output so
                                  downstream nodes can reference it.
                                type: object
                                additionalProperties: {}
                            required:
                              - type
                              - event_id
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - action
                              event_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                                description: The action event ID
                              name:
                                description: Display name override
                                type: string
                              configuration:
                                description: Action-specific configuration (JSONB)
                                type: object
                                additionalProperties: {}
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                              webhook_payload:
                                description: >-
                                  Expected payload for webhook nodes. When
                                  provided, this is saved as the node output so
                                  downstream nodes can reference it.
                                type: object
                                additionalProperties: {}
                            required:
                              - type
                              - event_id
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - agent
                              event_id:
                                type: string
                                format: uuid
                                pattern: >-
                                  ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                                description: The agent event ID
                              name:
                                description: Display name override
                                type: string
                              configuration:
                                description: Agent-specific configuration (JSONB)
                                type: object
                                additionalProperties: {}
                              prompt:
                                description: >-
                                  Prompt configuration for the auto-generated
                                  prompt child node
                                type: object
                                properties:
                                  prompt_md:
                                    description: Agent system prompt in markdown
                                    type: string
                                  initial_message:
                                    description: >-
                                      Agent initial message — accepts a plain
                                      string or Plate paragraph array
                                    type: array
                                    items: {}
                                  initial_message_uninterruptible:
                                    description: >-
                                      Whether the voice agent initial message is
                                      uninterruptible.
                                    type: boolean
                                  initial_message_delay_ms:
                                    description: >-
                                      Milliseconds to wait before the voice
                                      agent speaks its initial message (0 –
                                      10000, 0 means no delay). If the other
                                      party speaks first, the wait ends early
                                      and the initial message becomes the
                                      agent's first turn.
                                    type: integer
                                    minimum: 0
                                    maximum: 10000
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                              - event_id
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - tool
                              name:
                                description: Display name override
                                type: string
                              function:
                                description: Tool function definition.
                                type: object
                                properties:
                                  description:
                                    type: array
                                    items: {}
                                  message:
                                    type: object
                                    properties:
                                      type:
                                        type: string
                                        enum:
                                          - ai
                                          - fixed
                                          - none
                                      description:
                                        type: array
                                        items: {}
                                      example:
                                        type: string
                                  parameters:
                                    type: array
                                    items:
                                      type: object
                                      properties:
                                        name:
                                          type: string
                                        description:
                                          type: array
                                          items: {}
                                        example:
                                          type: string
                                        required:
                                          type: boolean
                                        binding:
                                          type: object
                                          properties:
                                            mode:
                                              type: string
                                              enum:
                                                - agent
                                                - fixed
                                            value:
                                              anyOf:
                                                - type: string
                                                - type: array
                                                  items: {}
                                          required:
                                            - mode
                                      required:
                                        - name
                                  hold_music:
                                    type: object
                                    properties:
                                      type:
                                        type: string
                                        enum:
                                          - static
                                          - dynamic
                                      static:
                                        type: object
                                        properties:
                                          id:
                                            type: string
                                          name:
                                            type: string
                                          description:
                                            type: string
                                        required:
                                          - id
                                          - name
                                      dynamic:
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
                                      - type
                                  hold_music_asset_id:
                                    type: string
                                    format: uuid
                                    pattern: >-
                                      ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                                  tool_index_id:
                                    type: string
                                  tool_index_hash:
                                    type: string
                                  is_mcp:
                                    type: boolean
                                  mcp_server_credential_id:
                                    type: string
                                  mcp_tool_name:
                                    type: string
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - prompt
                              name:
                                description: Display name override
                                type: string
                              prompt_md:
                                description: System prompt in markdown (prompt nodes only)
                                type: string
                              initial_message:
                                description: >-
                                  Initial message — accepts a plain string or
                                  Plate paragraph array (prompt nodes only)
                                type: array
                                items: {}
                              initial_message_uninterruptible:
                                description: >-
                                  Whether the voice agent initial message is
                                  uninterruptible.
                                type: boolean
                              initial_message_delay_ms:
                                description: >-
                                  Milliseconds to wait before the voice agent
                                  speaks its initial message (0 – 10000, 0 means
                                  no delay). If the other party speaks first,
                                  the wait ends early and the initial message
                                  becomes the agent's first turn.
                                type: integer
                                minimum: 0
                                maximum: 10000
                              model:
                                description: >-
                                  LLM model selection as a TemplatedValue (e.g.
                                  { type: "static", static: { id: "gpt-4.1",
                                  name: "gpt-4.1" } }).
                                type: object
                                properties:
                                  type:
                                    type: string
                                    enum:
                                      - static
                                      - dynamic
                                  static:
                                    type: object
                                    properties:
                                      id:
                                        type: string
                                      name:
                                        type: string
                                      description:
                                        type: string
                                    required:
                                      - id
                                      - name
                                  dynamic:
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
                                  - type
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - condition
                              name:
                                description: Display name override
                                type: string
                              type_of_condition:
                                description: >-
                                  Type of condition branch. "conditional"
                                  evaluates rules, "fallback" catches unmatched
                                  cases.
                                type: string
                                enum:
                                  - fallback
                                  - conditional
                              order:
                                description: >-
                                  Order among sibling conditional branches.
                                  Auto-calculated if omitted.
                                type: integer
                                minimum: -9007199254740991
                                maximum: 9007199254740991
                              conditions:
                                description: >-
                                  Condition rules. Each entry follows the
                                  ConditionSchema: { id?, title?, ors: [{ ands:
                                  [{ field: { group_id, variable_id },
                                  condition: '<operator>', value: [{ type:
                                  'paragraph', children: [{ text: '...' }] }] }]
                                  }], output?: [...] }. The 'value' field MUST
                                  be an array of Plate paragraph objects — plain
                                  strings are rejected. Use an empty array [] to
                                  clear all conditions.
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
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - module-change
                              name:
                                description: Display name override
                                type: string
                              configuration:
                                description: >-
                                  Module-change configuration (JSONB). Defaults
                                  to {}.
                                type: object
                                additionalProperties: {}
                              module_node_index:
                                description: >-
                                  Index of the target prompt node in the nodes
                                  array. Resolved to configuration.moduleId
                                  after all nodes are created.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - loop
                              name:
                                description: Display name override
                                type: string
                              execute_in_parallel:
                                description: >-
                                  Whether loop iterations run in parallel.
                                  Defaults to true. This only controls execution
                                  strategy; variables produced by loop body
                                  nodes resolve as lists outside the loop in
                                  both sequential and parallel modes.
                                type: boolean
                              iterate_for:
                                description: >-
                                  Fixed number of iterations. Mutually exclusive
                                  with iterate_over. Fixed-count loop bodies
                                  expose iteration_index and
                                  execute_in_parallel.
                                nullable: true
                                type: integer
                                minimum: -9007199254740991
                                maximum: 9007199254740991
                              iterate_over:
                                description: >-
                                  Expression to iterate over (array variable).
                                  Mutually exclusive with iterate_for.
                                  Collection loop bodies expose iteration_index,
                                  execute_in_parallel, and the configured
                                  loop_variable.
                                nullable: true
                                type: string
                              loop_variable:
                                description: >-
                                  Collection loops only. Name of the current
                                  item variable accessible inside the loop body.
                                  Defaults to "iteration_element". Collection
                                  loops also expose iteration_index and
                                  execute_in_parallel. Fixed-count loops expose
                                  iteration_index and execute_in_parallel
                                  instead.
                                nullable: true
                                type: string
                              do_child_run:
                                description: >-
                                  Whether each iteration runs as a standalone
                                  child run instead of inline in the parent run.
                                  Defaults to false.
                                type: boolean
                              configuration:
                                description: >-
                                  Tolerated fallback: loop settings may be
                                  nested here instead of at the top level. They
                                  are hoisted to the top level server-side (a
                                  top-level value wins), so this is
                                  type-validated. Prefer setting the fields at
                                  the top level.
                                type: object
                                properties:
                                  execute_in_parallel:
                                    type: boolean
                                  iterate_for:
                                    nullable: true
                                    type: integer
                                    minimum: -9007199254740991
                                    maximum: 9007199254740991
                                  iterate_over:
                                    nullable: true
                                    type: string
                                  loop_variable:
                                    nullable: true
                                    type: string
                                  do_child_run:
                                    type: boolean
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - path
                              name:
                                description: Display name override
                                type: string
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                          - type: object
                            properties:
                              type:
                                type: string
                                enum:
                                  - loop_break
                              name:
                                description: Display name override
                                type: string
                              parent_node_index:
                                description: >-
                                  Index of the parent node in the nodes array.
                                  Required for non-trigger nodes.
                                type: integer
                                minimum: 0
                                maximum: 9007199254740991
                            required:
                              - type
                skip_test_all:
                  default: false
                  description: >-
                    When true, skip the automatic background test-all validation
                    after node creation. Useful when the caller will run
                    test-all separately (e.g. MCP tools that need synchronous
                    results).
                  type: boolean
              required:
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
                  latest_version:
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
                  variables:
                    type: array
                    items:
                      type: object
                      properties:
                        id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        key:
                          type: string
                        value_production:
                          type: string
                        value_staging:
                          type: string
                        value_development:
                          type: string
                        is_hidden_in_ui:
                          type: boolean
                      required:
                        - id
                        - key
                        - value_production
                        - value_staging
                        - value_development
                        - is_hidden_in_ui
                      additionalProperties: false
                required:
                  - id
                  - org_id
                  - name
                  - slug
                  - tag_ids
                  - timestamp
                  - latest_version
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

Fuente original: https://docs.happyrobot.ai/api-reference/workflows/create-a-workflow
