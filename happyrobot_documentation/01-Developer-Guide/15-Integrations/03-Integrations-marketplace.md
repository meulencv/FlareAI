---
title: "Integrations marketplace"
description: "Browse and connect hundreds of integrations through a single connection flow"
---

# Integrations marketplace

> Browse and connect hundreds of integrations through a single connection flow

The integrations marketplace gives you access to a wide range of external services — CRM systems, HR platforms, applicant tracking systems, accounting tools, ticketing systems, and file storage providers — through a single connection flow.

## How it works

When you connect a provider through the marketplace, HappyRobot handles the credential exchange and stores an account token on your behalf. Your workflows can then use that connection to read records, create entries, update data, and more — without any direct API keys or OAuth setup on your side.

## Browsing the marketplace

Open the marketplace from **Settings > Integrations**. You can filter integrations by:

* **Category** — Browse by type: CRM, HRIS, ATS, Accounting, Ticketing, or File Storage
* **Collections** — Featured, New Arrivals, Most Popular, and Enterprise curated lists
* **Search** — Filter by name

Each integration card shows:

* The provider logo and name
* Whether the integration is already connected
* A sync status badge once connected

## Connecting an integration

<Steps>
  <Step title="Open the integration card">
    Find the integration you want in the marketplace and click its card.
  </Step>

  <Step title="Start the connection flow">
    Click **Connect** to launch the guided connection flow. You'll be walked through authenticating with the provider — typically a standard OAuth handshake or credential entry form.
  </Step>

  <Step title="Grant access">
    Follow the prompts to sign in to the provider and authorize access. HappyRobot receives a token — no raw credentials are stored.
  </Step>

  <Step title="Use in workflows">
    Once connected, the integration appears as an action node option in the workflow editor. See [Using integrations in workflows](#using-integrations-in-workflows) below.
  </Step>
</Steps>

## Using integrations in workflows

Marketplace integrations appear as action nodes in the workflow editor alongside native integrations. Each connected provider supports a set of standard actions based on its category. To add an action, click **+** in the workflow editor, select the connected integration, choose an action, and configure its fields.

### List records

Retrieve a list of records from the connected system. Returns a paginated array of objects.

* **Credential** — the connected credential for this provider
* **Object type** — the type of record to list (for example, `Contact`, `Account`, or `Ticket`)
* **Filter** — optional filter expression to narrow results
* **Cursor** — optional pagination cursor for fetching subsequent pages

### Get record

Fetch a single record by ID.

* **Credential** — the connected credential
* **Object type** — the type of record to retrieve
* **Record ID** — the ID of the record

### Create record

Create a new record in the connected system.

* **Credential** — the connected credential
* **Object type** — the type of record to create
* **Fields** — key/value pairs for the record's fields. Supports workflow variables.

### Update record

Update an existing record by ID.

* **Credential** — the connected credential
* **Object type** — the type of record to update
* **Record ID** — the ID of the record to update
* **Fields** — key/value pairs for the fields to change

### Download file

Download a file from a file storage provider (SharePoint, OneDrive, etc.) and make it available as a workflow variable for downstream nodes.

* **Credential** — the connected credential
* **File ID** — the ID of the file to download

### Passthrough request

Send a raw API request to the provider's underlying API. Use this when the standard actions don't cover what you need.

* **Credential** — the connected credential
* **Method** — HTTP method (GET, POST, PATCH, DELETE)
* **Path** — provider-specific API path
* **Body** — optional JSON body

### Webhook trigger

Start a workflow when records change in a connected system — for example, when a new contact is created, an existing employee is updated, or a ticket is deleted. Requires that the provider supports webhooks.

* **Credential** — the connected credential
* **Common Model** — the standard record type to listen for (for example, `Contact`, `Employee`, or `Ticket`). Available models depend on the provider's category
* **Event Types** — which data changes trigger the workflow. Choose any combination of:
  * **Data Added** — a new record was created
  * **Data Changed** — an existing record was updated
  * **Data Removed** — a record was deleted

Records pushed by the provider are normalized to the marketplace's common model schema, so the same trigger configuration works across providers in the same category.

## All marketplace providers

The marketplace exposes the following providers, grouped by category. Expand a section to see the full list.

<AccordionGroup>
  <Accordion title="CRM">
    Accelo, ActiveCampaign, Affinity, Capsule, Close, Copper, HubSpot, Insightly, Keap, Microsoft Dynamics 365 Sales, Nutshell, Pipedrive, Pipeliner, Salesflare, SugarCRM, Teamleader, Teamwork CRM, Vtiger, Zendesk Sell, Zoho CRM.
  </Accordion>

  <Accordion title="HRIS">
    7shifts, ADP DECIDIUM, ADP Next Gen, ADP RUN, ADP Workforce Now, AllianceHCM, Altera Payroll, BambooHR, Breathe, Cezanne HR, Charlie HR, ChartHop, ClayHR, CoolCare, CyberArk, Darwinbox, Dayforce, Deel, Employment Hero, Factorial, Folks HR, Fourth, Freshteam, Generic SFTP, Google Workspace, Gusto, Hailey HR, HiBob, HR Cloud, HR Partner, HRWorks, Humaans, Humi, Insperity Premier, intelliHR, IRIS Cascade, iSolved, JumpCloud, Justworks, Kallidus, Keka, Kenjo, Lano, Leapsome, Lucca, Microsoft Entra ID, Namely, Nmbrs, Officient, Okta, OneLogin, Oracle HCM Cloud, OysterHR, PayCaptain, Paychex, Paycom, Paycor, PayFit, Paylocity, PeopleHR, Personio, PingOne, Planday, PrismHR, Proliant, Remote, Revolut People, Rippling, Sage HR, Sage People, SAP SuccessFactors, Sesame HR, Shapes, Simployer, Square Payroll, TriNet, TriNet HR Platform, UKG Pro, UKG Pro Workforce Management, UKG Ready, Zelt, Zoho People.
  </Accordion>

  <Accordion title="ATS (Applicant Tracking)">
    ApplicantStack, Ashby, Asymbl, Avature, Breezy, Bullhorn, Bullhorn Recruitment Cloud, CATS, Clockwork, Comeet, Cornerstone TalentLink, Crelate, d.Vinci, Easycruit, EngageATS, Eploy, Flatchr, Fountain, Freshteam ATS, Gem, Greenhouse, Greenhouse Job Board API, Harbour ATS, Homerun, iCIMS, Infinite BrassRing, JazzHR, JobAdder, JobDiva, JobScore, Jobsoid, Jobvite, JOIN, Lever, Manatal, Occupop, onlyfy, Oracle Fusion Recruiting Cloud, Oracle Taleo, Personio Recruiting, Pinpoint, Polymer, RecruiterFlow, Recruitive, SmartRecruiters, Taleez, TalentLyft, TalentReef, Teamtailor, Tellent Recruitee, Traffit, Tribepad, UKG Pro Recruiting, Welcome to the Jungle, Workable, Zoho Recruit.
  </Accordion>

  <Accordion title="Accounting">
    Clear Books, FreeAgent, FreshBooks, Microsoft Dynamics 365 Business Central, Microsoft Dynamics Finance & Operations, Moneybird, NetSuite, Oracle Fusion Cloud ERP, QuickBooks Desktop, QuickBooks Online, Sage Business Cloud Accounting, Sage Intacct, Wave Financial, Xero, Zoho Books.
  </Accordion>

  <Accordion title="Ticketing & Project Management">
    Aha!, Asana, Azure DevOps, Basecamp, Bitbucket, ClickUp, Dixa, Freshdesk, Freshservice, Front, GitHub Issues, GitLab, Gladly, Gorgias, Help Scout, Hive, HubSpot Service Hub, Intercom, Ironclad, Jira, Jira Data Center, Jira Service Management, Kustomer, Linear, Pivotal Tracker, Rally, Re:amaze, Salesforce Service Cloud, ServiceNow, Shortcut, SpotDraft, Teamwork, Trello, Wrike, Zendesk, Zoho BugTracker, Zoho Desk.
  </Accordion>

  <Accordion title="File Storage">
    Box, Dropbox, Google Drive, OneDrive, SharePoint.
  </Accordion>

  <Accordion title="Knowledge Base">
    Confluence, Notion.
  </Accordion>

  <Accordion title="Marketing">
    Customer.io, GetResponse, HubSpot Marketing Hub, Klaviyo, Mailchimp, MessageBird (Bird), Podium, SendGrid, Brevo (formerly Sendinblue).
  </Accordion>

  <Accordion title="Data Warehouse">
    Azure Synapse, Google BigQuery, Postgres, Amazon Redshift.
  </Accordion>
</AccordionGroup>

<Note>
  The marketplace catalog is updated regularly. The list above reflects the providers available at the time of writing — the in-product marketplace is always the source of truth.

  The marketplace only shows providers that are actually connectable for your organization, so a card you can see is a card you can complete the connection flow for. If a provider you expect is missing, contact support to have it enabled.
</Note>

## Notes

* **Salesforce** also has a dedicated in-house integration (found under **Data and Storage**) in addition to the marketplace version. Both are available.
* Sync status is shown on each connected integration card. If a sync stalls, you can force a re-sync from the integration's settings.
* Each marketplace integration shares a single credential per connected account. If you need to connect multiple accounts for the same provider, connect the integration multiple times.

## Next steps

<CardGroup cols={2}>
  <Card title="Credentials" icon="key" href="02-Credentials.md">
    Understand how credentials are stored and managed.
  </Card>

  <Card title="Integrations overview" icon="plug" href="01-Integrations-Overview.md">
    Learn how all integrations work in workflows.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/marketplace
