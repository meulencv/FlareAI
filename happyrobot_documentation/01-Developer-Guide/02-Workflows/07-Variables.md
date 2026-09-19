---
title: "Variables"
description: "Using variables and dynamic data in workflows"
---

# Variables

> Using variables and dynamic data in workflows

Variables let you pass data between nodes and customize behavior dynamically. Every node can reference data from previous nodes, trigger inputs, and environment settings.

## Referencing variables

Type **@** in any text field in the workflow editor to open the variable picker. It lists all available variables from the trigger and previous nodes — select one to insert it. No need to remember variable names — just type `@` and browse the list.

Keep typing after the `@` to filter the list by variable or group name; the text you type stays inline in the field, so nothing is lost if you decide not to insert a variable after all. Use the arrow keys to move through the matches and **Enter** or **Tab** to insert the highlighted one. The picker works the same way in every field that accepts variables — prompt editors and templated node fields alike.

Variables are resolved at runtime. When the workflow executes, each variable reference is replaced with the actual value from the run.

The picker lists both individual fields and their parent containers. When a node output is an object or an array, you can reference an individual leaf field (e.g. `extract.address.city`) or the whole object or list (e.g. `extract.address`) — useful when you want to pass an entire structure to a downstream node or API call. Each entry shows its type (string, number, boolean, object, or array) so you can tell containers apart from leaf values.

### In API calls

When referencing variables outside the UI — in API requests, webhook payloads, or other programmatic configurations — use double curly brace syntax:

```
Hello {"{{customer_name}}"}, your order {"{{order_id}}"} is ready for pickup.
```

Each `{"{{ }}"}` expression is replaced with the actual value at runtime.

## Referencing node outputs

Each node in a workflow produces output data that downstream nodes can reference. Type `@` to browse outputs organized by node.

For example, if an AI Extract node called "Extract Order" produces a field called `order_number`, type `@` and select `Extract Order > order_number`.

In API configurations, use the double curly brace format: `{"{{extract_order.order_number}}"}`.

## Workflow variables

Workflow variables are values you define in the workflow settings panel. They're useful for storing configuration that's referenced across multiple nodes.

**Creating workflow variables:**

1. Open the workflow settings panel
2. Navigate to the **Variables** tab
3. Add a variable with a name and default value

You can organize related variables into groups for easier management. Variables support string, number, and boolean types.

## Trigger variables

When a trigger fires, the data it captures becomes available as variables to all downstream nodes automatically.

**Webhook triggers** make all JSON body fields available. If you POST:

```json theme={null}
{
  "phone_number": "+15551234567",
  "customer_name": "Maria Garcia",
  "priority": "high"
}
```

Then `phone_number`, `customer_name`, and `priority` are all available in every node — type `@` to reference them.

**Phone call triggers** provide `caller_number`, `called_number`, and SIP header data.

**Email triggers** provide `sender`, `subject`, `body`, and `attachments`.

## Environment variables

Environment variables are set at the organization or workflow level and are available to all runs. They're ideal for configuration that differs between environments (development, staging, production) or should be kept out of the workflow definition.

**Organization-level variables** are available to every workflow in your organization. Set them in **Settings > Environment Variables**. Each variable can have different values per environment.

**Workflow-level variables** are specific to a single workflow. Set them in the workflow's settings panel. These also support per-environment values.

<Warning>
  Use environment variables for sensitive values like API keys, tokens, and secrets. Never hardcode credentials in node configurations — reference them as environment variables instead.
</Warning>

Environment variables appear in the `@` variable picker alongside node outputs and trigger data. Type `@` to reference them.

See [Environment variables](../16-Account-and-Settings/08-Environment-Variables.md) for setup instructions.

## Built-in variable groups

HappyRobot provides several built-in variable groups that are always available without any configuration.

### Current variables

The `current` group exposes runtime context about the organization, workflow, and the run itself. These resolve when the workflow executes.

| Variable                           | Description                                                                                                 |
| ---------------------------------- | ----------------------------------------------------------------------------------------------------------- |
| `current.org_name`                 | Name of the organization that owns the workflow                                                             |
| `current.org_id`                   | Organization ID                                                                                             |
| `current.use_case_name`            | Name of the workflow                                                                                        |
| `current.use_case_id`              | Workflow ID                                                                                                 |
| `current.today`                    | Current date and time, formatted as a human-readable string                                                 |
| `current.run_id`                   | Unique ID of the current run                                                                                |
| `current.run_url`                  | Deep link to the current run in the HappyRobot platform (useful for outbound notifications and escalations) |
| `current.version_id`               | ID of the workflow version the run is executing on                                                          |
| `current.version_name`             | Name of the workflow version the run is executing on                                                        |
| `current.execution_environment`    | Environment the run is executing in: `development`, `staging`, or `production`                              |
| `current.is_within_business_hours` | `true` if the run is happening within configured business hours, `false` otherwise                          |

### Time variables

The `time` group exposes the current timestamp in common timezones, resolved at the moment the workflow runs. Reference them with `@` in the editor or with double curly braces in API configurations.

Each timezone variable resolves to a human-readable timestamp. The `time.now_iso` variable is the exception — it resolves to the current UTC time in **ISO 8601** format (e.g. `2026-06-23T14:32:10.000Z`), which is the machine-readable format to use when passing the current time to an API, webhook, or other system that expects a standard timestamp.

| Variable                       | Timezone             | Format                                     |
| ------------------------------ | -------------------- | ------------------------------------------ |
| `time.now_iso`                 | UTC                  | ISO 8601 (e.g. `2026-06-23T14:32:10.000Z`) |
| `time.now_utc`                 | UTC                  | Human-readable                             |
| `time.now_america_new_york`    | America/New\_York    | Human-readable                             |
| `time.now_america_los_angeles` | America/Los\_Angeles | Human-readable                             |
| `time.now_america_chicago`     | America/Chicago      | Human-readable                             |
| `time.now_america_denver`      | America/Denver       | Human-readable                             |
| `time.now_america_mexico_city` | America/Mexico\_City | Human-readable                             |
| `time.now_america_bogota`      | America/Bogota       | Human-readable                             |
| `time.now_america_sao_paulo`   | America/Sao\_Paulo   | Human-readable                             |
| `time.now_europe_london`       | Europe/London        | Human-readable                             |
| `time.now_europe_paris`        | Europe/Paris         | Human-readable                             |
| `time.now_europe_berlin`       | Europe/Berlin        | Human-readable                             |
| `time.now_europe_madrid`       | Europe/Madrid        | Human-readable                             |
| `time.now_asia_dubai`          | Asia/Dubai           | Human-readable                             |
| `time.now_asia_singapore`      | Asia/Singapore       | Human-readable                             |
| `time.now_asia_tokyo`          | Asia/Tokyo           | Human-readable                             |
| `time.now_australia_sydney`    | Australia/Sydney     | Human-readable                             |

Use these variables anywhere you need the current time — for example, in AI prompts to give the agent awareness of the current time, or in conditions to check whether a call is happening during business hours.

### Transfer variables

The `transfer` group exposes the outcome of call [transfers](../05-Voice-Agents/08-Transfer-popup.md) at the agent level. These values aggregate across every transfer node in the workflow — they resolve to the successful transfer if one occurred, otherwise the most recent attempt. This lets you answer "was the call transferred?" at the end of a run without knowing which transfer node fired.

| Variable                                             | Description                                                        |
| ---------------------------------------------------- | ------------------------------------------------------------------ |
| `transfer.succeeded`                                 | `true` if a transfer completed successfully                        |
| `transfer.completed_at`                              | Timestamp when the transfer completed                              |
| `transfer.error`                                     | Error message if the transfer failed, otherwise empty              |
| `transfer.warm_handoff_rep_picked_up`                | `true` if the representative answered the warm handoff             |
| `transfer.warm_handoff_rep_call_connected`           | `true` if the representative's call connected                      |
| `transfer.warm_handoff_rep_left_before_transferring` | `true` if the representative hung up before the transfer completed |
| `transfer.warm_handoff_pressed_one`                  | `true` if the representative pressed 1 to accept the handoff       |
| `transfer.warm_handoff_pressed_nine`                 | `true` if the representative pressed 9 to decline the handoff      |

Reference these in conditions, AI prompts, or downstream action nodes — for example, to send a Slack alert when `transfer.succeeded` is `false`, or to log `transfer.error` for failed handoffs.

### Transcript segments on transferred calls

A voice agent's `transcript` covers the whole call, including whatever was said after a [transfer](../05-Voice-Agents/06-Prompts-and-Tools.md#call-transfer) connected. Two extra entries split it at the transfer point, so you can act on one half without the other:

| Variable                   | Picker label               | Description                                                              |
| -------------------------- | -------------------------- | ------------------------------------------------------------------------ |
| `transcript.pre_transfer`  | Transcript Before Transfer | The part of the conversation before the call was handed off              |
| `transcript.post_transfer` | Transcript After Transfer  | The part after the handoff — typically the representative and the caller |

Both appear under the voice agent node's `transcript` in the `@` picker and can be referenced anywhere a variable resolves at runtime: prompts, conditions, and node configuration. A common use is pointing an [AI Extract](../03-Core-Nodes/02-AI-Extract.md) or [AI Classify](../03-Core-Nodes/03-AI-Classify.md) node at `transcript.post_transfer` to summarize only what the representative discussed.

<Note>
  These segments are computed when a variable is read, not stored on the node's output. That means they can't be added as columns in the [runs table](../09-Runs-and-Monitoring/01-Runs-Overview.md) or used as the source for an [experiment custom metric](../10-Experiments/03-Experiment-metrics.md) — those read persisted node output. They only appear for voice agents; text agent transcripts are never transferred.
</Note>

## Common patterns

<AccordionGroup>
  <Accordion title="Passing phone numbers dynamically">
    Webhook triggers often receive the phone number to call. In the UI, type `@` and select the `phone_number` variable to pass it to an outbound voice agent node. In API configurations:

    ```
    Destination number: {"{{phone_number}}"}
    ```

    The voice agent dials whatever number was included in the webhook payload.
  </Accordion>

  <Accordion title="Using extracted data in follow-up actions">
    An AI Extract node can pull structured data from a conversation transcript. Use those extracted fields in a follow-up action node — type `@` in the UI to browse extracted fields, or reference them in API configs:

    ```
    Subject: Load update for {"{{extract.load_number}}"}
    Body: Carrier {"{{extract.carrier_name}}"} confirmed pickup at {"{{extract.pickup_time}}"}.
    ```
  </Accordion>

  <Accordion title="Conditional logic based on variable values">
    Condition nodes can evaluate variables from any previous node. For example, route based on AI classification — in the UI, select the variable with `@` and configure the operator:

    * Field: `classify.category`
    * Operator: `text_equals`
    * Value: `urgent`

    The "true" branch handles urgent requests, while the "false" branch follows the standard flow.
  </Accordion>
</AccordionGroup>

---

Fuente original: https://docs.happyrobot.ai/workflows/variables
