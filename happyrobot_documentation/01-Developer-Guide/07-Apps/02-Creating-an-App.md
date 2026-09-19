---
title: "Creating an App"
description: "Start a new app from a template or import an existing GitHub repository"
---

# Creating an App

> Start a new app from a template or import an existing GitHub repository

You can create an app two ways: from a built-in **template** or by **importing** an existing GitHub repository. Both paths produce the same result — a managed repository, a deployment project, environment variables, and a public URL — so most of what you do afterwards is identical.

## From a template

The fastest way to get started. HappyRobot clones a starter project, provisions a deployment, and opens the sandbox so you can start editing.

<Steps>
  <Step title="Open the Apps tab">
    Navigate to **Apps** in the sidebar and click **Create App**.
  </Step>

  <Step title="Name your app">
    Enter a name (e.g., *Carrier Portal*). HappyRobot generates a URL-safe **slug** from the name and appends a short random suffix to keep it globally unique.
  </Step>

  <Step title="Add an optional description">
    The description is shown in the apps list and exposed to your code as `NEXT_PUBLIC_APP_DESCRIPTION`.
  </Step>

  <Step title="Pick a template">
    Select a template. **Next.js Full-Stack** is the recommended starting point for new apps.
  </Step>

  <Step title="Create the app">
    Click **Create**. HappyRobot creates a managed GitHub repository from the template, provisions a Vercel project, injects the platform's standard environment variables, and starts your first build. When the build finishes, the app is live at its public URL.
  </Step>
</Steps>

## Templates

| Template               | Framework            | Deploys to  | Status                               |
| ---------------------- | -------------------- | ----------- | ------------------------------------ |
| **Next.js Full-Stack** | Next.js (App Router) | Vercel      | Recommended — actively maintained    |
| **Vite Static**        | Vite                 | AWS Amplify | Deprecating — kept for existing apps |

<Note>
  New apps should use the **Next.js Full-Stack** template. The Vite Static template remains supported for existing apps but is no longer recommended for new projects.
</Note>

Each template ships with a working project structure, dependencies, build scripts, and any framework-specific configuration. You can edit anything — the template is just a starting point.

## Importing an existing repository

If you already have a Next.js project on GitHub, you can import it instead of starting from a template. Imports are useful for migrating an existing app onto the platform without having to copy code by hand.

<Steps>
  <Step title="Open the import flow">
    Click **Create App**, then choose **Import from existing repo**.
  </Step>

  <Step title="Provide the source">
    Enter the source repository URL (`https://github.com/owner/repo`) and a GitHub **personal access token** with read access to the repo. The token is used once to fetch the source.
  </Step>

  <Step title="Name the imported app">
    Give the imported app a name and optional description.
  </Step>

  <Step title="Create the app">
    HappyRobot fetches the source, validates that it's a Next.js project, creates a new managed GitHub repository in the HappyRobot organization, and pushes the imported code as a single squashed commit. The original source URL is preserved in the commit message.
  </Step>
</Steps>

<Warning>
  The first build of an imported app often fails. Arbitrary repositories rarely match the platform's deployment expectations on the first try — build commands, environment variables, or framework configuration may need adjusting. Open the app in the sandbox and use the AI agent: it can read the build logs and iterate until the build succeeds.
</Warning>

Imports always deploy to Vercel. The Amplify deployment path is reserved for legacy Vite Static apps.

## Naming and slugs

| Field           | Rules                                                                                                                                                                         |
| --------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Name**        | Free-form. Used as the display name in the apps list and the breadcrumb.                                                                                                      |
| **Slug**        | Auto-generated from the name. Lowercased, kebab-cased, capped at 38 characters, with a 5-character random suffix appended for uniqueness. Slugs are immutable after creation. |
| **Description** | Optional. Shown in the apps list and injected into the app as `NEXT_PUBLIC_APP_DESCRIPTION`.                                                                                  |

The 38-character cap on the slug exists so the full subdomain (`<slug>.<apps-domain>`) fits inside the SSL certificate's Common Name limit. Long names are truncated automatically.

## What gets created behind the scenes

When you create an app, HappyRobot provisions:

* A managed **GitHub repository** in the HappyRobot organization, seeded from the template (or your imported source).
* A **Vercel project** (or Amplify app, for the legacy Vite template) linked to the repository so every push triggers a build.
* A **public URL** on a HappyRobot-managed domain — `https://<slug>.happyrobot.ai` (or your organization's configured apps domain). Apps are always served from a HappyRobot subdomain in production.
* A set of **platform-managed environment variables** that expose your app's identity to your code. See [environment variables](07-Environment-Variables.md#platform-managed-variables).

You don't need to manage the GitHub repository, Vercel project, or DNS yourself — everything is created and wired up for you.

## Next steps

<CardGroup cols={3}>
  <Card title="Edit your app" icon="code" href="03-Sandbox-Editor.md">
    Open the sandbox and start writing code.
  </Card>

  <Card title="Add environment variables" icon="lock" href="07-Environment-Variables.md">
    Configure secrets and runtime config.
  </Card>

  <Card title="Deploy your changes" icon="rocket" href="05-Deploying.md">
    Push your app live.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/apps/creating-an-app
