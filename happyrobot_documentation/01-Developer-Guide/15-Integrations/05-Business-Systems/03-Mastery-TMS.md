---
title: "Mastery TMS"
description: "Retrieve loads and carriers, submit offers, book carriers, and post tracking updates in Mastery"
---

# Mastery TMS

> Retrieve loads and carriers, submit offers, book carriers, and post tracking updates in Mastery

The Mastery integration connects your workflows to [Mastery Logistics Systems](https://www.masterylogistics.com/). Look up a load or a carrier, run a full offer-and-book cycle on a route, assign drivers, and post tracking, stop, bounce, and incident updates back to the load — all from workflow action nodes.

## Authentication

Mastery uses an OAuth client-credentials exchange against your own token endpoint.

<Steps>
  <Step title="Enable the Mastery integration">
    Go to **Settings > Integrations** and enable **Mastery**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential** and fill in:

    * **Base URL** — your Mastery API endpoint (e.g. `https://your-api.com`)
    * **Token URL** — the OAuth token endpoint (e.g. `https://your-api.com/oauth/token`)
    * **Username** — the API user
    * **Password** — the API user's password
  </Step>

  <Step title="Save and verify">
    Save the credential and verify it appears as **Active**. Every Mastery action node selects a credential — statically or through a [variable](../../02-Workflows/07-Variables.md) — and reports `Missing required fields: credentialId` until one is set.
  </Step>
</Steps>

## Available actions

| Action                     | Description                                                                      |
| -------------------------- | -------------------------------------------------------------------------------- |
| **Find load by reference** | Looks up a load by a reference number.                                           |
| **Find carrier**           | Looks up a carrier by MC/DOT number or by carrier code.                          |
| **Submit offer**           | Posts a carrier offer on a route and returns an offer ID.                        |
| **Get offer status**       | Reads the current status of a submitted offer.                                   |
| **Book and assign**        | Books a carrier onto a route and, optionally, assigns a driver in the same call. |
| **Driver assignment**      | Assigns or removes a driver on a route.                                          |
| **Update from workflow**   | Posts tracking, stop, driver, bounce, and incident updates to a load.            |

Every field on every action supports [variables](../../02-Workflows/07-Variables.md), so an agent can fill them from the conversation.

### Find load by reference

| Field                | Required | Description                                  |
| -------------------- | -------- | -------------------------------------------- |
| **Reference number** | Yes      | The reference number to look the load up by. |

### Find carrier

Provide **either** an MC/DOT number **or** a carrier code — not both. The node reports an error if you fill in both or neither.

| Field            | Required | Description                  |
| ---------------- | -------- | ---------------------------- |
| **MC number**    | One of   | The carrier's MC number.     |
| **DOT number**   | One of   | The carrier's DOT number.    |
| **Carrier code** | One of   | The carrier code in Mastery. |

### Submit offer

Posts the offer and returns `offer_id` along with the offer acknowledgement. It does **not** wait for the carrier's reply — poll separately with **Get offer status**.

| Field                                        | Required | Description                                                                    |
| -------------------------------------------- | -------- | ------------------------------------------------------------------------------ |
| **Route number**                             | Yes      | The route the offer is placed on.                                              |
| **Carrier code** / **Override carrier code** | One of   | The offering carrier.                                                          |
| **Offer amount**                             | Yes      | The offered rate.                                                              |
| **Trailer type**, **Trailer length**         | Yes      | Equipment on the offer.                                                        |
| **Empty city**, **Empty state**              | Yes      | Where the equipment comes empty.                                               |
| **Empty datetime**                           | No       | Defaults to today at midnight UTC.                                             |
| **Currency**, **Unit**                       | No       | Default to `USD` and `ft`.                                                     |
| **Notes**, **Reference number**              | No       | Free-text bookkeeping carried onto the offer.                                  |
| **Type**, **Reason**                         | No       | Advanced offer classification. Default to an active offer with reason `OTHER`. |

### Get offer status

| Field        | Required | Description                                  |
| ------------ | -------- | -------------------------------------------- |
| **Offer ID** | Yes      | The `offer_id` returned by **Submit offer**. |

Each execution is a single read, so place this node inside a [loop](../../03-Core-Nodes/10-Loops.md) when you want to wait for a reply. The status is one of `offer_pending`, `offer_accepted`, `offer_declined`, `offer_countered`, or `offer_unknown_response`, plus offer-response fields such as the counter price and response notes when the carrier sends them.

### Book and assign

| Field                                               | Required     | Description                                                                                                                                                                                                                                                  |
| --------------------------------------------------- | ------------ | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Route number**                                    | Yes          | The route to book.                                                                                                                                                                                                                                           |
| **Carrier code** / **MC number** / **DOT number**   | One of       | The carrier being booked.                                                                                                                                                                                                                                    |
| **Empty city**, **Empty state**, **Empty datetime** | Yes          | Expected-ready location and time.                                                                                                                                                                                                                            |
| Booking detail                                      | At least one | **Linehaul amount**, trailer type or length, empty location or datetime, notes, or CC emails. Mastery rejects a booking with an empty body.                                                                                                                  |
| Driver fields                                       | No           | **Driver name/phone**, **second driver name/phone**, **tractor number**, **trailer number**, **tracking method**, **tracking enabled**, **dispatched**. Filling in any of them chains a driver assignment onto the booking; leaving them all blank skips it. |

### Driver assignment

| Field                      | Required    | Description                                                                                                                                                     |
| -------------------------- | ----------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Action**                 | Yes         | **Assign driver** or **Remove driver**.                                                                                                                         |
| **Route number**           | Yes         | The route to change.                                                                                                                                            |
| Driver or equipment detail | Assign only | At least one of driver name/phone, second driver name/phone, tractor number, trailer number, or tracking method. Removal needs nothing beyond the route number. |

Tracking and dispatch default to enabled when left blank.

### Update from workflow

One node that inspects which fields you filled in and performs the matching updates — stop events, driver assignment, tracking, bounce, and incident work.

| Group                | Fields                                                                                                                |
| -------------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Load**             | **Custom load ID** (required).                                                                                        |
| **Origin stop**      | In time, out time, ETA.                                                                                               |
| **Destination stop** | In time, out time, ETA.                                                                                               |
| **Driver**           | Driver name, driver phone, wrong driver.                                                                              |
| **Carrier**          | Carrier code, needs bounce, bounce reason.                                                                            |
| **Tracking**         | Tracking method, current location.                                                                                    |
| **Issues**           | Has issues, **Issue type** (dropdown of Mastery issue-type terms, defaults to `carrier_related`), notes, incident ID. |
| **Attribution**      | Employee ID, employee code, customer code.                                                                            |

## Example use case

A carrier calls in about a load. The voice agent asks for the reference number and runs **Find load by reference**, then **Find carrier** with the caller's MC number. When the carrier makes an offer, a tool runs **Submit offer** on the route and a loop polls **Get offer status** until Mastery returns an accept, decline, or counter. On an accept, **Book and assign** books the carrier and records the driver in the same step, and a follow-up call uses **Update from workflow** to post the driver's ETA.

## Related

<CardGroup cols={2}>
  <Card title="McLeod TMS" icon="truck" href="01-McLeod-TMS.md">
    McLeod LoadMaster integration.
  </Card>

  <Card title="Credentials" icon="key" href="../02-Credentials.md">
    How credentials are stored, scoped, and selected in nodes.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/business-systems/mastery
