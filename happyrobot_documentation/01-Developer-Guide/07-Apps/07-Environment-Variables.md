---
title: "Environment Variables"
description: "Configure secrets and runtime values for your app"
---

# Environment Variables

> Configure secrets and runtime values for your app

Apps support **environment variables** for secrets, API keys, and any other config that shouldn't be hard-coded in the repository. Values are encrypted at rest, never exposed back to the UI, and automatically synced to your deployment provider so they're available to your app at build and runtime.

<Note>
  Environment variables are available for apps deployed to Vercel — the default for new Next.js Full-Stack apps. Legacy Vite Static apps on Amplify don't expose this panel.
</Note>

## Managing environment variables

Open your app and click **Environment variables** in the header. The panel lists every variable currently set on the app and lets you add, update, or delete entries.

### Adding or updating a variable

<Steps>
  <Step title="Click Add variable">
    Open the **Environment variables** panel and click **Add variable**.
  </Step>

  <Step title="Enter a key">
    Use UPPER\_SNAKE\_CASE (e.g., `DATABASE_URL`). The key must start with an uppercase letter or underscore and contain only uppercase letters, digits, and underscores. If the key already exists, the form tells you so — edit the existing entry instead.
  </Step>

  <Step title="Enter a value per environment">
    Give the variable a **Production** value, a **Preview** value, or both. Each environment holds its own value, so a variable can point at a production database in Production and a scratch one in Preview. Maximum value size is 64 KB per environment.
  </Step>

  <Step title="Save">
    Click **Create**. Values are encrypted on save, synced to your deployment provider for the environments you selected, and a redeploy is triggered so the new values are picked up by the next build.
  </Step>
</Steps>

### Values by environment

A variable does not have to exist in every environment.

| Action                             | How                                                                                                                                                                                                                               |
| ---------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Add an environment's value**     | Click **Add Production value** or **Add Preview value** and type the value.                                                                                                                                                       |
| **Change one environment's value** | Type a new value in that environment's field. Leaving the field blank (it shows **Unchanged**) keeps the saved value.                                                                                                             |
| **Remove an environment's value**  | Click the **×** next to that environment's field. The panel confirms with *Production value will be removed when saved* before you commit, and the value is deleted when you save. A variable must keep at least one environment. |

**Preview** values can only be set once the app has a Preview deployment. Until then the Preview option is disabled and shows **Set up Preview to configure its value**.

<Note>
  The [sandbox editor](03-Sandbox-Editor.md) and the `.env.local` file you download for [local development](04-Local-development.md) use your **Preview** values when the app has a Preview deployment, and your **Production** values otherwise. Restart the sandbox after changing those values so the running dev server picks them up.
</Note>

Each row in the panel lists the environments a variable is set for, so you can see at a glance which keys are production-only.

### Deleting a variable

Click the delete icon next to any variable. HappyRobot removes it from every environment on the deployment provider, deletes it from storage, and triggers a redeploy.

## Naming rules

| Rule                      | Detail                                                                                                                                                                               |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| **Format**                | Must match `^[A-Z_][A-Z0-9_]*$` — UPPER\_SNAKE\_CASE starting with a letter or underscore.                                                                                           |
| **`NEXT_PUBLIC_` prefix** | Allowed, but the value is inlined into the client bundle and readable by anyone using your app. The form warns you when a key starts with `NEXT_PUBLIC_`. Never use it for a secret. |
| **Reserved keys**         | Several keys are managed by the platform and cannot be set manually. See [platform-managed variables](#platform-managed-variables) below.                                            |
| **Uniqueness**            | Each key exists once per app, with up to one value per environment. Adding an existing key again is rejected — edit the existing variable instead.                                   |

## Encryption and write-only behavior

Values are encrypted with JWE before being stored. Once saved, **values cannot be retrieved through the platform** — the UI shows only the key, never the value. This is intentional: it prevents anyone with read access to the platform from harvesting secrets.

If you need to confirm what a value should be, store it somewhere you control (a password manager, your provider's vault, etc.). To rotate a secret, save a new value over the existing key.

## Platform-managed variables

When you create an app, HappyRobot automatically sets a handful of variables that expose the app's identity to your code. You don't need to set these yourself, and you can't override them.

| Key                                  | Description                                                                                     |
| ------------------------------------ | ----------------------------------------------------------------------------------------------- |
| `HR_PLATFORM_URL`                    | The base URL of the HappyRobot platform — useful when your app calls back into HappyRobot APIs. |
| `NEXT_PUBLIC_ORG_ID`                 | The organization ID this app belongs to. Browser-safe.                                          |
| `NEXT_PUBLIC_APP_SLUG`               | The app's slug. Browser-safe.                                                                   |
| `NEXT_PUBLIC_APP_NAME`               | The app's display name. Browser-safe.                                                           |
| `NEXT_PUBLIC_APP_DESCRIPTION`        | The optional description from the app's settings. Browser-safe.                                 |
| `NEXT_PUBLIC_TWIN_GATEWAY`           | The Twin gateway URL — only set if your organization has Twin configured.                       |
| `VERCEL`, `VERCEL_URL`, `VERCEL_ENV` | Provided by Vercel at build time. Reserved so user variables can't shadow them.                 |

Variables prefixed with `NEXT_PUBLIC_` are inlined into the client bundle and visible in the browser — never put secrets in a `NEXT_PUBLIC_*` variable.

## When deploys are triggered

Every change to environment variables triggers a redeploy automatically — there's no separate "apply changes" step. The redeploy uses the most recent commit on `main`, so your code doesn't change, only the values your code sees.

If you change several variables at once, the redeploys may queue up. The deployment provider executes them in order and only the most recent successful build is served at the public URL.

## Using variables in your code

Inside a Next.js Full-Stack app, environment variables are available the same way they are on any Next.js project:

```ts theme={null}
// Server-side (route handlers, server components, server actions)
const dbUrl = process.env.DATABASE_URL;

// Client-side (only NEXT_PUBLIC_* variables)
const orgId = process.env.NEXT_PUBLIC_ORG_ID;
```

Only variables prefixed with `NEXT_PUBLIC_` are exposed to the browser. Everything else stays on the server.

## Next steps

<CardGroup cols={3}>
  <Card title="Deploying" icon="rocket" href="05-Deploying.md">
    Trigger a manual deploy.
  </Card>

  <Card title="Sandbox editor" icon="code" href="03-Sandbox-Editor.md">
    Open the editor and reference your variables in code.
  </Card>

  <Card title="Build history" icon="clock-rotate-left" href="06-Build-History-and-Versioning.md">
    Watch the redeploy that picks up your new values.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/apps/environment-variables
