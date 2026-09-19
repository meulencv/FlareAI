---
title: "Salesforce"
description: "Query, create, update, and delete Salesforce CRM records from workflows"
---

# Salesforce

> Query, create, update, and delete Salesforce CRM records from workflows

The Salesforce integration lets your workflows interact with Salesforce CRM. Use SOQL to query records and run create, read, update, and delete operations on any Salesforce object — all from within the workflow editor.

## Authentication

Salesforce uses OAuth for authentication.

<Steps>
  <Step title="Enable the Salesforce integration">
    Go to **Settings > Integrations** and enable **Salesforce**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential**. Before you're redirected, you can expand the **Advanced** section to set a custom **Salesforce Domain** (see below). Leave it blank to use the default. Then continue to Salesforce's authorization page.
  </Step>

  <Step title="Authorize access">
    Sign in with a Salesforce account that has API access and approve the requested permissions.
  </Step>

  <Step title="Verify the connection">
    After redirecting back, the credential will appear as **Active** and will be available for selection in workflow nodes.
  </Step>
</Steps>

### Custom Salesforce domain

By default, HappyRobot authenticates against Salesforce's standard login endpoint. If your org uses a sandbox or a [My Domain](https://help.salesforce.com/s/articleView?id=sf.domain_name_overview.htm), set the domain in the **Advanced** section when adding a credential:

| Domain                        | When to use                |
| ----------------------------- | -------------------------- |
| `login.salesforce.com`        | Production orgs (default). |
| `test.salesforce.com`         | Sandbox orgs.              |
| `mycompany.my.salesforce.com` | Your org's My Domain.      |

The domain must end in `.salesforce.com` or `.force.com`. Setting the correct domain ensures the OAuth flow and subsequent API calls target the right Salesforce instance.

## Available actions

| Action            | Description                                      |
| ----------------- | ------------------------------------------------ |
| **SOQL Query**    | Execute a SOQL query and return matching records |
| **Create Record** | Create a new record in a Salesforce object       |
| **Get Record**    | Retrieve a record by ID from a Salesforce object |
| **Update Record** | Update fields on an existing record              |
| **Delete Record** | Delete a record by ID                            |

## Action reference

### SOQL Query

Execute a SOQL (Salesforce Object Query Language) query to retrieve records from any Salesforce object.

| Field          | Required | Description                                                                                               |
| -------------- | -------- | --------------------------------------------------------------------------------------------------------- |
| **Credential** | Yes      | The Salesforce OAuth credential to use                                                                    |
| **Query**      | Yes      | A valid SOQL query string (for example, `SELECT Id, Name, Phone FROM Contact WHERE AccountId = '001...'`) |

The node returns an array of records matching the query.

### Create Record

Create a new record in a Salesforce object such as `Contact`, `Lead`, `Account`, or any custom object.

| Field           | Required | Description                                                                           |
| --------------- | -------- | ------------------------------------------------------------------------------------- |
| **Credential**  | Yes      | The Salesforce OAuth credential to use                                                |
| **Object type** | Yes      | The API name of the Salesforce object (for example, `Contact`, `Lead`, `Opportunity`) |
| **Fields**      | No       | Key-value pairs to set on the new record                                              |

### Get Record

Retrieve a single Salesforce record by its ID.

| Field           | Required | Description                                                              |
| --------------- | -------- | ------------------------------------------------------------------------ |
| **Credential**  | Yes      | The Salesforce OAuth credential to use                                   |
| **Object type** | Yes      | The API name of the Salesforce object                                    |
| **Record ID**   | Yes      | The 18-character Salesforce record ID                                    |
| **Fields**      | No       | Comma-separated list of fields to return (returns all fields if omitted) |

### Update Record

Update one or more fields on an existing Salesforce record.

| Field           | Required | Description                            |
| --------------- | -------- | -------------------------------------- |
| **Credential**  | Yes      | The Salesforce OAuth credential to use |
| **Object type** | Yes      | The API name of the Salesforce object  |
| **Record ID**   | Yes      | The ID of the record to update         |
| **Fields**      | No       | Key-value pairs of fields to update    |

### Delete Record

Permanently delete a Salesforce record by ID.

| Field           | Required | Description                            |
| --------------- | -------- | -------------------------------------- |
| **Credential**  | Yes      | The Salesforce OAuth credential to use |
| **Object type** | Yes      | The API name of the Salesforce object  |
| **Record ID**   | Yes      | The ID of the record to delete         |

## Troubleshooting

### "External client app is not installed in this org"

This error means your Salesforce org's security settings are blocking the OAuth connection. Many Salesforce orgs — especially enterprise ones — require an admin to explicitly approve external Connected Apps before users can authorize them.

To resolve this, a **Salesforce administrator** in your org needs to approve the HappyRobot Connected App:

<Steps>
  <Step title="Open Connected Apps OAuth Usage">
    In Salesforce Setup, search for **Connected Apps OAuth Usage** in the Quick Find box and select it.
  </Step>

  <Step title="Find the HappyRobot app">
    Look for the HappyRobot app in the list. It appears after at least one user in your org has attempted the OAuth flow. If you don't see it, try connecting Salesforce from HappyRobot first, then return to this page.
  </Step>

  <Step title="Install or unblock the app">
    Click **Install** next to the HappyRobot app. If the app is already listed but blocked, click **Unblock** instead.
  </Step>

  <Step title="Retry the connection">
    Go back to **Settings > Integrations** in HappyRobot and connect Salesforce again. The OAuth flow should now complete successfully.
  </Step>
</Steps>

<Info>
  For more details on managing external Connected Apps, see Salesforce's documentation on [managing Connected Apps](https://help.salesforce.com/s/articleView?id=sf.connected_app_manage.htm).
</Info>

## Dynamic credentials

All Salesforce actions support [dynamic credentials](../02-Credentials.md#dynamic-credentials). Pass a credential ID through a workflow variable at runtime to support multi-tenant workflows where different callers authenticate with different Salesforce orgs.

## Example use case

After a voice agent completes a sales call, a workflow uses **SOQL Query** to look up the lead by phone number, then **Update Record** to log the call outcome — disposition, notes, and next steps — directly on the Salesforce lead record.

## Related

<CardGroup cols={2}>
  <Card title="Google Sheets" icon="table" href="01-Google-Sheets.md">
    Read and write data to Google Sheets spreadsheets.
  </Card>

  <Card title="Snowflake" icon="snowflake" href="02-Snowflake.md">
    Query data from Snowflake data warehouse.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/salesforce
