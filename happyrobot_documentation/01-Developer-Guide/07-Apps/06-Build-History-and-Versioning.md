---
title: "Build History and Versioning"
description: "Browse past deployments, inspect logs, and roll back via Git"
---

# Build History and Versioning

> Browse past deployments, inspect logs, and roll back via Git

Every [deploy](05-Deploying.md) creates a new **build** — a snapshot of your app at the commit you pushed. HappyRobot tracks every build for the lifetime of the app so you can audit what shipped, debug failures, and recover from regressions.

## Opening the build history

From the app detail page, open the **Build history** dropdown in the header. The dropdown lists builds in reverse chronological order, with pagination for older entries. Each row shows:

| Field              | Description                                                                                                             |
| ------------------ | ----------------------------------------------------------------------------------------------------------------------- |
| **Build number**   | Sequential build identifier assigned by the deployment provider.                                                        |
| **Status**         | One of `PENDING`, `RUNNING`, `SUCCEED`, `FAILED`, or `CANCELLED`. See [build statuses](05-Deploying.md#build-statuses). |
| **Commit**         | The 7-character commit SHA that was deployed.                                                                           |
| **Commit message** | The message you entered when you deployed (or `Deploy from sandbox` if blank).                                          |
| **Start time**     | When the build began.                                                                                                   |
| **End time**       | When the build finished, or empty while still running.                                                                  |

Click any build to open its logs.

## Build logs

Build logs capture the full output from your deployment provider — dependency install, framework build, and any errors or warnings. Each log line includes:

| Field       | Description                                                            |
| ----------- | ---------------------------------------------------------------------- |
| `timestamp` | When the line was emitted.                                             |
| `level`     | `info`, `warning`, or `error`.                                         |
| `step`      | The build phase that produced the line (install, build, deploy, etc.). |
| `text`      | The log message itself.                                                |

Use the logs to diagnose failures — or paste the relevant section to the AI agent in the [sandbox editor](03-Sandbox-Editor.md) and ask it to fix the underlying issue.

<Note>
  Live streaming and full historical logs are available for apps deployed to Vercel — the default for new apps. Legacy Vite Static apps on Amplify show build status and metadata, but log streaming may be limited.
</Note>

## Versioning model

Each successful build is effectively an immutable version of your app:

* The exact code that shipped is preserved as a Git commit in the managed GitHub repository.
* The deployment provider keeps the built artifact, so older versions remain queryable via the provider.
* The public URL always points to the most recent successful deployment.

There is no separate "version number" you assign — the commit SHA is the version. To see what's currently live, look at the commit on the most recent `SUCCEED` build.

## Rolling back

Apps don't have a one-click rollback button in the platform. To revert to a previous version:

<Steps>
  <Step title="Identify the good commit">
    Open the build history and find the last `SUCCEED` build you want to return to. Note its commit SHA.
  </Step>

  <Step title="Revert on GitHub">
    Open the managed GitHub repository and revert the offending commits — either by reverting individual commits or by resetting the `main` branch back to the good commit.
  </Step>

  <Step title="Push the revert">
    The push triggers a new build automatically. Once it succeeds, the rolled-back version is live at the public URL.
  </Step>
</Steps>

You can also revert from the sandbox editor: open the app, ask the AI agent to revert to a specific commit, and deploy.

<Tip>
  For most rollbacks, the AI agent is the fastest path: tell it which build introduced the regression (paste the commit SHA or build number) and ask it to revert that change. It will edit the relevant files, deploy, and the next successful build is your rollback.
</Tip>

## Audit trail

Because every deployment is a Git commit on a managed repository, you always have a full audit trail:

* **Who deployed** — Recorded via the commit author on each push.
* **What changed** — The diff between commits.
* **When** — Commit timestamps and build start/end times.
* **Why** — The commit message entered at deploy time.

This information is available both in the build history and directly on GitHub.

## Next steps

<CardGroup cols={3}>
  <Card title="Deploying" icon="rocket" href="05-Deploying.md">
    Push a new build live.
  </Card>

  <Card title="Sandbox editor" icon="code" href="03-Sandbox-Editor.md">
    Open the editor to fix or revert changes.
  </Card>

  <Card title="Environment variables" icon="lock" href="07-Environment-Variables.md">
    Configure runtime config without redeploying manually.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/apps/build-history
