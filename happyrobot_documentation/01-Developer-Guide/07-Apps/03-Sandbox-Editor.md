---
title: "Sandbox Editor"
description: "Edit your app with a live preview and an AI coding agent"
---

# Sandbox Editor

> Edit your app with a live preview and an AI coding agent

Opening an app for editing launches the **sandbox** — a temporary development environment that runs alongside your app's code. The sandbox includes a browser-based code editor, a live preview, and an AI coding agent that can read, write, and run commands on your behalf.

## Layout

The sandbox is divided into three panels:

| Panel                     | Purpose                                                                                                                                     |
| ------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------- |
| **Code editor** (left)    | Browse the file tree, edit source files, and search across the codebase. Syntax highlighting and standard keyboard shortcuts are available. |
| **Live preview** (center) | Renders your app from the sandbox's dev server. Reloads automatically as you save changes.                                                  |
| **Agent sidebar** (right) | A conversational AI coding agent. Ask it to make changes, explain code, or fix a failing build.                                             |

Press <kbd>Cmd</kbd>+<kbd>K</kbd> (or <kbd>Ctrl</kbd>+<kbd>K</kbd>) to toggle the agent sidebar.

## The dev server

The sandbox runs a development server (Next.js or Vite, depending on your template) so the preview updates as you edit. The server has a lifecycle of its own and the editor surfaces its state in real time.

| State                     | What it means                                                                                                                    |
| ------------------------- | -------------------------------------------------------------------------------------------------------------------------------- |
| `installing_deps`         | Running `npm install` after a fresh clone or a dependency change.                                                                |
| `starting`                | Booting the dev server.                                                                                                          |
| `running`                 | Dev server is up and the preview is live.                                                                                        |
| `restarting`              | Picking up a config change that requires a full restart.                                                                         |
| `stopped` / `idle`        | No dev server running.                                                                                                           |
| `crashed` / `deps_failed` | Something went wrong. The error message is shown in the editor — most issues are recoverable by asking the agent to take a look. |

You don't normally need to interact with the dev server directly. It starts automatically when you open the editor, restarts when needed, and stops when your session ends.

## The AI coding agent

Every sandbox includes an AI coding agent in the right-hand sidebar. The agent can read your repository, edit files, run shell commands, and trigger deploys — everything you can do, plus it has the build logs in context.

### What the agent can do

<CardGroup cols={2}>
  <Card title="Implement features" icon="wand-magic-sparkles">
    Describe what you want — a new page, a form, a data fetch — and the agent edits the relevant files for you.
  </Card>

  <Card title="Fix build failures" icon="screwdriver-wrench">
    When a build fails, the agent can read the build logs, find the cause, and apply a fix without you having to dig through stack traces.
  </Card>

  <Card title="Run commands" icon="terminal">
    Install packages, run formatters and linters, or execute one-off scripts — the agent can shell out inside the sandbox.
  </Card>

  <Card title="Answer questions" icon="circle-question">
    Ask "how does this auth flow work" or "where is the API client defined" and the agent navigates the codebase to answer.
  </Card>
</CardGroup>

### Working with the agent

* **Be specific about the outcome.** "Add a search bar to the contacts page that filters by name" works better than "make the contacts page better."
* **Iterate.** If the first attempt isn't right, follow up with corrections — the agent keeps the conversation in context.
* **Let it read the logs.** When something breaks, deploy and ask the agent to look at the latest build. It can read the full log and propose a fix.

### Attachments

You can attach files to a message — images, PDFs, screenshots of designs, or sample data — to give the agent more context. Each file can be up to 25 MB, and you can attach up to 10 files per message.

### Dictation

Click the **microphone** button in the agent's composer to dictate instead of typing. Recognized speech is appended to whatever is already in the message box, so you can mix typing and dictation, and click the button again (it turns into a stop button) when you're done. Dictation uses your browser's speech recognition, so it needs a browser that supports it — Chrome or Edge, for example. The button is disabled where it isn't available.

### Chat history

The agent keeps each conversation as its own chat. Use **New session** to start a fresh one — helpful when you switch to an unrelated task and don't want the previous context carried along — and **Session history** to reopen an earlier chat. The list is ordered most recently updated first, and each row shows the chat's title and when it was last updated, with a check mark on the one you're in.

From the list you can:

* **Switch** to a chat by clicking it — the agent picks that conversation back up where you left it.
* **Rename** it (pencil icon) — give the chat a name that says what it was for. Type the new name and press **Enter** to save, or **Escape** to cancel.
* **Delete** it (trash icon) — remove the chat and its history.

Renaming is worth doing once a chat covers real work — a list of chats named for the feature each one built is much easier to navigate a week later.

## Sessions

A sandbox session is tied to your editing window. While the session is active, the dev server runs, the agent has memory of your conversation, and your edits are stored in a working copy of the repository. Sessions expire after a period of idleness — reload the editor page to start a fresh session. Unpushed edits in an expired session are lost, so deploy or commit anything you want to keep.

<Tip>
  Treat the sandbox like an ephemeral working copy. Deploy regularly to keep your work safe — every deploy commits your changes to the managed GitHub repository.
</Tip>

## Next steps

<CardGroup cols={3}>
  <Card title="Deploy your changes" icon="rocket" href="05-Deploying.md">
    Commit and push from the sandbox.
  </Card>

  <Card title="Review build history" icon="clock-rotate-left" href="06-Build-History-and-Versioning.md">
    See past deployments and their logs.
  </Card>

  <Card title="Manage env vars" icon="lock" href="07-Environment-Variables.md">
    Add secrets and runtime config.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/apps/sandbox-editor
