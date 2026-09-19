---
title: "Deploying"
description: "Push your app live and watch the build run"
---

# Deploying

> Push your app live and watch the build run

Deploying an app commits your sandbox changes to the managed GitHub repository, triggers a build on your deployment provider, and updates the live public URL when the build succeeds. The whole flow runs from inside the editor — you don't need to touch GitHub or the provider's dashboard.

## Deploying from the sandbox

<Steps>
  <Step title="Save your changes">
    Make sure every file you want to ship is saved in the editor.
  </Step>

  <Step title="Open the deploy dialog">
    Click **Deploy** in the editor toolbar. A dialog appears asking for a commit message.
  </Step>

  <Step title="Write a commit message">
    Describe what changed. The message becomes the GitHub commit message and is shown in the [build history](06-Build-History-and-Versioning.md). If you skip it, HappyRobot uses `Deploy from sandbox`.
  </Step>

  <Step title="Confirm">
    Click **Deploy**. HappyRobot commits your changes, pushes to the managed repository, and the deployment provider picks them up and starts a new build.
  </Step>
</Steps>

You can also ask the AI agent in the sidebar to deploy for you — it has access to the same deploy action and will use the commit message you give it.

## What happens during a build

Once the deploy is triggered, the build runs on Vercel (or Amplify, for legacy Vite Static apps). A typical Next.js build:

1. Installs dependencies (`npm install`).
2. Builds the project (`npm run build`).
3. Starts the production server and warms it up.
4. Promotes the new version to the public URL.

Build progress streams back into the platform. You can leave the build dialog open and watch the logs live, or close it and check the [build history](06-Build-History-and-Versioning.md) later.

## Build statuses

| Status      | Meaning                                     |
| ----------- | ------------------------------------------- |
| `PENDING`   | Build is queued and hasn't started yet.     |
| `RUNNING`   | Build is currently executing.               |
| `SUCCEED`   | Build finished and the new version is live. |
| `FAILED`    | Build failed. Open the logs to see why.     |
| `CANCELLED` | Build was cancelled before completing.      |

## When a build fails

A failed build does not take down your app — the previous successful deployment stays live. To recover:

1. Open the build in the [build history](06-Build-History-and-Versioning.md) and read the logs.
2. Open the app in the sandbox.
3. Either fix the issue yourself or ask the AI agent to look at the latest build — it can read the logs directly and propose a fix.
4. Deploy again.

<Tip>
  For imported apps, the first deploy usually fails because the imported project's build configuration doesn't match the deployment provider's expectations. The agent is good at reading those logs and making the small adjustments needed — give it the failed build and ask it to get the build green.
</Tip>

## Public URLs

After a successful deployment, your app is reachable at its **public URL** on a HappyRobot-managed domain — every app is served from `https://<slug>.happyrobot.ai` (or your organization's configured apps domain). HappyRobot provisions a managed subdomain for every app at creation time and routes traffic to the underlying deployment behind the scenes.

The public URL is stable across builds. Successful deploys swap the underlying version atomically; failed deploys do not affect it, so the previous version stays live until the next build succeeds.

### Custom URLs

App slugs are [opaque by design](02-Creating-an-App.md#naming-and-slugs), so an app's default hostname isn't memorable — `slate-harbor-k29xd.happyrobot.ai`. You can give an app **one** friendlier subdomain on the same apps domain, so it's reachable at `dispatch.happyrobot.ai` instead.

<Steps>
  <Step title="Open the app">
    Open the app from the Apps list.
  </Step>

  <Step title="Choose Custom URL">
    Open the **⋯** menu in the app header and choose **Custom URL**.
  </Step>

  <Step title="Enter a slug">
    Type the slug you want. The panel shows the resulting hostname as you type. Up to 30 characters, lowercase letters, numbers, and hyphens, with no leading or trailing hyphen.
  </Step>

  <Step title="Save">
    Click **Save**. The app becomes reachable at the new hostname right away.
  </Step>
</Steps>

Notes on how it behaves:

* **The original URL keeps working.** Adding a custom URL doesn't retire the generated one — both resolve to the same deployment. The app's **Public URL** shown in the platform switches to the custom hostname.
* **One custom slug per app.** Saving a new slug replaces the previous one, and the old hostname stops resolving.
* **Slugs are unique across the platform.** If the slug is taken by another app — or by another app's generated slug — the save is rejected. It also cannot match the app's own generated slug.
* **The length cap comes from the certificate.** The exact cap is shown in the panel and derives from your organization's apps domain: the full hostname has to fit inside the SSL certificate's 64-character Common Name limit, or no certificate can be issued and the URL would never resolve.
* **Nothing else changes.** The app slug, [preview URL](03-Sandbox-Editor.md), GitHub repository, environment variables, and access controls are untouched.
* **Remove it any time.** Open the panel again and choose **Remove custom URL**. HappyRobot confirms first, then the custom hostname stops working and the app stays reachable at its original URL.

<Warning>
  A custom slug is a public hostname. Every certificate issued for it is published permanently to public **certificate transparency** logs, and those records can't be deleted — so a slug naming a customer discloses that they work with you. That exposure is why HappyRobot generates an opaque slug by default. The panel warns you before you save; only use a recognizable name when the customer has asked for that specific URL.
</Warning>

Custom URLs are available on managed Next.js apps that have been deployed at least once, and require deploy access to the app.

## Environment variable changes

Adding, updating, or removing an [environment variable](07-Environment-Variables.md) automatically triggers a redeploy so the new values are baked into the next build. You don't need to deploy manually after changing env vars.

## Permissions

To deploy an app you need edit access to it. Edit access is granted either:

* **At the workspace level** — Members with workspace-or-higher access can deploy any app in the organization.
* **Per app** — Specific members can be granted edit access to a single app via RBAC.

See [Team members and roles](../16-Account-and-Settings/02-Members-and-Access.md) for how to assign access.

## Next steps

<CardGroup cols={3}>
  <Card title="Build history" icon="clock-rotate-left" href="06-Build-History-and-Versioning.md">
    Browse past builds and inspect their logs.
  </Card>

  <Card title="Environment variables" icon="lock" href="07-Environment-Variables.md">
    Configure secrets and runtime config.
  </Card>

  <Card title="Sandbox editor" icon="code" href="03-Sandbox-Editor.md">
    Back to the editor and the AI agent.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/apps/deploying
