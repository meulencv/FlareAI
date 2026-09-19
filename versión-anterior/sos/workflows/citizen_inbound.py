"""WF-Citizen-Inbound: "112 virtual". Un ciudadano llama (web call) y avisa de una emergencia.

El agente recoge qué ocurre y dónde (eligiendo el lugar conocido más cercano de la lista de
activos de Twin, que se le pasa en el prompt) y registra el aviso con la tool `registrar_aviso`,
que lo convierte en una evidencia `call` para WF-Ingest. También puede informar del estado de un
incidente abierto (`consultar_estado`).
"""

from ._builder import Agent, CallWorkflow, P, Prompt, Python, Ref, Tool, Trigger, TwinSQL, WorkflowSpec
from ._voice import voice_agent_config

LUGARES_SQL = "SELECT ref, name, kind, lat, lon FROM assets WHERE kind IN ('town','hospital','school','plant','port','forest_reserve') ORDER BY name"
ABIERTOS_SQL = "SELECT id::text AS id, type, status, summary, priority FROM incidents WHERE status NOT IN ('closed','dismissed') ORDER BY priority DESC, created_at DESC LIMIT 5"

LISTA = r'''
import json as _json
def _load(v):
    try: return _json.loads(v) if isinstance(v, str) and v else []
    except Exception: return []
lugares = _load(input_data.get("lugares")); abiertos = _load(input_data.get("abiertos"))
L = ["Lugares conocidos (ref → nombre, tipo):"] + ["- %s → %s (%s)" % (p.get("ref"), p.get("name"), p.get("kind")) for p in lugares]
A = ["Incidentes abiertos ahora mismo:"] + (["- %s [%s/%s prioridad %s]: %s" % (i.get("id"), i.get("type"), i.get("status"), i.get("priority"), i.get("summary")) for i in abiertos] or ["- ninguno"])
output = {"lugares": "\n".join(L), "abiertos": "\n".join(A), "lugares_json": _json.dumps(lugares)}
'''

AVISO = r'''
import json as _json
def _load(v):
    try: return _json.loads(v) if isinstance(v, str) and v else []
    except Exception: return []
lugares = _load(input_data.get("lugares_json"))
ref = (input_data.get("lugar_ref") or "").strip()
lugar = next((p for p in lugares if p.get("ref") == ref), None)
tipo = (input_data.get("tipo") or "unknown").strip().lower()
if tipo not in ("wildfire", "industrial", "chemical", "maritime", "flood", "unknown"): tipo = "unknown"
desc = (input_data.get("descripcion") or "").strip()
detalle = {"caller": input_data.get("nombre"), "phone": input_data.get("telefono"), "place_ref": ref, "place_text": input_data.get("lugar_texto"),
           "direction": input_data.get("direccion_fuego"), "people_at_risk": input_data.get("personas_en_peligro"), "transcript_summary": desc,
           "run_id": input_data.get("run_id")}
output = {"ok": lugar is not None, "lat": (lugar or {}).get("lat", ""), "lon": (lugar or {}).get("lon", ""), "tipo": tipo,
          "summary": ("Aviso ciudadano en %s: %s" % ((lugar or {}).get("name") or input_data.get("lugar_texto"), desc))[:300],
          "details_json": _json.dumps(detalle, ensure_ascii=False), "lugar_nombre": (lugar or {}).get("name") or ""}
'''

T = "entrada"

PROMPT = Prompt(
    """# Quién eres
Eres **Flare**, operador virtual del 112 del Centro de Coordinación de Emergencias. Hablas en español
de España, con calma y frases cortas. Tu prioridad es la seguridad de quien llama.

# Qué tienes que conseguir (en este orden, sin interrogar: conversación natural)
1. Si hay peligro inmediato para la persona, primero indícale que se ponga a salvo.
2. Qué ocurre (fuego/humo forestal, incendio industrial/químico, barco, inundación...) y qué ve
   exactamente (color del humo, llamas, tamaño, hacia dónde avanza).
3. Dónde: pídele el pueblo/zona y elige el **lugar conocido** más adecuado de esta lista
   (usa su `ref`; si no encaja ninguno, elige el más cercano y anota el texto exacto que te dice):
""", Ref("lista", "lugares"), """
4. Si hay personas en peligro y cuántas; su nombre y un teléfono de contacto.
5. Llama a `registrar_aviso` con todo (una sola vez). Confírmale que el aviso está registrado, que
   se está verificando con satélite y medios, y dale un consejo de seguridad concreto.

Si la persona pregunta por un incidente en curso, usa lo siguiente para informar (sin alarmar):
""", Ref("lista", "abiertos"), """

# Reglas
- No inventes: si no sabes algo, dilo.
- Nunca digas que los bomberos ya van de camino salvo que lo sepas por los incidentes abiertos.
- Termina con `registrar_aviso` llamada y una despedida breve.
""",
)

spec = WorkflowSpec(
    key="citizen_inbound",
    name="SOS · 112 virtual (web call)",
    icon="microphone",
    description="Un ciudadano avisa por voz; el agente registra la evidencia y la envía a la ingesta.",
    trigger=Trigger(T, "web_call", config={"require_webcall_auth": True, "open_runs_page_on_trigger": False}).add(
        TwinSQL("lugares", LUGARES_SQL, max_rows=200, outputs={"rows": [{"ref": "serra", "name": "Serra", "kind": "town", "lat": 39.68, "lon": -0.42}]}).add(
            TwinSQL("abiertos", ABIERTOS_SQL, max_rows=5, outputs={"rows": [{"id": "x", "type": "wildfire", "status": "verified", "summary": "s", "priority": 3}]}).add(
                Python("lista", LISTA, inputs={"lugares": Ref("lugares", "rows"), "abiertos": Ref("abiertos", "rows")},
                       outputs={"lugares": "- serra → Serra (town)", "abiertos": "- ninguno", "lugares_json": "[]"}).add(
                    Agent(
                        "agente", "inbound_voice_agent", PROMPT,
                        config=voice_agent_config("Flare 112"),
                        initial_message="Emergencias, le atiende Flare. ¿Qué está ocurriendo y dónde se encuentra?",
                    ).add(
                        Tool(
                            "registrar_aviso",
                            "Registra el aviso del ciudadano como evidencia de emergencia. Llámala una vez cuando tengas qué ocurre y dónde.",
                            [
                                {"name": "lugar_ref", "description": "ref del lugar conocido más cercano (de la lista del prompt)", "required": True, "example": "serra"},
                                {"name": "lugar_texto", "description": "Lugar tal y como lo describe la persona", "required": True, "example": "detrás de la urbanización alta de Serra"},
                                {"name": "tipo", "description": "wildfire | industrial | chemical | maritime | flood | unknown", "required": True, "example": "wildfire"},
                                {"name": "descripcion", "description": "Qué ve la persona, en 1-3 frases", "required": True},
                                {"name": "direccion_fuego", "description": "Hacia dónde avanza el fuego/humo si lo sabe (norte, hacia el pueblo...)", "required": False},
                                {"name": "personas_en_peligro", "description": "Personas en peligro y cuántas, o 'ninguna'", "required": False},
                                {"name": "nombre", "description": "Nombre de quien llama", "required": False},
                                {"name": "telefono", "description": "Teléfono de contacto", "required": False},
                            ],
                            Python(
                                "aviso_prep", AVISO,
                                inputs={k: Ref("registrar_aviso", k) for k in ("lugar_ref", "lugar_texto", "tipo", "descripcion", "direccion_fuego", "personas_en_peligro", "nombre", "telefono")}
                                | {"lugares_json": Ref("lista", "lugares_json"), "run_id": Ref("$current", "run_id")},
                                outputs={"ok": True, "lat": 39.68, "lon": -0.42, "tipo": "wildfire", "summary": "s", "details_json": "{}", "lugar_nombre": "Serra"},
                            ).add(
                                CallWorkflow(
                                    "ingesta", "ingest", fire_and_forget=True,
                                    data={"source_type": "call", "source_ref": Ref("$current", "run_id"),
                                          "lat": Ref("aviso_prep", "lat"), "lon": Ref("aviso_prep", "lon"),
                                          "observed_at": Ref("$time", "now_iso"), "reliability": "",
                                          "incident_type": Ref("aviso_prep", "tipo"), "summary": Ref("aviso_prep", "summary"),
                                          "details_json": Ref("aviso_prep", "details_json")},
                                )
                            ),
                            expose=["ok", "lugar_nombre"],
                        )
                    )
                )
            )
        )
    ),
)
