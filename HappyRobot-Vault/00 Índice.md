---
tags: [happyrobot, índice]
---

# 🧭 Índice — Vault HappyRobot / S.O.S. Agentic Crisis Engine

Este vault documenta todo lo descubierto y construido sobre **HappyRobot**: primero la web de voz
**FlareAI Web Voice** (2026-09-18) y después el **S.O.S. Agentic Crisis Engine** para el reto de
HackSpain 2026 (2026-09-19): gestión autónoma de crisis con Twin, workflows, Reasoning Agent, voz
y dashboard con aprobación humana.

> Objetivo del vault: que la próxima vez que se retome este trabajo (yo u otro asistente), se pueda
> leer aquí el contexto completo sin tener que redescubrir nada. Empieza por
> [[SOS Crisis Engine - arquitectura]] y [[Cómo arrancar todo]].

## Mapa de notas

### Conceptos (cómo funciona HappyRobot en general)
- [[Qué es HappyRobot]]
- [[Autenticación y hosts API]]
- [[Workflows y nodos]]
- [[Formato de nodos por API]] ← el JSON real de cada nodo (no está en la doc)
- [[Twin - base de datos]]
- [[Reasoning Agent y tools]]
- [[Signals]]
- [[Python Sandbox]]
- [[Templates de workflow]]
- [[Voice Tokens y LiveKit]]
- [[Catálogo de voces]]
- [[Apps y MCP]]

### Proyecto (lo que hemos construido)
- [[2026-09-19#Atlas nacional de infraestructura de emergencias|Atlas nacional de emergencias]] — SQLite/GeoJSON, extracción, calidad y consultas espaciales
- [[SOS Crisis Engine - arquitectura]]
- [[Workflows SOS]] (los 9 desplegados)
- [[Esquema de datos SOS]]
- [[Motor de riesgo]]
- [[Base de datos local embebida]]
- [[Intérprete local de workflows]]
- [[Dashboard y simulador]]
- [[Escenario demo - giro de viento]]
- [[Cómo desplegar - sos deploy]]
- [[Cómo arrancar todo]]
- Legacy 2026-09-18: [[FlareAI Web Voice - workflow]] · [[Web app - server y frontend]]

### Referencia
- [[IDs y recursos]]
- [[Endpoints usados]]
- [[Catálogo de nodos]]
- [[Problemas y soluciones]] (18 problemas concretos y su solución)

### Bitácora
- [[2026-09-18]] — agente de voz web + vault
- [[2026-09-19]] — S.O.S. Crisis Engine completo (plan, laboratorio de formatos, deploy, local, simulador, dashboard)

## Estado actual (resumen rápido, 2026-09-19)
- **Atlas local de emergencias de FlareAI**: generados y verificados SQLite, GeoJSON y manifiesto;
  25.136 entidades, 22.575 georreferenciadas y presencia en las 52 provincias/ciudades autónomas.
  Pendientes 2.561 registros oficiales sin ubicación fiable; cobertura no exhaustiva ni
  disponibilidad operativa comprobada. Fuentes OSM, Sanidad, Madrid y DERA; 25 pruebas del
  módulo. Procedimiento, decisiones y limitaciones en
  [[2026-09-19#Atlas nacional de infraestructura de emergencias|la bitácora del atlas]].
- **Telegram como alternativa de prueba**: workflow `FlareAI Telegram Demo` creado, web en
  `http://127.0.0.1:8092`, bot dedicado, vinculación de un chat privado y prefijo obligatorio de
  simulacro. 27 pruebas SMS/Telegram con mocks pasan. Bot real conectado y chat vinculado:
  Telegram aceptó un mensaje directo de diagnóstico, pendiente confirmar recepción con el usuario.
  **El envío por HappyRobot sigue bloqueado por 401**; la prueba directa no ejecutó ese workflow.
- **SMS pendiente del mentor**: autenticación resuelta, pero un envío autorizado terminó en
  Telnyx 40305 por asociación al perfil de mensajería. El Twilio gestionado comprado no aparece
  como toll-free seleccionable. No hay entrega confirmada ni se compraron números desde el agente.
  Detalles en [[Cómo arrancar todo]] y [[2026-09-19]]. Los puntos siguientes describen el estado histórico de SOS.
- 🧹 **Plataforma vaciada (2026-09-19, tarde)**: los 9 workflows SOS se **borraron** de HappyRobot a
  petición del usuario (sin Twin no servían). Siguen definidos como código: `python -m sos deploy`
  los vuelve a crear en una pasada cuando haya Twin. En la org solo quedan `FlareAI Web Voice`
  (lo usa el dashboard como voz de reserva) y `test`.
- ⚠️ **Twin no provisionado** (404) y API key sin `twin.manage` → **acción del usuario**:
  Settings → Twin Database → Enable + key con Full Twin access. Mientras: Postgres embebido en
  `.local/pg` con el mismo esquema, y `sos twin sync-to-twin` para migrar.
- ✅ `python main_simulation.py` funciona en local de punta a punta (aviso 112 → satélite →
  verificación IA → plan/acciones → aprobación → llamadas → giro de viento → re-plan + signal).
- ✅ Dashboard en `http://localhost:8000` (`python web/server.py`), voz por web call (agente básico
  hasta que haya Twin).
- ✅ 12 tests (`.venv/bin/python -m pytest -q tests`). Commit `be1bb86` + docs.
- 🔑 Secretos solo en `.env` / variables de workflow; nunca en repo ni vault.

Relacionado: [[2026-09-19]] · [[Cómo arrancar todo]] · [[Base de datos local embebida]]
