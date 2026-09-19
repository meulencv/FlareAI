---
title: "Telephony"
description: "Manage phone numbers, SIP trunks, and audio assets"
---

# Telephony

> Manage phone numbers, SIP trunks, and audio assets

The Telephony page manages your phone infrastructure and audio assets. Buy and configure phone numbers, verify caller IDs, connect SIP trunks for your own telephony, and manage audio assets like recording disclaimers and hold music. The page is organized into four tabs: **Phone Numbers**, **Verified Numbers**, **Audio Library**, and **Compliance**.

## Phone numbers

The **Phone Numbers** tab shows one row per phone number. HappyRobot keeps a registry of every number it can see across your Twilio, Telnyx, and WhatsApp connections and your SIP trunks, so a number you own in more than one place appears once, with all of its providers on the same row.

### Buying a phone number

<Steps>
  <Step title="Start the purchase">
    Go to **Assets > Telephony** and click **Buy Number**.
  </Step>

  <Step title="Name the number">
    Enter a descriptive name so you can identify the number later (e.g., "Inbound Support Line" or "Outbound Sales").
  </Step>

  <Step title="Select country and area code">
    Choose the country using the flag selector. For US and Canadian numbers, you can also specify an area code to get a local number.
  </Step>

  <Step title="Choose a provider">
    Select your telephony provider (see provider options below).
  </Step>

  <Step title="Select number type">
    Choose the number type based on availability for your selected country.
  </Step>
</Steps>

<Note>
  For **regular US Twilio numbers**, the purchase dialog lets you attach an approved [business profile](#business-profiles) for compliance. Selecting one is optional — the dialog warns when no approved profile is set but still allows the purchase.
</Note>

### Providers

| Provider    | Notes                                                          |
| ----------- | -------------------------------------------------------------- |
| **Twilio**  | Full support for all number types and regions.                 |
| **Telnyx**  | Supported for most regions, including US/CA toll-free numbers. |
| **VoIP.ms** | Additional provider option for supported regions.              |

### Number types

For **US and Canadian** numbers:

* **Regular** — Standard local or national number
* **Toll-Free** — Caller pays no charges (e.g., 800, 888, 877 prefixes)

For **international** numbers, availability varies by country:

* **Local** — Number with a local area code
* **National** — Nationally reachable number
* **Mobile** — Mobile phone number
* **Toll-Free** — International toll-free number

### US and Canadian toll-free numbers

A US or CA toll-free number can't send SMS until the carrier verifies who is messaging and why, so buying one opens a **toll-free verification** form in the purchase dialog. This applies to both **Twilio** and **Telnyx**; the number is bought and the verification submitted in one step, and messaging stays blocked until the carrier approves it.

The form is split into four tabs:

| Tab           | What it covers                                                                                                                |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Business**  | Legal name, website, business type, registration details, and the registered address.                                         |
| **Technical** | The inbound message webhook URL and method, an optional fallback URL, and the email that receives verification notifications. |
| **Use case**  | Estimated monthly message volume, use-case categories, a summary of what you send, and a sample production message.           |
| **Opt-in**    | How recipients consent to messages, an opt-in screenshot URL, and any additional information.                                 |

Requirements differ slightly by provider:

| Requirement                                          | Twilio                                | Telnyx                                                       |
| ---------------------------------------------------- | ------------------------------------- | ------------------------------------------------------------ |
| Business registration number, authority, and country | Required, except for sole proprietors | Required for every business type, including sole proprietors |
| Opt-in image URL                                     | Optional                              | Required                                                     |

<Tip>
  The opt-in image is a screenshot of where recipients agree to receive messages — a web form with a consent checkbox, a printed sign-up sheet, or your keyword opt-in instructions. Host it at a public URL before starting the form.
</Tip>

### The phone numbers table

| Column               | What it shows                                                                                                                                                                                                                   |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**             | The label you gave the number, or the number itself when it has no name.                                                                                                                                                        |
| **Number**           | The number in E.164 format, with a copy button.                                                                                                                                                                                 |
| **Providers**        | A badge per provider connection on that number — **Twilio**, **Telnyx**, **WhatsApp** — plus **SIP** when a custom SIP trunk carries it. A badge turns amber when HappyRobot can no longer see that connection at the provider. |
| **Calling Status**   | Whether the number can take and place voice calls.                                                                                                                                                                              |
| **Messaging Status** | Whether the number can send and receive messages.                                                                                                                                                                               |
| **Usage**            | A dot per environment the number is published in. Hover to see each workflow, version, and environment. Empty means the number isn't used by any published version.                                                             |

### Calling and messaging status

Both status columns roll every provider on the row up into one badge:

| Badge            | Meaning                                                                                                               |
| ---------------- | --------------------------------------------------------------------------------------------------------------------- |
| **Synced**       | At least one provider is configured and routed to HappyRobot. The number works for that capability.                   |
| **Other region** | The number is claimed by a different HappyRobot region or cluster, so this workspace can't route it.                  |
| **Not synced**   | No provider is routed to HappyRobot yet. Use the row's sync actions.                                                  |
| **Missing**      | HappyRobot can no longer find the number at any provider that reported it.                                            |
| *(empty)*        | No provider on the number supports that capability at all — a voice-only number has no messaging status, for example. |

Hover a badge for the per-provider breakdown. Calling shows **Inbound** and **Outbound** separately — a one-directional SIP trunk leaves the other direction blank — and each line names the reason it isn't synced: *No trunk*, *Voice unsupported*, *TwiML app configured*, *External webhook configured*, or *Toll-free verification required*, for example. Messaging reasons include *SMS unsupported* and *Messaging profile missing*. WhatsApp connections add their own, such as *Calling disabled*, *Meta SIP enabled*, and *SRTP is not DTLS*.

<Note>
  Only numbers whose calling is **Synced** appear in workflow number pickers — the inbound voice trigger, the outbound voice agent's caller ID, and the [Forward call](../05-Voice-Agents/07-Forward-call.md) node. A number that isn't routed to HappyRobot can't take or place a call, so picking it would attach a trigger that never fires. WhatsApp connections are left out of outbound picker options, since they can't place PSTN calls.
</Note>

### Syncing the registry

HappyRobot refreshes the registry from your providers when you open the **Phone Numbers** tab. To pull changes you just made at the carrier, use the **Sync phone numbers** button (circular arrow) in the page controls. If one provider fails, the others still sync and a warning names the one that didn't.

### Phone number settings

Choose **Edit** on a number's action menu to see its number, type, and providers, and to change:

| Setting                | Description                                                                                                                                                                                                                                                                                                                                                                                           |
| ---------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**               | Descriptive label for the number. Names must be unique within the workspace.                                                                                                                                                                                                                                                                                                                          |
| **Transfer Caller ID** | Shown for numbers with a Twilio connection. Controls what number a human agent sees on their phone when a call is directly transferred to them. Choose **Our Number** to show the HappyRobot phone number, or **Caller's Number** to pass through the original caller's number. This setting doesn't apply to warm or whisper transfers — for warm handoffs, use the per-node toggle described below. |

<Note>
  Numbers no longer carry an environment you set by hand. A number's environment now comes from the published workflow versions that use it, which is what the **Usage** column and the **Environment** filter read.
</Note>

Renaming a number writes the new name back to whichever provider owns it, so it survives a reload: Twilio numbers are renamed in Twilio, Telnyx numbers get the name as their customer reference, and a custom SIP trunk's number is renamed on the trunk. Names are trimmed and can be up to 255 characters — a blank or over-long name is rejected rather than saved.

### Showing the caller's number on warm handoffs and forwards

**Transfer Caller ID** above applies to direct transfers. Warm handoffs and the [Forward call](../05-Voice-Agents/07-Forward-call.md) node have their own per-node toggle, **Show the original caller's number**:

* On the **Transfer** node, it appears under **Advanced Telephony** when the transfer is a warm handoff.
* On the **Forward call** node, it appears under **Advanced configuration**.

Both are off by default and require carrier-side support. On a bring-your-own Twilio account the toggle has no effect until [Immutable Call Forwarding](https://www.twilio.com/en-us/changelog/elastic-sip-trunking---immutable-call-forwarding-with-calltoken-) is enabled on the account in Twilio; when the carrier gives HappyRobot no way to authorize the number, the call still connects and shows your number instead. Test on your own numbers before relying on it.

<Note>
  When the destination sees the caller's number, a callback from that phone reaches the caller rather than your business. Leave the toggle off if callbacks should come back to you.
</Note>

### Choosing the number a transfer or forward dials from

Transfers and forwards can also pick which of your numbers the **outbound** leg originates on, using the **From number** field:

* On the **Transfer** node, it appears under **Advanced Telephony** for warm handoffs and whisper transfers.
* On the **Forward call** node, it appears under **Advanced configuration**.

The field is a picker over the numbers your organization owns, including SIP numbers, because the value resolves a **SIP trunk** rather than only a caller ID — pointing it at an internal trunk keeps the outbound leg off your carrier. Leave it empty and the leg dials from the number the call arrived on; use **Clear** to return to that default.

<Warning>
  A [web call](../02-Workflows/05-Triggers.md#web-call) arrives on no number of its own, so a transfer or forward on a web call workflow has nothing to fall back to and **From number** becomes required. See [Choosing the number to dial out from](../05-Voice-Agents/07-Forward-call.md#choosing-the-number-to-dial-out-from).
</Warning>

### Where a number is used

Choose **View usage** on a number's action menu to see every workflow and version that references it, grouped by workflow. From here you can detach the number:

* **Per version** — remove the number from a single version.
* **From all versions** — hover a workflow's header row and use **Remove from all versions** to detach the number from every non-live version of that workflow in one action. Live versions can't be edited, so they're skipped and left untouched; the confirmation tells you how many versions will change and how many live ones are being left alone.

### Number actions

Each row's **…** menu is grouped by what the action applies to. Actions you don't have permission for are hidden.

| Group                   | Action                                                      | What it does                                                                                                                                                                                                     |
| ----------------------- | ----------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| *(number)*              | **Edit**                                                    | Open the settings dialog above.                                                                                                                                                                                  |
|                         | **View usage**                                              | Show every workflow and version using the number.                                                                                                                                                                |
|                         | **Manage tags**                                             | Assign [Scope Tags](../16-Account-and-Settings/04-Scope-Tags.md) to the number. Tags apply to the number as a whole, across all of its providers, and are what access scopes and workflow resource compatibility are evaluated against. |
|                         | **Free number**                                             | Detach the number from every non-live use case at once. Only offered when the number is in use and none of those uses are live.                                                                                  |
| **Twilio** / **Telnyx** | **Sync calling**                                            | Provision the carrier number for HappyRobot voice. If the number already points somewhere else at Twilio, the confirmation names the routing that will be replaced.                                              |
|                         | **Toll-free verification**                                  | Open the toll-free verification flow. Shown for toll-free Twilio numbers.                                                                                                                                        |
|                         | **Assign profile**                                          | Attach an approved [business profile](#business-profiles). Shown for regular Twilio numbers.                                                                                                                     |
|                         | **Release number**                                          | Release the number at the provider. Blocked while the number is used by any workflow version.                                                                                                                    |
| **WhatsApp**            | **Register number** / **Sync messaging** / **Sync calling** | See [WhatsApp numbers](#whatsapp-numbers) below.                                                                                                                                                                 |
| **SIP**                 | **Delete SIP trunk**                                        | Delete a custom SIP trunk. Blocked while the number is in use.                                                                                                                                                   |

<Warning>
  **Release number** removes the number from your provider account and may not be recoverable. **Free number** and **Delete SIP trunk** only change HappyRobot.
</Warning>

<Note>
  **Sync calling** appears only while the provider still reports the capability as available and the number has no trunk yet. Telnyx numbers are routed for calling by HappyRobot — contact support if a Telnyx number shows **Not synced**.
</Note>

### Filtering phone numbers

Use filters to find specific numbers in your inventory:

* **Type** — Twilio, Telnyx, SIP Trunk, or WhatsApp
* **Environment** — Production, Staging, Development, or Inactive. This matches the environments the number is published in; **Inactive** means no published version uses it.
* **Sync status** — Synced, Other Region, or Not Synced, matching the **Calling Status** column
* **Number type** — Toll-Free Only or Regular Only

Search matches both the number's name and its digits.

### Twilio number capabilities

Voice agents require a voice-capable number. HappyRobot reads each number's capabilities from the provider and reports them in the status columns:

* A number that supports SMS but not voice shows **Voice unsupported** in the **Calling Status** tooltip, and **Sync calling** is hidden for it.
* A number that supports neither shows **Voice unsupported** and **SMS unsupported**. HappyRobot doesn't support fax- or MMS-only numbers.

This prevents failed sync attempts on numbers the carrier would reject as not SIP-trunking capable.

### Telnyx numbers being ported

Telnyx numbers with a **port-pending** status are hidden from the inventory. Until the port completes, the number still belongs to the losing carrier — listing it would show the same number twice, once under each carrier, while the port is in flight. It appears as a Telnyx number once the port takes effect.

## WhatsApp numbers

WhatsApp numbers are managed from the **Phone Numbers** tab, alongside your carrier numbers. Everything that used to live on the WhatsApp integration's **Cloud Migration** tab — verification, Cloud API registration, and calling settings — is now on the number's own row.

A WhatsApp Business number with [Business Calling](../15-Integrations/04-Communication/08-WhatsApp.md#whatsapp-business-calling) enabled can take voice calls through HappyRobot, and appears in the inbound voice trigger's number picker alongside your carrier numbers.

Which WhatsApp actions a row offers depends on what HappyRobot already knows about the number:

| Action              | Shown when                                                                                                                                                                                                                                                        |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Register number** | The number is a Twilio or Telnyx number that isn't on a WhatsApp Business Account (WABA) yet. When the number exists at more than one carrier, the menu offers **Register via Twilio** and **Register via Telnyx** so you choose which one Meta verifies against. |
| **Sync messaging**  | The number is on a WABA but its messaging isn't routed to HappyRobot.                                                                                                                                                                                             |
| **Sync calling**    | The number is registered on Cloud API but Business Calling isn't routed to HappyRobot.                                                                                                                                                                            |

<Note>
  Your Meta account needs Business Verification before a WhatsApp number can take calls.
</Note>

### Syncing a number already on WhatsApp

<Steps>
  <Step title="Configure messaging">
    Choose **Sync messaging** on the number's action menu. If Meta still needs to verify the number, pick **SMS** or **Voice call**, click **Request code**, enter the code Meta sends, and click **Configure messaging**. If the number is already verified, the dialog just confirms — HappyRobot updates the WhatsApp subscription, callback, and Cloud API registration.
  </Step>

  <Step title="Configure calling">
    Choose **Sync calling** and confirm. HappyRobot turns on WhatsApp Business Calling for the number and points its call events at this cluster. The action is disabled with a tooltip until messaging is synced, because Cloud API registration has to come first.
  </Step>

  <Step title="Use the number">
    Once **Calling Status** reads **Synced**, the number is available in the inbound voice trigger's number picker.
  </Step>
</Steps>

#### Numbers shared across providers

The same phone number can exist as both a carrier number and a WhatsApp number. Both connections now live on a single row, and the **Providers** column shows a badge for each, so you can see at a glance that a number carries voice through Twilio and messaging through WhatsApp. The two still route independently — hover the **Calling Status** and **Messaging Status** badges for the per-provider breakdown.

The inbound voice trigger's number picker shows a provider badge on each option and on each selected number, so you can tell the carrier and WhatsApp connections apart when wiring a workflow.

WhatsApp connections route through the WhatsApp connector rather than a SIP trunk, so they're excluded from SIP dispatch rules and can't be assigned a caller ID or released from the numbers table.

### Registering a carrier number on WhatsApp

Registering adds one of your existing numbers to your WhatsApp Business Account so it can send WhatsApp messages and take WhatsApp calls. The number keeps working for regular voice calls and SMS.

<Steps>
  <Step title="Start the registration">
    On the **Phone Numbers** tab, open the number's action menu and choose **Register number** under **WhatsApp**. Meta verifies by calling the number and reading a code aloud, so it has to be voice-capable — the action is disabled with a tooltip on numbers that can't receive Meta's call.
  </Step>

  <Step title="Choose the WhatsApp account">
    Pick the [WhatsApp credential](../15-Integrations/04-Communication/08-WhatsApp.md) whose Business Account the number should join. If you only have one, it's selected for you.
  </Step>

  <Step title="Set the display name">
    Enter the name people see on WhatsApp (for example, "Acme Logistics"). Meta reviews display names separately — the name can stay pending after the number is linked.
  </Step>

  <Step title="Say where the verification call should go">
    Enter a phone you can answer. For the length of the code window, calls to the number being registered are forwarded there so you can hear the code, then routing goes back to normal.
  </Step>

  <Step title="Enter the code">
    Meta calls and reads a verification code aloud. Type it into the dialog and click **Verify**. You have 10 minutes, and you need to stay on the screen — leaving cancels the attempt and restores the number's routing.
  </Step>
</Steps>

Once the code is accepted, HappyRobot registers the number on WhatsApp Cloud API and — if your account is eligible — turns on WhatsApp Business Calling automatically.

### When the verification call can't be forwarded

Before anything starts, the dialog checks where the code would actually land and warns you if it can't redirect the call. In that case Meta's call goes wherever the number already points, and you read the code off that run's [transcript](../09-Runs-and-Monitoring/03-Transcripts-and-Messages.md) instead. This happens when:

* **The number answers a live workflow.** HappyRobot won't take a production number off the air to register it.
* **The number isn't one HappyRobot can repoint** — a Telnyx number, or a Twilio number on an account HappyRobot doesn't manage. If the number isn't answering anything at all, you won't be able to retrieve the code.
* **Call forwarding isn't configured** in your environment.

<Tip>
  When the warning appears, open the **Runs** table in a *new tab* before starting — navigating away from the dialog loses track of the attempt.
</Tip>

### Attempt statuses

| Status                | Meaning                                                                                      |
| --------------------- | -------------------------------------------------------------------------------------------- |
| **Adding the number** | HappyRobot is adding the number to your WABA and asking Meta to place the verification call. |
| **Awaiting code**     | Meta has called. Enter the code before the 10-minute window closes.                          |
| **Verifying**         | The code was submitted and is being checked with Meta.                                       |
| **Registering**       | The code was accepted; the number is being registered on WhatsApp Cloud API.                 |
| **Linked**            | Done. The number is live on Cloud API under the display name you gave.                       |
| **Failed**            | Meta refused the request. The dialog shows the reason — click **Try again** to restart.      |
| **Expired**           | The code window passed before the code was used. Start a new attempt.                        |

<Warning>
  Cancelling or dismissing an attempt removes it from HappyRobot but does **not** detach the number from your WABA. A number that already finished registering stays live on Meta and has to be removed in Business Manager.

  Meta also limits registration attempts per number (ten per 72 hours), so avoid starting attempts you don't intend to finish.
</Warning>

## SIP trunks

For organizations that bring their own telephony infrastructure, SIP trunks let you connect your existing phone system to HappyRobot.

### Creating a SIP trunk

| Field                  | Description                                                                                                                                                                              |
| ---------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Direction**          | Which sides of the call this trunk handles: **Inbound and outbound** (both), **Inbound only**, or **Outbound only**. Required fields change based on the selected direction (see below). |
| **Phone numbers**      | Array of phone numbers in +E.164 format (e.g., `+15551234567`). These are the numbers routed through this trunk.                                                                         |
| **SIP server address** | Your SIP server's domain or IP address with port (e.g., `sip.example.com:5060`). Required for outbound and bidirectional trunks; not required for inbound-only trunks.                   |

### Direction requirements

| Direction                | SIP server address | Source-IP allowlist |
| ------------------------ | ------------------ | ------------------- |
| **Inbound and outbound** | Required           | Required            |
| **Inbound only**         | Not required       | Required            |
| **Outbound only**        | Required           | Not required        |

### Optional settings

| Setting                         | Description                                                                                                                                                                                                                                                                                                                                                                                           |
| ------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Allowed addresses**           | IP addresses or CIDR ranges to whitelist for inbound traffic. Restricts which servers can send calls to HappyRobot through this trunk. Required for inbound and bidirectional trunks.                                                                                                                                                                                                                 |
| **Genesys carrier**             | Toggle for carriers whose source IPs are pre-trusted by HappyRobot's SBC (Genesys is the current example). When enabled, the per-trunk **Allowed addresses** field is hidden and submitted empty — inbound calls are still gated at the SBC by the infrastructure-level allowlist. Use this when you're connecting a Genesys SIP trunk and have already coordinated the IP allowlist with HappyRobot. |
| **Authentication**              | Toggle to enable username/password authentication for the SIP trunk connection.                                                                                                                                                                                                                                                                                                                       |
| **Attribute → Header mappings** | For inbound and bidirectional trunks, map call attributes to outbound SIP header names. When a workflow tool sets a room attribute during a call (for example, on hangup), HappyRobot surfaces that value to your carrier as the mapped SIP header. Both the attribute and header names must use valid SIP token characters. Leave empty for no mapping.                                              |

<Note>
  Manually created SIP trunks (custom provider) are billed on a yearly recurring schedule. The billing item is created automatically when the trunk is provisioned and ends when the trunk is deleted.
</Note>

## Verified numbers

Verified numbers are external phone numbers — numbers you don't own in HappyRobot — that you've proven you control. Once verified, a number can be set as the **Verified caller ID** on outbound voice agents, so the recipient sees that number on their phone instead of the underlying HappyRobot or Twilio number.

The **Verified Numbers** tab is the source of truth for your organization's caller-ID state. Verifications you start from the HappyRobot UI and any numbers you previously verified directly in the Twilio Console both appear here.

### Verifying a number

<Steps>
  <Step title="Start a verification">
    Open **Assets > Telephony > Verified Numbers** and click **Add New > Verified Number**. Enter the phone number in E.164 format (e.g., `+15551234567`) and a descriptive friendly name.
  </Step>

  <Step title="Answer the verification call">
    HappyRobot starts a Twilio validation request, which triggers a phone call to the number you entered. The verification dialog displays a 6-digit code.
  </Step>

  <Step title="Enter the code">
    On the receiving phone, enter the 6-digit code on the keypad when prompted. The dialog polls for the result and updates automatically when Twilio confirms the code.
  </Step>

  <Step title="Use the number">
    Once verified, the number is available in the **Verified caller ID** dropdown on outbound voice agent nodes. See [Outbound calls — Destination and caller ID](../05-Voice-Agents/03-Outbound-Calls.md#destination-and-caller-id).
  </Step>
</Steps>

### Status reference

Each row in the table shows the verification's current status:

| Status        | Meaning                                                                                                                                                           |
| ------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Pending**   | Verification is in progress — waiting for the user to enter the code.                                                                                             |
| **Completed** | Verification succeeded. The number can be used as a verified caller ID.                                                                                           |
| **Failed**    | The user entered the wrong code, or Twilio reported a failure. Start a new verification to retry.                                                                 |
| **Expired**   | The verification window closed before the code was entered. Start a new verification to retry.                                                                    |
| **Removed**   | The number was deleted from Twilio (either here or in the Twilio Console). Flows configured to use this number as the caller ID will fail until it's re-verified. |

### Managing verified numbers

* **Rename** — Update the friendly name from the row's action menu. This also updates the name in Twilio.
* **Delete** — Remove the number from Twilio. If any voice agents are configured to use it as the verified caller ID, those flows will fail at call time.

<Note>
  HappyRobot syncs with Twilio on every visit to the Verified Numbers tab. Numbers added or removed directly in the Twilio Console show up the next time the page loads.
</Note>

## Audio library

The audio library manages audio assets used by your voice agents during calls.

### Asset types

| Type                   | Description                                                                                     |
| ---------------------- | ----------------------------------------------------------------------------------------------- |
| **Disclaimer**         | Recording notices played at the start of a call to inform the caller about recording.           |
| **Hold Music**         | Audio played while the caller is on hold or during call transfers.                              |
| **Warm Handoff Intro** | Audio played to the receiving agent during a warm handoff before connecting them to the caller. |

### Creating a disclaimer

You can create disclaimers using two methods:

**TTS generation** — Generate a disclaimer using text-to-speech:

1. Select a voice from the voice library
2. Type the disclaimer text (max 1,000 characters)
3. Preview the audio before saving to make sure it sounds right

**Custom upload** — Upload a pre-recorded disclaimer:

1. Upload a WAV file (max 10 MB)
2. The file is automatically converted to 8 kHz for telephony compatibility

<Tip>
  The **Custom upload** option is recommended when legal compliance requires specific approved wording — have your legal team sign off on the recording before uploading.
</Tip>

### Uploading hold music

Upload hold music as a WAV file (max 10 MB, auto-converted to 8 kHz). Hold music plays when an agent places a caller on hold or during call transfers.

Every tool node's **Hold music** picker also offers three built-in tracks before your uploads:

| Track               | When to use it                                                                                                                                                                      |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Acoustic**        | A short instrumental loop, for holds where a ringing tone would be misleading.                                                                                                      |
| **Ring tones**      | North American ringback, so the caller believes the line is still ringing.                                                                                                          |
| **Ring tones (EU)** | The ETSI ringback tone (425 Hz, one second on and four seconds off) European callers expect. Use this on EU-facing numbers — the North American tone sounds wrong to those callers. |

### Warm handoff intro audio

By default, the Transfer node plays a built-in audio clip to the receiving agent during a warm handoff. To use a custom recording instead:

1. Upload the audio as a WAV file in the audio library (max 10 MB, auto-converted to 8 kHz).
2. Open the Transfer node in your workflow.
3. Under the warm handoff settings, set **Intro mode** to **Custom** and select your audio asset.

### Using audio assets

* **Disclaimers** — Reference your disclaimer in the voice agent's recording settings. See [Inbound calls > Recording and disclaimers](../05-Voice-Agents/02-Inbound-Calls.md#recording-and-disclaimers) for configuration details.
* **Hold music** — Reference hold music in voice agent tool nodes that trigger holds or transfers.
* **Warm handoff intro** — Reference custom intro audio in the Transfer node's warm handoff settings.

### Managing assets

View each asset's duration, assigned environment, and usage across workflows. The platform tracks where each asset is referenced.

**Renaming an asset** — Choose **Edit** on an asset to change its **name** and **description**. Both are labels only; the audio file itself is unchanged, so every workflow that references the asset keeps working. Use this to fix a typo or relabel an asset instead of re-uploading it.

Descriptions are optional everywhere an asset is created — upload, TTS disclaimer, and warm handoff intro — which lets the library hold a short label such as "Recording disclaimer — Spanish" rather than the whole spoken script.

<Info>
  Assets with active usages cannot be deleted. Remove all references to an asset from your workflows before deleting it.
</Info>

## Compliance

Certain phone number types or regions may require a compliance application before the number can be activated. The **Compliance** tab tracks two kinds of resources — **compliance bundles** and **business profiles** — each with a status:

* **Approved** — The application was accepted and the number is active.
* **Pending** — The application is under review.
* **Rejected** — The application was denied. Review the rejection reason and resubmit with corrections.

### Business profiles

A **Business Profile** is a Twilio Secondary Business Profile used to satisfy US calling regulations. Once a profile is approved, you can attach it to regular US Twilio numbers you purchase.

#### Creating a business profile

<Steps>
  <Step title="Open the Business Profile dialog">
    On the **Compliance** tab, click **Add New > Business Profile**.
  </Step>

  <Step title="Fill in the Business tab">
    Enter the business details: **Display Name**, **Business Name**, **Business Identity**, **Business Type**, **Business Industry**, **Registration Identifier** (e.g., EIN), **Registration Number**, **Region of Operation**, **Website URL**, and an optional **Social Media URL**.
  </Step>

  <Step title="Fill in the Address tab">
    Enter the registered business address — **Street**, **Suite/Apt**, **City**, **State**, **Postal Code**, and **Country**.
  </Step>

  <Step title="Fill in the Representative tab">
    Enter an authorized representative's contact details, including name, job position, email, and phone number.
  </Step>

  <Step title="Submit for review">
    Submit the profile to Twilio. It appears in the compliance table as **Pending** until Twilio completes its review.
  </Step>
</Steps>

#### Syncing from Twilio

If you already created business profiles directly in the Twilio Console, click the **Sync Business Profiles from Twilio** button on the **Compliance** tab to import them and refresh their statuses.

#### Assigning a business profile to a number

When you buy a **regular US Twilio number**, you can select an approved business profile in the purchase dialog. If you don't have an approved profile yet, the dialog shows a warning but still lets you complete the purchase. You can also assign a profile to an existing number later from the phone number's action menu.

<Note>
  Through the [API](https://docs.happyrobot.ai/api-reference), pass the approved profile's ID as `business_profile_application_id` on the [buy phone number](https://docs.happyrobot.ai/api-reference) request when purchasing a regular US Twilio number.
</Note>

### Renaming a compliance resource

To rename a bundle or business profile, open the row's action menu (the ellipsis **…** icon) and select **Rename**. Enter the new name and confirm. Renaming is available directly from the compliance table without navigating to the resource's settings page.

## Next steps

<CardGroup cols={3}>
  <Card title="Inbound calls" icon="phone-arrow-down-left" href="../05-Voice-Agents/02-Inbound-Calls.md">
    Configure agents to handle incoming calls.
  </Card>

  <Card title="Outbound calls" icon="phone-arrow-up-right" href="../05-Voice-Agents/03-Outbound-Calls.md">
    Set up automated outbound calling.
  </Card>

  <Card title="Voice agents" icon="microphone" href="../05-Voice-Agents/01-Voice-Agents-Overview.md">
    Get started with AI voice agents.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/assets/telephony
