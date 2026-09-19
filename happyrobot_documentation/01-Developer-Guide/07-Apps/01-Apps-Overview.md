---
title: "Apps Overview"
description: "Build, edit, and deploy custom web applications inside HappyRobot"
---

# Apps Overview

> Build, edit, and deploy custom web applications inside HappyRobot

Apps are custom web applications you build and ship from inside HappyRobot. Each app is backed by a managed GitHub repository, edited in a browser-based sandbox alongside an AI coding agent, and deployed to a live URL with one click. Apps are scoped to your organization, share environment variables with the rest of the platform, and can be used as front-ends for the [workflows](../02-Workflows/01-Workflows-Overview.md) and agents you already run on HappyRobot.

## What you can build

<CardGroup cols={2}>
  <Card title="Internal tools" icon="screwdriver-wrench">
    Spin up dashboards, admin consoles, and internal forms that read and write to your HappyRobot data without standing up a separate frontend project.
  </Card>

  <Card title="Customer-facing portals" icon="users">
    Ship branded portals where customers can submit requests, track interactions, or trigger your workflows on demand.
  </Card>

  <Card title="Workflow front-ends" icon="diagram-project">
    Wrap a workflow in a UI: collect input from a form, fire the workflow, and display results — all without leaving the platform.
  </Card>

  <Card title="Agent companions" icon="robot">
    Build companion interfaces for your voice and text agents — live transcripts, knowledge lookup, escalation surfaces, and more.
  </Card>
</CardGroup>

## How an app works

<Steps>
  <Step title="Create from a template or import">
    Start from the **Next.js Full-Stack** template, or import an existing GitHub repository. HappyRobot provisions a managed repo, a deployment project on Vercel, and a unique public URL.
  </Step>

  <Step title="Edit in the sandbox">
    Open the app to launch a sandboxed editor with a live preview and an AI agent sidebar. Edit files directly, or describe what you want and let the agent make the changes for you.
  </Step>

  <Step title="Deploy with one click">
    Press **Deploy** to commit your changes, push them to GitHub, and trigger a build. Build progress streams back into the platform.
  </Step>

  <Step title="Iterate from build logs">
    Every build is recorded with status, commit, and full logs. If a build fails, open it in the editor and the agent can read the logs and fix the problem.
  </Step>
</Steps>

## Core concepts

| Concept                  | Description                                                                                                                                           |
| ------------------------ | ----------------------------------------------------------------------------------------------------------------------------------------------------- |
| **App**                  | A custom web application scoped to your organization. Each app has a name, a unique slug, a managed GitHub repo, and a public URL.                    |
| **Template**             | A starter project that defines the runtime and framework. New apps use the [Next.js Full-Stack template](02-Creating-an-App.md#templates) by default. |
| **Sandbox**              | The browser-based editing environment — code editor, live preview, and AI agent — that runs while you're working on an app.                           |
| **Agent**                | The AI coding assistant embedded in the sandbox. It can read your code, run commands, and edit files in response to your prompts.                     |
| **Build**                | One deployment attempt. Each build has a status, commit, and logs, and is listed in the [build history](06-Build-History-and-Versioning.md).                         |
| **Environment variable** | A server-only secret or config value, encrypted at rest and injected at build time. See [environment variables](07-Environment-Variables.md).         |
| **Public URL**           | The live URL where your deployed app is reachable.                                                                                                    |

## Key features

<CardGroup cols={2}>
  <Card title="Managed Git repository" icon="github">
    HappyRobot creates and manages a GitHub repository for every app. Your changes are committed and pushed automatically when you deploy.
  </Card>

  <Card title="Live preview and hot reload" icon="bolt">
    The sandbox runs a dev server with hot reload. Edits to your code show up in the preview pane almost immediately.
  </Card>

  <Card title="Embedded AI coding agent" icon="wand-magic-sparkles">
    Describe what you want in plain English. The agent reads your codebase, edits files, runs commands, and can recover from build failures by reading the logs.
  </Card>

  <Card title="Encrypted environment variables" icon="lock">
    Add secrets and config values through the platform. Values are encrypted, write-only, and synced to your deployment provider on every change.
  </Card>

  <Card title="Build history and logs" icon="clock-rotate-left">
    Every deployment is recorded. Browse past builds, inspect logs, and check which commit went live.
  </Card>

  <Card title="Org-scoped access control" icon="shield-halved">
    Apps inherit your organization's RBAC. Grant access to individual apps or to all apps with workspace-level permissions.
  </Card>
</CardGroup>

## Next steps

<CardGroup cols={3}>
  <Card title="Create an app" icon="plus" href="02-Creating-an-App.md">
    Start a new app from a template or import an existing repo.
  </Card>

  <Card title="Sandbox editor" icon="code" href="03-Sandbox-Editor.md">
    Edit code with live preview and the AI coding agent.
  </Card>

  <Card title="Local development" icon="laptop-code" href="04-Local-development.md">
    Clone an app and run it on your own machine.
  </Card>

  <Card title="Deploying" icon="rocket" href="05-Deploying.md">
    Push your changes live and watch the build run.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/apps/overview
