# Billing

Ruta en la web: API Reference › Platform V2 API › Billing

4 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [Get usage totals](01-Get-usage-totals.md) | Returns the authenticated organization's total voice minutes, emails, and text messages between the inclusive start and end datetimes. Use Get usage details for the same usage grouped by workflow. |
| 2 | [Get usage details](02-Get-usage-details.md) | Returns the authenticated organization's voice minutes, emails, and text messages grouped by workflow between the inclusive start and end datetimes. Filter by one or more workflow IDs using repeated use_case_id parameters or a comma-separated list; omit the filter to include all workflows. |
| 3 | [Get credits](03-Get-credits.md) | Returns the authenticated organization's billable credit consumption by workflow for an inclusive date range, grouped daily, weekly, or monthly. Each row includes the period, full folder path, workflow identity, total credits, and the same L1 → L2 → L3 component breakdown shown in Settings → Usage,… |
| 4 | [Get run credits](04-Get-run-credits.md) | Returns credit consumption for a single run, broken down with the same L1 -> L2 -> L3 component taxonomy as Get credits (category -> subcomponents). Scoped to the authenticated organization via API key. |

---

[← Volver](../README.md)
