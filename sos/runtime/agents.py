"""Políticas locales que sustituyen a los agentes de HappyRobot cuando se ejecuta sin la plataforma.

Cada política devuelve la lista de tools que "el agente" invocaría: [(nombre_tool, parámetros)].
- `analista`: versión determinista del Reasoning Agent de WF-Assess (verificación por coherencia
  de fuentes + motor de riesgo). En la plataforma esto lo decide el LLM con el mismo contexto.
- `voz_saliente` / `voz_112`: conversaciones guionizadas por el simulador (runtime.scenario).
"""

from __future__ import annotations

import json
from typing import Any

from .local import LocalRuntime, RunContext, dig
from ..workflows._builder import Node


def _load(v: Any, default: Any) -> Any:
    if v in (None, ""):
        return default
    if isinstance(v, (dict, list)):
        return v
    try:
        return json.loads(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------------------------
# Analista de crisis (determinista)
# ---------------------------------------------------------------------------------------------

def analista(rt: LocalRuntime, node: Node, ctx: RunContext) -> list[tuple[str, dict]]:
    row = dig(ctx.outputs.get("contexto"), "rows.0") or {}
    inc = _load(row.get("incident"), {})
    evidence = _load(row.get("evidence"), [])
    contacts = _load(row.get("contacts"), [])
    resources = _load(row.get("resources"), [])
    prior = _load(row.get("prior_actions"), [])
    cfg = _load(row.get("config"), {})
    risk = _load(dig(ctx.outputs.get("riesgo"), "risk_json"), {})
    reason = ctx.outputs.get(ctx.spec.trigger.name, {}).get("reason", "")

    # -- verificación: fuentes independientes y fiabilidad combinada ---------------------------
    hints = cfg.get("verification_hints", {}) or {}
    defaults = hints.get("source_reliability", {})
    by_source: dict[str, float] = {}
    for e in evidence:
        r = e.get("reliability")
        r = float(r) if r not in (None, "") else float(defaults.get(e.get("source_type"), 0.5))
        by_source[e["source_type"]] = max(by_source.get(e["source_type"], 0.0), r)
    p_false = 1.0
    for r in by_source.values():
        p_false *= (1.0 - r)
    confidence = round(1.0 - p_false, 2) if by_source else 0.0
    min_sources = int(hints.get("min_independent_sources", 2))
    strong = any(r >= 0.9 for r in by_source.values())
    if not evidence:
        status = "dismissed"
    elif len(by_source) >= min_sources and confidence >= 0.6 or strong:
        status = "active" if inc.get("status") in ("verified", "active") else "verified"
    else:
        status = "candidate"

    heading = risk.get("spread_heading_deg")
    rumbo = f"avanza con rumbo {heading:.0f}°" if isinstance(heading, (int, float)) else "sin viento conocido"
    threatened = risk.get("threatened_assets", [])
    names = ", ".join(t["name"] for t in threatened[:4]) or "sin activos en la trayectoria"
    tipo = inc.get("type") or "unknown"
    summary = f"Incidente {tipo} en ({inc.get('lat')}, {inc.get('lon')}); {rumbo}; amenaza a: {names}."
    rationale = (f"{len(evidence)} evidencias de {len(by_source)} fuentes ({', '.join(by_source)}); "
                 f"confianza combinada {confidence}; motivo: {reason}")
    calls: list[tuple[str, dict]] = [("guardar_evaluacion", {
        "status": status, "confidence": confidence, "incident_type": tipo, "summary": summary, "rationale": rationale,
    })]

    priority = int(risk.get("priority") or 0)
    existing = {(a.get("kind"), (a.get("rationale") or "").split("→")[-1].strip()) for a in prior if a.get("status") != "rejected"}

    def propose(kind: str, contact_ref: str = "", resource_ref: str = "", prio: int = 50, instructions: str = "", why: str = "") -> None:
        key = (kind, contact_ref or resource_ref)
        if key in existing:
            return
        existing.add(key)
        calls.append(("proponer_accion", {"kind": kind, "contact_ref": contact_ref, "resource_ref": resource_ref,
                                          "priority": prio, "instructions": instructions, "rationale": f"{why} → {contact_ref or resource_ref}"}))

    if status in ("verified", "active") and priority >= 2:
        prios = [t["name"] for t in threatened]
        needed = risk.get("needed_capabilities", ["water"])
        recommended = [r for r in risk.get("recommended_resources", []) if r.get("compatible")][:2]
        calls.append(("guardar_plan", {
            "summary": f"Proteger vidas en la trayectoria ({', '.join(prios[:3]) or 'perímetro'}); ataque con medios de {'/'.join(needed)}; "
                       f"evacuación escalonada por ETA y corte de accesos.",
            "priorities": "; ".join(prios),
            "resource_plan": "; ".join(f"{r['ref']}: {'ataque directo' if r['kind'] == 'brigade' else 'descargas sobre cabeza' if r['kind'] == 'hydroplane' else 'contención'}" for r in recommended),
            "notification_order": "; ".join([c["ref"] for c in contacts if c.get("role") == "citizen" and c.get("asset_ref") in {t.get("ref") for t in threatened}]
                                            + [c["ref"] for c in contacts if c.get("role") in ("commander", "police", "mayor")][:3]),
        }))
        # evacuaciones: ciudadanos en zonas amenazadas, por ETA
        order = {t.get("ref"): i for i, t in enumerate(threatened)}
        citizens = sorted((c for c in contacts if c.get("role") == "citizen" and c.get("asset_ref") in order),
                          key=lambda c: (order[c["asset_ref"]], c.get("priority", 100)))
        for i, c in enumerate(citizens[:3]):
            t = next(x for x in threatened if x.get("ref") == c["asset_ref"])
            propose("evacuate_call", contact_ref=c["ref"], prio=1 + i,
                    instructions=f"Evacúe {c.get('asset_name')} ahora: el fuego puede llegar en ~{t.get('eta_hours')} h. "
                                 f"Salga en dirección contraria al humo y acuda al punto de encuentro (polideportivo de Náquera). Lleve documentación y medicación.",
                    why=f"Zona en la trayectoria del viento, ETA {t.get('eta_hours')} h")
        # coordinación con el mando del primer medio compatible (o cualquier mando)
        cmd_ref = next((r.get("contact_ref") for r in resources if r.get("ref") == (recommended[0]["ref"] if recommended else None) and r.get("contact_ref")), None)
        cmd_ref = cmd_ref or next((c["ref"] for c in contacts if c.get("role") == "commander"), "")
        if cmd_ref:
            propose("coordination_call", contact_ref=cmd_ref, prio=2,
                    instructions=f"Asignación: {', '.join(r['name'] for r in recommended) or 'medios disponibles'}. Prioridad {risk.get('priority_label')}. "
                                 f"Objetivo: proteger {', '.join(prios[:2]) or 'el perímetro'}; el frente {rumbo}. Confirmar ETA y necesidades.",
                    why="Mando responsable de los medios compatibles")
        for r in recommended:
            propose("dispatch", resource_ref=r["ref"], prio=3, instructions=f"Desplegar {r['name']} sobre el incidente (ETA {r.get('eta_min')} min).", why="Medio compatible más cercano disponible")
        police = next((c["ref"] for c in contacts if c.get("role") == "police"), "")
        if police:
            propose("notify", contact_ref=police, prio=5, instructions="Cortar accesos a la zona amenazada y apoyar evacuación.", why="Control de tráfico")
    elif status == "candidate" and confidence < 0.6:
        drone = next((r for r in resources if r.get("kind") == "drone" and r.get("status") == "available"), None)
        if drone:
            propose("dispatch", resource_ref=drone["ref"], prio=4, instructions="Reconocimiento térmico para confirmar el aviso.", why="Una sola fuente: confirmar antes de evacuar")
    return calls


# ---------------------------------------------------------------------------------------------
# Voz (guionizada por el simulador)
# ---------------------------------------------------------------------------------------------

def voz_saliente(rt: LocalRuntime, node: Node, ctx: RunContext) -> list[tuple[str, dict]]:
    trig = ctx.outputs.get(ctx.spec.trigger.name, {})
    script = getattr(rt, "scenario", {}).get("outbound", {})
    answer = script.get(trig.get("contact_name"), script.get("*", {"outcome": "accepted", "notes": "Confirma que evacúa.", "new_info": ""}))
    return [("registrar_resultado", {"outcome": answer.get("outcome", "accepted"), "notes": answer.get("notes", ""), "new_info": answer.get("new_info", "")})]


def voz_112(rt: LocalRuntime, node: Node, ctx: RunContext) -> list[tuple[str, dict]]:
    aviso = getattr(rt, "scenario", {}).get("aviso") or {
        "lugar_ref": "serra", "lugar_texto": "detrás de la urbanización alta de Serra", "tipo": "wildfire",
        "descripcion": "Humo negro y llamas en el monte, hacia el pueblo", "direccion_fuego": "hacia el pueblo",
        "personas_en_peligro": "ninguna", "nombre": "Vecino de Serra", "telefono": "+34600000099",
    }
    return [("registrar_aviso", aviso)]


POLICIES = {
    "assess.analista": analista,
    "outbound_voice.agente": voz_saliente,
    "citizen_inbound.agente": voz_112,
}
