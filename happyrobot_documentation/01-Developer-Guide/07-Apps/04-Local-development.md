---
title: "Local development"
description: "Clone an app and run it against your HappyRobot workspace"
---

# Local development

> Clone an app and run it against your HappyRobot workspace

You can run a Next.js app on your own machine while it talks to the same workspace as the deployed version. This is useful for anything the [sandbox editor](03-Sandbox-Editor.md) makes awkward — attaching a debugger, running your own test suite, or iterating with local tooling — and every change you push still deploys the same way.

<Note>
  **Develop locally** is available for apps created from the **Next.js Full-Stack** template that have a managed GitHub repository, to anyone with permission to edit the app. It doesn't appear for legacy Vite Static apps.
</Note>

## Setting up

Open the app's detail page, open the actions menu (**⋯**), and choose **Develop locally**. The panel walks through four steps.

<Steps>
  <Step title="Clone the repository">
    Copy the `git clone` command from the panel and run it. This is the same managed repository the platform deploys from — you're working directly against it, not a fork.
  </Step>

  <Step title="Download the environment">
    Click **Download .env.local** and save the file at the root of the clone.
  </Step>

  <Step title="Configure Git">
    Run the two `git config --local` commands from the panel inside the clone. They set the commit identity the platform expects, so pushes from your machine deploy cleanly. Because they use `--local`, they only affect this clone and leave your global Git config alone.
  </Step>

  <Step title="Run the app">
    Run `npm install` and then `npm run dev`. The app starts on `localhost` and reads its configuration from `.env.local`.
  </Step>
</Steps>

## What's in the .env.local file

The download contains both halves of your app's configuration:

* Your custom [environment variables](07-Environment-Variables.md), including their secret values. Where a variable holds a different value per environment, the download uses the **Preview** value when the app has a Preview deployment, and the **Production** value otherwise.
* The platform-managed values — `HR_PLATFORM_URL`, `NEXT_PUBLIC_ORG_ID`, `NEXT_PUBLIC_APP_SLUG`, `NEXT_PUBLIC_APP_NAME`, `NEXT_PUBLIC_APP_DESCRIPTION`, and the Twin gateway URL where Twin is configured. See [platform-managed variables](07-Environment-Variables.md#platform-managed-variables).

<Warning>
  The downloaded `.env.local` contains real secret values, including your custom environment variables. Keep it out of version control — the template's `.gitignore` already excludes `.env.local` — and don't share it.
</Warning>

Download the file again whenever you change an environment variable in the platform; the local copy doesn't update on its own.

## Signing in locally

Apps running on `localhost` can authenticate against your workspace through the same HappyRobot sign-in flow the deployed app uses, so features that depend on the signed-in user work locally without separate test credentials or stubbing out the auth layer. Access is still checked against your workspace membership and the app's permissions — running locally doesn't bypass either.

## Deploying your changes

Local development doesn't change how deploys work. Push a commit to the managed repository and the platform builds and deploys it exactly as it would a change made in the sandbox. See [Deploying](05-Deploying.md) and [Build history](06-Build-History-and-Versioning.md).

## Next steps

<CardGroup cols={3}>
  <Card title="Sandbox editor" icon="code" href="03-Sandbox-Editor.md">
    Edit the same app in the browser.
  </Card>

  <Card title="Environment variables" icon="lock" href="07-Environment-Variables.md">
    Manage the values that end up in your local env file.
  </Card>

  <Card title="Deploying" icon="rocket" href="05-Deploying.md">
    Push your changes live.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/apps/local-development
