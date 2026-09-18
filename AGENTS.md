# AGENTS.md — FlareAI

Instrucciones para cualquier agente IA (Claude Code, Cursor, Codex CLI, etc.) que trabaje en
este repositorio.

## Proyecto

**S.O.S. Agentic Crisis Engine** (HackSpain 2026, reto HappyRobot): gestión autónoma de crisis
sobre HappyRobot. Lee primero `HappyRobot-Vault/00 Índice.md` y `README.md`.

- `sos/` — todo lo que vive en HappyRobot, como código: cliente API (`happyrobot/`), esquema Twin y
  seed (`twin/`), los 9 workflows + DSL + deployer (`workflows/`), motor de riesgo (`risk/`),
  intérprete local de los workflows (`runtime/`), fuentes (`sources/`), simulador (`simulation/`).
  `python -m sos deploy` crea/actualiza/publica los workflows por API.
- `web/` — dashboard operativo (stdlib + Leaflet/LiveKit por CDN). `main_simulation.py` — demo.
- `config/` — pesos/umbrales y escenario demo. `tests/` — pytest. `deploy-state.json` — ids desplegados.
- `.local/` — Postgres embebido (mientras Twin no está provisionado). **Regla del usuario: no
  instalar nada fuera de esta carpeta** (venv + `.local`).
- `voice/`, `main.py` — legado (web de voz simple, mapa FIRMS en terminal).
- `HappyRobot-Vault/` — vault de **Obsidian** con la documentación de cómo funciona HappyRobot
  y de todo lo construido (formatos de nodos por API, problemas resueltos, IDs, bitácora).
- `.claude/skills/obsidian-docs/` — skill de Claude Code equivalente a la sección siguiente.

Secretos: solo en `.env` (`HAPPYROBOT_API_KEY`) o como variables de workflow; nunca en el repo/vault.

## Documentar en el vault de Obsidian (`HappyRobot-Vault/`)

Cuando el usuario pida **documentar**, **añadir al vault**, **apuntar esto en Obsidian**, o al
cerrar una sesión de trabajo relevante sobre HappyRobot/FlareAI que deba recordarse después,
sigue estas reglas.

### Por qué existe

El vault es la memoria persistente y legible del proyecto: para que cualquiera (otro agente,
otra sesión, otra persona) entienda el qué, el cómo y el porqué sin releer el historial del
chat.

### Estructura

```
HappyRobot-Vault/
├── 00 Índice.md        # mapa de navegación — actualizar SIEMPRE sus enlaces al añadir notas
├── Conceptos/           # cómo funciona HappyRobot en general (API, auth, nodos, voces...)
├── Proyecto/            # lo específico construido aquí (workflows, código, cómo arrancarlo)
├── Referencia/           # chuletas: IDs, endpoints, catálogos, problemas/soluciones
└── Bitácora/             # una nota por fecha (YYYY-MM-DD.md) con el registro cronológico
```

Si el vault no existe todavía, créalo con esta misma estructura antes de escribir notas.

### Reglas de estilo (toda nota nueva o editada)

1. **Frontmatter YAML** al inicio:
   ```yaml
   ---
   tags: [happyrobot, <categoría: concepto|proyecto|referencia|bitácora>]
   ---
   ```
   Las notas de Bitácora añaden también `date: YYYY-MM-DD`.
2. **Wikilinks (`[[Nombre de la nota]]`)** liberalmente. Cada nota termina con una línea
   `Relacionado: [[...]] · [[...]]`. Un link a una nota que aún no existe está bien.
3. **Una nota = un tema concreto**, nombre de fichero descriptivo en español, título estilo
   frase (`Autenticación y hosts API.md`, no `auth.md`). Evita notas cajón de sastre.
4. **Actualiza `00 Índice.md`** cada vez que crees una nota nueva: añade su enlace en la
   sección correspondiente y refresca el bloque "Estado actual" si algo cambió.
5. **Prioriza el "por qué" sobre el "qué"**: decisiones, alternativas descartadas, motivos
   concretos ("elegimos X porque Y falló con este error exacto").
6. **Comandos/código reproducibles** en bloques \`\`\`bash / \`\`\`json cuando documentes un
   procedimiento técnico.
7. **Nunca guardes secretos completos** (API keys, tokens, contraseñas). Si hay que
   referenciar una credencial, usa solo los últimos 3-4 caracteres o un alias, y anota dónde
   vive el valor real (variable de entorno, gestor de secretos).
8. **Bitácora**: al cerrar una sesión con cambios relevantes, añade o actualiza
   `Bitácora/YYYY-MM-DD.md` (fecha real) con: petición inicial del usuario, pasos realizados en
   orden, resultado al cierre, y "Pendiente / próximos pasos" si aplica. Si ya existe una nota
   de ese día, amplíala en vez de sobreescribirla.

### Flujo a seguir

1. Comprueba si `HappyRobot-Vault/` ya existe. Si no, créala.
2. Repasa qué se descubrió (comportamientos, límites de la API) y qué se construyó/cambió
   (código, workflows, IDs) en la sesión.
3. Decide carpeta (Conceptos / Proyecto / Referencia) para cada pieza; prefiere ampliar una
   nota existente antes que duplicar (busca primero con grep/búsqueda de archivos).
4. Escribe/edita las notas siguiendo las reglas de estilo.
5. Actualiza `00 Índice.md`.
6. Añade la entrada de `Bitácora/YYYY-MM-DD.md` del día.
7. Antes de terminar, verifica que no haya secretos completos filtrados
   (`grep -rn "sk_live_\|sk-\|Bearer " HappyRobot-Vault/`, ajustando el patrón al secreto
   relevante).
8. Resume al usuario qué notas se crearon/actualizaron, enlazando el índice.
