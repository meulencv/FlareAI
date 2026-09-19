---
title: "Add nodes to a version"
description: "Adds one or more nodes to the specified version. Nodes are processed sequentially in array order, so later nodes can reference earlier ones via `parent_node_index` (0-based index into this array) or existing DB nodes via `parent_node_id`. Each node must include a `type` discriminator: `"trigger"`, `…"
---

# Add nodes to a version

> Adds one or more nodes to the specified version. Nodes are processed sequentially in array order, so later nodes can reference earlier ones via `parent_node_index` (0-based index into this array) or existing DB nodes via `parent_node_id`. Each node must include a `type` discriminator: `"trigger"`, `"action"`, `"agent"`, `"tool"`, `"prompt"`, `"condition"`, `"module-change"`, `"loop"`, `"path"`, or `"loop_break"`. When a trigger node is included, all existing nodes in the version are replaced and the batch defines the entire workflow from scratch. The entire operation is atomic — if any node fails, all changes are rolled back.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json post /versions/{version_id}/nodes
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
  /versions/{version_id}/nodes:
    post:
      tags:
        - Versions
      summary: Add nodes to a version
      description: >-
        Adds one or more nodes to the specified version. Nodes are processed
        sequentially in array order, so later nodes can reference earlier ones
        via `parent_node_index` (0-based index into this array) or existing DB
        nodes via `parent_node_id`. Each node must include a `type`
        discriminator: `"trigger"`, `"action"`, `"agent"`, `"tool"`, `"prompt"`,
        `"condition"`, `"module-change"`, `"loop"`, `"path"`, or `"loop_break"`.
        When a trigger node is included, all existing nodes in the version are
        replaced and the batch defines the entire workflow from scratch. The
        entire operation is atomic — if any node fails, all changes are rolled
        back.
      parameters:
        - schema:
            type: string
            minLength: 1
          in: path
          name: version_id
          required: true
          description: Version UUID or slug
      requestBody:
        content:
          application/json:
            schema:
              type: object
              properties:
                nodes:
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
                              Expected payload for webhook nodes. When provided,
                              this is saved as the node output so downstream
                              nodes can reference it.
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
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
                            type: integer
                            minimum: 0
                            maximum: 9007199254740991
                          webhook_payload:
                            description: >-
                              Expected payload for webhook nodes. When provided,
                              this is saved as the node output so downstream
                              nodes can reference it.
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
                              Prompt configuration for the auto-generated prompt
                              child node
                            type: object
                            properties:
                              prompt_md:
                                description: Agent system prompt in markdown
                                type: string
                              initial_message:
                                description: >-
                                  Agent initial message — accepts a plain string
                                  or Plate paragraph array
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
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
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
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
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
                              Initial message — accepts a plain string or Plate
                              paragraph array (prompt nodes only)
                            type: array
                            items: {}
                          initial_message_uninterruptible:
                            description: >-
                              Whether the voice agent initial message is
                              uninterruptible.
                            type: boolean
                          initial_message_delay_ms:
                            description: >-
                              Milliseconds to wait before the voice agent speaks
                              its initial message (0 – 10000, 0 means no delay).
                              If the other party speaks first, the wait ends
                              early and the initial message becomes the agent's
                              first turn.
                            type: integer
                            minimum: 0
                            maximum: 10000
                          model:
                            description: >-
                              LLM model selection as a TemplatedValue (e.g. {
                              type: "static", static: { id: "gpt-4.1", name:
                              "gpt-4.1" } }).
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
                                    Paragraph object. When the containing field
                                    is an array of this schema, send a flat
                                    Paragraph[] array. Do not send a bare
                                    Paragraph object. Only send Paragraph[][]
                                    when the containing field is explicitly an
                                    array of arrays. Paragraph object schema:
                                    {type: 'paragraph', children: Array<{text:
                                    string} | {type: 'variable', children:
                                    [{text: ''}], group_id: string, variable_id:
                                    string}>}
                            required:
                              - type
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
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
                              Type of condition branch. "conditional" evaluates
                              rules, "fallback" catches unmatched cases.
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
                              ConditionSchema: { id?, title?, ors: [{ ands: [{
                              field: { group_id, variable_id }, condition:
                              '<operator>', value: [{ type: 'paragraph',
                              children: [{ text: '...' }] }] }] }], output?:
                              [...] }. The 'value' field MUST be an array of
                              Plate paragraph objects — plain strings are
                              rejected. Use an empty array [] to clear all
                              conditions.
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
                                      flat Paragraph[] array. Do not send a bare
                                      Paragraph object. Only send Paragraph[][]
                                      when the containing field is explicitly an
                                      array of arrays. Paragraph object schema:
                                      {type: 'paragraph', children: Array<{text:
                                      string} | {type: 'variable', children:
                                      [{text: ''}], group_id: string,
                                      variable_id: string}>}
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
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
                              Module-change configuration (JSONB). Defaults to
                              {}.
                            type: object
                            additionalProperties: {}
                          module_node_index:
                            description: >-
                              Index of the target prompt node in the nodes
                              array. Resolved to configuration.moduleId after
                              all nodes are created.
                            type: integer
                            minimum: 0
                            maximum: 9007199254740991
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
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
                              Whether loop iterations run in parallel. Defaults
                              to true. This only controls execution strategy;
                              variables produced by loop body nodes resolve as
                              lists outside the loop in both sequential and
                              parallel modes.
                            type: boolean
                          iterate_for:
                            description: >-
                              Fixed number of iterations. Mutually exclusive
                              with iterate_over. Fixed-count loop bodies expose
                              iteration_index and execute_in_parallel.
                            nullable: true
                            type: integer
                            minimum: -9007199254740991
                            maximum: 9007199254740991
                          iterate_over:
                            description: >-
                              Expression to iterate over (array variable).
                              Mutually exclusive with iterate_for. Collection
                              loop bodies expose iteration_index,
                              execute_in_parallel, and the configured
                              loop_variable.
                            nullable: true
                            type: string
                          loop_variable:
                            description: >-
                              Collection loops only. Name of the current item
                              variable accessible inside the loop body. Defaults
                              to "iteration_element". Collection loops also
                              expose iteration_index and execute_in_parallel.
                              Fixed-count loops expose iteration_index and
                              execute_in_parallel instead.
                            nullable: true
                            type: string
                          do_child_run:
                            description: >-
                              Whether each iteration runs as a standalone child
                              run instead of inline in the parent run. Defaults
                              to false.
                            type: boolean
                          configuration:
                            description: >-
                              Tolerated fallback: loop settings may be nested
                              here instead of at the top level. They are hoisted
                              to the top level server-side (a top-level value
                              wins), so this is type-validated. Prefer setting
                              the fields at the top level.
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
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
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
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
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
                          parent_node_id:
                            description: >-
                              ID of an existing parent node. Mutually exclusive
                              with parent_node_index.
                            type: string
                            format: uuid
                            pattern: >-
                              ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                          parent_node_index:
                            description: >-
                              0-based index of a node earlier in this request's
                              nodes array to use as parent. Mutually exclusive
                              with parent_node_id.
                            type: integer
                            minimum: 0
                            maximum: 9007199254740991
                        required:
                          - type
              required:
                - nodes
        required: true
      responses:
        '201':
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
                        version_id:
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        type:
                          type: string
                        name:
                          nullable: true
                          type: string
                        parent_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        event_id:
                          nullable: true
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12})$
                        timestamp:
                          type: string
                        loop_end_id:
                          description: >-
                            ID of the auto-created loop_end node (only present
                            for loop nodes)
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        condition_id:
                          description: >-
                            ID of the auto-created condition child (only present
                            for path nodes)
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                        fallback_id:
                          description: >-
                            ID of the auto-created fallback child (only present
                            for path nodes)
                          type: string
                          format: uuid
                          pattern: >-
                            ^([0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-8][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}|00000000-0000-0000-0000-000000000000|ffffffff-ffff-ffff-ffff-ffffffffffff)$
                      required:
                        - id
                        - version_id
                        - type
                        - timestamp
                      additionalProperties: false
                required:
                  - data
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

Fuente original: https://docs.happyrobot.ai/api-reference/versions/add-nodes-to-a-version
