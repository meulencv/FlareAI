---
title: "Google Sheets"
description: "Read and write data to Google Sheets"
---

# Google Sheets

> Read and write data to Google Sheets

The Google Sheets integration lets your workflows read from and write to Google Sheets spreadsheets. Query rows, append data, update cells, and delete records — all with dynamic spreadsheet and worksheet selection.

## Authentication

Google Sheets uses OAuth for authentication. You'll be redirected to Google's sign-in page to authorize access to your spreadsheets.

<Steps>
  <Step title="Enable the Google Sheets integration">
    Go to **Settings > Integrations** and enable **Google Sheets**.
  </Step>

  <Step title="Add a credential">
    Click **Add Credential**. You'll be redirected to Google's authorization page.
  </Step>

  <Step title="Grant permissions">
    Sign in with the Google account that has access to the spreadsheets you want to use, and approve the requested permissions (Google Drive and user info access).
  </Step>

  <Step title="Verify the connection">
    After redirecting back, the credential will appear as **Active**. Your spreadsheets will be available for selection in workflow nodes.
  </Step>
</Steps>

## Available events

### Actions

| Event              | Description                                   |
| ------------------ | --------------------------------------------- |
| **Get All Rows**   | Retrieves all rows from a worksheet           |
| **Get Rows**       | Retrieves rows matching specified criteria    |
| **Append Row**     | Adds a new row to the end of a worksheet      |
| **Update Row**     | Updates an existing row by row number         |
| **Update Columns** | Updates specific columns across multiple rows |
| **Delete Row**     | Deletes a row from a worksheet                |

## Dynamic selections

When configuring Google Sheets events in the workflow editor, spreadsheets, worksheets, and columns are loaded dynamically from your Google account. Select from dropdown lists rather than entering IDs manually.

<Tip>
  Use **Get Rows** with filter criteria to find specific records, then pass the row data to downstream nodes for processing. This is useful for looking up customer information, rate data, or configuration values stored in spreadsheets.
</Tip>

## Example use case

After a voice agent completes a carrier call, the workflow uses **Append Row** to log the call details — carrier name, MC number, rate offered, and disposition — to a shared Google Sheet that the brokerage team reviews daily.

## Related

<CardGroup cols={2}>
  <Card title="Snowflake" icon="snowflake" href="02-Snowflake.md">
    Query data from Snowflake data warehouse.
  </Card>

  <Card title="Redis" icon="database" href="03-Redis.md">
    Key-value caching and storage with Redis.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/integrations/data/google-sheets
