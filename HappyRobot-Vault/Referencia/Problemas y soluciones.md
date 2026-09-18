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

## 8. `404 "Twin database not available"` y `403 "API key cannot perform action twin.manage"`
**Causa**: Twin no está provisionado en la org, y la key no tiene permiso de gestión de Twin.
**Solución**: activar Twin en Settings → Twin Database; crear key con *Full Twin access*. Mientras
tanto, Postgres embebido local con la misma interfaz ([[Base de datos local embebida]]).

## 9. `400 "Body cannot be empty when content-type is set to 'application/json'"`
**Causa**: `POST /versions/{v}/unlock` (y similares) sin cuerpo.
**Solución**: el cliente envía siempre `{}` en POST/PUT/PATCH/DELETE.

## 10. `400 "Cannot add nodes to a locked version"`
**Causa**: igual que #5 pero al añadir nodos. **Solución**: `unpublish` + `unlock` antes de tocar nodos (automático en `sos deploy`).

## 11. Objetos anidados llegan como `map[n:3 text:veo humo]`
**Causa**: los valores de variables se serializan como texto; los objetos usan el formato de Go.
**Solución**: sobres planos; JSON strings para lo estructurado; rutas con punto (`payload.text`).

## 12. `{{$var:…}}` no se resuelve en `prompt_md`
**Causa**: el prompt usa otra sintaxis. **Solución**: `{{<node_id>.<campo>}}` (`Prompt()` en el DSL).

## 13. Un `path` creado solo trae "Path 1" y "Fallback" (incompletos) → `Cannot publish: some nodes have incomplete configuration`
**Solución**: borrar los hijos automáticos del path justo después de crearlo (lo hace el deployer).

## 14. `iterate_over: expected string, received object`
**Solución**: en el Loop, `iterate_over` es un string `{{$var:<node>.rows}}`.

## 15. Los tools bloquean el publish hasta abrir su "Tool Call Result"
**Solución**: `POST …/tools/{t}/tool-call-result/generate` + `PUT …/visibility {node_id, exposed_fields}`.

## 16. Empates de `observed_at` en la simulación (todo ocurre en el mismo segundo)
**Causa**: `now_iso` sin milisegundos → la observación meteo nueva no ganaba a la vieja.
**Solución**: ordenar por `observed_at DESC, created_at DESC` en todas las consultas.

## 17. Instalé Postgres con Homebrew fuera del proyecto (error de proceso)
**Causa**: no había Postgres ni Docker; instalé `postgresql@17` globalmente. El usuario exige que
todo viva en la carpeta. **Solución**: `brew uninstall` + `brew autoremove` y binarios embebidos en
`.local/pg` (zonky). Regla para el futuro: nada fuera del repo/venv.

## 18. La API key del llamador queda en `__headers__` de la salida del trigger
**Observación** (seguridad): al disparar un run vía `POST /workflows/{id}/runs` o hook, la cabecera
`Authorization` completa se guarda en los datos del run (visible en la plataforma). Otra razón para
rotar las keys tras el hackathon y no compartir runs.

Relacionado: [[Workflows y nodos]] · [[Autenticación y hosts API]] · [[Formato de nodos por API]] · [[Twin - base de datos]]
