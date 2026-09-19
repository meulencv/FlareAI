# Knowledge Bases

Ruta en la web: API Reference › Platform V2 API › Knowledge Bases

7 páginas.

## Páginas

| # | Página | Descripción |
| --- | --- | --- |
| 1 | [Get knowledge bases](01-Get-knowledge-bases.md) | List all knowledge bases for the organization. |
| 2 | [Post knowledge bases](02-Post-knowledge-bases.md) | Create a new knowledge base for the organization. |
| 3 | [Get knowledge bases files](03-Get-knowledge-bases-files.md) | List all files in a knowledge base. Use this endpoint to check file processing status after triggering chunking via POST /:kbId/trigger-chunking. |
| 4 | [Post knowledge bases upload urls](04-Post-knowledge-bases-upload-urls.md) | Step 1 of the file upload flow. Creates file records in the database and returns presigned object-storage URLs (valid for 3 minutes). Upload each file using uploadUrl and send uploadHeaders when present, then call POST /:kbId/trigger-chunking with the returned fileIds to start processing. |
| 5 | [Post knowledge bases trigger chunking](05-Post-knowledge-bases-trigger-chunking.md) | Step 2 of the file upload flow. Call this endpoint after uploading files to object storage using the presigned URLs and any uploadHeaders from POST /:kbId/upload-urls. Triggers embedding generation for the specified files. Files will be available in the knowledge base within 10-15 minutes. Use GET /… |
| 6 | [Delete knowledge bases](06-Delete-knowledge-bases.md) | Delete a knowledge base and all associated files and chunks. This action is irreversible. |
| 7 | [Delete knowledge bases files](07-Delete-knowledge-bases-files.md) | Delete a file from a knowledge base. This removes the file from storage and deletes all associated chunks. This action is irreversible. |

---

[← Volver](../README.md)
