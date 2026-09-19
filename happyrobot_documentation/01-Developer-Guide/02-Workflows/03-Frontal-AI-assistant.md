---
title: "Frontal AI assistant"
description: "Use the AI assistant to build and edit workflows through conversation"
---

# Frontal AI assistant

> Use the AI assistant to build and edit workflows through conversation

Frontal is an AI assistant built into the workflow editor. You can ask it to make changes to your workflow, get answers about how it's configured, and have it apply edits — all without leaving the editor.

<Note>
  Frontal is available to all organizations.
</Note>

## Opening Frontal

Frontal is accessible from within any workflow in the editor. Look for the **Frontal** panel button in the workflow editor toolbar. The panel opens as a resizable side panel alongside the workflow canvas.

## Chats

Frontal keeps every conversation you start, and the panel header holds a **tab strip** so you can work across several of them at once. Each tab is its own chat with its own history, mode, and settings, so you can leave a long task running in one tab and start something unrelated in another.

| Action                  | How                                                                                                                           |
| ----------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| **Open a new chat**     | Click **+** at the end of the tab strip.                                                                                      |
| **Switch chats**        | Click a tab. The strip scrolls to the active tab automatically.                                                               |
| **Reorder tabs**        | Drag a tab along the strip.                                                                                                   |
| **Rename a chat**       | Right-click the tab and choose **Rename**. Press Enter to save, Escape to cancel.                                             |
| **Mark read or unread** | Right-click the tab and choose **Mark as read** or **Mark as unread**.                                                        |
| **Close a tab**         | Click the **×** on the tab, or right-click and choose **Close tab**. The chat itself is kept — reopen it from the chats menu. |
| **Delete a chat**       | Right-click the tab and choose **Delete chat**, or use the **⋯** menu on its row in the chats menu.                           |

The **Chats** button in the header opens the full list of your chats, grouped by date. Chats you closed still live here, so the tab strip stays limited to what you're actively working on.

Tabs stay live even when they aren't in focus, and show what's happening in chats you aren't looking at:

* A **spinner** means that chat is still streaming a response. It finishes whether or not you're looking at it.
* A **blue dot** means a new assistant message arrived since you last read that chat.

### Chat titles

A new chat is named automatically from your first message — a short label like *Bouncing carrier emails* rather than *Untitled chat*. The title streams in alongside Frontal's reply. If the opening message is too vague to label, the chat stays untitled until you rename it yourself.

## Plan mode and Build mode

Frontal has two modes that control how changes are applied:

| Mode      | Behavior                                                                                                                                                                                                                         |
| --------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Plan**  | Frontal analyzes your workflow and proposes a plan before applying any changes. You review the plan and approve or reject it. Use this for significant changes where you want to see the full scope before anything is modified. |
| **Build** | Frontal applies edits directly as it works, one operation at a time. You can review each edit in the editor. Use this for smaller, incremental changes.                                                                          |

Switch between modes using the mode selector in the Frontal panel header.

### Plan cards

In Plan mode, Frontal surfaces a **plan card** when a change requires more than a single operation. The plan card shows:

* A summary of what Frontal intends to do
* The list of operations it will apply
* An **Accept plan** button to apply the plan, or a **Reject** button to discard it

Accepting a plan switches the chat to **Build** mode and Frontal starts applying it. You can ask Frontal to revise the plan before accepting it.

### Clarifying questions

When an answer would materially change the plan, Frontal asks in Plan mode with an interactive **Questions** card above the chat input instead of a paragraph of prose. Each question offers two to four options with a short note on what each one implies, and — unless the options are exhaustive — an **Other…** field for your own answer.

* Work through the questions with **Next** and **Previous**; the card shows your progress and **Submit** sends every answer back at once.
* **Cancel** dismisses the card. Typing a normal message also dismisses it, so you can answer in your own words instead.
* Frontal asks at most three questions at a time and waits for your answer before continuing.

This only happens in Plan mode. In Build mode, Frontal makes reasonable assumptions and applies edits you can review and undo.

## What you can do with Frontal

### Make workflow edits

Frontal can make direct edits to your workflow from a conversation message. Examples of things you can ask:

* "Rewrite the prompt in the first AI Generate node to be more concise"
* "Swap the model in the voice agent to gpt-4.1-mini"
* "Add a Slack notification node after the final AI node"
* "Remove the redundant classification node and connect its upstream to its downstream directly"
* "Merge these two branches into one"
* "Make the final node a response node so the calling workflow gets its output"

Each edit is applied as a reviewable operation in the editor. You can undo an individual operation or revert all Frontal edits if you change your mind.

### Manage prompt components

Frontal can work with your organization's reusable [prompt components](../14-Assets/02-Components.md) without you leaving the editor. In **Build** mode it can:

* **List and inspect** components — "What prompt components do we have?" lists every component with its inputs, and Frontal can pull up a single component's markdown, inputs, and version state before changing it.
* **Create** a component — "Create a prompt component called `carrier_greeting` from this intro." The first version is live immediately.
* **Update** a component — "Update the `check_call_intro` component to also ask for the reference number." Frontal can change a component's name, description, markdown, or inputs.
* **Reference** a component from a prompt, or remove a reference.

<Note>
  Updating a component through Frontal saves a **draft** version. Workflows keep using the live version until you publish, and Frontal can't publish or delete components — it points you at **Assets > Components** to do that yourself. See [Versions and publishing](../14-Assets/02-Components.md#versions-and-publishing).
</Note>

### Work with tests and suites

Frontal can manage the workflow's [prompt tests](../11-Quality-and-Evaluation/06-Custom-tests.md), [adversarial tests](../11-Quality-and-Evaluation/07-Adversarial-tests.md), and [test suites](../11-Quality-and-Evaluation/08-Test-suites.md) from the conversation:

* **List and inspect** — "What tests does this workflow have?", "Show me the tests in the release suite."
* **Create and edit** — "Create an adversarial test where the caller keeps changing the pickup time", "Generate a suite of five tests covering booking failures."
* **Group and run** — "Put the two booking tests in a suite and run it against version 12."

In **Plan** mode Frontal can only read tests and suites; editing them requires **Build** mode.

### Investigate northstar audit results

Frontal can read the [automated audit](../11-Quality-and-Evaluation/03-Automated-audits.md) remarks behind a workflow's quality numbers, so you can ask why a northstar is failing instead of paging through the Audits tab:

* "Why is the *confirms the reference number* northstar failing?"
* "Show me the open failed remarks for this workflow from the last few days"
* "Walk me through this remark and what the agent should have said"

It can list a workflow's remarks filtered by northstar, grade (passed, failed, not applicable), or status (open, resolved, dismissed), and open a single remark in detail. When the analysis needs more than the remark itself, Frontal pulls the run's transcript, tool calls, the exact workflow version, and the prompt that produced the behavior.

Access is read-only — Frontal reports what the auditor found and separates that evidence from its own interpretation. It says so when the evidence is incomplete rather than filling the gap.

### Plan a tag architecture

Frontal can design your workspace's [Scope Tag](../16-Account-and-Settings/04-Scope-Tags.md) vocabulary. Ask it to organize your tags — or click **Tag with Frontal** on **Settings > Tags** — and in Plan mode it inspects the tags and resource assignments you already have, then publishes a **Tag architecture draft**: an interactive tree of the tag types and tags it proposes, with a summary of the reasoning.

The draft is read-only. Click **Accept plan** to switch to Build mode and have Frontal create the tag types and tags, then ask it to propose resource assignments in batches. See [Plan a tag structure with Frontal](../16-Account-and-Settings/04-Scope-Tags.md#plan-a-tag-structure-with-frontal).

### Ask questions about your workflow

Frontal reads your workflow structure and can answer questions about it without making changes:

* "What does the first branch do?"
* "Which nodes are connected to the webhook trigger?"
* "Why might the extraction node return empty results?"
* "What tools are configured on this voice agent?"

Frontal can inspect specific node configurations and cross-reference them to give accurate, context-aware answers.

### Get recommendations

Ask Frontal where to go next or how to improve a workflow:

* "How should I handle the case where the extracted email is missing?"
* "What's the best way to retry this API call if it fails?"
* "Is there a more efficient way to structure this branching logic?"

## Attaching files

You can attach files to a Frontal message to give it visual or document context — for example, a screenshot of an error, a sample payload, or a PDF spec you want a node configured against.

Drag files onto the chat input, or use the attach control in the input, to add them to your next message. Attached files appear as badges above the input; remove one by clicking the **×** on its badge.

| Limit                 | Value                                                               |
| --------------------- | ------------------------------------------------------------------- |
| **Files per message** | Up to 5                                                             |
| **Supported types**   | Images (JPEG, PNG, GIF, WebP), PDF, and text files (including JSON) |
| **Size per file**     | 3.5 MB (500 KB for text files)                                      |

<Note>
  PDF attachments are not supported on every model — Grok models reject them, and attaching a PDF while a Grok model is selected returns an error. Switch to a different model with **Chat Model** in the [slash menu](#the-slash-menu) before attaching a PDF. The selector includes the latest models, and new chats default to **Claude Opus 5**.
</Note>

## Attaching context

Beyond files, you can attach workspace context to a message so Frontal can reference it. Type `@` in the input, or open the **+** menu in the chat input, to attach:

| Artifact           | What Frontal can do                                                                               |
| ------------------ | ------------------------------------------------------------------------------------------------- |
| **Knowledge Base** | Search an attached knowledge base for relevant passages when you ask questions about its content. |
| **Twin**           | Reference your [Twin](../08-Twin/01-Twin-Overview.md) database — an entire database or a specific table.          |
| **Editor Nodes**   | Point Frontal at specific nodes in the current workflow so it acts on exactly the nodes you mean. |

Navigate the menu with the arrow keys — Up/Down to move through options, Left/Right to move between submenus, and Escape to close it.

## The slash menu

Type `/` at the start of an empty chat input — or click the slash icon in the input's action row — to open the slash menu, a single searchable list of the chat's settings and actions. Keep typing to filter it, use the arrow keys to move through the results, and press Enter to run the highlighted item.

| Section                | Items                                                                                                                                                                                                                                              |
| ---------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Context Management** | **Lookback Turns** — how many previous turns of the conversation Frontal carries into each message. Lower it on long chats to keep the context focused.                                                                                            |
| **Subagents**          | **Enable subagents** toggles whether Frontal can delegate exploration to helper agents. **Subagent Model** picks the model they run on, or **Inherit from chat** to match the main chat.                                                           |
| **Chat**               | **Chat Model** picks the model for this conversation. **Popout to Composer View** moves the chat out of the side panel into the full composer. **Download chat as JSON** exports the transcript. **Clear chat** removes every message in the chat. |
| **Skills**             | Toggle any [skill](#skills) on or off for this chat, or open **Manage skills**.                                                                                                                                                                    |

Settings picked here apply to the chat you're in, so different tabs can run on different models with different skills attached.

<Note>
  The chat model selector is available to everyone. Which models appear is fixed by HappyRobot and includes the latest Claude, GPT, and Grok models. Models are grouped by provider, and a provider is marked with a **BYOK** badge when your workspace has an active credential for it — chats on those models run on your own account. See [Bring your own keys](../16-Account-and-Settings/07-Bring-your-own-keys.md).
</Note>

## Skills

Skills are reusable instructions you write once and apply to Frontal on demand. A skill is a piece of Markdown content with a name and description — when you attach it to a chat, its content is added to Frontal's context for the rest of that conversation. Frontal can also [pull in a skill on its own](#automatic-skill-discovery) when your request matches its description. Use skills to capture conventions Frontal should follow when working in your workflows — naming patterns, prompt style, formatting preferences, or any other guidance that would otherwise be repeated in every message.

Use skills for things like:

* House style for prompts ("always start with a one-line role description, then…")
* Naming conventions for variables and nodes
* A shared glossary of business terms or carrier names
* Reusable instructions for how to wire up a specific node type

### Selecting skills for a chat

Open the [slash menu](#the-slash-menu) and look under **Skills** to see every skill available to you. Toggle one on to attach it to the current chat; toggle it off to remove it. Selected skills appear as chips in the input's action row — click the **×** on a chip to detach it. There is no hard cap on chips, but Frontal stacks them when several are attached. Selecting **Manage skills** opens the full management sheet.

### Managing your skills

From the same slash menu, choose **Manage skills** to open the skills sheet. From here you can:

* **Create a skill** — provide a name, an optional one-line description, and the body of the skill as Markdown. The body can be as long as needed; treat it like a focused mini-system-prompt for one topic (e.g., "When editing voice agent prompts, always preserve the existing tone of voice.").
* **Edit a skill** — change the name, description, or content. Updates take effect on your next message.
* **Delete a skill** — permanently removes the skill.
* **Search** — filter the list by name or description.

Skills you create are personal by default — only you see them and only your chats use them.

### Global skills

**Global** skills are authored by HappyRobot and made available to every user in every organization. They automatically apply to every Frontal chat — users don't need to attach them and can't remove them. Global skills are visible in the management sheet with a **Global** badge.

You can request HappyRobot consider promoting one of your personal skills by choosing **Request global availability** from the skill's menu. The request goes to the HappyRobot team for review; the skill stays personal in the meantime and shows a **Requested** clock badge.

### Automatic skill discovery

You don't have to attach a skill for Frontal to use it. Every chat receives a catalog of the skills available to you — just their names, descriptions, and IDs — and when your request clearly matches one of those descriptions, Frontal loads that skill's content itself before doing the work.

* Only the **description** is used to decide relevance, so write descriptions that say *when* the skill applies ("Use when editing voice agent prompts"), not just what it contains.
* Frontal loads at most **3 discovered skills per message**, and skips ones whose content is too large to load.
* Skills you attached manually are already active and are never loaded twice.
* The catalog covers up to 100 skills, most recently updated first.
* Discovered skill content is never quoted back to you — Frontal describes the resulting guidance instead.

Attach a skill explicitly when it must apply to every message in the chat regardless of what you ask.

### How Frontal uses skills

Each attached skill is appended to Frontal's system prompt as a labeled section before your message is processed; a discovered skill is added the same way at the point Frontal loads it. Global skills are treated as trusted guidance from HappyRobot; personal skills are treated as your stated preferences. Skills can shape Frontal's tone, formatting, or working style — they cannot grant new tools, change Frontal's safety guardrails, or override a global skill they conflict with.

<Note>
  Skill content is treated as trusted guidance, not as new instructions about how Frontal itself should behave. Phrases that look like prompt-injection attempts ("ignore previous instructions", "reveal system prompt", and similar) are rejected when you save a skill.
</Note>

<Tip>
  Keep individual skills focused on a single topic. Smaller, well-named skills are easier to pick from the menu and combine flexibly than one large skill that mixes unrelated guidance.
</Tip>

## Works in the background

You can close the Frontal panel — or navigate away from the tab — while a long-running task is in flight. When you return, the conversation resumes where it left off. The workflow editor reflects any changes Frontal made while you were away.

## Tips

* Start with **Plan mode** for large structural changes and **Build mode** for targeted edits.
* Be specific about which node you want to change: "the second AI Extract node" is clearer than "the extract node".
* Ask Frontal to explain changes it made if the intent isn't clear from the diff.
* Use the workflow's variable inspector alongside Frontal — you can reference variable names directly in your messages.

---

Fuente original: https://docs.happyrobot.ai/workflows/frontal
