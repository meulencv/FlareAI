---
tags: [happyrobot, proyecto]
---

# S.O.S. Agentic Crisis Engine — arquitectura

Proyecto para el reto HappyRobot de HackSpain 2026 ("¿Puede la IA gestionar una crisis?").
Decisiones del usuario (2026-09-19): **todo en HappyRobot**, la verificación la hace **una IA que
evalúa los casos** (no una regla rígida de 2 fuentes), llamadas salientes **simuladas por web call**
(la org no tiene números ni SIP), dashboard **web propia en el repo**, arquitectura **muy modular**.

## Principios

- **Twin es la única fuente de verdad** ([[Esquema de datos SOS]]); mientras no esté provisionado,
  un Postgres embebido idéntico ([[Base de datos local embebida]]).
- **Cada capacidad es un workflow** pequeño, componible con *Call Workflow* ([[Workflows SOS]]).
- **El repo define la plataforma como código**: `python -m sos deploy` crea/actualiza/publica los
  9 workflows por API ([[Cómo desplegar - sos deploy]]). Cambiar algo = editar el spec y redesplegar.
- **La IA decide, el código mide**: el Reasoning Agent evalúa y propone; el [[Motor de riesgo]] es
  determinista y testeado.
- **Parametrización** en la tabla `config` (pesos, umbrales, `auto_approve_kinds`, canal de voz),
  editable en caliente desde el dashboard.
- **Human-in-the-loop**: las acciones nacen `proposed`; el operador aprueba con 1 clic (WF-Approve);
  puede escuchar/tomar el control de una llamada (`voice/tokens` con `session_id`).

## Flujo

```
Fuentes (112 web call · FIRMS · meteo · simulador) → WF-Ingest → Twin.evidence + incidents
   → WF-Assess (contexto SQL → riesgo → Reasoning Agent → tools: evaluación / plan / acciones)
   → acciones proposed → dashboard (WF-Approve) → WF-Execute (adapter por tipo)
   → llamada web (WF-Outbound-Voice) → resultado → (nueva evidencia → WF-Ingest)
Meteo: WF-Weather-Inject → giro de viento → signal a llamadas + WF-Assess (reason=wind_shift)
```

## Dos modos de ejecución, un solo código

| | local (hoy) | cloud (con Twin) |
|---|---|---|
| Datos | Postgres embebido `.local/pg` | Twin |
| Workflows | [[Intérprete local de workflows]] (`sos.runtime`) sobre los mismos specs | HappyRobot |
| Analista | política determinista `sos/runtime/agents.py` | Reasoning Agent (LLM) |
| Voz | web call con el agente básico *FlareAI Web Voice* (sin Twin los workflows SOS de voz fallan en el 1er nodo) | WF-112 y WF-Outbound-Voice |
| Selección | `SOS_DB=auto` (Twin si usable) | idem |

## Repo

```
sos/happyrobot   cliente API (stdlib)         sos/twin       esquema · migrate · seed · sync
sos/workflows    _builder (DSL) · deploy · 9 specs           sos/risk       motor de riesgo
sos/runtime      intérprete local + políticas de agentes     sos/sources    firms · open_meteo
sos/simulation   escenario giro de viento                    web/           dashboard
config/          weights.json · scenarios/demo_es.json       tests/         12 tests
main_simulation.py · deploy-state.json (ids desplegados, sin secretos)
```

Relacionado: [[Workflows SOS]] · [[Esquema de datos SOS]] · [[Dashboard y simulador]] · [[Cómo arrancar todo]] · [[2026-09-19]]
