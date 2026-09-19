---
title: "Managing Tables"
description: "Create tables, columns, foreign keys, and views in your Twin database"
---

# Managing Tables

> Create tables, columns, foreign keys, and views in your Twin database

The Twin workspace is where you design your database schema and inspect your data. Open it from **Twin** in the sidebar.

<Note>
  Changing a table's shape — creating tables and views, editing columns, adding foreign keys, dropping tables — needs **Manage Twin schema**. Working with the contents of a table — inserting, editing, deleting, and importing rows — needs **Edit Twin data**. Controls you don't have permission for are hidden or read-only. See [Twin permissions](01-Twin-Overview.md#permissions).
</Note>

## Creating a table

<Steps>
  <Step title="Open the New Table sheet">
    Click **New Table** in the Twin workspace toolbar. A side sheet opens with the table-creation form.
  </Step>

  <Step title="Name the table">
    Table names must be lowercase, start with a letter or underscore, contain only letters, numbers, and underscores, and be at most 63 characters. Names cannot be changed after the table is created.
  </Step>

  <Step title="Define columns">
    Add a row per column. Each column has a name, a type, an optional default value, and an optional primary-key flag. Drag the handle to reorder. Two default columns are added for convenience:

    * **`id`** — `int8` primary key (auto-incrementing)
    * **`created_at`** — `timestamp` with default `now()`

    Remove or edit either if you don't want them.
  </Step>

  <Step title="(Optional) Add foreign keys">
    Expand **Foreign keys** to link columns in this table to columns in other tables. See [foreign keys](#foreign-keys) below.
  </Step>

  <Step title="Create the table">
    Click **Create**. The table is provisioned and appears in the Twin workspace immediately.
  </Step>
</Steps>

## Column types

| Type        | Description            | Common use                                           |
| ----------- | ---------------------- | ---------------------------------------------------- |
| `int8`      | 64-bit integer         | Auto-incrementing IDs, counts                        |
| `int4`      | 32-bit integer         | Smaller integers when range is bounded               |
| `float8`    | Double-precision float | Decimals, monetary values, measurements              |
| `float4`    | Single-precision float | Lower-precision decimals                             |
| `text`      | UTF-8 string           | Names, emails, descriptions, JSON-as-text            |
| `boolean`   | True/false             | Flags                                                |
| `timestamp` | Date and time          | Created/updated timestamps; supports `now()` default |
| `uuid`      | UUID                   | Stable cross-system identifiers                      |
| `jsonb`     | JSON value             | Structured payloads, free-form metadata              |

### Default values

Set a column's default in the **Default** field when creating or editing it. Common defaults:

* `now()` for `timestamp` columns
* `gen_random_uuid()` for `uuid` primary keys (auto-applied when you mark a `uuid` column as primary)
* Literal values like `0`, `''`, or `false`

`int8` primary keys automatically use `BIGSERIAL` so new rows get a generated ID — you don't need to set a default.

## Foreign keys

Foreign keys enforce referential integrity (a value in one table must exist in another) and let the Twin workspace draw relationships between tables on the canvas.

### Adding a foreign key

<Steps>
  <Step title="Open the Foreign keys section">
    Inside the **New Table** sheet, the **Edit Columns** sheet, or the table preview panel, expand the **Foreign keys** section.
  </Step>

  <Step title="Click Add foreign key">
    A side sheet opens with the foreign-key configuration.
  </Step>

  <Step title="Pick the source and target columns">
    Choose the column on the current table and the column on the referenced table. Types must match — the editor warns you if they don't.
  </Step>

  <Step title="Choose ON UPDATE and ON DELETE actions">
    | Action          | Behavior                                                               |
    | --------------- | ---------------------------------------------------------------------- |
    | **NO ACTION**   | Reject the change if dependent rows exist (default).                   |
    | **RESTRICT**    | Same as NO ACTION, evaluated immediately.                              |
    | **CASCADE**     | Propagate the update or delete to dependent rows.                      |
    | **SET NULL**    | Null out the source column. Requires the source column to be nullable. |
    | **SET DEFAULT** | Set the source column back to its default.                             |
  </Step>

  <Step title="Preview and apply">
    For an existing table, HappyRobot checks for orphan rows that would violate the constraint. If any are found, the constraint is **blocked** and a sample is shown — fix or remove the orphans in the [SQL console](05-SQL-Console-and-Capacity.md) and retry. For a draft table being created, the foreign key is recorded and applied when the table is created.
  </Step>
</Steps>

### Composite foreign keys

You can pair multiple source columns to multiple target columns in the same foreign key. Add columns in matching order on both sides — they're paired by index.

### Removing a foreign key

Open the table's **Foreign keys** section, click the foreign-key row, and choose **Remove**. The constraint is dropped from PostgreSQL immediately.

## Views

A view is a saved `SELECT` that appears alongside tables in the workspace. Views are read-only and useful for pre-canned queries, joins, and filtered projections that you want to query the same way you query a table.

<Steps>
  <Step title="Open the New View sheet">
    Click **New View** in the Twin workspace toolbar.
  </Step>

  <Step title="Name the view">
    View names follow the same rules as table names: lowercase letters, numbers, underscores, starting with a letter or underscore, max 63 characters.
  </Step>

  <Step title="Write the query">
    Enter a `SELECT` statement. The editor validates the syntax client-side and infers column names and types from the query.
  </Step>

  <Step title="Create">
    Click **Create**. The view appears in the workspace and can be queried via the [REST API](../15-Integrations/06-Data-and-Storage/07-Twin-database.md#bulk-insert-rows-via-api), [MCP](../../02-Developer-Tools/01-MCP/04-Twin-MCP.md), workflow nodes, or SQL console.
  </Step>
</Steps>

<Note>
  Views cannot be edited after creation. To change a view, drop it and recreate it with the new query.
</Note>

## Editing columns

Open a table and click **Edit columns** to open the schema editor.

You can:

* Add a column — name, type, optional default
* Remove a column — irreversible; data in that column is lost
* Rename a column — updates references in foreign keys automatically
* Change a default value
* Manage foreign keys (same as the New Table sheet)

If the table is a [polling table](03-Polling-Tables.md), you also see a **Polling configuration** section to view and adjust the polling interval.

## Inserting rows

Click **Insert row** on any table to open the row-creation form.

* Each editable column appears as an input matched to its type — `text` and `jsonb` use a textarea, `boolean` uses a toggle, etc.
* Auto-generated `int8` primary keys are shown as **Auto-generated** and are not editable.
* Required columns (`NOT NULL` without a default) are validated before save. Common errors:
  * *Column `x` is required and cannot be NULL*
  * *Value `y` for `x` already exists* (unique constraint)
  * *Invalid `<type>` value: `z`* (type mismatch)

If you leave changes unsaved, closing the sheet prompts you to discard them.

## Editing and deleting rows

In the table preview:

* Click the edit icon on a row to open the row editor for inline updates.
* Select rows with the row checkboxes for batch operations.
* Click **Delete** to remove the selected rows. A confirmation prompt is shown for destructive deletes.

For larger or scripted changes, use the [SQL console](05-SQL-Console-and-Capacity.md) instead.

## Importing data from CSV

Twin includes a CSV importer for bulk-loading rows into an existing table.

<Steps>
  <Step title="Open Import CSV">
    Open a table and click **Import CSV** in the toolbar. A side panel opens.
  </Step>

  <Step title="Upload a file">
    Drag and drop a `.csv` file or click to browse. The first row must be the header, and headers must match the table's column names.
  </Step>

  <Step title="Review the column match">
    The panel shows which CSV headers map to which table columns and surfaces any mismatches. Fix the header row in your CSV if needed and re-upload.
  </Step>

  <Step title="Import">
    Click **Import**. Rows are inserted in safely-sized batches with a live progress bar. Errors are surfaced with the row ranges and reason. You can cancel the import mid-process.
  </Step>
</Steps>

NULL values are handled per type — leave the cell blank to insert NULL for numeric, UUID, or timestamp columns.

## Table icons

Each table can show a custom icon on the Twin canvas, which is useful for grouping or differentiating tables visually.

<Steps>
  <Step title="Open the icon dialog">
    Click the icon next to a table title and choose **Change icon**.
  </Step>

  <Step title="Paste an HTTPS URL">
    The URL must use HTTPS and be at most 512 characters. The dialog previews the icon as you type.
  </Step>

  <Step title="Save">
    Click **Save**. The icon appears next to the table everywhere in the Twin workspace.
  </Step>
</Steps>

Click **Clear** in the same dialog to remove a custom icon.

## Dropping a table

Open the table, click the overflow menu, and choose **Drop table**. The confirmation dialog requires you to acknowledge that all rows in the table will be deleted.

<Warning>
  Dropping a table is irreversible. The table and all its data are removed immediately. Restore from a backup or rebuild the table from scratch if you need it back.
</Warning>

## Next steps

<CardGroup cols={3}>
  <Card title="Polling tables" icon="arrows-rotate" href="03-Polling-Tables.md">
    Tables that sync automatically from external APIs.
  </Card>

  <Card title="Workflow run dumps" icon="chart-line" href="04-Workflow-Run-Dumps.md">
    Auto-populate a table from workflow runs.
  </Card>

  <Card title="SQL console and capacity" icon="terminal" href="05-SQL-Console-and-Capacity.md">
    Run SQL queries and configure your database.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/twin/managing-tables
