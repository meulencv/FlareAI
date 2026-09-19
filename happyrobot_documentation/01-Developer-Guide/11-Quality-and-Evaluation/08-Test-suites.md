---
title: "Test suites"
description: "Group prompt and adversarial tests into suites and run them together against a workflow version"
---

# Test suites

> Group prompt and adversarial tests into suites and run them together against a workflow version

A test suite is a shared container for the tests of a workflow. One suite can hold both [prompt tests](06-Custom-tests.md) and [adversarial tests](07-Adversarial-tests.md), so a release check that mixes the two runs as a single unit with one set of results and one run history.

Suites live on the workflow's **Tests** page, alongside the tests themselves.

## The Tests page

Open a workflow and go to **Evals > Tests**. Every test and suite for the workflow is listed in one table.

| Control                         | What it does                                                                                                                                                  |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Version picker**              | Selects the workflow version that tests run against and that the page's results are scoped to. Your selection follows you to the other pages of the workflow. |
| **Search**                      | Filters by test, prompt, or agent name.                                                                                                                       |
| **All / Prompt / Adversarial**  | Filters the table by test type. Each filter shows its own count.                                                                                              |
| **Group by workflow structure** | Toggles between a flat list and a tree that groups tests under the prompt or agent they target.                                                               |
| **New**                         | Creates a **Test**, a **Suite**, or a **Folder**.                                                                                                             |
| **Run**                         | Runs **All tests** or **Selected tests** against the selected version.                                                                                        |

Suites appear as expandable rows. Expand one to see its member tests, or select it to open its panel on the right.

### Running tests

The **Run** menu starts tests without opening them one at a time:

* **All tests** runs every test you have permission to run for the selected version.
* **Selected tests** switches the table into selection mode so you can tick individual tests, suites, or folders, then start just those.

Tests whose target prompt or agent doesn't exist in the selected version can't be started, and neither can tests in a suite that is still generating. When a suite is fully selected it runs as a suite — the results land in the suite's execution history instead of only on the individual tests.

## Creating a suite

Click **New > Suite** and pick how the suite gets its tests.

<Tabs>
  <Tab title="Manual">
    <Steps>
      <Step title="Choose Manual">
        Select **Manual** to build the suite from tests that already exist.
      </Step>

      <Step title="Name the suite">
        Give it a name — for example, "Release smoke checks" — and optionally a description of what it verifies and when you'd run it.
      </Step>

      <Step title="Pick member tests">
        Search the **Prompt** and **Adversarial** tests of the workflow and select the ones to include. A suite needs at least one member.
      </Step>

      <Step title="Create the suite">
        Click **Create suite**. The suite opens in the right panel.
      </Step>
    </Steps>
  </Tab>

  <Tab title="AI-assisted">
    <Steps>
      <Step title="Choose AI-assisted">
        Select **AI-assisted** to generate editable tests from your workflow and its northstars. This option requires northstar access.
      </Step>

      <Step title="Write a generation prompt">
        Describe what the suite should cover — for example, "Cover successful bookings, unavailable slots, and callers changing their minds."
      </Step>

      <Step title="Set the number and types of tests">
        **Number of tests** is the total across the selected types, up to 10; the model chooses the mix. Under **Test types**, enable **Prompt**, **Adversarial**, or both. A type that the selected version can't support is disabled.
      </Step>

      <Step title="Configure adversarial settings (if generating adversarial tests)">
        These settings are shared by every generated adversarial test:

        | Setting               | Description                                                                                                       |
        | --------------------- | ----------------------------------------------------------------------------------------------------------------- |
        | **Adversary model**   | The model that plays the simulated user.                                                                          |
        | **Environment**       | The environment whose configuration is used when the selected version runs — development, staging, or production. |
        | **Timeout (seconds)** | Time budget for each test, from 30 to 3600. Cleanup can continue briefly after the deadline.                      |
        | **Message guidance**  | Suggested maximum number of messages per adversary, from 1 to 100. The timeout is the hard stop.                  |
      </Step>

      <Step title="Choose the northstars to cover">
        Pick **All** enabled northstars, **Selected** northstars, or **By category**. Coverage guides what gets generated; it doesn't change how existing tests are graded.
      </Step>

      <Step title="Generate">
        Click **Generate tests**. Generation runs in the background against the version you had selected.
      </Step>
    </Steps>
  </Tab>
</Tabs>

### While generation runs

An AI-assisted suite shows a **Generating** badge and its tests appear as they finish. Tests in a generating suite can't be run yet. If generation fails, the suite's panel reports the error and offers **Retry generation**.

Generation runs once from the suite's configuration. After it finishes, edit the generated tests and the suite's membership by hand — regenerating isn't how you iterate on them.

## Managing membership

Membership changes never touch test definitions or run history:

* Adding a test that already belongs to another suite moves it; a test belongs to one suite at a time.
* Removing a test from a suite leaves the test in place.
* Deleting a suite leaves its tests in place. Delete tests individually from their own rows.

Use **Edit suite** in the suite's panel to change its name, description, members, and — for an AI-assisted suite — its northstar scope.

## Reviewing results

Select a suite to open its panel, which has three tabs.

| Tab            | What it shows                                                                                                                                                                                                         |
| -------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Overview**   | The suite's tests with their targets and types, plus the generation prompt, source version, and northstar scope for an AI-assisted suite.                                                                             |
| **Executions** | Every suite run, newest first, with its version, progress, and outcome summary — for example, `8 passed · 2 failed`. Open a run to see each test's outcome, and follow a result through to that test's own execution. |
| **Audits**     | The northstar grades produced by the selected execution, so you can see which criteria failed and why.                                                                                                                |

A running suite reports progress as its tests complete, and you can **Cancel** a suite run that's still in flight. Individual test outcomes use the same labels as the tests themselves — **Passed**, **Failed**, **Error**, **Timed out**, **Canceled**, or **N/A** when no grade applies.

### Filtering history

The filter button above an execution history narrows it down:

* **Version** — the current version only, or all versions
* **Outcome** — failed executions only, or all
* **Execution** — a specific suite run, when you're looking at a test that ran inside one

### Inspecting the workflow path

Generated suites store the workflow path their tests were built from. Use **View logic graph** on a suite or adversarial test to see that saved path as a diagram — it reflects the version the test was generated against, not today's draft.

## Suites through the API

Suites are also available in the [Platform API](https://docs.happyrobot.ai/api-reference/overview) and the [TypeScript SDK](../../02-Developer-Tools/02-TypeScript-SDK/11-Quality-and-testing.md#test-suites), including creating suites, changing membership, starting generation, running a suite, and reading results.

```ts theme={null}
const { suite } = await client.testSuites.create({
  useCaseId: "workflow-id",
  name: "Booking regression",
  members: [{ kind: "custom", id: "test-id" }],
});

const { suite_run_id } = await client.testSuites.run(suite.id, "version-id");
const { run, results } = await client.testSuites.results(suite_run_id);
```

## Next steps

<CardGroup cols={3}>
  <Card title="Prompt tests" icon="flask" href="06-Custom-tests.md">
    Test a single prompt node against expected responses and tool calls.
  </Card>

  <Card title="Adversarial tests" icon="user-secret" href="07-Adversarial-tests.md">
    Challenge an agent across a full conversation.
  </Card>

  <Card title="Northstars" icon="star" href="02-Northstars.md">
    Define the criteria that grade both kinds of test.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/evaluate/test-suites
