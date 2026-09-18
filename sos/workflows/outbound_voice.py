"""WF-Outbound-Voice: llamada saliente simulada por web call (evacuación o coordinación).

El navegador (dashboard) pide un token con `data` = parámetros del trigger Web Call:
    action_id, incident_id, kind, role (citizen|commander|police|mayor), contact_name, place,
    instructions, incident_summary
y "descuelga". El agente habla en español con el rol adecuado, y registra el resultado en Twin
mediante la tool `registrar_resultado`. Si el interlocutor aporta información nueva, se envía a
WF-Ingest como evidencia (source_type=call).

Signals: el agente está suscrito a `usecase.*` y al topic `incident.*`; si el viento cambia,
WF-Feeder-Weather publica un signal y el agente actualiza las instrucciones en la misma llamada.
"""

from ._builder import Agent, CallWorkflow, Otherwise, P, Paths, Prompt, Python, Ref, Tool, Trigger, TwinWrite, When, WorkflowSpec
from ._voice import voice_agent_config

SAMPLE = {
    "action_id": "00000000-0000-0000-0000-000000000003",
    "incident_id": "00000000-0000-0000-0000-000000000000",
    "kind": "evacuate_call",
    "role": "citizen",
    "contact_name": "María Ferrer",
    "place": "Serra",
    "instructions": "Evacúe hacia Náquera por la CV-310. Punto de encuentro: polideportivo.",
    "incident_summary": "Incendio forestal al oeste de Serra que avanza hacia el este.",
    "incident_lat": "39.70",
    "incident_lon": "-0.47",
}

T = "entrada"

PROMPT = Prompt(
    """# Quién eres
Eres **Flare**, agente de voz del Centro de Coordinación de Emergencias. Hablas en español de España,
con calma, claridad y frases cortas. Estás llamando a **""", Ref(T, "contact_name"), """** (rol: """, Ref(T, "role"),
    """, zona: """, Ref(T, "place"), """).

# Situación
""", Ref(T, "incident_summary"), """

# Objetivo de esta llamada (tipo: """, Ref(T, "kind"), """)
""", Ref(T, "instructions"), """

# Cómo actuar según el rol
- **citizen** (ciudadano): confirma que hablas con la persona correcta, explica el peligro en una frase,
  da las instrucciones de evacuación (ruta y punto de encuentro), pregunta si necesita ayuda para salir
  (movilidad, personas a cargo, animales) y si ve algo relevante (humo, fuego, dirección). Repite la
  instrucción clave antes de despedirte.
- **commander** (mando de bomberos/brigada): tono profesional y directo. Comunica la situación, la
  prioridad y la asignación propuesta; pregunta ETA, medios disponibles y si acepta la asignación.
  Recoge cualquier información táctica nueva.
- **police / mayor**: comunica la situación y lo que se necesita (cortes de tráfico, aviso vecinal).

# Reglas
- No inventes datos: si te preguntan algo que no sabes, dilo y ofrece que el centro les llamará.
- Si recibes una señal (signal) con instrucciones nuevas (p.ej. "el viento ha girado"), interrumpe con
  tacto y transmite la nueva instrucción de inmediato.
- Antes de terminar, llama SIEMPRE a la herramienta `registrar_resultado` con el resultado de la
  llamada. Después despídete y termina.
""",
)

RESULTADO = r'''
import json as _json
outcome = (input_data.get("outcome") or "unknown").strip().lower()
if outcome not in ("accepted", "refused", "no_answer", "needs_help", "already_safe", "unknown"): outcome = "unknown"
status = "done" if outcome in ("accepted", "already_safe", "no_answer") else ("failed" if outcome == "refused" else "done")
new_info = (input_data.get("new_info") or "").strip()
result = {"outcome": outcome, "notes": input_data.get("notes"), "new_info": new_info, "needs_help": outcome == "needs_help",
          "run_id": input_data.get("run_id"), "at": input_data.get("now")}
output = {"status": status, "result_json": _json.dumps(result, ensure_ascii=False), "has_new_info": bool(new_info),
          "summary": ("Aviso en llamada con %s (%s): %s" % (input_data.get("contact_name"), input_data.get("place"), new_info))[:300]}
'''

spec = WorkflowSpec(
    key="outbound_voice",
    name="SOS · Llamada saliente (web call)",
    icon="phone",
    description="Agente de voz que llama (web call simulado) a ciudadanos o mandos con instrucciones concretas.",
    trigger=Trigger(T, "web_call", config={"require_webcall_auth": True, "open_runs_page_on_trigger": False}, sample=SAMPLE).add(
        # La llamada empieza: la acción pasa a 'executing' con el run_id (para escuchar/tomar control).
        TwinWrite(
            "marcar_executing", "actions", primary="id",
            values={
                "id": ("uuid", Ref(T, "action_id")),
                "incident_id": ("uuid", Ref(T, "incident_id")),
                "kind": ("text", Ref(T, "kind")),
                "status": ("text", "executing"),
                "run_id": ("text", Ref("$current", "run_id")),
                "updated_at": ("timestamp", Ref("$time", "now_iso")),
            },
            outputs={"ok": True},
        ).add(
            Agent(
                "agente", "inbound_voice_agent", PROMPT,
                config=voice_agent_config("Flare"),
                initial_message=P("Hola, le llamo del Centro de Coordinación de Emergencias. ¿Hablo con ", Ref(T, "contact_name"), "?"),
                signals=["incident.*"],
            ).add(
                Tool(
                    "registrar_resultado",
                    "Registra el resultado de la llamada. Llámala una vez, justo antes de despedirte.",
                    [
                        {"name": "outcome", "description": "accepted | refused | no_answer | needs_help | already_safe | unknown", "required": True, "example": "accepted"},
                        {"name": "notes", "description": "Resumen de lo hablado en 1-2 frases", "required": True},
                        {"name": "new_info", "description": "Información nueva y relevante que haya aportado la persona (lo que ve, dirección del fuego, personas atrapadas). Vacío si no hay.", "required": False},
                    ],
                    Python(
                        "resultado_prep", RESULTADO,
                        inputs={"outcome": Ref("registrar_resultado", "outcome"), "notes": Ref("registrar_resultado", "notes"),
                                "new_info": Ref("registrar_resultado", "new_info"), "contact_name": Ref(T, "contact_name"),
                                "place": Ref(T, "place"), "run_id": Ref("$current", "run_id"), "now": Ref("$time", "now_iso")},
                        outputs={"status": "done", "result_json": "{}", "has_new_info": False, "summary": "s"},
                    ).add(
                        TwinWrite(
                            "resultado_write", "actions", primary="id",
                            values={
                                "id": ("uuid", Ref(T, "action_id")),
                                "incident_id": ("uuid", Ref(T, "incident_id")),
                                "kind": ("text", Ref(T, "kind")),
                                "status": ("text", Ref("resultado_prep", "status")),
                                "result": ("jsonb", Ref("resultado_prep", "result_json")),
                                "executed_at": ("timestamp", Ref("$time", "now_iso")),
                                "updated_at": ("timestamp", Ref("$time", "now_iso")),
                            },
                            outputs={"ok": True},
                        ).add(
                            Paths(
                                "info_rutas",
                                When("hay_info", Ref("resultado_prep", "has_new_info"), "boolean_true", None,
                                     CallWorkflow(
                                         "nueva_evidencia", "ingest", fire_and_forget=True,
                                         data={"source_type": "call", "source_ref": Ref("$current", "run_id"),
                                               "lat": Ref(T, "incident_lat"), "lon": Ref(T, "incident_lon"),
                                               "observed_at": Ref("$time", "now_iso"), "reliability": "0.6",
                                               "incident_type": "unknown", "summary": Ref("resultado_prep", "summary"),
                                               "details_json": Ref("resultado_prep", "result_json")},
                                     )),
                                Otherwise("sin_info", Python("fin", "output={'ok': True}", outputs={"ok": True})),
                            )
                        )
                    ),
                    expose=["status"],
                )
            )
        )
    ),
)
