---
title: "Transfer popup"
description: "Send a context popup to human agents when transferring a call"
---

# Transfer popup

> Send a context popup to human agents when transferring a call

The Transfer Popup action node stores structured transfer data — including the caller's phone number, a conversation summary, a map location, the full transcript, and any custom data fields — which can then be viewed in a popup card. The popup can be embedded in the telephony system for incoming calls (requires configuration) or shared as a URL to any user who needs call context, giving the receiving agent immediate context before they say hello.

## How it works

The popup is associated with the caller's phone number. When the transfer completes, the receiving agent sees the popup card in the HappyRobot interface. The card is stored for a configurable number of days so agents can review it later.

## Adding the node

<Steps>
  <Step title="Open the node picker">
    In the workflow editor, click **+** to add a new action node.
  </Step>

  <Step title="Select Transfer Popup">
    Search for or select **Transfer Popup** from the action node list, then choose **Create Popup**.
  </Step>

  <Step title="Configure the popup">
    Fill in the phone number and enable any optional sections.
  </Step>
</Steps>

## Configuration

### Phone number (required)

The caller's phone number. This is how the popup is matched to the incoming transfer. Supports [variables](../02-Workflows/07-Variables.md).

### Transfer summary (optional)

A short text description of the call — for example, what the caller needs or what was discussed. You can generate this from a preceding AI Generate node or write it as a fixed template. Supports variables.

### Location (optional)

Displays a map pin on the popup card. Useful for dispatch or logistics workflows where the caller's physical location matters.

| Field            | Description                                                                |
| ---------------- | -------------------------------------------------------------------------- |
| **Latitude**     | Decimal latitude (required when location is enabled)                       |
| **Longitude**    | Decimal longitude (required when location is enabled)                      |
| **Description**  | Optional text label for the location                                       |
| **Last updated** | Optional ISO 8601 timestamp indicating when the location data was recorded |

### Transcript (optional)

The full conversation transcript up to the point of transfer. Use the `@transcript` variable from the voice agent node to pass the live transcript automatically.

### Enable feedback (optional)

Adds a feedback button to the popup, allowing the receiving agent to submit a rating or comment on the AI handoff.

### Require authentication (optional)

By default, anyone with the popup URL can open it and view the call context. Enable **Require authentication** to protect the popup with an access key so the URL alone is not enough to open it.

When you turn this on, HappyRobot generates an **Access key**. From the node settings you can **copy** the key or **regenerate** it — regenerating invalidates the previous key immediately. Share the key only with the systems or people that should be able to see the popup.

To open a protected popup, the viewer must present the access key as one of the following HTTP headers:

* `X-API-Key: <access key>`
* `Authorization: Bearer <access key>`

Requests without a valid key are rejected and no popup data is returned. Popups created before this option existed default to no authentication until you enable it.

### TTL (days) (optional)

How long the popup data is stored (1–365 days). Defaults to 10 days if not set. After the TTL expires, the popup data is deleted.

### Data (optional)

A structured set of custom key-value fields displayed on the popup card. Use this to surface any workflow variables that are relevant to the agent — for example, load details, account numbers, or call disposition.

Data fields support two levels of nesting:

* **Top-level fields** render as section headers.
* **Nested fields** render as labeled key-value rows under a header.

Each field value supports [variables](../02-Workflows/07-Variables.md), so you can pass extracted data from earlier nodes.

## Example

A freight brokerage workflow receives an inbound call, extracts the caller's load number and pickup location via AI Extract, and then transfers the call to a dispatcher. Before the transfer, a Transfer Popup node is configured like this:

| Field                | Value                                                                              |
| -------------------- | ---------------------------------------------------------------------------------- |
| Phone number         | `@caller_phone`                                                                    |
| Transfer summary     | `@ai_generate_summary`                                                             |
| Location (enabled)   | Lat: `@load_pickup_lat`, Lng: `@load_pickup_lng`, Description: `@load_origin_city` |
| Transcript (enabled) | `@transcript`                                                                      |
| Data                 | `Load number`: `@load_number`, `Carrier`: `@carrier_name`                          |

The dispatcher receives the call and immediately sees the load number, pickup location on a map, and a summary of what the caller said — without asking the caller to repeat themselves.

## Notes

* The Transfer Popup node does not require any integration setup. Authentication is optional — enable **Require authentication** to protect the popup with an access key (see above).
* It can be placed anywhere in the workflow before or after the voice agent node — typically just before a Direct Transfer or Warm Handoff node.
* All fields except **Phone number** are optional and can be toggled independently.

---

Fuente original: https://docs.happyrobot.ai/voice-agents/transfer-node-popup
