---
title: "Northstars"
description: "Define behavioral quality criteria for your agents"
---

# Northstars

> Define behavioral quality criteria for your agents

Northstars are the quality standards that define how your agent should behave. Each northstar describes a specific behavioral expectation — like "the agent must confirm the appointment date before ending the call" or "the agent should not mention competitor products." When [automated audits](03-Automated-audits.md) run, an LLM judge grades each run against your northstars.

## Prompt-level and agent-level northstars

The **Behavioral Northstars** table is a tree. Each agent is a top-level group and its prompts nest underneath, so a northstar can be owned by a single prompt node or by the agent:

| Scope      | What it grades                                                  | When to use                                                                                       |
| ---------- | --------------------------------------------------------------- | ------------------------------------------------------------------------------------------------- |
| **Prompt** | Only the part of the conversation that prompt node produced     | Behavior specific to one step — what the agent must confirm while collecting an appointment time  |
| **Agent**  | The agent's whole conversation, across every one of its prompts | Behavior that must hold everywhere — never quoting a rate, always identifying the company by name |

Agent-level northstars are listed under the agent's header, above its prompt groups. They have no coverage state of their own, since coverage is assessed per prompt.

### Where prompt component northstars appear

[Prompt components](../14-Assets/02-Components.md) used by your prompts appear as folders in the tree, placed at their narrowest scope:

* A component used by **one prompt** of an agent is listed under that prompt
* A component shared by **several prompts** of the same agent is listed once under the agent

The component owns those northstars, so editing them changes the component everywhere it's used. See [Northstars on prompt components](#northstars-on-prompt-components).

### Northstars from called workflows

When your workflow invokes another one with a [Call Workflow](../03-Core-Nodes/12-Call-Workflow.md) node, the callee's northstars — both its prompt-level and its agent-level ones — are listed in their own section, with one entry per called workflow rather than one per call site, so a workflow invoked from several places appears a single time. You can enable or disable those northstars for your call path, but you can't add or delete them here; edit them in the workflow that owns them.

### Northstars for a single version

A workflow version can add a northstar to an embedded [prompt component](../14-Assets/02-Components.md) or to a prompt in a workflow it calls, without changing what the component or the callee owns. Use the **Add custom northstar** action on the component's or called workflow's section in the northstars table.

These northstars are graded only for the version that created them. They're the right choice when a rule matters for one workflow's use of shared content — for example, a component reused across regions where only one region has an extra confirmation requirement.

## Categories

Every northstar belongs to a category that determines how the LLM judge evaluates it:

| Category       | What it checks                                                                                                                                                    |
| -------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Notes**      | Whether the agent follows general behavioral guidelines — tone, formatting, information handling                                                                  |
| **Style**      | Whether the agent's communication style matches expectations — formality, word choice, conversation flow                                                          |
| **Tool**       | Whether the agent calls the correct tools with the correct arguments at the right time                                                                            |
| **Sequential** | Whether the agent completes conversation stages in the right order — useful for multi-step workflows where certain information must be gathered before proceeding |

<Note>
  The **sequential** category requires additional configuration. You specify a **current stage** (what should happen) and a **prerequisite stage** (what must happen first). For example: current stage "confirm appointment" requires prerequisite stage "collect preferred time."
</Note>

## Priority levels

Assign a priority to each northstar to indicate how critical the behavior is:

| Priority   | When to use                                                    |
| ---------- | -------------------------------------------------------------- |
| **High**   | Core requirements — violations indicate a serious problem      |
| **Medium** | Important behaviors that should generally be followed          |
| **Low**    | Nice-to-have behaviors — helpful for tracking but not critical |

Priority levels help you focus review effort on the most impactful audit failures.

## Creating a northstar

<Steps>
  <Step title="Open the evaluate tab">
    In the workflow editor, navigate to the **Evaluate** tab and select the **Behavioral Northstars** subtab.
  </Step>

  <Step title="Choose what the northstar applies to">
    Pick a prompt node to grade one step of the conversation, or an agent to grade its whole conversation across every prompt. See [Prompt-level and agent-level northstars](#prompt-level-and-agent-level-northstars).
  </Step>

  <Step title="Add the northstar">
    On a prompt row, open the **+** menu and choose **Northstar**. On an agent row, click the **+** button.
  </Step>

  <Step title="Fill in the details">
    * **Name** — A short, descriptive name (e.g., "Confirms appointment before ending call")
    * **Description** — A detailed explanation of the expected behavior. Be specific — the LLM judge uses this description to evaluate runs.
    * **Category** — Select the appropriate category (notes, style, tool, or sequential)
    * **Priority** — Set the priority level
  </Step>

  <Step title="Add examples (recommended)">
    Add **positive examples** (conversations that pass this northstar) and **negative examples** (conversations that fail it). Examples improve grading accuracy by giving the LLM judge concrete references.
  </Step>

  <Step title="Save">
    Click **Create** to save the northstar. It immediately begins evaluating new runs.
  </Step>
</Steps>

## Editing northstars

Click on any northstar card in the sidebar to view its details. Use the edit button to modify the name, description, category, priority, or examples. Changes apply to future audit evaluations — existing audit results are not re-evaluated.

You can also:

* **Enable/disable** individual northstars with the toggle switch
* **Enable/disable all** northstars at once using the header buttons
* **Delete** a northstar from the hover action menu

## Copying northstars from another version

If you have northstars defined in one workflow version and want to reuse them in another, you can copy them without manually recreating each one.

<Steps>
  <Step title="Open the northstars table row menu">
    In the **Behavioral Northstars** subtab, hover over any northstar row and open its action menu (the `...` icon at the end of the row).
  </Step>

  <Step title="Click Copy from version">
    Select **Copy from version** from the menu. A dialog opens listing all other versions of this workflow.
  </Step>

  <Step title="Select the source version">
    Choose the version whose northstars you want to copy.
  </Step>

  <Step title="Click Copy & Replace">
    Click **Copy & Replace**. All northstars for the selected prompt node in the current version are replaced with the northstars from the source version.
  </Step>
</Steps>

<Warning>
  "Copy & Replace" overwrites the northstars for that prompt node in the current version. Existing northstars for that prompt are deleted and replaced with the copied ones.
</Warning>

## Positive and negative examples

Examples significantly improve grading accuracy. They teach the LLM judge what passing and failing behavior looks like in practice.

* **Positive examples** — Conversation excerpts where the agent correctly follows the northstar. Include the relevant context so the judge can understand why it passes.
* **Negative examples** — Conversation excerpts where the agent violates the northstar. Include what the agent did wrong and optionally what it should have done instead.

Examples can come from two sources:

* **Manual** — You write them directly when creating or editing the northstar
* **Audit feedback** — When you confirm an audit remark as accurate, the conversation excerpt is added as an example — positive if the remark passed, negative if it failed. Marking the remark inaccurate removes it again. See [audit feedback](03-Automated-audits.md#audit-feedback).

## Auto-generation and coverage

HappyRobot can automatically generate northstars from your prompt content. The system analyzes your prompt instructions and creates northstars that cover the key behavioral expectations.

Generation runs at the **agent** level, covering the agent's own northstars and those of all of its prompts in one pass. Open the **⋯** menu on an agent row and pick a mode:

| Mode                 | What it does                                                                                                                                                            |
| -------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Force regenerate** | Replaces the prompt- and agent-level northstars for that agent. Existing prompt folders are deleted, so anything you customized under them is lost.                     |
| **Re-iterate**       | Re-evaluates the existing prompt- and agent-level northstars against the current prompts. Northstars may be updated or removed, but the set isn't rebuilt from scratch. |

Both modes ask for confirmation first. Generation happens in the background, so you can navigate away and come back:

* A **Generating** badge on the agent row means a run is in flight. Actions on that agent are disabled until it finishes, and the table refreshes on its own and fills in the new northstars when the run completes.
* An **Error** badge means the run failed. Start it again from the same menu.
* The status comes from the server, so a run started by a teammate — or before you reloaded the page — still shows as running.

If a version has no northstars yet, the empty state's **Auto Generate** button runs a force regeneration for every agent in the workflow.

### Coverage

Coverage is the share of a group's northstars that a coverage assessment has traced back to specific lines of your prompt content. A northstar that no assessment has cited is badged **Unfulfilled** — a rule the group is expected to satisfy that its current content doesn't, usually because the prompt no longer says what the northstar expects, or the northstar was written against content that has since moved.

* **Coverage badge** — Shown in the group header as a percentage. Under 50% is red, 50–80% orange, above 80% green.
* **Assess Coverage** — Run an assessment from the group's action menu to recompute coverage and identify gaps. Like generation, it runs in the background and the list refreshes itself when it completes.
* No badge appears for an empty group — nothing was assessed, which is not the same as 0% coverage.

<Tip>
  Start with auto-generated northstars to get broad coverage, then manually refine the ones that matter most. Prefer **Re-iterate** over **Force regenerate** once you've customized northstars by hand — force regenerating discards them. Add specific examples from real conversations to improve grading accuracy over time.
</Tip>

## Northstars on prompt components

A prompt component carries its own northstars so every workflow that embeds it inherits the same quality bar. Because the component owns the rubric, every workflow referencing it is graded against the same rules instead of each one rewriting them.

Go to **Assets > Components**, open the prompt component, and select its **Northstars** tab. The page supports the same actions as the workflow table — create, edit, enable/disable, and delete — plus:

| Action              | What it does                                                                                                                                        |
| ------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Generate**        | Creates northstars from the component's own content. Skipped if the component already has some.                                                     |
| **Regenerate**      | Replaces the component's northstars with a freshly generated set. Every workflow using the component is affected.                                   |
| **Assess Coverage** | Recomputes the component's coverage percentage, shown as a badge in the page header against the same red/orange/green thresholds used in workflows. |

Generation and coverage assessment both run in the background: the list refreshes itself as they progress, and a run started elsewhere still shows as running when you open the page. Rows no assessment has cited are badged **Unfulfilled**.

## Prompt change detection

When you modify a prompt node, the system detects the change and can automatically flag it as an [issue](05-Issues.md). This ensures that northstars stay aligned with the current prompt — if a prompt changes significantly, you may need to update or regenerate the associated northstars.

## Next steps

<CardGroup cols={2}>
  <Card title="Automated audits" icon="magnifying-glass" href="03-Automated-audits.md">
    See how northstars are used to evaluate runs.
  </Card>

  <Card title="Custom tests" icon="flask" href="06-Custom-tests.md">
    Create test cases that validate specific northstars.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/evaluate/northstars
