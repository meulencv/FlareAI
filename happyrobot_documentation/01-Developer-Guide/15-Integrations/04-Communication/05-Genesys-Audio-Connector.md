---
title: "Genesys Audio Connector"
description: "Stream Genesys Cloud calls to a HappyRobot voice agent over WebSocket"
---

# Genesys Audio Connector

> Stream Genesys Cloud calls to a HappyRobot voice agent over WebSocket

The Genesys Audio Connector lets a HappyRobot voice agent handle calls that originate in Genesys Cloud. When a call reaches a Genesys queue or flow configured with the Audio Connector action, Genesys streams the call audio to HappyRobot over a WebSocket using the Genesys [AudioHook](https://developer.genesys.cloud/organization/audiohook/) protocol, and your workflow's [Inbound Voice Agent](../../05-Voice-Agents/02-Inbound-Calls.md) handles the conversation in real time — no separate phone number or SIP trunk required.

Use this integration when your contact center already runs on Genesys Cloud and you want to route specific calls to an AI voice agent without re-routing telephony. This is different from the [Genesys SIP carrier](../../14-Assets/03-Telephony.md) and Genesys UUI compatibility options, which route calls over SIP — the Audio Connector streams raw call audio over a WebSocket instead.

## How it works

<Steps>
  <Step title="Genesys streams the call">
    A caller reaches a Genesys Architect flow that includes an **Audio Connector** action pointing at HappyRobot. Genesys opens a WebSocket to HappyRobot and streams the call audio.
  </Step>

  <Step title="HappyRobot matches the workflow">
    HappyRobot verifies the AudioHook request signature using your Genesys credential and matches the call to the workflow node and [environment](../../02-Workflows/09-Environments.md) identified by the `node_id` input variable you configured in Genesys.
  </Step>

  <Step title="The voice agent takes the call">
    The workflow's **Inbound Voice Agent** node handles the conversation using the audio streamed from Genesys, and the run appears in the [Runs](../../09-Runs-and-Monitoring/01-Runs-Overview.md) tab like any other call.
  </Step>
</Steps>

## Setup

### Step 1: Create a Genesys credential

You need the Genesys Audio Connector **API key** and **client secret** from your Genesys Cloud configuration. HappyRobot uses them to verify the signature of incoming AudioHook requests.

<Steps>
  <Step title="Enable the Genesys integration">
    In HappyRobot, go to **Settings > Integrations** and enable **Genesys**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and select **Genesys**. Enter the two fields:

    | Field             | Description                                                |
    | ----------------- | ---------------------------------------------------------- |
    | **API Key**       | The Genesys Audio Connector API key.                       |
    | **Client Secret** | The Genesys Audio Connector client secret (shared secret). |

    Both are stored securely and used only to verify AudioHook request signatures.
  </Step>
</Steps>

### Step 2: Add the Genesys Audio Connector trigger

<Steps>
  <Step title="Add the trigger to your workflow">
    In the workflow editor, add the **Genesys Audio Connector** trigger. The workflow must also contain an **Inbound Voice Agent** node to handle the conversation.
  </Step>

  <Step title="Select your Genesys credential">
    In the trigger's **Genesys credential** field, pick the credential you created in Step 1.
  </Step>

  <Step title="Copy the connection details">
    The trigger exposes read-only values to copy into Genesys:

    | Field              | Where it goes in Genesys                                                                                                                                                                                                                                                                                                                                               |
    | ------------------ | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
    | **Connection URL** | Set this `wss://…/api/v1/audiohook/ws` URL as the **Audio Connector URI** in your Genesys Architect flow.                                                                                                                                                                                                                                                              |
    | **Connector IDs**  | One ID per environment — **Production**, **Staging**, and **Development**. Copy the ID for the environment this Architect flow should reach and add it in the Genesys Audio Connector action under **Session Variables – Inputs**, as an input variable named `node_id` — or as the action's **Connector ID**. The values stay stable when you republish the workflow. |

    Production is the bare ID; staging and development append `.staging` and `.development`. Use the environment tabs above the field to switch between them and copy the one you need.
  </Step>

  <Step title="Declare input variables (optional)">
    Under **Input variables**, list the names of the Genesys `inputVariables` this flow sends on the Audio Connector session. Names only — declare each one exactly as the Architect flow sets it under **Session Variables – Inputs**.

    Generate the trigger's output schema to reference them downstream with `@`. Declaring them up front puts them in the `@` picker straight away, so you can build the nodes that consume them before the first call has run. The caller context the connector always sends — the caller's number, the called number, language, and the Genesys conversation identifiers — comes through on its own and doesn't need to be declared.
  </Step>
</Steps>

<Warning>
  `customConfig` does not apply to the Audio Connector. The connector reads `inputVariables` (and the action's Connector ID), so a `node_id` or variable passed through `customConfig` never reaches HappyRobot.
</Warning>

### Step 3: Configure the Genesys Architect flow

In Genesys Cloud, add an **Audio Connector** action to the Architect flow that should hand off to HappyRobot:

* Set the **Audio Connector URI** to the **Connection URL** from the trigger.
* Under **Session Variables – Inputs**, add an input variable named `node_id` with the value copied from the trigger — or set the action's **Connector ID** to that value.
* Add any additional input variables you listed under **Input variables** so their values flow into the workflow.

Publish the Genesys flow, publish your HappyRobot workflow, then place a test call through the Genesys flow to confirm the voice agent answers.

### One flow per environment

Each Connector ID pins the call to a single [environment](../../02-Workflows/09-Environments.md), so a staging Architect flow and a production Architect flow can both be live against the same HappyRobot workflow at the same time — the same way an inbound phone number can differ per environment.

<Note>
  Flows configured with the older plain node ID keep working, but they always answer from **production** whenever production is live. Swap in the environment-specific Connector ID when you need a staging flow to reach your staging version.
</Note>

<Tip>
  To test against staging before going live, build a second Architect flow with the **staging** Connector ID. Both flows stay valid, so you can leave the staging one in place permanently instead of swapping the ID back and forth.
</Tip>

## Handing the call back to Architect

The **Genesys transfer** node hands control of the call back to the Architect flow so the flow can route the caller — to a queue, an external number, or anywhere else it knows how to reach. HappyRobot does not perform the transfer itself: it ends the Genesys session and returns a set of output variables, and the Architect flow reads them and decides what to do. The caller stays on the line throughout.

Add it as a child of a [tool node](../../04-Tools/02-Creating-Tools.md) under the voice agent's prompt, the same way you'd add a [Direct Transfer](../../05-Voice-Agents/06-Prompts-and-Tools.md#call-transfer) action. When the agent calls that tool, the transfer node runs and the session ends.

<Note>
  Output variables only reach Architect on the disconnect, which only happens when the agent leaves the call. Adding, pasting, or moving a Genesys transfer node under a tool therefore turns on that tool's **End call after execution** automatically and locks it — the values would never be sent otherwise. On a published (locked) version the toggle can't be written, so the node warns you instead. A version saved before this rule is blocked from publishing until the owning tool ends the call, and the block names the tool.
</Note>

### Configuration

| Field               | Required | Description                                                                                                                                                                                                                                                              |
| ------------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Queue**           | Yes      | The value the Architect flow receives and routes on (for example, `Q_HappyRobotTest`). Supports [variables](../../02-Workflows/07-Variables.md), so you can reference the calling tool's own parameter and let the agent choose the destination per call. Sent as `ESCALATION_TARGET`. |
| **Reason**          | No       | Free text for the flow to log or report on. Not used for routing. Sent as `ESCALATION_REASON`.                                                                                                                                                                           |
| **Escalation flag** | —        | Always sent as `ESCALATION_REQUIRED=true`. There is no value to configure.                                                                                                                                                                                               |

### Advanced configuration

* **Variable names** — Rename any of the three variables above. The names must match the ones declared under **Session Variables – Outputs** on the Genesys Audio Connector action exactly. A mismatch is silent: the variable arrives unset and the flow takes its default branch.
* **Additional variables** — Key-value pairs sent alongside the three above. Values support variables. These must also be declared on the Genesys side.

<Warning>
  A Genesys transfer node needs a Genesys Audio Connector trigger. In a workflow triggered any other way there is no Genesys session to hand back, and the node warns you in the editor and fails at run time.

  If the caller hangs up before the agent uses the node, Genesys receives no variables at all and the flow takes its default branch.
</Warning>

## Next steps

<CardGroup cols={2}>
  <Card title="Inbound calls" icon="phone-arrow-down-left" href="../../05-Voice-Agents/02-Inbound-Calls.md">
    Configure the voice agent that handles the streamed call.
  </Card>

  <Card title="Triggers" icon="bolt" href="../../02-Workflows/05-Triggers.md">
    See all the ways a workflow can start.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/communication/genesys-audio-connector
