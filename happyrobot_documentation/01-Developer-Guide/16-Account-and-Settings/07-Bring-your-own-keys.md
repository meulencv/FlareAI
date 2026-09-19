---
title: "Bring your own keys"
description: "Run HappyRobot AI features on your organization's own OpenAI, Anthropic, or Gemini credentials"
---

# Bring your own keys

> Run HappyRobot AI features on your organization's own OpenAI, Anthropic, or Gemini credentials

By default, every model request HappyRobot makes on your behalf runs on HappyRobot's own provider credentials. **Bring your own keys (BYOK)** lets you register your organization's LLM provider credentials instead, so the usage is billed to your provider account under your own rate limits and data agreements.

## Where to find it

Go to **Settings > API Keys**, open the **⋮** menu next to **Create API Key**, and choose **Bring your own keys**.

Managing credentials requires the same permission as managing [API keys](06-API-Keys.md) for the workspace. The page is scoped to one workspace — credentials are not shared between workspaces.

## Supported providers

You can configure one credential per provider.

| Provider      | What you provide                                                                          |
| ------------- | ----------------------------------------------------------------------------------------- |
| **OpenAI**    | An API key                                                                                |
| **Anthropic** | An API key                                                                                |
| **Gemini**    | A Google Cloud **project ID** and a **service account JSON** key with access to Vertex AI |

## Adding a credential

<Steps>
  <Step title="Open the provider card">
    Each provider has a card showing its current status. Click **Configure** on the provider you want to set up (or **Replace** if a credential is already stored).
  </Step>

  <Step title="Paste the credential">
    For OpenAI and Anthropic, paste the API key. For Gemini, enter the Google Cloud project ID and paste the full service account JSON — it must include `type`, `client_email`, and `private_key`.
  </Step>

  <Step title="Save">
    HappyRobot validates the credential against the provider before storing it. A credential the provider rejects is not saved, and the error from the provider is shown so you can correct it.
  </Step>
</Steps>

<Warning>
  Credentials are write-only. Once saved, they are never returned by the platform or the API — the card shows only the last four characters of an API key, or the project ID and whether a service account is present. If you lose the original credential, replace it with a new one.
</Warning>

## Credential status

Each card carries a status badge and the time of its last validation.

| Status                | Meaning                                                                                                                                                        |
| --------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Not configured**    | No credential stored for this provider. Requests use HappyRobot's platform credentials.                                                                        |
| **Active**            | The credential validated successfully and is in use.                                                                                                           |
| **Validation failed** | The provider rejected the credential, or it could not be reached. The error is shown on the card, and requests fall back to HappyRobot's platform credentials. |
| **Disabled**          | The credential is stored but not used. Requests fall back to HappyRobot's platform credentials.                                                                |

Beyond **Replace**, each configured card offers:

* **Validate** — re-checks the stored credential with the provider and updates the status and timestamp
* **Disable** / **Enable** — stops or resumes using the credential without deleting it. Enabling re-validates first, so a credential that has since been revoked comes back as **Validation failed** rather than **Active**
* **Remove** — deletes the stored credential

Validation makes a minimal, low-cost call to the provider: a moderation request for OpenAI, a model list for Anthropic, and a token count against Vertex AI for Gemini.

## What runs on your credential

Today, an active credential is used for [Frontal](../02-Workflows/03-Frontal-AI-assistant.md) chat requests on **OpenAI** and **Anthropic** models.

Everywhere a model is selected — Frontal's **Chat Model** picker, and the model pickers on [AI Extract](../03-Core-Nodes/02-AI-Extract.md), [AI Classify](../03-Core-Nodes/03-AI-Classify.md), [AI Generate](../03-Core-Nodes/04-AI-Generate.md), and prompt nodes — providers with an active organization credential are marked with a **BYOK** badge, so you can see which requests are eligible to run on your own account.

<Note>
  BYOK never blocks a request. If no active credential exists for the provider, or the credential is disabled or failing, the request runs on HappyRobot's platform credentials instead.
</Note>

If a provider rejects your credential mid-request with an HTTP 401 — for example because the key was rotated or revoked on the provider's side — HappyRobot marks it **Validation failed**, records the reason on the card, and falls back to platform credentials for subsequent requests. Save a new credential to resume BYOK.

## Next steps

<CardGroup cols={2}>
  <Card title="API keys" icon="key" href="06-API-Keys.md">
    Create and revoke keys for the HappyRobot API.
  </Card>

  <Card title="Models" icon="microchip-ai" href="../14-Assets/05-Models.md">
    Every model available across workflows and agents.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/settings/bring-your-own-keys
