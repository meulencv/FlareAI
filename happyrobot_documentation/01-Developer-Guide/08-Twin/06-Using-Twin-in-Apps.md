---
title: "Using Twin in Apps"
description: "Consume Twin data from a HappyRobot App, and version your schema safely alongside App deploys"
---

# Using Twin in Apps

> Consume Twin data from a HappyRobot App, and version your schema safely alongside App deploys

When you build an [App](../07-Apps/01-Apps-Overview.md) on HappyRobot and your organization has a deployed [Twin gateway](05-SQL-Console-and-Capacity.md#api-gateway), the gateway URL is automatically injected into your App as an environment variable. Your App can read and write Twin data without you wiring up a separate backend, managing credentials, or hosting a database connection.

This page covers two things:

1. **How to consume Twin from your App's code** — env vars, headers, code examples.
2. **How to version Twin schema changes alongside App deploys** — what redeploys, what doesn't, and how to roll out breaking changes safely.

## Prerequisites

Before any of this works, you need:

* A **deployed Twin gateway**. See [SQL console and capacity → API Gateway](05-SQL-Console-and-Capacity.md#api-gateway) for setup. Status must be **Running**.
* An **App** in your organization. See [creating an App](../07-Apps/02-Creating-an-App.md).

When both exist, every new App build automatically receives the gateway URL as `NEXT_PUBLIC_TWIN_GATEWAY`. Existing Apps pick it up on their next deploy.

## How the gateway is wired into your App

When HappyRobot builds your App, it injects a small set of [platform-managed environment variables](../07-Apps/07-Environment-Variables.md#platform-managed-variables). For organizations with a deployed Twin gateway, that set includes:

```bash theme={null}
NEXT_PUBLIC_TWIN_GATEWAY=https://<your-gateway-host>
```

You don't set this yourself — it's added at build time. If your org doesn't have a Twin gateway deployed, the variable is simply absent, and your App code should handle that case (or feature-gate the Twin-dependent parts).

Every request to the gateway must include your **organization ID** in a header:

```
x-org-id: <your-org-id>
```

Your App's org ID is also injected as `NEXT_PUBLIC_ORG_ID`, so you can build the header right from your code.

## Calling Twin from your App

The gateway is a REST API rooted at the gateway URL. Here's a minimal Next.js example reading from a `customers` table:

```ts theme={null}
// app/api/customers/route.ts
export async function GET() {
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_TWIN_GATEWAY}/customers?limit=50`,
    {
      headers: {
        "x-org-id": process.env.NEXT_PUBLIC_ORG_ID!,
      },
    }
  );

  if (!res.ok) {
    return new Response("Twin error", { status: res.status });
  }

  const rows = await res.json();
  return Response.json(rows);
}
```

And writing a row:

```ts theme={null}
const res = await fetch(
  `${process.env.NEXT_PUBLIC_TWIN_GATEWAY}/customers`,
  {
    method: "POST",
    headers: {
      "x-org-id": process.env.NEXT_PUBLIC_ORG_ID!,
      "Content-Type": "application/json",
      Prefer: "return=representation",
    },
    body: JSON.stringify({ name: "Alice", email: "alice@example.com" }),
  }
);

const inserted = await res.json();
```

The gateway is a thin REST wrapper over your Twin database. It reflects your schema automatically — any tables, columns, views, or foreign keys you add in the Twin workspace become available immediately. You don't need to redeploy your App when you add a new column.

<Tip>
  Build a single fetch helper in your App that prepends the gateway URL and `x-org-id` header. It keeps the rest of your code readable and gives you one place to add caching, retries, or error handling later.
</Tip>

### Server-side only — and why

Although `NEXT_PUBLIC_TWIN_GATEWAY` is prefixed with `NEXT_PUBLIC_` (so the value is available in the browser bundle), **don't call the gateway directly from the browser**. The gateway is bound to your organization by the `x-org-id` header alone; anyone who can read the bundle can issue requests as your org.

Always proxy Twin calls through a server route, server action, or route handler. Add your own auth check there.

```ts theme={null}
// app/api/customers/route.ts — proxies through the server
import { getCurrentUser } from "@/lib/auth";

export async function GET() {
  const user = await getCurrentUser();
  if (!user) return new Response("Unauthorized", { status: 401 });

  // Now safe to call Twin
  const res = await fetch(
    `${process.env.NEXT_PUBLIC_TWIN_GATEWAY}/customers`,
    { headers: { "x-org-id": process.env.NEXT_PUBLIC_ORG_ID! } }
  );
  return Response.json(await res.json());
}
```

## Deploy interactions: when do redeploys happen?

Understanding when an App rebuilds vs. when Twin changes pick up automatically is the key to safe iteration.

| Change                                     | Triggers App redeploy?                 | Notes                                                                                                                                              |
| ------------------------------------------ | -------------------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| Add a column, table, or view in Twin       | **No**                                 | The gateway reflects schema changes automatically. Your App sees new endpoints/columns on the next request.                                        |
| Remove or rename a column or table         | **No** — but your App's code may break | The gateway picks up the removal immediately. If your App's code still references the dropped column, fix the code and deploy.                     |
| Add or change a foreign key                | **No**                                 | Constraints are enforced on writes immediately.                                                                                                    |
| Deploy the Twin gateway for the first time | **Yes — the next App deploy**          | The `NEXT_PUBLIC_TWIN_GATEWAY` env var is injected on the next build. Apps built before the gateway existed don't have it; redeploy to pick it up. |
| Delete the Twin gateway                    | **Yes** (you must redeploy without it) | The env var is removed on the next build. Apps built while the gateway existed still have it but the endpoint stops responding.                    |
| Change Twin instance class or storage      | **No**                                 | The gateway URL doesn't change. Expect brief downtime if you upgrade the instance class.                                                           |
| Change your App's code                     | **Yes**                                | Standard App deploy. Pulls the latest gateway URL automatically.                                                                                   |

## Versioning Twin schema alongside App deploys

Twin doesn't have built-in schema versioning — there's one database per org, and changes apply immediately to anyone reading or writing. That means **schema changes and the App code that consumes them have to be sequenced carefully** when those changes are not strictly additive.

### Additive changes (safe — do them anytime)

Adding tables, columns (nullable or with defaults), views, indexes, and foreign keys to columns that already comply doesn't break existing readers or writers.

**Recommended order:**

1. Make the schema change in the Twin workspace.
2. Update App code to use the new column/table.
3. Deploy the App.

### Breaking changes (require a multi-step rollout)

Dropping or renaming a column or table, tightening a constraint, or changing a column's type can break Apps mid-flight. Use an expand–migrate–contract pattern:

<Steps>
  <Step title="Expand">
    Add the new column or table alongside the old one. Don't delete anything yet.
  </Step>

  <Step title="Backfill">
    Use the [SQL console](05-SQL-Console-and-Capacity.md#sql-console) or a [workflow run dump backfill](04-Workflow-Run-Dumps.md#backfilling-historical-runs) to populate the new shape from the old one.
  </Step>

  <Step title="Dual-write">
    Update your App code to write to **both** the old and new shapes. Deploy the App.
  </Step>

  <Step title="Migrate reads">
    Update your App code to read from the new shape. Deploy the App. Confirm reads look correct.
  </Step>

  <Step title="Contract">
    Once you're confident nothing reads from the old shape, drop the old column or table.
  </Step>
</Steps>

### Coordinating with workflow nodes

The same considerations apply to [Read from Twin and Write to Twin nodes](../15-Integrations/06-Data-and-Storage/07-Twin-database.md) — they reference column names directly. If you're about to drop a column, search your workflows for references first, then deploy a new workflow version that doesn't reference it before applying the schema change.

### Use version control for App code, not Twin schema

App code lives in a managed GitHub repository and is versioned by Git. [Build history](../07-Apps/06-Build-History-and-Versioning.md) gives you a per-deploy record of what shipped and lets you roll back to a previous build if needed.

Twin schema is **not** versioned by HappyRobot. If you want history for your schema, treat the SQL console statements you run as code: keep them in your App repo (or another repo) as `.sql` files alongside the App code that depends on them. That way, rolling back the App also gives you the SQL that was current at that time.

## Rolling back

A failed App deploy or a broken schema change generally has two paths back:

* **App code regression?** Open the App's [build history](../07-Apps/06-Build-History-and-Versioning.md) and identify the last good commit. Revert in Git and redeploy the App.
* **Twin schema regression?** Re-apply the previous schema using the [SQL console](05-SQL-Console-and-Capacity.md#sql-console). Twin does not snapshot DDL changes automatically, so the rollback is whatever DDL you saved.

The two systems decouple intentionally: code changes are reversible by re-deploying a previous commit; schema changes require running the inverse DDL by hand or restoring from an RDS snapshot (contact support).

## Local development

To run your App locally against your real Twin database, set the two variables in `.env.local`:

```bash theme={null}
NEXT_PUBLIC_TWIN_GATEWAY=https://<your-gateway-host>
NEXT_PUBLIC_ORG_ID=<your-org-id>
```

Grab the gateway URL from **Settings → Twin Database** and your org ID from the URL of any platform page (it's the segment after the host).

Be careful — local development reads from and writes to the same database your production App uses. If you need to experiment with destructive changes, work in a sandbox table you can drop afterward, or wait until Twin supports per-environment databases.

## Next steps

<CardGroup cols={3}>
  <Card title="Apps overview" icon="browser" href="../07-Apps/01-Apps-Overview.md">
    Everything else about how Apps work on HappyRobot.
  </Card>

  <Card title="App environment variables" icon="lock" href="../07-Apps/07-Environment-Variables.md">
    Full list of platform-managed variables in Apps.
  </Card>

  <Card title="Sandbox editor" icon="code" href="../07-Apps/03-Sandbox-Editor.md">
    Edit your App's code and call Twin from inside the sandbox.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/twin/using-in-apps
