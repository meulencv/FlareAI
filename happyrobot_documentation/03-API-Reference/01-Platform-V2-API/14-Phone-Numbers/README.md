# Phone Numbers

Ruta en la web: API Reference › Platform V2 API › Phone Numbers

12 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [List phone numbers](01-List-phone-numbers.md) | Returns all phone numbers for the authenticated organization, including Twilio, Telnyx, and SIP trunk numbers with caller ID information. |
| 2 | [Purchase a phone number](02-Purchase-a-phone-number.md) | Purchases a new phone number from Twilio or Telnyx. For toll-free numbers (US/CA only), also submits toll-free verification. Rate limited to one purchase every 10 minutes per organization. Send force=true in the body to bypass this limit (use with caution — each number has a recurring monthly cost). |
| 3 | [Validate toll-free numbers for TextAgent](03-Validate-toll-free-numbers-for-TextAgent.md) | Validates toll-free phone numbers for use with TextAgent SMS. Outbound numbers are always valid. Inbound numbers are blocked if a live inbound TextAgent already uses them. |
| 4 | [Delete a toll-free verification](04-Delete-a-toll-free-verification.md) | Deletes a toll-free verification request by its SID. |
| 5 | [Free up a phone number](05-Free-up-a-phone-number.md) | Removes a phone number from all workflows it is assigned to. The phone number must not be used in any live version. |
| 6 | [Delete a phone number](06-Delete-a-phone-number.md) | Permanently deletes a phone number. The phone number must not be in use by any workflow. |
| 7 | [Get phone number usage](07-Get-phone-number-usage.md) | Returns usage information for a phone number across all workflows and versions. |
| 8 | [Remove phone number from a workflow](08-Remove-phone-number-from-a-workflow.md) | Removes a phone number from a specific workflow and version. The version must not be live. |
| 9 | [Get toll-free verification status](09-Get-toll-free-verification-status.md) | Returns toll-free verification status and submitted data for a phone number. Returns 204 when no verification exists. |
| 10 | [Submit toll-free verification](10-Submit-toll-free-verification.md) | Submits a toll-free verification request for a phone number. Requires business_name, notification_email, and sms_url. |
| 11 | [Create and attach SIP trunk](11-Create-and-attach-SIP-trunk.md) | Creates a SIP trunk and attaches it to a Twilio phone number. Sets up both inbound and outbound trunks in LiveKit. |
| 12 | [Update a phone number](12-Update-a-phone-number.md) | Updates the display name and caller ID setting for a phone number. |

---

[← Volver](../README.md)
