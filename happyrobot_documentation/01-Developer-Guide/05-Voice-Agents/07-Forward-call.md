---
title: "Forward call"
description: "Send an incoming call straight to a phone number with no agent on the line"
---

# Forward call

> Send an incoming call straight to a phone number with no agent on the line

The **Forward call** action node connects an incoming caller to a phone number without any AI agent taking the call. The caller hears ringback while the destination rings and is connected as soon as someone answers. If nobody answers within the ringing timeout, the caller is hung up on.

Use it when a call should reach a person or another system directly — an after-hours line, a specific department, or a fallback number — and there is nothing for an agent to do first.

## Forward call vs. Transfer

Both nodes send a call to a phone number, but they work differently:

|                                            | **Forward call**                                                                            | **Transfer**                                                                                       |
| ------------------------------------------ | ------------------------------------------------------------------------------------------- | -------------------------------------------------------------------------------------------------- |
| Agent on the call                          | None                                                                                        | The voice agent is on the call and hands it off                                                    |
| Where the call lives                       | Stays on HappyRobot, which plays ringback and detects whether the destination answered      | Can hand the leg to the carrier (outside-agent transfer) and drop HappyRobot out of the media path |
| Warm handoff, whisper message, digit press | Not available — there's no agent to speak                                                   | Available                                                                                          |
| Typical placement                          | Directly after an inbound trigger, or on a branch that decides a human should take the call | Under a tool call, so the agent can decide when to transfer                                        |

Because there's no agent, the Forward call node has no agent, warm handoff, handoff message, whisper message, or digit press settings.

## Adding the node

<Steps>
  <Step title="Open the node picker">
    In the workflow editor, click **+** to add a new action node.
  </Step>

  <Step title="Select Forward call">
    Search for **Forward call** under the **Phone** integration.
  </Step>

  <Step title="Set the destination">
    Enter the number to forward to. Everything else is optional.
  </Step>
</Steps>

## Configuration

### To number (required)

The phone number to forward the call to, in E.164 format (for example `+12223334444`). Supports [variables](../02-Workflows/07-Variables.md), so the destination can come from an earlier node — a TMS lookup, a classification result, or a schedule check.

### Ringing timeout (seconds)

How long to ring the destination before giving up and hanging up on the caller. Defaults to `45`. Supports variables that resolve to a number.

Unlike a transfer, there is nothing on the call to fall back to when the destination doesn't pick up, so this timeout is always enforced.

### Advanced configuration

Expand **Advanced configuration** for the remaining settings.

| Setting                               | Description                                                                                                                                                                                                                                                                                                                        |
| ------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **To extension**                      | An extension to dial at the destination. Supports variables.                                                                                                                                                                                                                                                                       |
| **From number**                       | The number the forwarded leg dials out from. Picked from your organization's [telephony inventory](../14-Assets/03-Telephony.md) — see [Choosing the number to dial out from](#choosing-the-number-to-dial-out-from). Leave it empty to dial from the number the call arrived on.                                                             |
| **Show the original caller's number** | Presents the inbound caller's number to the destination instead of yours, so the person answering sees who is actually calling. Off by default. Hidden on [web call](#web-call-workflows) workflows, which have no caller leg to present. See [Caller ID on forwards and warm handoffs](#caller-id-on-forwards-and-warm-handoffs). |
| **SIP headers**                       | Custom SIP headers sent with the forwarded call, as key-value pairs. Values support variables. Rows without a key are discarded.                                                                                                                                                                                                   |

## Choosing the number to dial out from

**From number** selects which of your numbers the outbound leg originates on. It picks the **SIP trunk**, not just the caller ID — so pointing it at an internal trunk keeps the forwarded leg off your carrier even though the call arrived on a carrier number.

* Leave it empty and the leg dials from the number the call arrived on. That's the right default for a call that came in on one of your phone numbers.
* The picker only offers numbers your organization owns, including SIP numbers, because the value has to resolve to a trunk. Type to search, and use **Clear** to go back to the default.
* The same field is on the **Transfer** node under **Advanced Telephony**, for warm handoffs and whisper transfers.

### Web call workflows

A [web call](../02-Workflows/05-Triggers.md#web-call) arrives in the browser, on no phone number of its own — so there is nothing for the forwarded leg to fall back to. **From number** is required in that case, and the node shows a warning until you set one:

> This workflow is triggered by a web call, which arrives on no number of its own. Set "From number" under Advanced configuration — until then the forwarded leg has no trunk to dial from and will fail.

Because a web call has no caller leg to present, **Show the original caller's number** doesn't appear on web call workflows.

<Note>
  On the **Transfer** node, a web call also rules out a **direct transfer**, which hands over the caller's own phone leg. Use a warm handoff or whisper transfer instead, both of which dial a fresh leg from your **From number**. A transfer placed outside an agent can only be a direct transfer, so on a web call workflow it has to move inside the agent.
</Note>

## Caller ID on forwards and warm handoffs

By default the destination sees your HappyRobot number. Enable **Show the original caller's number** to pass the caller's own number through instead.

The same toggle is available on the **Transfer** node for **warm handoffs**, under **Advanced Telephony**.

<Warning>
  This requires carrier-side support. On a bring-your-own Twilio account it has no effect until [Immutable Call Forwarding](https://www.twilio.com/en-us/changelog/elastic-sip-trunking---immutable-call-forwarding-with-calltoken-) is enabled on the account in Twilio. When the carrier gives HappyRobot no way to authorize the number, the call still connects — it just shows your number. Test a forward or transfer on your own numbers before relying on it.
</Warning>

Also note that when the destination sees the caller's number, a callback from that phone reaches the **caller**, not your business. Leave the toggle off if callbacks should come back to you.

## Failure handling

The Forward call node has no **Continue on failure** toggle. A dial that fails or goes unanswered is reported as a completed node whose output says the forward did not connect (`forward_succeeded` is `false`), so you branch on the node's output rather than on node failure. The node is attempted once — it is never retried, since a retry would dial the destination twice.

## Recordings

A forward writes its own session, so its recording appears on the Forward call node in the run's **Details** tab, the same way an agent node's recording does. See [Recordings](../09-Runs-and-Monitoring/04-Recordings.md).

## Next steps

<CardGroup cols={2}>
  <Card title="Inbound calls" icon="phone-arrow-down-left" href="02-Inbound-Calls.md">
    Set up the trigger and agent that receive the call.
  </Card>

  <Card title="Telephony" icon="phone" href="../14-Assets/03-Telephony.md">
    Manage the phone numbers and SIP trunks calls arrive on.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/voice-agents/forward-call
