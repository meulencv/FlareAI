---
title: "Quality and testing"
description: "Run test suites and adversarial tests, manage northstar criteria, custom evals, issues, and audit remarks"
---

# Quality and testing

> Run test suites and adversarial tests, manage northstar criteria, custom evals, issues, and audit remarks

Group tests into shared suites, challenge agents with adversarial tests, define quality criteria with northstars, and track issues across conversations.

## Test suites

A suite is a shared container for a workflow's tests. One suite can hold prompt tests (`kind: "custom"`) and adversarial tests (`kind: "e2e"`), run them together, and report their results as a single execution. See [Test suites](../../01-Developer-Guide/11-Quality-and-Evaluation/08-Test-suites.md).

| Method                         | HTTP                                   | Description                                                       |
| ------------------------------ | -------------------------------------- | ----------------------------------------------------------------- |
| `list(useCaseId)`              | `GET /test-suites/`                    | List the suites of a workflow                                     |
| `candidates(useCaseId)`        | `GET /test-suites/candidates`          | List tests that can be added to a suite                           |
| `create(body)`                 | `POST /test-suites/`                   | Create a suite, optionally with members or a generation config    |
| `get(suiteId)`                 | `GET /test-suites/:id`                 | Get a suite                                                       |
| `update(suiteId, body)`        | `PATCH /test-suites/:id`               | Update name, description, members, coverage, or generation config |
| `delete(suiteId)`              | `DELETE /test-suites/:id`              | Delete the suite, leaving its tests in place                      |
| `members(suiteId)`             | `GET /test-suites/:id/members`         | List the suite's member tests                                     |
| `membership(suiteId, body)`    | `PATCH /test-suites/:id/members`       | Attach or (with `detach: true`) remove members                    |
| `generate(suiteId, versionId)` | `POST /test-suites/:id/generate`       | Start AI generation for an `ai_assisted` suite                    |
| `run(suiteId, versionId)`      | `POST /test-suites/:id/run`            | Run every member test, returns `suite_run_id`                     |
| `runs(suiteId)`                | `GET /test-suites/:id/runs`            | List suite runs                                                   |
| `results(runId)`               | `GET /test-suites/runs/:runId`         | Get a suite run with per-test results                             |
| `cancel(runId)`                | `POST /test-suites/runs/:runId/cancel` | Cancel a suite run in flight                                      |

```ts theme={null}
const { suite } = await client.testSuites.create({
  useCaseId: "workflow-id",
  name: "Booking regression",
  members: [{ kind: "custom", id: "test-id" }],
});

// A test belongs to one suite at a time — attaching moves it
await client.testSuites.membership(suite.id, {
  members: [{ kind: "e2e", id: "scenario-id" }],
});

const { suite_run_id } = await client.testSuites.run(suite.id, "version-id");
const { run, results } = await client.testSuites.results(suite_run_id);
```

Generation runs once from the suite's `generationConfig` against a concrete version. After it succeeds, edit the generated definitions and the membership directly. A suite's coverage scope guides generation and does not override how existing tests are graded.

***

## Adversarial tests

Adversarial tests put a simulated user in front of one of your agents and grade the resulting conversation against northstars. Create and run them through `client.e2eScenarios`. See [Adversarial tests](../../01-Developer-Guide/11-Quality-and-Evaluation/07-Adversarial-tests.md).

| Method                       | HTTP                          | Description                                              |
| ---------------------------- | ----------------------------- | -------------------------------------------------------- |
| `list(useCaseId)`            | `GET /e2e-scenarios/`         | List the adversarial tests of a workflow                 |
| `create(body)`               | `POST /e2e-scenarios/`        | Create a test from structured seeds and a persona        |
| `get(scenarioId)`            | `GET /e2e-scenarios/:id`      | Get a test                                               |
| `update(scenarioId, body)`   | `PATCH /e2e-scenarios/:id`    | Update persona, model, scope, limits, or seeds           |
| `delete(scenarioId)`         | `DELETE /e2e-scenarios/:id`   | Delete a test                                            |
| `run(scenarioId, versionId)` | `POST /e2e-scenarios/:id/run` | Run against an explicit version, returns `scenarioRunId` |
| `runs(scenarioId, limit?)`   | `GET /e2e-scenarios/:id/runs` | List runs with their result state and audit remarks      |

```ts theme={null}
const { scenario } = await client.e2eScenarios.create({
  targetUseCaseId: "workflow-id",
  targetAgentNodePersistentId: "agent-persistent-id",
  targetEnvironment: "production",
  // "agent_isolated" runs only the agent; "whole_run" executes every node
  mode: "agent_isolated",
  seeds: [],
  name: "Booking probe",
  adversarialPrompt: "Ask to book load L-7.",
  // Optional: the simulated user's first message, used only when your agent
  // doesn't speak first
  openingMessage: "Hi, I need to update my account details",
  timeoutSeconds: 120,
});

await client.e2eScenarios.run(scenario.id, "version-id");
const { runs } = await client.e2eScenarios.runs(scenario.id);
```

<Note>
  `client.adversarialTests` and `client.adversarialSuites` are now read-only: they expose retained history — `get`, `listRuns`, `getRun`, `getRunMessages`, and `getEffectiveScope` — for tests created before the cutover. Creating, updating, and running go through `client.e2eScenarios` and `client.testSuites`.
</Note>

***

## Northstars

Quality criteria that define how the agent should behave, used to automatically grade conversations. Use these to set expectations for agent behavior and provide feedback to improve grading accuracy.

| Method                              | HTTP                              | Description                                                              |
| ----------------------------------- | --------------------------------- | ------------------------------------------------------------------------ |
| `get(northstarId)`                  | `GET /northstars/:id`             | Get a northstar                                                          |
| `update(northstarId, body)`         | `PATCH /northstars/:id`           | Update name, description, examples, category, priority, or enabled state |
| `delete(northstarId)`               | `DELETE /northstars/:id`          | Delete a northstar                                                       |
| `getHistory(northstarId)`           | `GET /northstars/:id/history`     | Get the full regeneration chain, oldest first                            |
| `submitFeedback(northstarId, body)` | `POST /northstars/:id/feedback`   | Rate correctness (-2 to +2), optionally trigger regeneration             |
| `deleteFeedback(northstarId)`       | `DELETE /northstars/:id/feedback` | Remove your feedback on a northstar                                      |

```ts theme={null}
const { northstar } = await client.northstars.get("northstar-id");
await client.northstars.update("northstar-id", {
  enabled: true,
  priority: "high",
});

const { history } = await client.northstars.getHistory("northstar-id");

// Rate a northstar (-2 = strongly wrong, +2 = strongly correct)
await client.northstars.submitFeedback("northstar-id", {
  correctness: 2,
  feedback: "This criterion is perfect.",
  trigger_regeneration: false,
});

await client.northstars.deleteFeedback("northstar-id");
```

***

## Custom evals

Test a specific prompt node against expected outputs or northstar criteria. Use these to define repeatable test cases for individual nodes and track their pass/fail history over time.

| Method                     | HTTP                         | Description                                                    |
| -------------------------- | ---------------------------- | -------------------------------------------------------------- |
| `get(evalId)`              | `GET /custom-evals/:id`      | Get a custom eval                                              |
| `update(evalId, body)`     | `PATCH /custom-evals/:id`    | Update messages, expected outputs, variables, or northstar IDs |
| `delete(evalId)`           | `DELETE /custom-evals/:id`   | Delete a custom eval                                           |
| `run(evalId, body)`        | `POST /custom-evals/:id/run` | Execute the eval, returns `run_id`                             |
| `listRuns(evalId, query?)` | `GET /custom-evals/:id/runs` | List runs with pass/fail and judge reasoning                   |

```ts theme={null}
const { test } = await client.customEvals.get("eval-id");
await client.customEvals.update("eval-id", {
  name: "Greeting check",
  expected_response: "Hello, how can I help you?",
});

const { run_id } = await client.customEvals.run("eval-id", {
  version_id: "v-id",
});

const { runs } = await client.customEvals.listRuns("eval-id");
```

***

## Issues

Quality issues (flags) raised when a conversation fails a northstar or quality check. Use this to triage and resolve flagged conversations.

| Method                  | HTTP                | Description                                                       |
| ----------------------- | ------------------- | ----------------------------------------------------------------- |
| `update(issueId, body)` | `PATCH /issues/:id` | Update issue status (`open` / `approved` / `rejected` / `closed`) |

```ts theme={null}
await client.issues.update("issue-id", { status: "approved" });
```

***

## Audit remarks

Individual northstar grades attached to a conversation. Feedback on audit remarks improves future grading accuracy by providing signal on whether the automated grade was correct.

| Method                                | HTTP                                 | Description                                                             |
| ------------------------------------- | ------------------------------------ | ----------------------------------------------------------------------- |
| `getFeedback(auditRemarkId)`          | `GET /audit-remarks/:id/feedback`    | Get the calling identity's feedback for this remark, or `null`          |
| `submitFeedback(auditRemarkId, body)` | `POST /audit-remarks/:id/feedback`   | Submit thumbs up/down; thumbs-up adds the remark as a northstar example |
| `deleteFeedback(auditRemarkId)`       | `DELETE /audit-remarks/:id/feedback` | Delete the calling identity's feedback                                  |

All three endpoints accept both **user-level and org-level** [API keys](../../01-Developer-Guide/16-Account-and-Settings/06-API-Keys.md), so automation can submit feedback without a key tied to a person. Feedback is scoped to whichever identity created it: a user key sees and replaces the feedback of that user, and an org key sees and replaces the feedback of that key.

The returned feedback object records which identity created it, and exactly one of the two fields is set:

| Field                | Set when                                                                                      |
| -------------------- | --------------------------------------------------------------------------------------------- |
| `created_by`         | The feedback was submitted with a user-level key (or from the platform UI). `null` otherwise. |
| `created_by_api_key` | The feedback was submitted with an org-level key. `null` otherwise.                           |

```ts theme={null}
const feedback = await client.auditRemarks.getFeedback("audit-remark-id");

// Thumbs up
await client.auditRemarks.submitFeedback("audit-remark-id", {
  polarity: true,
});

// Thumbs down with attribution
await client.auditRemarks.submitFeedback("audit-remark-id", {
  polarity: false,
  issue_attribution: "northstar",
  comment: "The northstar criteria was wrong here.",
});

await client.auditRemarks.deleteFeedback("audit-remark-id");
```

---

Fuente original: https://docs.happyrobot.ai/developer-tools/sdk/quality
