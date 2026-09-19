---
title: "Loops"
description: "Iterate over collections or repeat actions a fixed number of times"
---

# Loops

> Iterate over collections or repeat actions a fixed number of times

The Loop node repeats a sequence of workflow steps — either iterating over a collection of items or running a fixed number of times. Any combination of nodes can be placed inside the loop body.

## Configuration

### Mode

Choose how the loop determines its iterations:

* **Fixed count** — Run a set number of iterations
* **Collection** — Iterate over each item in an array

### Iterate for

*(Fixed count mode)* The number of times to repeat the loop body. Supports variables — type `@` to insert a dynamic count from a previous node.

### Iterate over

*(Collection mode)* A variable reference to an array. The loop runs once for each item in the array. Type `@` to select a variable.

For example, if a previous node outputs a list of phone numbers, select that output and the loop body executes once per phone number.

### Loop variable

The name used to reference the current iteration's item inside the loop body. Defaults to `iteration_element`.

Must match the pattern `[a-zA-Z_][a-zA-Z0-9_]*` (letters, numbers, and underscores, starting with a letter or underscore).

Inside the loop, type `@` in any field and select the loop variable name to access the current item.

### Execute in parallel

Toggle to run all iterations concurrently instead of sequentially.

* **Off (default)** — Iterations run one after another in order. Use when order matters or when calling rate-limited APIs.
* **On** — All iterations run at the same time. Use for independent operations where speed matters.

### Child runs

Toggle **Materialize each item as a child run** to run each iteration as a separate run instead of expanding the loop inline within the parent run. Each item produces its own child run with its own transcript, status, and outputs, which you can open and monitor independently in the [Runs](../09-Runs-and-Monitoring/01-Runs-Overview.md) table.

Use this for high-volume fan-out — for example, kicking off one run per item in a large list — where you want each iteration tracked, monitored, and retried independently.

* **Off (default)** — Iterations run inside the parent run, and outputs are collected back into the parent as [lists](#referencing-loop-results-outside-the-loop).
* **On** — Each iteration is dispatched as its own run. Child runs link back to the parent through the **Parent run** column in the runs table.

<Warning>
  When child runs are enabled, the loop is terminal in the parent run — **nodes placed after the Loop End do not run**, and the editor blocks attaching new nodes to the Loop End of a child-run loop. Because the iterations run as their own runs, the loop produces no in-graph output for downstream nodes to reference. Use this mode when each item should be handled as an independent execution rather than aggregated back into the parent.
</Warning>

## How loop variables work

Inside the loop body, the current iteration's item is available under the loop variable name. If your loop variable is `iteration_element`:

* **In collection mode:** `iteration_element` holds the current item from the array (could be a string, number, or object)
* **In fixed count mode:** `iteration_element` holds the current iteration index (starting from 0)

Reference the loop variable by typing `@` in any node field inside the loop and selecting it from the picker.

### Referencing loop results outside the loop

When a downstream node outside the loop references an output variable produced by a node inside the loop, that variable resolves to a **list** — one value per iteration. This applies to **both sequential and parallel loops**. A single-iteration loop still returns a one-item list, and sequential loops preserve iteration order.

The variable picker shows a blue `[]` suffix next to the variable name to indicate this, and variable groups that resolve to lists display a blue **List** badge in the picker header.

For example, if a node inside the loop produces a `result` variable and you reference it from a node after the Loop End, the variable resolves as a list `[result_iteration_1, result_iteration_2, ...]`.

Use an AI Generate node or custom code node after the loop to aggregate or process this list.

<Note>
  In the [public API and SDK](https://docs.happyrobot.ai/api-reference), variable groups that resolve as arrays are flagged with `is_list: true` on the available-variables endpoint.
</Note>

## Output schema generation

Loop nodes support output schema generation through the Testing Drawer, the same mechanism used for action and event nodes.

Click **Generate Output Schema** in the loop node's configure panel footer to open the Testing Drawer. Run the loop with sample data to capture its output structure. Once generated, downstream nodes can reference the loop's output variables using the `@` picker.

The button is disabled until the loop node is fully configured (mode, iteration source, and loop variable all set). Once a schema is generated, the button label changes to **View Output Schema**. You can regenerate it any time by running another test.

<Info>
  Without a generated schema, the loop node's outputs are not available in the variable picker for downstream nodes. Generate a schema after building and testing your loop body to unlock variable access.
</Info>

## Loop End

When you add a Loop node, a **Loop End** marker is automatically placed to define where the loop body ends. All nodes between the Loop node and Loop End are executed on each iteration. Nodes after Loop End continue with normal (non-looping) execution.

## Loop Break

A **Loop Break** node exits the loop early — when execution reaches it, the loop stops iterating immediately and the workflow continues from the Loop End. It works like a `break` statement in a programming language.

Add a Loop Break node inside the loop body (typically as the branch of a [Condition](09-Conditionals.md)) to stop looping as soon as a condition is met — for example, once you find a matching record or receive a successful response, instead of running every remaining iteration.

### Loop Break and parallel loops

A Loop Break only makes sense in a sequential loop — there is no "remaining iterations" to skip when every iteration already started at once.

You can still add a Loop Break inside a loop that has **Execute in parallel** switched on, so you can build the branch and flip the loop to sequential afterwards. The loop's configure panel flags the conflict while it exists:

> Parallel loops cannot contain Loop Break. Switch this loop to sequential execution to publish.

The conflict blocks [publishing](../02-Workflows/08-Versions-and-Publishing.md) until you either switch the loop to sequential execution or remove the Loop Break. This applies the same way in [Frontal](../02-Workflows/03-Frontal-AI-assistant.md) and through the [MCP server](../04-Tools/06-MCP-Server-Setup.md).

<Warning>
  A Loop Break node cannot be placed under a Paths node that uses the **evaluate all matching paths** policy. If a branch contains a Loop Break, that Paths node must route to a single path. The editor blocks switching such a Paths node to "evaluate all" while a Loop Break exists in its branches.
</Warning>

## Example

A previous node returns an array of 50 phone numbers to call. The Loop node iterates over the collection, and inside the loop body, an outbound voice agent node calls `iteration_element` (the current phone number) with a Schedule node adding a 2-second delay between iterations for rate limiting.

<Info>
  Loop nodes appear as a container in the workflow editor. Drag nodes into the loop body to include them in each iteration. The Loop End marker closes the container automatically.
</Info>

## Related

<CardGroup cols={2}>
  <Card title="Schedule" icon="clock" href="07-Schedule.md">
    Add delays between loop iterations for rate limiting.
  </Card>

  <Card title="Conditionals" icon="code-branch" href="09-Conditionals.md">
    Add branching logic inside loop bodies.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/core-nodes/loops
