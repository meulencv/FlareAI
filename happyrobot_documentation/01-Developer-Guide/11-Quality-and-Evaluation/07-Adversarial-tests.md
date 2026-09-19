---
title: "Adversarial tests"
description: "Simulate a user challenging an agent across a full conversation and grade the result against northstars"
---

# Adversarial tests

> Simulate a user challenging an agent across a full conversation and grade the result against northstars

An adversarial test puts a simulated user in front of one of your agents and lets the conversation play out, then grades what the agent did against your [northstars](02-Northstars.md). Where a [prompt test](06-Custom-tests.md) checks a single response, an adversarial test checks how the agent holds up over a whole exchange — a caller who keeps changing their mind, one who pushes for information the agent shouldn't give, one who never answers the question asked.

Adversarial tests live on the workflow's **Tests** page, next to prompt tests, and can be grouped into [test suites](08-Test-suites.md).

## Creating a test

Open a workflow, go to **Evals > Tests**, and click **New > Test > Adversarial**. The workflow version you have selected supplies the agents you can target and the saved inputs the test starts from.

<Steps>
  <Step title="Pick the agent">
    Choose the agent under test. The simulated user talks to this agent.
  </Step>

  <Step title="Choose the execution scope">
    | Scope             | Behavior                                                                                                    |
    | ----------------- | ----------------------------------------------------------------------------------------------------------- |
    | **Agent only**    | Runs just the selected agent. Upstream nodes are skipped and their saved outputs are supplied as variables. |
    | **Full workflow** | Seeds the trigger, then every node executes for real.                                                       |

    <Warning>
      **Full workflow** runs real side effects — webhooks fire, integrations write, messages send. Point it at an environment where that's acceptable.
    </Warning>
  </Step>

  <Step title="Set the target environment">
    The run targets the deployed version for the environment you choose — development, staging, or production — not the editor draft.
  </Step>

  <Step title="Write the simulated participant prompt">
    Describe the persona and what they're trying to do: "Ask to book load L-7, then claim the rate was quoted \$200 higher." Pick the **Adversarial model** that plays this participant.
  </Step>

  <Step title="Choose the northstars to grade">
    Under **Northstars to grade**, grade against all enabled northstars or narrow to specific categories — **Notes**, **Style**, **Tool**, or **Sequential**.
  </Step>

  <Step title="Set the limits">
    **Opening message** is used only when your agent doesn't speak first. **Adversary message guidance** (1–100) suggests how many messages the simulated user should send; **Timeout (seconds)** (30–3600) is the hard stop.
  </Step>

  <Step title="Add additional participants (optional)">
    When the run can reach other agents, give each one its own persona prompt, model, and message limit. Only the agent under test can receive simulated inbound traffic, so the form warns you if a reachable agent is an inbound agent — a run that reaches it fails.
  </Step>

  <Step title="Review the seeded node outputs">
    The test stores a snapshot of the trigger and upstream node outputs it starts from. These values are saved with the test and don't follow later changes to their source; use **Refresh from source** to re-derive them from the current editor outputs or from the source run.
  </Step>

  <Step title="Create the test">
    Click **Create test**. Run it from the test's row or from the page's **Run** menu.
  </Step>
</Steps>

### Starting from a completed run

A test created from a completed run reuses that run's saved inputs, and its simulated participant prompt is reconstructed from the run transcript. **Restore** rebuilds that prompt from the transcript again if you've edited it and want to start over.

## Reviewing results

Select a test to open its panel.

| Tab          | What it shows                                                                                                                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Overview** | Run configuration (execution scope, adversarial model, timeout), the simulated participant instructions, the northstars being graded, additional participants, test inputs, and the saved workflow graph. |
| **Runs**     | Execution history, newest first, with the version each ran against. Open one for the full **Conversation** and a link to the **Workflow run** it produced.                                                |
| **Audits**   | The northstar grades for the selected execution, with the judge's reasoning and any corrections.                                                                                                          |

Executions report these outcomes:

| Status                                    | Meaning                                                                                      |
| ----------------------------------------- | -------------------------------------------------------------------------------------------- |
| **Queued** / **Running** / **Evaluating** | The run is in flight, or the conversation finished and grading is underway.                  |
| **Passed** / **Failed**                   | Grading finished with a verdict.                                                             |
| **Timed out**                             | The run hit its timeout.                                                                     |
| **Error**                                 | The run itself failed. **Audit error** means the conversation completed but grading did not. |
| **N/A**                                   | No grade applies.                                                                            |

Use the filter button above the history to limit it to the current version or to failed executions only.

## Adversarial tests through the API

Adversarial tests are available in the [Platform API](https://docs.happyrobot.ai/api-reference/overview) and the [TypeScript SDK](../../02-Developer-Tools/02-TypeScript-SDK/11-Quality-and-testing.md#adversarial-tests), including deriving seeds from a version, creating and editing tests, running them against an explicit version, and reading run history.

```ts theme={null}
const { scenario } = await client.e2eScenarios.create({
  targetUseCaseId: "workflow-id",
  targetAgentNodePersistentId: "agent-persistent-id",
  targetEnvironment: "production",
  mode: "agent_isolated",
  seeds: [],
  name: "Booking probe",
  adversarialPrompt: "Ask to book load L-7.",
});

await client.e2eScenarios.run(scenario.id, "version-id");
```

## Next steps

<CardGroup cols={3}>
  <Card title="Test suites" icon="layer-group" href="08-Test-suites.md">
    Group adversarial and prompt tests and run them together.
  </Card>

  <Card title="Northstars" icon="star" href="02-Northstars.md">
    Define the criteria adversarial runs are graded against.
  </Card>

  <Card title="Automated audits" icon="magnifying-glass" href="03-Automated-audits.md">
    How grading works and how to give feedback on it.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/evaluate/adversarial-tests
