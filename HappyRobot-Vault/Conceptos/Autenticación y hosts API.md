---
tags: [happyrobot, concepto, api]
---

# Autenticación y hosts de la API

## Hosts (clústeres)

HappyRobot tiene **varios clústeres regionales** con la misma API pero datos distintos.
Una API key solo funciona en el clúster donde vive esa organización.

| Clúster | Base URL |
|---|---|
| Global / US | `https://platform.happyrobot.ai/api/v2` |
| **EU** ⭐ (el nuestro) | `https://platform.eu.happyrobot.ai/api/v2` |
| v1 legacy (solo lectura, 10 operaciones) | `https://platform.happyrobot.ai/api/v1` |

> 🔎 **Descubrimiento importante**: nuestra primera API key probada daba `"invalid or revoked
> API key"` en el host global. Probamos el host **EU** y ahí sí funcionó. Nuestra organización
> vive en `platform.eu.happyrobot.ai`. Si una key falla con "invalid or revoked", **antes de
> asumir que está mal, probar el otro clúster**.

## Autenticación

Header estándar Bearer token:

```
Authorization: Bearer <api_key>
```

Las keys tienen forma `sk_live_...`. Se generan desde **Settings > Profile > Generate API Key**
en la propia plataforma.

⚠️ Probamos otras variantes de header (`Authorization: <key>` sin Bearer, `x-api-key`,
`Authorization: Api-Key <key>`) y todas fallan con `"missing bearer token"`. Solo funciona el
formato `Bearer <key>`.

## Permisos por key

Cada API key tiene permisos propios dentro de la organización. Nos encontramos con:
- Una key que **podía leer** (`GET /workflows/`) pero **no crear** workflows → error
  `403 Forbidden — "Cannot create use cases"`.
- Otra key (segunda que nos dio el usuario) sí tenía permiso de creación.

→ Si algo falla con 403, probablemente sea un tema de permisos de la key, no de sintaxis.

## Dónde guardamos la key real

**Nunca en el repo ni en este vault.** Se pasa como variable de entorno al arrancar el
servidor:

```bash
export HAPPYROBOT_API_KEY=sk_live_...
```

Ver [[IDs y recursos]] para las keys usadas (redactadas) y [[Web app - server y frontend]]
para cómo se usa sin exponerla al navegador.

Relacionado: [[Endpoints usados]]
