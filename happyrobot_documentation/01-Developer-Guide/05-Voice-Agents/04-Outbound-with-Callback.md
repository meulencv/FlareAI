---
title: "Outbound with Callback"
description: "Handle callbacks from missed outbound calls"
---

# Outbound with Callback

> Handle callbacks from missed outbound calls

The outbound with callback voice agent extends the standard [outbound agent](03-Outbound-Calls.md) with intelligent callback handling. When you place an outbound call and the recipient doesn't answer, they can call back on one of your assigned numbers. HappyRobot detects the callback, links it to the original outbound attempt, cancels any pending retries, and resumes the workflow from a dedicated callback node — with full context from the original call.

This is the right choice when your outbound calls are to people who are likely to call back — for example, truck drivers who miss calls while driving and return them at the next stop.

## How callbacks work

<Steps>
  <Step title="Outbound call is placed">
    The workflow triggers an outbound call, just like a standard outbound agent. The agent dials the recipient and either connects, reaches voicemail, or gets no answer.
  </Step>

  <Step title="Call fails or is missed">
    If the call doesn't connect, the workflow can retry according to your retry configuration. The original run ID and workflow variables are preserved for callback matching.
  </Step>

  <Step title="Recipient calls back">
    The recipient sees the missed call and dials back. The call arrives on one of your assigned phone numbers.
  </Step>

  <Step title="Callback is detected">
    HappyRobot matches the incoming call to the original outbound attempt using phone number matching. The system identifies this as a callback rather than a new inbound call.
  </Step>

  <Step title="Retries are cancelled">
    Any pending retry workflows for the original outbound call are automatically cancelled. The callback signal prevents duplicate outreach — the recipient is already on the phone.
  </Step>

  <Step title="Workflow resumes from callback node">
    Instead of running the full workflow from the beginning, execution resumes from the **callback node** — a separate prompt node you configure specifically for callback conversations. The original workflow variables and run context are preserved.
  </Step>
</Steps>

## Setting up outbound with callback

<Steps>
  <Step title="Add an outbound with callback node">
    In the workflow editor, add an **Outbound Voice Agent with Callback** action node. This replaces the standard outbound voice agent when you need callback support.
  </Step>

  <Step title="Configure phone numbers for callback monitoring">
    Select the phone numbers that should be monitored for callbacks in the **Numbers** field. When a recipient calls back on any of these numbers, the system will detect the callback and route it to this workflow. You must select at least one number.

    Choose numbers that make sense as the "from" number on your outbound calls — the recipient will see this number in their missed call log and call it back.
  </Step>

  <Step title="Configure the outbound agent">
    Set up the destination, caller ID, agent prompt, voice, and all other call settings. These are the same as a standard [outbound agent](03-Outbound-Calls.md) — destination, recording, voicemail, business hours, and all other fields are available.
  </Step>

  <Step title="Configure the callback prompt">
    The outbound with callback node has a separate **callback prompt node** that defines how the agent behaves when the recipient calls back. This is a distinct prompt from the initial outbound prompt, because the conversation context is different — the recipient is returning your call, not being cold-called.

    Write a prompt that acknowledges the callback context. The agent has access to the `is_outbound_callback` variable and all original workflow data, so it can say things like:

    > "Hi, thanks for calling back. We had tried reaching you earlier about load @trigger.load\_id heading to @trigger.destination. Do you have a few minutes to go over the details?"
  </Step>

  <Step title="Add downstream nodes after the callback">
    Nodes placed after the callback prompt node execute when a callback conversation completes. These can be the same as or different from the nodes after the initial outbound attempt — depending on whether you need different follow-up logic for callbacks.
  </Step>
</Steps>

## Configuration reference

The outbound with callback agent shares **all** configuration fields with the standard [outbound voice agent](03-Outbound-Calls.md) — destination, recording, voicemail handling, error handling (including the **Gracefully handle invalid number** toggle), phone tree navigation, audio, transcription, [user-to-user information (UUI)](03-Outbound-Calls.md#user-to-user-information-uui), business hours, contact intelligence, and real-time analysis all work identically. Refer to the [outbound calls documentation](03-Outbound-Calls.md#configuration-reference) for those fields.

Below are the fields that are unique to the callback variant.

### Callback phone numbers

The **Numbers** field is the key differentiator from the standard outbound agent. It defines which phone numbers are monitored for incoming callbacks.

When a recipient misses your outbound call, they see your number in their call log. When they call that number back, HappyRobot checks whether the incoming call matches a recent outbound attempt from this workflow. If it does, the call is routed to the callback prompt instead of being treated as a new inbound call.

**How to configure:**

* Select one or more phone numbers from your organization's telephony settings.
* These should match (or be associated with) the **From number** used for the outbound call, since that's what the recipient sees in their missed call log.
* You can monitor multiple numbers to cover different area codes or routing scenarios.

<Warning>
  A phone number can only be monitored for callbacks by one workflow at a time. If the same number is used for both a callback workflow and a separate inbound workflow, callback detection takes priority — returning callers will be routed to the callback workflow, not the inbound one.
</Warning>

### Callback prompt node

The callback prompt lives on the **Inbound** tab of the agent's [prompt node](06-Prompts-and-Tools.md#prompt-node-tabs), alongside **Outbound** and **Built-in**. It only executes during callback calls and has its own:

* **System prompt** — Tailor the conversation for the callback context
* **Initial message** — What the agent says first (e.g., "Thanks for calling back!")
* **Model selection** — Can use a different LLM than the outbound prompt
* **Tools** — Can have different tools attached than the outbound conversation

This separation is important because the conversation dynamics are different. In the original outbound call, the agent initiates contact and needs to establish context. In a callback, the recipient is voluntarily returning the call — they expect the agent to know why they were contacted and get to the point quickly.

#### Sync inbound

The **Sync inbound** toggle (below the outbound prompt, under **Protect initial message from interruptions**) controls whether the callback prompt is written separately or mirrors the outbound prompt:

* **On** — Inbound callbacks reuse the outbound prompt. The callback editor becomes read-only and stays in sync with the outbound prompt as you edit it. Use this when the same instructions work for both the initial call and the callback.
* **Off** (default) — The callback prompt is edited independently, so you can tailor it to the callback context.

<Note>
  The **Sync inbound** toggle is available only when the prompt is not using a custom LLM.
</Note>

### Special variables

Two variables are automatically available during callback conversations:

**`is_outbound_callback`** — A boolean flag set to `true` when the current call is a callback. Use this in:

* **Prompts**: `{{#if is_outbound_callback}}The customer is returning our call.{{/if}}`
* **Conditions**: Branch your workflow differently for callbacks vs. first-time connections
* **Tool logic**: Skip certain verification steps during callbacks since the recipient initiated contact

**`previous_run_id`** — The run ID of the original outbound attempt. Use this to:

* Query data from the original run via the API
* Link callback records to the original attempt in your CRM
* Reference outputs from nodes that executed before the original call

All variables from the original workflow trigger are also preserved and available in the callback context. If the original trigger included `@trigger.load_id`, `@trigger.customer_name`, etc., these are all accessible during the callback.

### Environment-specific configuration

Unlike the standard outbound agent, the outbound with callback agent supports **separate configuration per environment** (development, staging, production). This means you can:

* Use different phone numbers for callback monitoring in each environment
* Test callback flows in development without affecting production numbers
* Gradually roll out callback configuration changes through staging

Configure environment-specific settings in the workflow editor by switching between environment tabs.

## Callback detection flow

When a call arrives on a monitored number, HappyRobot determines whether it's a callback or a new inbound call:

1. **Call arrives** — An incoming call hits a phone number that's configured for callback monitoring.
2. **Number matching** — HappyRobot looks up recent call logs between the caller's phone number and the numbers used for outbound calls in this workflow.
3. **Match found** — If a matching outbound attempt is found in recent history, the call is classified as a callback. If no match is found, the call is treated as a regular inbound call (routed to a separate inbound workflow, if one is configured for that number).
4. **Retry cancellation** — The system sends a cancellation signal to any active retry workflows for the matched outbound run. This happens immediately — any scheduled retries are stopped before they dial.
5. **Workflow execution** — A new execution begins from the callback node, inheriting all variables from the original outbound workflow. The `is_outbound_callback` flag is set to `true` and `previous_run_id` is set to the original run's ID.

<Info>
  Callback detection uses phone number matching against recent call history. The recipient must call back from the same number that was dialed in the outbound attempt. If they call from a different number, the system won't recognize it as a callback.
</Info>

## Differences from standard outbound

| Feature                     | Outbound                                | Outbound with Callback                                                        |
| --------------------------- | --------------------------------------- | ----------------------------------------------------------------------------- |
| Callback detection          | No — missed calls are just missed calls | Yes — monitors assigned numbers and matches return calls to original attempts |
| Callback prompt             | N/A                                     | Separate prompt node with its own instructions, model, and tools              |
| Retry cancellation          | Manual — retries continue regardless    | Automatic — retries cancel the moment a callback is detected                  |
| Phone number config         | Single from number                      | Multiple monitored numbers for callback routing                               |
| Environment-specific config | No                                      | Yes — separate configuration per environment (dev/staging/prod)               |
| Special variables           | Standard workflow variables             | Adds `is_outbound_callback` and `previous_run_id`                             |
| Workflow resumption         | N/A                                     | Resumes from callback node with full context from original attempt            |

## When to use outbound with callback

Use the callback variant when:

* **Recipients often call back** — Truck drivers, field workers, busy professionals who miss calls and return them later
* **Context matters** — The callback conversation should reference the original outbound reason without starting from scratch
* **Retries should stop** — You don't want to keep calling someone who has already called you back
* **Campaign analytics** — You want to track callback rates and link callbacks to original outbound attempts

Use the standard outbound agent when:

* **Callbacks aren't expected** — Automated notifications, one-way confirmations
* **Each call is independent** — No need to link outbound and inbound calls
* **Simpler setup** — You don't need callback detection or separate callback prompts

## Next steps

<CardGroup cols={3}>
  <Card title="Outbound calls" icon="phone-arrow-up-right" href="03-Outbound-Calls.md">
    Standard outbound calling reference.
  </Card>

  <Card title="Prompts and tools" icon="message" href="06-Prompts-and-Tools.md">
    Write prompts and attach tools to your agent.
  </Card>

  <Card title="Variables" icon="brackets-curly" href="../02-Workflows/07-Variables.md">
    Pass data between nodes and across callbacks.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/voice-agents/outbound-with-callback
