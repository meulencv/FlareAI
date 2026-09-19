---
title: "Built-in Tools"
description: "Default tools that come with voice and text agents"
---

# Built-in Tools

> Default tools that come with voice and text agents

AI agents come with built-in tools that handle common behaviors without requiring custom tool nodes. Some are always available; others activate based on agent configuration.

## The Built-in tab

Built-in tools are configured on the agent's **prompt node**, not on the agent node. Open the prompt node and switch to the **Built-in** tab — next to **Behavior** — to see every built-in the current channel supports, toggle the ones you want, and expand a row to configure it.

The tab is channel-aware: a voice agent shows hang up, stay silent, and press digit, while a text agent shows the built-ins its channel supports (email actions on email, interactive messages on WhatsApp, and so on). Turning a built-in on or off here is what makes the corresponding tool available to the model.

<Note>
  On an outbound-with-callback voice agent the prompt node's tabs are **Outbound**, **Inbound**, and **Built-in**. Built-in tools are shared across both call directions.
</Note>

### Seeing what's active from the canvas

A prompt node with active built-ins shows a **built-in** badge on the canvas. Hover it to list the built-ins currently enabled for that agent, and click an entry to jump straight to its configuration in the **Built-in** tab. This is the quickest way to confirm what the model can actually call before you publish.

### Referencing a built-in from the prompt

You can name a tool inline in the prompt instead of typing its runtime identifier by hand. Type `/` in the prompt editor and pick from:

* **Built-in tools** — the built-ins for this channel
* **Custom tools** — [tool nodes](02-Creating-Tools.md) attached below this prompt
* **MCP tools** — tools exposed by a connected [MCP server](05-MCP-Tools.md)

The tool is inserted as a chip that resolves to the tool's runtime name when the agent runs, and it follows renames automatically. A chip for a built-in that is switched off — or for a tool node that was deleted — is shown as disabled, so a prompt that instructs the agent to use a tool it doesn't have is visible at a glance.

## Voice agent built-in tools

| Tool        | Internal Name  | Availability | Description                                                      |
| ----------- | -------------- | ------------ | ---------------------------------------------------------------- |
| Hangup      | `_hangup`      | Always       | Ends the call gracefully.                                        |
| Stay silent | `_stay_silent` | Configurable | Lets the agent skip speaking for a turn without ending the call. |
| Press digit | `_press_digit` | Configurable | Presses digits to navigate automated phone menus.                |
| Voicemail   | `_voice_mail`  | Conditional  | Handles voicemail detection on outbound calls.                   |

<AccordionGroup>
  <Accordion title="Hangup">
    Always injected for voice agents. When the agent determines the conversation is complete, it calls this tool to end the call.

    The agent is instructed not to end calls prematurely — before hanging up, it confirms the caller has no further questions and generates a natural goodbye message.

    No configuration is required. This tool is always on and its switch in the **Built-in** tab cannot be turned off.
  </Accordion>

  <Accordion title="Stay silent">
    Enabled with the **Stay silent** switch in the prompt node's **Built-in** tab. When on, the agent can choose not to respond during its turn where silence is more natural — for example, when the caller says "hang on, let me find that number," the agent won't fill the pause with unnecessary speech.

    Turn it off if the agent should always say something on every turn.

    **Play acknowledgement** — a sub-setting that appears under **Stay silent** once it's on. By default the agent says a short "Mhmm." before going quiet, which signals to the caller that the line is still live. Turn it off for complete silence, which suits callers who are reading out a long list of numbers and shouldn't be interrupted at all.
  </Accordion>

  <Accordion title="Press digit">
    Enabled with the **Press digit** switch in the prompt node's **Built-in** tab. The agent can press digits (0–9, `*`, `#`) to navigate IVR and automated phone menus.

    **Parameter:**

    | Name  | Type   | Description                                                    |
    | ----- | ------ | -------------------------------------------------------------- |
    | `key` | string | The digit or symbol to press. Valid values: `0`–`9`, `*`, `#`. |

    Tell the agent how to navigate the menu (e.g., "Press 1 for English, then press 3 for dispatch, then press 0 to speak with an agent."). Where these instructions go depends on the agent type:

    * **Outbound agents** have a dedicated instructions field inside the expanded **Press digit** row, separate from the main conversation prompt. It supports [variables](../02-Workflows/07-Variables.md).
    * **Inbound agents** don't have a separate field — add the navigation instructions directly to the agent's main prompt.

    <Tip>
      Keep navigation instructions specific to the IVR the agent will encounter. If the menu changes often, use flexible guidance like "Listen to the options and press the number for the billing department."
    </Tip>
  </Accordion>

  <Accordion title="Voicemail">
    Available on **outbound voice agents only**. Unlike the built-ins above, voicemail is configured on the agent node's **Behavior** tab rather than the prompt node.

    Three modes are available:

    | Mode       | Behavior                                                                              |
    | ---------- | ------------------------------------------------------------------------------------- |
    | **Hangup** | Silently ends the call when voicemail is detected.                                    |
    | **Fixed**  | Leaves a specific pre-written voicemail message, then hangs up.                       |
    | **AI**     | The agent generates a voicemail message based on the prompt and conversation context. |

    <Info>
      Voicemail detection uses strict rules — the tool is only invoked when the system is confident a voicemail greeting or recording system is active. Background noise, hold music, or brief silences will not trigger it.
    </Info>

    See [Outbound Calls](../05-Voice-Agents/03-Outbound-Calls.md) for details.
  </Accordion>
</AccordionGroup>

## Text agent built-in tools

| Tool                      | Internal Name                               | Availability  | Description                                                                     |
| ------------------------- | ------------------------------------------- | ------------- | ------------------------------------------------------------------------------- |
| Terminate                 | `_terminate`                                | Always        | Ends the agent's chain of thought.                                              |
| End conversation          | `hr_builtin_tool__end_conversation`         | Configurable  | Gracefully ends the conversation.                                               |
| Escalate to human         | `hr_builtin_tool__escalate_to_human`        | Configurable  | Hands the conversation to a human agent.                                        |
| Skip turn                 | `hr_builtin_tool__skip_turn`                | Configurable  | Marks the current event handled without sending a message or running an action. |
| Read media                | `hr_builtin_tool__read_media`               | Configurable  | Reads images, documents, and voice notes the contact sent.                      |
| Skip turn                 | `hr_builtin_tool__skip_turn`                | Configurable  | Takes no action for the current event and waits for the next one.               |
| Send email                | `hr_builtin_tool__send_email_{provider}`    | Email channel | Starts a new email thread.                                                      |
| Reply to email            | `hr_builtin_tool__reply_email_{provider}`   | Email channel | Replies in the current email thread.                                            |
| Forward email             | `hr_builtin_tool__forward_email_{provider}` | Email channel | Forwards the current email to new recipients.                                   |
| Send voice note           | `hr_builtin_tool__send_voice_note`          | WhatsApp      | Replies with a spoken voice note.                                               |
| Send WhatsApp buttons     | `hr_builtin_tool__send_whatsapp_buttons`    | WhatsApp      | Sends a message with quick-reply buttons.                                       |
| Send WhatsApp list        | `hr_builtin_tool__send_whatsapp_list`       | WhatsApp      | Sends a message with a selectable list.                                         |
| Send images and documents | `hr_builtin_tool__send_whatsapp_media`      | WhatsApp      | Sends an image or PDF for the contact to view or download.                      |

<AccordionGroup>
  <Accordion title="Terminate">
    Always injected for text agents. The agent calls this tool when it determines there are no more actions to take in the current turn. This is an internal control tool — no message is sent to the user, and it does not appear in the **Built-in** tab.
  </Accordion>

  <Accordion title="End conversation">
    Enabled with the **End conversation** switch in the prompt node's **Built-in** tab. Lets the agent gracefully close the conversation when the interaction is complete.

    The message behavior is configurable:

    | Type      | Behavior                                                                 |
    | --------- | ------------------------------------------------------------------------ |
    | **AI**    | The agent generates a closing message based on the conversation context. |
    | **Fixed** | A pre-written closing message is sent.                                   |
    | **None**  | The conversation ends silently.                                          |

    Provide a description to guide when the agent should end the conversation (e.g., "End the conversation when the customer confirms their issue is resolved and has no further questions.").
  </Accordion>

  <Accordion title="Escalate to human">
    Enabled with the **Escalate to human** switch in the prompt node's **Built-in** tab. Allows the agent to hand off the conversation to a human when it cannot resolve the issue.

    Expanding the row splits the configuration in two: the agent-facing behavior (when to escalate and what to say) and **Handoff setup**, where you choose the destination and configure the connection.

    Escalation modes available:

    | Mode                    | Description                                                                                                                                                                                                                                                                                                                                            |
    | ----------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
    | **HappyRobot Platform** | Uses the built-in escalation system within HappyRobot.                                                                                                                                                                                                                                                                                                 |
    | **CXone**               | Escalates to NICE CXone contact center. Requires a CXone credential and channel ID.                                                                                                                                                                                                                                                                    |
    | **Richpanel**           | Escalates to a Richpanel helpdesk queue. Requires a Richpanel credential.                                                                                                                                                                                                                                                                              |
    | **Generic Webhook**     | Escalates to any HTTP endpoint. Split into **Inbound API** (your handoff system → HappyRobot) and **Outbound events** (HappyRobot → your handoff system). Each of the three outbound events carries its own status badge — *Disabled*, *Setup required*, or *Enabled* — so a hook that is switched on but missing a URL is obvious before you publish. |
    | **Email in Thread**     | Email-specific escalation with three action types (see below).                                                                                                                                                                                                                                                                                         |

    **Email in Thread** action types:

    | Action                   | Behavior                                                                 |
    | ------------------------ | ------------------------------------------------------------------------ |
    | **CC reply with quotes** | CCs a person on a reply that includes the quoted conversation.           |
    | **Forward thread**       | Forwards the entire email thread to the specified recipient.             |
    | **Handoff and end**      | Hands off the conversation to a person and ends the agent's involvement. |

    See [Escalation](../06-Text-Agents/01-Text-Agents-Overview.md#escalation) for the full field reference, including the inbound reply and escalation-control endpoints.

    <Tip>
      Provide clear guidance in the escalation tool's description field about when the agent should escalate — for example, "Escalate if the customer asks to speak with a manager or if you cannot resolve the issue after two attempts."
    </Tip>
  </Accordion>

  <Accordion title="Skip turn">
    Enabled with the **Skip turn** switch at the bottom of the prompt node's **Built-in** tab. Off by default, and only available on channel-backed text agents — the card renders on reasoning agents, but the setting isn't part of their schema and is dropped on save. Use it when an event needs no message and no action — an informational status update, for example.

    When the agent calls it:

    * No message is sent.
    * No configured tool or workflow action runs.
    * The current event is marked as handled.
    * If the agent also produces a message or another action in the same turn, skip turn is ignored and those outputs continue normally.

    Skip turn does not put the agent into a waiting mode. The next eligible message, [signal](../02-Workflows/06-Signals.md), reminder, or tool result follows the agent's normal response settings.

    Skipped turns are rendered in the run history, so it's clear the agent decided to stay quiet rather than failing to respond.
  </Accordion>

  <Accordion title="Read media">
    Available when OCR or transcription is enabled in the **Automatically process media** row of the prompt node's **Built-in** tab. The agent uses it to extract text from an image or document, or to transcribe an audio or voice message the contact sent, so it can act on the contents.

    Each capability is set with a single dropdown — **Disabled**, **Standard**, or **Advanced** — rather than a separate toggle and tier. See [Media processing](../06-Text-Agents/01-Text-Agents-Overview.md#media-processing).
  </Accordion>

  <Accordion title="Email built-in tools">
    Available on the **email** channel when the agent's email provider is Gmail, Outlook, or Postmark. Three tools appear in the **Built-in** tab: **Send email** (start a new thread), **Reply to email** (reply in the current thread), and **Forward email** (forward the current thread to new recipients).

    Each argument on these tools can either be decided by the agent or pinned by you:

    | Argument                         | Tools          | Description                                                           |
    | -------------------------------- | -------------- | --------------------------------------------------------------------- |
    | **To**                           | All three      | Recipients for the email.                                             |
    | **CC** / **BCC**                 | All three      | Optional copied and hidden recipients.                                |
    | **Subject**                      | Send email     | Subject for the new thread.                                           |
    | **Body**                         | All three      | Body of the email, or the introductory text above a forwarded thread. |
    | **Reply to all**                 | Reply to email | Include every original recipient in the reply.                        |
    | **Include conversation history** | Reply to email | Include previous messages in the sent reply.                          |

    Leave an argument on its default to let the agent fill it from the conversation, or switch it to a fixed value — free text with [variables](../02-Workflows/07-Variables.md) for text and recipient fields, or an explicit true/false for the boolean options. Pinning a value guarantees the agent can't choose a different one, which is useful for a fixed CC list or a mandatory subject prefix.

    <Warning>
      A pinned argument left blank blocks publishing. The node reports `Missing custom value for <tool>: <argument>` until you fill it in or hand the argument back to the agent.
    </Warning>
  </Accordion>

  <Accordion title="WhatsApp built-in tools">
    **Send voice note** appears when **Send voice notes** is switched on and its reply mode is set to *Let the agent decide*. **Send WhatsApp buttons** and **Send WhatsApp list** appear when **Interactive messages** is switched on in the **Built-in** tab. **Send images and documents** appears when the **Send images and documents** row is switched on.

    See [WhatsApp](../06-Text-Agents/03-WhatsApp.md#built-in-tools) for channel-specific detail.
  </Accordion>
</AccordionGroup>

## Naming conflicts

<Warning>
  If you create a custom tool with a name like `stay_silent`, `pause`, `hold`, `mute`, or similar, the platform will display a warning that this capability may already be built in. Review the built-in tools above before creating custom alternatives to avoid unexpected behavior.
</Warning>

## Related

<CardGroup cols={3}>
  <Card title="Creating Tools" icon="wrench" href="02-Creating-Tools.md">
    Build custom tools with parameters, messages, and child action nodes.
  </Card>

  <Card title="Outbound Calls" icon="phone-arrow-up-right" href="../05-Voice-Agents/03-Outbound-Calls.md">
    Configure voicemail handling and phone tree navigation for outbound voice agents.
  </Card>

  <Card title="Text Agents" icon="message" href="../06-Text-Agents/01-Text-Agents-Overview.md">
    Set up escalation and end conversation behavior for text agents.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/tools/built-in-tools
