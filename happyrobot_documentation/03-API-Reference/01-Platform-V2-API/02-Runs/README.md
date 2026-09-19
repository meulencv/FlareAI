# Runs

Ruta en la web: API Reference › Platform V2 API › Runs

10 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [\[Legacy\] List runs](01-Legacy-List-runs.md) | Lists runs for a use case. **Deprecated**: prefer GET /workflows/:workflow_id/runs instead. |
| 2 | [Cancel a run](02-Cancel-a-run.md) | Cancels a running or scheduled run for the caller's org by proxying to the workflows service. |
| 3 | [Get recordings for a run](03-Get-recordings-for-a-run.md) | Returns signed URLs for call recordings associated with a run. Optionally filter by session_id. |
| 4 | [List run sessions](04-List-run-sessions.md) | Returns paginated sessions for a run, ordered by timestamp. |
| 5 | [Get run](05-Get-run.md) | Returns metadata for a single run. Use /runs/:run_id/nodes for node summaries, /runs/:run_id/outputs/:output_id for a full node output payload, /runs/:run_id/sessions for session data, and /runs/:run_id/flags for issues. |
| 6 | [List run nodes](06-List-run-nodes.md) | Returns lightweight run node execution records in timestamp order. |
| 7 | [Get run output](07-Get-run-output.md) | Returns the full payload for a single output execution in a run. |
| 8 | [Mark run annotation](08-Mark-run-annotation.md) | Marks a run as correct, incorrect, or critical. When marked as incorrect or critical with a correction message, an issue is automatically created. |
| 9 | [List run flags](09-List-run-flags.md) | Returns paginated flags (issues) for a run, ordered by creation date. |
| 10 | [List audit remarks for a run](10-List-audit-remarks-for-a-run.md) | Returns all northstar audit remarks for a specific run, showing per-criterion pass/fail grades. |

---

[← Volver](../README.md)
