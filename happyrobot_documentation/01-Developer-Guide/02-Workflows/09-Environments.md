---
title: "Environments"
description: "Configuring development, staging, and production environments"
---

# Environments

> Configuring development, staging, and production environments

Environments let you test changes safely before deploying to production. Each environment runs its own version of the workflow with separate phone numbers, webhook endpoints, and integration credentials.

## Three environments

HappyRobot provides three built-in environments:

* **Development** — For local iteration and early testing. Use test credentials and development phone numbers.
* **Staging** — For pre-production validation. Use sandbox credentials and staging phone numbers.
* **Production** — Live traffic. Real customers, real integrations, real data.

Each environment runs its own published version of the workflow independently. You can have version 5 active in development, version 3 in staging, and version 2 in production — all at the same time.

## Deploying to an environment

<Steps>
  <Step title="Select the target environment">
    In the workflow editor, use the environment tabs to choose **Development**, **Staging**, or **Production**.
  </Step>

  <Step title="Publish your version">
    Click **Publish** to deploy the current workflow to the selected environment. Depending on your organization's settings, some environments may require an approval before publishing. See [Versions and publishing](08-Versions-and-Publishing.md) for details on the approval process.
  </Step>

  <Step title="Verify the deployment">
    Check the environment badge in the editor to confirm which version is active. A pulsating indicator shows the live version for each environment.
  </Step>
</Steps>

## Environment-specific settings

Several workflow settings can differ across environments:

* **Phone numbers** — Assign different numbers for each environment. Test numbers in development and staging won't interfere with production traffic.
* **Integration credentials** — Use sandbox API keys in development/staging and production keys in production. Configure these per environment in **Settings > Integrations**.
* **Environment variables** — Set different values per environment for URLs, feature flags, and other configuration. See [Environment variables](../16-Account-and-Settings/08-Environment-Variables.md).
* **Webhook endpoints** — Each environment has distinct endpoint URLs, so external systems can target the correct environment.
* **Node configuration** — Certain trigger nodes (inbound phone, email) support separate configurations per environment, so you can point each environment at different phone numbers or email accounts.

## Promoting changes

The recommended workflow for deploying changes:

<Steps>
  <Step title="Build in development">
    Iterate on your workflow in the editor. Publish to development to test with real integrations using test credentials.
  </Step>

  <Step title="Validate in staging">
    Publish to staging to test with realistic data and staging credentials. Run through your key scenarios and check run outputs, transcripts, and integration responses.
  </Step>

  <Step title="Publish to production">
    Once staging looks good, publish the same version to production. Monitor the first few runs to confirm everything works with live data.
  </Step>
</Steps>

<Tip>
  Always validate in staging before publishing to production — especially for workflows that handle phone calls or send emails. Catching issues in staging is much cheaper than fixing them in production.
</Tip>

## Best practices

* **Use all three environments.** Development for rapid iteration, staging for validation, production for live traffic.
* **Use environment variables for config that differs between environments.** API endpoints, feature flags, and thresholds should be environment variables, not hardcoded values.
* **Monitor runs after promoting.** Review the full run output — node-by-node execution, transcripts, and integration responses — before considering the deployment stable.
* **Keep credentials separate.** Never use production API keys in development or staging. Configure sandbox credentials for non-production integrations.

---

Fuente original: https://docs.happyrobot.ai/workflows/environments
