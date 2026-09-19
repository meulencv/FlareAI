---
title: "Discussions"
description: "Leave comments on workflow nodes and collaborate with your team on the canvas"
---

# Discussions

> Leave comments on workflow nodes and collaborate with your team on the canvas

Discussions are comment threads pinned to nodes on the workflow canvas. Use them to ask a question about a node, leave review feedback, flag something to fix, or explain why a node is configured the way it is — all without leaving the editor. Teammates reply in the same thread, get notified when you mention them, and resolve the discussion once it's handled.

Discussions are scoped to a specific workflow **version**, so feedback stays attached to the version it was written against as you iterate and publish.

## Starting a discussion

<Steps>
  <Step title="Pick the node (or nodes)">
    A discussion can be pinned to a single node or span several related nodes:

    * **One node** — right-click the node (or open its menu) and choose **Start discussion**.
    * **Multiple nodes** — select the nodes on the canvas, then click **Start a discussion** in the selection toolbar. A discussion can span up to 100 nodes.
  </Step>

  <Step title="Write your message">
    Type your comment in the composer. To pull a teammate into the thread, type **@** and pick their name — see [Mentions](#mentions). A message can be up to 12,000 characters and mention up to 50 people.
  </Step>

  <Step title="Post it">
    Post the message to create the thread. The nodes it's pinned to show a discussion indicator on the canvas so anyone editing the workflow can see there's a conversation attached.
  </Step>
</Steps>

## Replying and mentions

Anyone with access to the workflow can open a thread and reply. Each thread tracks its **author** and everyone who has participated.

### Mentions

Type **@** in the composer to mention a teammate from your organization. Mentioned users are flagged on the discussion so they can spot threads that need their attention in the [activity panel](#the-activity-panel). A single message can mention up to 50 people.

## Resolving discussions

When a thread is handled, **resolve** it to mark it done and clear it from the list of open discussions. Resolving records who resolved it and when. If the topic comes back up, **reopen** the discussion to continue the conversation in the same thread.

## The activity panel

The activity panel gives you one place to see every discussion in the workflow instead of hunting across the canvas node by node. It shows:

* **Open discussions in the current version**, with a count of how many are **unread**.
* Which threads **mention you**, so you can jump straight to the ones that need a reply.
* A **Mark all as read** action to clear the unread count in one click.

Selecting a discussion focuses the canvas on the node (or nodes) it's pinned to and opens the thread, so you can read the feedback next to the node it's about.

<Note>
  Discussions are tied to the workflow version they were created in. When you're viewing a different version, you'll see that version's discussions — feedback doesn't carry over automatically as you create new versions.
</Note>

## Next steps

<CardGroup cols={3}>
  <Card title="Versions and publishing" icon="code-branch" href="08-Versions-and-Publishing.md">
    Understand how workflow versions work.
  </Card>

  <Card title="Creating a workflow" icon="diagram-project" href="02-Creating-a-Workflow.md">
    Build a workflow from scratch on the canvas.
  </Card>

  <Card title="Node types" icon="shapes" href="04-Node-Types.md">
    Learn the building blocks of a workflow.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/workflows/discussions
