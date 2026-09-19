# Organization

Ruta en la web: API Reference › Platform V2 API › Organization

4 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [Get current organization](01-Get-current-organization.md) | Returns basic information about the authenticated organization. |
| 2 | [List members of the current organization](02-List-members-of-the-current-organization.md) | Returns members of the authenticated organization, including public profile information and each member's workspace-wide role. The role is null when a member only has scoped access. |
| 3 | [Add a member to the current organization](03-Add-a-member-to-the-current-organization.md) | Adds a member to the authenticated organization by email. Internal users are added immediately; everyone else receives an email invitation to accept. Role must be editor or viewer (owners cannot be assigned via the API); defaults to viewer. |
| 4 | [Remove a member from the current organization](04-Remove-a-member-from-the-current-organization.md) | Removes a member from the authenticated organization, identified by email or user_id. Owners cannot be removed via the API. |

---

[← Volver](../README.md)
