---
title: "Quality and evaluation overview"
description: "Define quality standards, automatically audit runs, and continuously improve agent behavior"
---

# Quality and evaluation overview

> Define quality standards, automatically audit runs, and continuously improve agent behavior

HappyRobot's quality and evaluation system helps you define what good agent behavior looks like, automatically check every run against those standards, and surface issues before they impact your customers. The system creates a continuous improvement loop:

1. **Define standards** — Write [northstars](02-Northstars.md) that describe expected agent behavior
2. **Audit runs** — Every run is [automatically evaluated](03-Automated-audits.md) against your northstars by an LLM judge
3. **Surface issues** — Failed audits and quality flags generate [issues](05-Issues.md) for review
4. **Test changes** — Validate prompt updates with [prompt tests](06-Custom-tests.md) and [adversarial tests](07-Adversarial-tests.md) before publishing, grouped into [test suites](08-Test-suites.md)

## Where to find it

The quality system lives in the workflow's sidebar:

* **Evals > Northstars** — Define the behavioral standards your agents are graded against
* **Evals > Tests** — Create and run [prompt tests](06-Custom-tests.md), [adversarial tests](07-Adversarial-tests.md), and [test suites](08-Test-suites.md), in one place
* **Monitor > Northstar Audits** — Review automated audit results, node errors, and quality flags

## Getting started

Start by defining northstars for your most important agent behaviors, then let the automated audit system evaluate your runs.

<CardGroup cols={2}>
  <Card title="Northstars" icon="star" href="02-Northstars.md">
    Define behavioral quality criteria that your agent should follow.
  </Card>

  <Card title="Automated audits" icon="magnifying-glass" href="03-Automated-audits.md">
    See how every run is automatically evaluated against your northstars.
  </Card>

  <Card title="Issues" icon="flag" href="05-Issues.md">
    Track and resolve quality problems surfaced by audits and flags.
  </Card>

  <Card title="Custom tests" icon="flask" href="06-Custom-tests.md">
    Create test cases with expected conversation flows and tool calls.
  </Card>

  <Card title="Adversarial tests" icon="user-secret" href="07-Adversarial-tests.md">
    Challenge an agent across a full conversation with a simulated user.
  </Card>

  <Card title="Test suites" icon="layer-group" href="08-Test-suites.md">
    Group prompt and adversarial tests and run them together.
  </Card>
</CardGroup>

---

Fuente original: https://docs.happyrobot.ai/evaluate/overview
