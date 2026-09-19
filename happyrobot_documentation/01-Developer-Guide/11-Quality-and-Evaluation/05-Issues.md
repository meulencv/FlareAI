---
title: "Issues"
description: "Track and resolve quality problems surfaced by audits and flags"
---

# Issues

> Track and resolve quality problems surfaced by audits and flags

Issues are quality problems that need attention. They can be auto-generated from failed audits, quality flags, and prompt change detection — or created manually when you spot a problem during review.

## How issues are created

Issues come from several sources:

| Source                      | Description                                                                                                                                                                                      |
| --------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Audit failures**          | When a run fails a northstar audit, the system can create an issue linking the failed remark to the relevant northstar and run                                                                   |
| **Quality flags**           | Automated metric-based checks (latency, interruption rate, audio quality) that fire when a run exceeds defined thresholds. See [quality flags](03-Automated-audits.md#quality-flags) for details.      |
| **Prompt change detection** | When a prompt node is modified, the system uses merkle hashing to detect significant changes and flags them as issues so you can review whether northstars need updating                         |
| **Manual creation**         | You can create issues directly from the audits page, or from any message in a run's transcript. See [giving feedback on a message](../09-Runs-and-Monitoring/03-Transcripts-and-Messages.md#giving-feedback-on-a-message). |

## Northstar-linked issues

An issue created from an assistant message can be attached to the [northstars](02-Northstars.md) the response violated, rather than left as a generic message issue. Open the message's feedback panel in the run transcript and choose **Violates an existing Northstar**.

The picker lists only the northstars that apply to that message — those owned by the prompt node that produced it, by any [prompt component](../14-Assets/02-Components.md) it embeds, by the agent, and by any workflow that called into it. Northstars disabled for the version aren't offered.

Select every northstar the response broke and one issue is created per northstar, each carrying the same priority, correction, and reason. In the **Flags** table, the northstar's name appears as a badge next to the issue's type, so you can see at a glance which rule a failure is about.

<Tip>
  Linking an issue to a northstar is what connects manual review back to your quality standards — a northstar that keeps collecting issues is either poorly defined or genuinely not being followed, and either way it's the next thing to fix.
</Tip>

## Issue types

Each issue is categorized by type:

| Type                     | What it tracks                                                        |
| ------------------------ | --------------------------------------------------------------------- |
| **Transcriber**          | Speech-to-text accuracy problems                                      |
| **Message**              | Incorrect or inappropriate agent messages                             |
| **Tool call**            | Wrong tool invocations or incorrect arguments                         |
| **End of sentence**      | Sentence boundary detection issues                                    |
| **Run**                  | General run-level quality problems                                    |
| **Interruption**         | Agent interrupted the user or was interrupted excessively             |
| **Audio quality**        | Poor audio metrics (DNSMOS, loudness)                                 |
| **Speaker leakage**      | Audio from the agent leaking into the user's transcription            |
| **Number accuracy**      | Numbers transcribed or spoken incorrectly                             |
| **Session behavior**     | Overall session-level behavioral issues                               |
| **Conversation quality** | General conversation flow and naturalness problems                    |
| **Latencies**            | Response latency is too high, or interruption/cut rates are excessive |

## Issue priorities

Issues are assigned a priority level:

| Priority   | When used                                                           |
| ---------- | ------------------------------------------------------------------- |
| **High**   | Urgent problems affecting core functionality or customer experience |
| **Medium** | Notable issues that should be addressed but aren't blocking         |
| **Low**    | Minor quality improvements to address when capacity allows          |

## Status workflow

Every issue follows a lifecycle:

```
Open → Approved → Closed
Open → Rejected → Closed
```

* **Open** — Newly created, awaiting review
* **Approved** — Confirmed as a real issue, needs resolution
* **Rejected** — Reviewed and determined to be a false positive or not actionable
* **Closed** — Resolved

## Viewing and managing issues

Issues appear in the **Flags** subtab of the Audits page. The table shows:

* Issue type and description, plus the linked northstar when the issue has one
* Priority and status
* Source (manual, audit, flag name)
* Associated run and session
* Who created it and when

Click an issue to open the detail panel with full context, including links to the source run, relevant northstar, and session data.

## Prompt change detection

The system uses merkle hashing to track changes in your prompt nodes. When you edit a prompt, the system:

1. Computes a hash of the current prompt content and tool configurations
2. Compares it against the last known hash
3. If the difference exceeds a threshold, creates an issue flagging the change
4. The issue includes a diff summary showing what percentage of the prompt changed and which sections were modified

This helps you keep northstars and tests aligned with your current prompt — significant prompt changes may require updating your quality standards.

## Next steps

<CardGroup cols={2}>
  <Card title="Automated audits" icon="magnifying-glass" href="03-Automated-audits.md">
    Understand how audits generate issues.
  </Card>

  <Card title="Northstars" icon="star" href="02-Northstars.md">
    Update northstars to address recurring issues.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/evaluate/issues
