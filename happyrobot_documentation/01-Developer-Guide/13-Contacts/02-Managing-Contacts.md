---
title: "Managing Contacts"
description: "Create, update, and organize contacts"
---

# Managing Contacts

> Create, update, and organize contacts

The **Contacts** page gives you a searchable, filterable view of every person your agents have interacted with. From here you can review contact details, manage tags and attributes, block contacts from specific workflows, and delete records you no longer need.

## How contacts are created

Contacts are created automatically — there is no manual creation flow. When an agent interacts with a phone number or email address that doesn't yet exist in your organization, HappyRobot creates a new contact record. If the contact already exists, the interaction is linked to the existing record.

Deduplication is enforced by a unique constraint on `org_id`, `type`, and `value`. This means each phone number or email address has exactly one contact record per organization.

You can also look up contacts programmatically using the `GET /contacts/resolve` API endpoint, which normalizes the identifier and returns the matching contact if one exists.

## The contacts list

The contacts list is a table showing all contacts for your organization. It uses cursor-based pagination with infinite scroll — new contacts load automatically as you scroll down.

| Column               | Description                                                                                             |
| -------------------- | ------------------------------------------------------------------------------------------------------- |
| **Contact**          | The phone number or email address                                                                       |
| **Interactions**     | Per-channel interaction counts, shown as icon badges (call, SMS, WhatsApp, Gmail, Outlook)              |
| **Tags**             | Color-coded tag badges extracted by AI, plus a **Blocked** badge if the contact has any workflow blocks |
| **Contact summary**  | AI-generated summary of the contact across all interactions                                             |
| **Last interaction** | Timestamp of the most recent communication event                                                        |

Click any row to open the contact details sidebar on the right side of the screen.

## Searching contacts

Use the search bar at the top of the contacts page to filter by phone number or email address. Search is case-insensitive and filters the list in real time as you type.

## Filtering contacts

Click the **Filter** button to access the filter dropdown. Filters can be combined and active filters appear as badges below the search bar, each with a clear button.

<AccordionGroup>
  <Accordion title="Interactions range">
    Filter contacts by their total interaction count. Set a minimum and/or maximum number of interactions to find highly active contacts or contacts with only a single touchpoint.
  </Accordion>

  <Accordion title="Last interaction date">
    Restrict the list to contacts whose most recent interaction falls within a date range. Use the **From** and **To** date pickers with time selection to narrow results to a specific window.
  </Accordion>

  <Accordion title="Tags">
    Filter by one or more tags. The tag filter includes a searchable dropdown with autocomplete — type to find tags and select multiple. Only contacts with at least one matching tag are shown.
  </Accordion>

  <Accordion title="Block status">
    Filter contacts by block status: **All**, **Blocked**, or **Not blocked**. Blocked contacts are those with at least one workflow block entry.
  </Accordion>
</AccordionGroup>

## Contact details sidebar

Click a contact row to open the details sidebar. The sidebar displays:

* **Contact value** — phone number or email address
* **Total interactions** — count across all channels
* **First and last interaction dates**
* **Associated workflows** — clickable badges showing which workflows this contact has interacted with
* **Extracted attributes** — key-value pairs extracted by AI, editable inline
* **Memories** — list of AI-extracted knowledge snippets (deletable individually)
* **Contact summary** — AI-generated overview of the contact
* **Interactions list** — searchable list of all communication events with timestamps and channel icons

## Editing extracted attributes

Extracted attributes are key-value pairs that AI pulls from conversations — such as a company name, MC number, or preferred language. You can edit attribute values directly in the sidebar:

1. Click on an attribute value to enter edit mode.
2. Modify the value and press **Enter** to save.
3. Press **Escape** to cancel without saving.

To delete an attribute, click the delete icon next to it.

## Blocking contacts

Blocking prevents specific workflows from targeting a contact in outbound campaigns. Blocks are per-workflow — you can block a contact from one workflow while leaving it available for others.

<Steps>
  <Step title="Open the block dialog">
    In the contact details sidebar, click the **Block** button (or **Unblock** if the contact already has blocks).
  </Step>

  <Step title="Select workflows">
    Choose one or more workflows to block the contact from. The dialog shows all workflows in your organization.
  </Step>

  <Step title="Add a reason (optional)">
    Enter an optional reason for the block. This is stored for audit purposes.
  </Step>

  <Step title="Save">
    Click **Save** to apply the blocks. The contact's **Blocked** badge appears in the contacts list and the `is_blocked` flag is set to `true`.
  </Step>
</Steps>

<Info>
  Blocking a contact does not delete any data. The contact record, interactions, and memories are preserved. The block only prevents the selected workflows from initiating new outbound interactions with this contact.
</Info>

To unblock, open the block dialog again and deselect the workflows you want to unblock. Removing all workflow blocks clears the **Blocked** badge and resets `is_blocked` to `false`.

## Deleting contacts

Deleting a contact permanently removes the contact record. This action cannot be undone.

<Steps>
  <Step title="Open the contact sidebar">
    Click the contact row to open the details sidebar.
  </Step>

  <Step title="Open the menu">
    Click the ellipsis menu (**...**) in the sidebar header.
  </Step>

  <Step title="Confirm deletion">
    Select **Delete** and confirm in the dialog. The contact, all associated memories, and block entries are permanently removed. Interaction records (communication events) are preserved but their contact reference is cleared.
  </Step>
</Steps>

<Warning>
  Deleting a contact cascades to memories and block list entries. Communication events are not deleted but their `contact_id` is set to null. This action is irreversible.
</Warning>

## API access

You can manage contacts programmatically using the v2 REST API. See the [API Reference](https://docs.happyrobot.ai/api-reference/overview) for full details.

| Endpoint                                  | Description                                             |
| ----------------------------------------- | ------------------------------------------------------- |
| `GET /contacts/`                          | List contacts with search, pagination, and filters      |
| `GET /contacts/resolve`                   | Look up a contact by type and value                     |
| `GET /contacts/{contact_id}`              | Get a single contact with interaction and memory counts |
| `GET /contacts/{contact_id}/interactions` | List interactions for a contact                         |
| `GET /contacts/{contact_id}/memories`     | List memories for a contact                             |

## Next steps

<CardGroup cols={3}>
  <Card title="Interaction history" icon="clock-rotate-left" href="03-Interaction-History.md">
    Explore past conversations, channels, and tags.
  </Card>

  <Card title="Memories" icon="brain" href="04-Memories.md">
    Configure AI memory extraction and context injection.
  </Card>

  <Card title="Contacts API" icon="code" href="https://docs.happyrobot.ai/api-reference/overview">
    Access contacts programmatically via the REST API.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/contacts/managing-contacts
