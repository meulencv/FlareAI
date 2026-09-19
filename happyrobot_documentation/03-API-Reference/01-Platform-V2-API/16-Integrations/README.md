# Integrations

Ruta en la web: API Reference › Platform V2 API › Integrations

5 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [List integrations](01-List-integrations.md) | Returns available integrations with optional events and credentials. Delegated providers (CRM, HRIS, ATS, etc.) are expanded into individual entries. Supports filtering by category, provider, and search. Paginated (default: 20 per page). |
| 2 | [List integration categories with providers](02-List-integration-categories-with-providers.md) | Returns a unified map of categories to their available providers. Includes both internal integration groups (Communications, Data, etc.) and delegated provider categories (CRM, HRIS, ATS, etc.). |
| 3 | [Get an integration](03-Get-an-integration.md) | Returns a single integration by ID, including its events and the organization's connected credentials. Supports both native integration UUIDs and delegated provider composite IDs (e.g. {uuid}--{provider_slug}). |
| 4 | [Create a credential for an integration](04-Create-a-credential-for-an-integration.md) | Creates a new credential for a form-based integration. OAuth integrations are not supported via API — use the HappyRobot platform UI instead. |
| 5 | [Update a credential for an integration](05-Update-a-credential-for-an-integration.md) | Replaces an existing form-based credential's title and data while preserving its ID and workflow references. Send the same complete payload as credential creation, including all required data fields. If credential_type is omitted, the integration's default type is used; send it explicitly for a non-… |

---

[← Volver](../README.md)
