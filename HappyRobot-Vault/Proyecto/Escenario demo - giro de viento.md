---
tags: [happyrobot, proyecto]
---

# Escenario demo — incendio en la Serra Calderona con giro de viento

Salida real de `python main_simulation.py` (local, 2026-09-19):

1. **Aviso 112** (una sola fuente) → incidente `candidate`, confianza 0.5 → el analista propone
   solo `dispatch` del dron para confirmar.
2. **FIRMS ×2 + viento O 40 km/h** → `active`, confianza 0.93, prioridad 4, riesgo 24 125; amenaza
   Serra, CEIP, Segart, Estivella; plan + 3 `evacuate_call` (María, Pep, Carmen por ETA),
   `coordination_call` a la jefa de la brigada forestal, `dispatch` brigada + hidroavión,
   `notify` a Guardia Civil (auto-aprobada → done).
3. **Aprobación 1 clic** → llamadas `ready`, medios `en_route`.
4. **Llamadas**: María "necesita ayuda" y aporta info nueva (vecina mayor sola) → nueva evidencia
   → re-evaluación (propone coordinación con Bomberos Sagunto porque los medios previos ya no
   están disponibles).
5. **Giro de viento 180°** → signal `incident.<id>` ("el viento ha girado 180 grados…"), re-evaluación:
   rumbo 270°, amenaza Serra, CEIP, **Olocau, Marines** → plan nuevo + `evacuate_call` a Amparo (Olocau).

Resumen: evidencias firms=2, call=2; acciones done=8, proposed=3; 4 planes.

Relacionado: [[Dashboard y simulador]] · [[Motor de riesgo]] · [[Signals]]
