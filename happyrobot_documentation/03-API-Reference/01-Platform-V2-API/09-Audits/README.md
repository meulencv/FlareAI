# Audits

Ruta en la web: API Reference › Platform V2 API › Audits

10 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [List northstar audits for a workflow](01-List-northstar-audits-for-a-workflow.md) | Returns paginated northstar audit results for a workflow, showing pass/fail rates per behavioral criterion. |
| 2 | [List audit remarks for a northstar](02-List-audit-remarks-for-a-northstar.md) | Returns cursor-paginated audit remarks for a specific northstar criterion, optionally filtered by grade. |
| 3 | [List audit remarks for a workflow](03-List-audit-remarks-for-a-workflow.md) | Returns cursor-paginated behavioral audit remarks across all northstar criteria for a workflow. Optionally filter by northstar, grade, or status. |
| 4 | [List node errors for a workflow](04-List-node-errors-for-a-workflow.md) | Returns paginated node execution errors for a workflow, grouped by node and error type. |
| 5 | [Get audit stats for the live workflow version](05-Get-audit-stats-for-the-live-workflow-version.md) | Returns aggregate audit statistics for the live (or most recently audited) version of a workflow. |
| 6 | [List audited versions for a workflow](06-List-audited-versions-for-a-workflow.md) | Returns all versions of a workflow that have audit data, indicating which is the live version. |
| 7 | [Get an audit remark by ID](07-Get-an-audit-remark-by-ID.md) | Returns a single behavioral audit remark, including its northstar criterion, grade, correction, evaluated messages, and status. |
| 8 | [Get feedback for an audit remark](08-Get-feedback-for-an-audit-remark.md) | Returns the current caller's feedback for an audit remark, or null if none exists. Supports user-level and org-level API keys. |
| 9 | [Submit feedback for an audit remark](09-Submit-feedback-for-an-audit-remark.md) | Submit a thumbs up/down for an audit remark. Supports user-level and org-level API keys. A thumbs-up automatically adds the remark as a northstar example. |
| 10 | [Delete feedback for an audit remark](10-Delete-feedback-for-an-audit-remark.md) | Removes the current caller's feedback for an audit remark. Supports user-level and org-level API keys. |

---

[← Volver](../README.md)
