---
title: "Get knowledge bases"
description: "List all knowledge bases for the organization."
---

# Get knowledge bases

> List all knowledge bases for the organization.



## OpenAPI

````yaml https://platform.happyrobot.ai/api/v2/docs/json get /knowledge-bases/
openapi: 3.0.3
info:
  title: Happyrobot Public API
  description: Public API endpoints for Happyrobot
  version: 0.1.1
servers:
  - url: https://platform.happyrobot.ai/api/v2
security:
  - bearerAuth: []
paths:
  /knowledge-bases/:
    get:
      tags:
        - Knowledge Bases
      description: List all knowledge bases for the organization.
      responses:
        '200':
          description: Default Response
components:
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: Opaque

````

---

Fuente original: https://docs.happyrobot.ai/api-reference/knowledge-bases/get-knowledge-bases
