---
title: "Credentials"
description: "Manage authentication for your integrations"
---

# Credentials

> Manage authentication for your integrations

Credentials store the authentication details that HappyRobot uses to connect to external services on your behalf. Each integration requires one or more credentials before you can use its events in workflows.

## Credential types

Different integrations support different authentication methods:

| Credential type                  | Description                                                                                                              | Used by                                                         |
| -------------------------------- | ------------------------------------------------------------------------------------------------------------------------ | --------------------------------------------------------------- |
| **User OAuth**                   | Redirects to the service's sign-in page to authorize access to a specific user account                                   | Gmail, Outlook, Slack, Microsoft Teams, Google Sheets, WhatsApp |
| **Service Account**              | Uses a JSON service account key to access organizational accounts without user interaction                               | Gmail                                                           |
| **Service Principal**            | Uses application-level credentials (Client ID, Tenant ID, Client Secret) to access organizational mailboxes              | Outlook                                                         |
| **Azure Communication Services** | Uses ACS endpoint and access key for high-volume transactional email                                                     | Outlook                                                         |
| **API Key**                      | A single API key string                                                                                                  | SendGrid                                                        |
| **API Client**                   | OAuth 2.0 client credentials exchanged for an access token at a token URL                                                | OAuth 2.0                                                       |
| **Service Account (JWT Bearer)** | Signs a short-lived assertion with a private key instead of sending a client secret                                      | OAuth 2.0                                                       |
| **Client Certificate (mTLS)**    | Presents a client certificate and private key to a mutually authenticated HTTPS endpoint                                 | OAuth 2.0                                                       |
| **Form-based**                   | Custom fields specific to the integration (e.g., Account SID + Auth Token for Twilio)                                    | Twilio SMS, McLeod, Turvo, Snowflake, Redis                     |
| **API Client**                   | OAuth 2.0 client credentials — a token URL plus the parameters, headers, and body fields used to request an access token | OAuth 2.0                                                       |
| **Service Account (JWT Bearer)** | Signs a short-lived assertion with a private key instead of sending a client secret                                      | OAuth 2.0                                                       |
| **Client Certificate (mTLS)**    | Presents a client certificate and private key to mutually authenticated HTTPS endpoints                                  | OAuth 2.0                                                       |
| **Identity Provider**            | Validates inbound JWTs against your identity provider                                                                    | OAuth 2.0                                                       |

## Creating credentials

<Steps>
  <Step title="Navigate to the integration">
    Go to **Settings > Integrations** and click on the integration you want to configure.
  </Step>

  <Step title="Click Add Credential">
    On the integration's settings page, click **Add Credential**. If the integration supports multiple credential types, select the type you want.
  </Step>

  <Step title="Authenticate or fill in fields">
    * **OAuth integrations**: You'll be redirected to the service's sign-in page. Grant the requested permissions and you'll be redirected back.
    * **Form-based integrations**: Fill in the required fields (API keys, tokens, URLs, etc.) and save.
    * **Dialog-based integrations**: Follow the configuration dialog to set up the connection.
  </Step>

  <Step title="Test the connection">
    Some integrations provide a **Test** button after adding credentials. Click it to verify the connection works before using it in workflows.
  </Step>
</Steps>

### Testing an API Client credential before saving

An **API Client** (OAuth 2.0 client credentials) credential is verified before it's stored. Fill in the form and click **Test Connection**: HappyRobot requests an access token from the token URL using exactly the values on screen, then discards it — nothing is saved and the token never reaches your browser.

* **Connection successful** means the token endpoint accepted those values, and the credential can be saved.
* **Connection failed** shows the error the authorization server returned, so you can fix the token URL, client ID, secret, scope, or extra parameters in place.

The request is made from HappyRobot's servers, so a passing test also confirms the endpoint is reachable from the platform. Editing any field — or switching credential type — clears the result, so test again before saving and what you store is always a combination that worked. The token URL must be `https://`.

## Client certificates (mTLS)

A **Client Certificate (mTLS)** credential holds the certificate HappyRobot presents when an endpoint requires mutual TLS. Create it under **Settings > Integrations > OAuth 2.0**, then select it on a [Webhook node](../03-Core-Nodes/06-Webhook.md#client-certificates-mtls).

| Field                        | Required | Description                                                                                                         |
| ---------------------------- | -------- | ------------------------------------------------------------------------------------------------------------------- |
| **Client Certificate (PEM)** | Yes      | The certificate chain presented to the remote server. Paste the whole block, including the `BEGIN` and `END` lines. |
| **Private Key (PEM)**        | Yes      | The unencrypted private key matching the certificate. Passphrase-protected keys aren't supported.                   |
| **CA Certificate (PEM)**     | No       | A private certificate authority used to verify the server. Leave empty to use the system roots.                     |

Paste each PEM block or click **Choose PEM file** to load it from a `.pem`, `.crt`, `.cer`, or `.key` file. All three fields are write-only: once saved they read back as a redacted placeholder and can only be replaced, not inspected. Because of that, HappyRobot validates the PEM blocks when you save and checks that the private key actually matches the certificate — a mismatched pair is rejected in the form rather than failing later at request time.

<Tip>
  Keep a copy of the certificate and key in your own secret store. Rotating an mTLS credential means pasting the new pair over the old one, and the saved values can't be exported from HappyRobot.
</Tip>

## Managing credentials through the API

Form-based credentials can also be created and replaced through the [Platform API](https://docs.happyrobot.ai/api-reference/overview):

| Operation | Endpoint                                                         |
| --------- | ---------------------------------------------------------------- |
| Create    | `POST /integrations/{integration_id}/create-credential`          |
| Update    | `PUT /integrations/{integration_id}/credentials/{credential_id}` |

An update **replaces** the credential's title and data while keeping its ID, so workflows that reference it keep working. A few rules to know:

* Send the same complete payload as creation, including every required data field — the update is not a partial patch.
* Omit `credential_type` to use the integration's default type; send it explicitly for any other type.
* Omitting `tag_ids` preserves the credential's existing tags. Sending an empty array removes them.
* OAuth credentials can't be created or updated this way — the authorization flow has to be completed in the platform UI, and the API returns `405 Method Not Allowed`.
* Credential secrets are never returned in a response.

## Credential statuses

Each credential has a status indicating its current health:

| Status      | Description                                                                                 |
| ----------- | ------------------------------------------------------------------------------------------- |
| **Active**  | The credential is working and ready to use in workflows                                     |
| **Expired** | The credential's access token or secret has expired and needs to be refreshed or re-created |
| **Error**   | The credential encountered an error — check the configuration and re-authenticate if needed |

<Warning>
  Expired or errored credentials will cause workflow runs to fail at the node that uses them. Monitor credential status regularly, especially for OAuth-based integrations where tokens can expire.
</Warning>

## Subscription management

Some integrations — Gmail, Outlook, and Microsoft Teams — use **subscriptions** to receive real-time events. Subscriptions are managed separately from credentials and have their own lifecycle.

Subscription statuses:

| Status        | Description                                |
| ------------- | ------------------------------------------ |
| **Active**    | Receiving events normally                  |
| **Pending**   | Subscription is being set up               |
| **Expired**   | Subscription has expired and needs renewal |
| **Failed**    | Subscription creation or renewal failed    |
| **Suspended** | Subscription has been paused               |

You can manage subscriptions from the **Subscriptions** tab on the integration's settings page. Use the **Unsubscribe** and **Resubscribe** buttons to control event delivery.

## Credential usage

Gmail and Outlook credentials and subscriptions track what depends on them, so you can see the impact of a change before making it.

Open a credential's or subscription's row menu and choose **View Usage**. The dialog lists every workflow using it, grouped by workflow, with each version's environment and whether the agents using it are inbound or outbound. Click the external-link icon on a version to open it in the editor.

<Warning>
  Deleting a credential or subscription that a **live** email agent uses is blocked. Open **View Usage**, unpublish the listed workflow versions, and try again.
</Warning>

## Environment-specific credentials

Certain integrations support separate credentials for different environments (development, staging, production). This lets you use test accounts during development and production accounts in live workflows. Integrations that support environment-specific configuration include:

* Gmail (New Email trigger)
* Outlook (New Email trigger)
* Voice agent phone numbers

<Tip>
  When setting up a workflow that uses environment-specific credentials, configure credentials for each environment you plan to deploy to. This prevents failures when publishing from staging to production.
</Tip>

## Security best practices

* **Rotate credentials regularly** — especially API keys and service account tokens.
* **Use the minimum required permissions** — when authorizing OAuth connections, only grant scopes that your workflows actually need.
* **Delete unused credentials** — remove credentials for integrations you no longer use.
* **Use Service Principals over user accounts** — for production workloads, service-level credentials are more reliable and don't depend on individual user accounts.

## Next steps

<CardGroup cols={3}>
  <Card title="Integrations overview" icon="plug" href="01-Integrations-Overview.md">
    Learn how integrations work in workflows.
  </Card>

  <Card title="Gmail" icon="envelope" href="04-Communication/01-Gmail.md">
    Set up Gmail with OAuth or Service Account.
  </Card>

  <Card title="Outlook" icon="envelope" href="04-Communication/02-Outlook.md">
    Connect Outlook with multiple auth methods.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/credentials
