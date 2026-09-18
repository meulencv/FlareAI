---
name: obsidian-docs
description: Documenta en el vault de Obsidian del proyecto (HappyRobot-Vault) lo descubierto o construido en la sesión — conceptos nuevos, decisiones, IDs/recursos, problemas y soluciones, y una entrada de bitácora del día. Úsala cuando el usuario pida "documentar", "añadir al vault", "apunta esto en Obsidian", o al cerrar una sesión de trabajo relevante sobre HappyRobot/FlareAI que deba recordarse en el futuro.
allowed-tools: Read, Write, Edit, Bash, Grep, Glob
---

# Documentar en el vault de Obsidian

Este proyecto mantiene un vault de Obsidian en `HappyRobot-Vault/` (raíz del repo) como
memoria persistente y legible del trabajo hecho con HappyRobot/FlareAI. El objetivo es que
cualquiera (yo mismo en una sesión futura, u otra persona) pueda abrir el vault y entender el
qué, el cómo y el porqué sin tener que releer el historial del chat.

## Estructura del vault

```
HappyRobot-Vault/
├── 00 Índice.md        # mapa de navegación — SIEMPRE actualizar sus enlaces al añadir notas
├── Conceptos/           # cómo funciona HappyRobot en general (API, auth, nodos, voces...)
├── Proyecto/            # lo específico que hemos construido (workflows, código, cómo arrancarlo)
├── Referencia/           # chuletas: IDs, endpoints, catálogos, problemas/soluciones
└── Bitácora/             # una nota por fecha (YYYY-MM-DD.md) con el registro cronológico
```

Si el vault no existe todavía en el proyecto, créalo con esta misma estructura antes de escribir
notas.

## Reglas de estilo (aplican a toda nota nueva o editada)

1. **Frontmatter YAML** al inicio de cada nota:
   ```yaml
   ---
   tags: [happyrobot, <categoría: concepto|proyecto|referencia|bitácora>]
   ---
   ```
   Las notas de Bitácora añaden también `date: YYYY-MM-DD`.

2. **Wikilinks (`[[Nombre de la nota]]`)** liberalmente para conectar ideas relacionadas. Cada
   nota termina con una línea `Relacionado: [[...]] · [[...]]`. Un link a una nota que aún no
   existe está bien — es un placeholder para escribirla después.

3. **Una nota = un tema concreto.** Nombres de fichero descriptivos en español, con mayúsculas
   tipo título (`Autenticación y hosts API.md`, no `auth.md`). Evita notas cajón de sastre.

4. **Actualiza `00 Índice.md`** cada vez que crees una nota nueva: añade su enlace en la
   sección correspondiente (Conceptos / Proyecto / Referencia / Bitácora) y refresca el bloque
   "Estado actual" si algo relevante cambió.

5. **Prioriza el "por qué" sobre el "qué".** El código y los comandos ya están en el repo; el
   vault vale por capturar decisiones, alternativas descartadas y motivos
   ("elegimos X porque Y falló con este error exacto").

6. **Incluye comandos/código reproducibles** (bloques \`\`\`bash, \`\`\`json) cuando documentes
   un procedimiento técnico — que se pueda copiar y ejecutar, no solo describir en prosa.

7. **Nunca guardes secretos completos** (API keys, tokens, contraseñas). Si hay que referenciar
   una credencial, usa solo los últimos 3-4 caracteres o un alias, y anota dónde vive el valor
   real (variable de entorno, gestor de secretos). Antes de escribir, revisa que no se cuele
   ningún secreto completo copiado de la conversación.

8. **Bitácora**: al cerrar una sesión de trabajo con cambios relevantes, añade o actualiza
   `Bitácora/YYYY-MM-DD.md` (fecha real de la sesión, no inventada) con: petición inicial del
   usuario (cita literal si es corta), pasos realizados en orden, resultado al cierre, y una
   sección "Pendiente / posibles próximos pasos" si aplica. Si ya existe una nota de ese día,
   añade a continuación en vez de sobreescribir lo anterior.

## Flujo a seguir cuando se invoca esta skill

1. Mira si `HappyRobot-Vault/` ya existe en el repo (`Glob` o `ls`). Si no, créala con la
   estructura de arriba, empezando por `00 Índice.md`.
2. Repasa la conversación reciente / cambios hechos en la sesión: qué se descubrió (conceptos
   de la API, límites, comportamientos), qué se construyó o cambió (código, workflows, IDs), y
   qué problemas se resolvieron.
3. Para cada pieza de conocimiento nueva, decide en qué carpeta encaja (Conceptos /
   Proyecto / Referencia) y si amplía una nota existente o merece una nota nueva — prefiere
   ampliar antes que duplicar; usa `Grep`/`Glob` para comprobar si ya hay una nota relacionada.
4. Escribe/edita las notas siguiendo las reglas de estilo de arriba.
5. Actualiza `00 Índice.md`.
6. Añade la entrada de `Bitácora/YYYY-MM-DD.md` del día.
7. Verifica que no haya secretos completos filtrados: `grep -rn "sk_live_\|sk-\|Bearer " HappyRobot-Vault/` (ajusta el patrón al tipo de secreto relevante en el proyecto) antes de dar la tarea por terminada.
8. Resume brevemente al usuario qué notas se crearon/actualizaron y enlaza el índice.
