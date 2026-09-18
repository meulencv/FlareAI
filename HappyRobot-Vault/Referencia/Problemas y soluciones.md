---
tags: [happyrobot, referencia, troubleshooting]
---

# Problemas y soluciones

## 1. `"invalid or revoked API key"`
**Causa real**: la key era válida pero pertenecía a la org del clúster **EU**, y estábamos
llamando al host global (`platform.happyrobot.ai`).
**Solución**: probar con `platform.eu.happyrobot.ai`. Ver [[Autenticación y hosts API]].

## 2. `"missing bearer token"`
**Causa**: header de auth mal formado. Probamos `Authorization: <key>`, `x-api-key: <key>`,
`Authorization: Api-Key <key>` — ninguno funciona.
**Solución**: solo `Authorization: Bearer <key>`.

## 3. `403 Forbidden — "Cannot create use cases"`
**Causa**: la API key no tenía permiso de creación de workflows (permiso por key, no por org).
**Solución**: usar otra key con más permisos (la segunda que nos dio el usuario).

## 4. `400 Bad Request — "Required credentials for template \"voice-agent\" are not configured..."`
**Causa**: el template `voice-agent` (llamadas **salientes** reales) necesita un SIP trunk
configurado en la organización, que no existe.
**Solución**: usar `inbound-voice-agent` en su lugar — no necesita credenciales de telefonía y
encaja con el objetivo real ("solo web call, no teléfono"). Ver [[Templates de workflow]].

## 5. `400 Bad Request — "Cannot update nodes on a locked version. Unlock or fork the version first."`
**Causa**: intentamos editar un nodo (`PUT /versions/{v}/nodes/{n}`) de una versión que ya
estaba **publicada** → publicar bloquea la versión.
**Solución**: `unpublish` el workflow → `unlock` la versión → editar el nodo → `publish` de
nuevo. Documentado paso a paso en [[FlareAI Web Voice - workflow]].

## 6. Voz/idioma por defecto en inglés
**Causa**: el template `inbound-voice-agent` no expone `language`/`voice` como input directo
al crear — hay que editarlo después en el nodo `agent`.
**Solución**: `PUT` el nodo "Inbound Voice Agent" con `agent.voices`, `agent.languages`,
`agent.language_accents` apuntando a una voz es-ES (ver [[Catálogo de voces]]).

## 7. `docs.happyrobot.ai` bloqueada
**Causa**: la documentación oficial pide un código de acceso.
**Solución**: usar el OpenAPI público sin auth en
`https://platform.happyrobot.ai/api/v2/docs/json` (ver [[Endpoints usados]]).

Relacionado: [[Workflows y nodos]] · [[Autenticación y hosts API]]
