---
title: "Navigating the platform"
description: "Find your way around the sidebar, tabs, and command menu"
---

# Navigating the platform

> Find your way around the sidebar, tabs, and command menu

The HappyRobot app is organized into three pieces of chrome that stay with you on every page: a **sidebar** for product areas and workspace resources, a **tab strip** for the pages you have open, and a **command menu** for jumping anywhere by keyboard.

<Note>
  Saved links and bookmarks keep working. The navigation changed, not the URLs behind it.
</Note>

## The sidebar

### Product areas

The top of the sidebar lists the products you have access to. You only see the ones your role permits.

| Area             | What lives there                                                                                                                                |
| ---------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Frontal**      | The standalone [Frontal](../02-Workflows/03-Frontal-AI-assistant.md) chat, for workspace conversations outside a specific workflow.                                     |
| **Workflows**    | Workflow analytics, [components](../14-Assets/02-Components.md), [voices](../14-Assets/04-Voices.md), and workflow settings such as global variables and scalability. |
| **Twin**         | The [Twin](../08-Twin/01-Twin-Overview.md) graph and SQL console, [knowledge bases](../14-Assets/01-Knowledge-Bases.md), and [contact intelligence](../13-Contacts/01-Contacts-Overview.md).   |
| **Interfaces**   | Your [apps](../07-Apps/01-Apps-Overview.md).                                                                                                                    |
| **Integrations** | Connected services and their credentials.                                                                                                       |

Selecting an area reveals its **sub-navigation** — the related views for that area — instead of scattering them across the whole app. Inside a workflow, the sub-navigation covers the editor, runs, experiments, evals (Northstars, custom tests, adversarial), and monitoring.

### Workspace resources

Below the product areas, the **Workspace** section is a single tree of everything you can open: workflows, apps, and components, either at the root or inside folders.

* Use the **filter** control to choose which resource types the tree shows — **Workflows**, **Components**, **Apps**. Your choice is remembered per workspace.
* Use the **+** control to create a workflow, prompt component, node component, app, or folder. Only the entries you have permission for appear.
* Drag a workflow, app, or component onto a folder to move it. Deleting a folder moves its contents up to the parent rather than deleting them.
* Your **Personal Playground** and, when relevant, **Others' Playgrounds** appear at the bottom of the tree.

When [Scope Tags](../16-Account-and-Settings/04-Scope-Tags.md) are enabled, resources inherit tags from the folder trail they sit in, and direct tags stay distinct from inherited ones. Moving a resource out of a folder asks whether to drop the tags it inherited there.

### Switching workspace

The workspace switcher at the bottom of the sidebar moves between the workspaces and parent organizations available to you.

## Tabs

Pages you open stay in a tab strip across the top of the app, so you can keep a run, an editor, and a dashboard side by side without losing your place.

* **Reorder** by dragging a tab.
* **Right-click** a tab for **Pin tab**, **Duplicate**, **Group**, **Rename**, **Icon**, and **Close tab**.
* **Pinned** tabs shrink to their icon and stay put; the close button becomes an unpin button.
* **Group** collects related tabs under a named, collapsible header. Choose **New group** or an existing one, and drag tabs in and out.
* **Rename** and **Icon** override the title and icon HappyRobot picks from the page. Choose **Based on location** to go back to the automatic one.

Tabs are saved to your account, so they survive a reload and follow you to another browser.

### Tab preferences

Configure how tabs behave under **Settings > Profile**:

| Preference                   | Description                                                                                                                                     |
| ---------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **App tabs**                 | Where open tabs are shared: **Show global tabs** (one set everywhere), **Tabs per parent org and child workspaces**, or **Tabs per workspace**. |
| **Reuse matching tabs**      | Switch to an already-open tab when its destination matches, instead of replacing the current tab.                                               |
| **Pin main navigation tabs** | Automatically pin main destinations and their listed views as you visit them.                                                                   |

## Command menu

Press <kbd>Cmd</kbd>+<kbd>K</kbd> (or <kbd>Ctrl</kbd>+<kbd>K</kbd>), or click the search icon in the sidebar header, to search across:

* **Recent** and **Open tabs**
* **Navigation** — every page you can reach
* **Workflows**, **Workspaces**, and **Parent organizations**
* **Create** — new workflow, workspace, knowledge base, API key, integration connection, or member invitation
* **Actions** and **Preferences** — copy the page URL, toggle the theme, toggle the sidebar, and change the tab preferences above
* **Help** — documentation and platform status

The menu only lists destinations and actions your role permits.

## Next steps

<CardGroup cols={3}>
  <Card title="Quickstart" icon="rocket" href="03-Quickstart.md">
    Build and run your first workflow.
  </Card>

  <Card title="Workflows" icon="diagram-project" href="../02-Workflows/01-Workflows-Overview.md">
    Learn the workflow builder.
  </Card>

  <Card title="Scope Tags" icon="tags" href="../16-Account-and-Settings/04-Scope-Tags.md">
    Control which resources each member sees.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/navigating-the-platform
