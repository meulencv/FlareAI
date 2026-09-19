"""WF-Execute: ejecuta UNA acción aprobada (o auto-aprobada) según su tipo.

Entrada (Workflow Function): action_id.

Adapters por tipo (`actions.kind`):
  evacuate_call / coordination_call → canal de voz según config.channels.voice:
      webcall (demo): la acción pasa a `ready`; el dashboard la muestra en "Sala de llamadas" y,
      al descolgar, el navegador abre WF-Outbound-Voice con los datos de la acción.
      phone (futuro): Outbound Voice Agent con número real (requiere SIP/número en la org).
  dispatch → el medio pasa a `en_route` asignado al incidente; la acción a `done`.
  notify   → (placeholder: Slack/email) la acción a `done`.

Para añadir un canal o tipo de acción nuevo: añadir una rama en `rutas` y, si hace falta,
una clave en config.channels.
"""

from ._builder import Otherwise, Paths, Python, Raw, Ref, Trigger, TwinSQL, TwinWrite, When, WorkflowSpec
from ._sqlgen import SQL_HELPERS

SAMPLE = {"action_id": "00000000-0000-0000-0000-000000000003"}

SQL_ACCION = SQL_HELPERS + r'''
aid = (input_data.get("action_id") or "").strip()
sql = """
SELECT a.id::text AS id, a.incident_id::text AS incident_id, a.kind, a.status, a.priority, a.payload::text AS payload,
       a.contact_id::text AS contact_id, a.resource_id::text AS resource_id,
       c.name AS contact_name, c.role AS contact_role, c.phone AS contact_phone,
       r.name AS resource_name, r.kind AS resource_kind, r.lat AS resource_lat, r.lon AS resource_lon,
       i.type AS incident_type, i.summary AS incident_summary, i.lat AS incident_lat, i.lon AS incident_lon,
       COALESCE((SELECT value->>'voice' FROM config WHERE key = 'channels'), 'webcall') AS voice_channel,
       CASE WHEN a.kind IN ('evacuate_call','coordination_call') THEN 'voice' ELSE a.kind END AS route
FROM actions a
LEFT JOIN contacts c ON c.id = a.contact_id
LEFT JOIN resources r ON r.id = a.resource_id
JOIN incidents i ON i.id = a.incident_id
WHERE a.id = %s
""" % q(aid)
output = {"sql": " ".join(sql.split())}
'''

T = "entrada"
A = "accion"


def a(field: str) -> Ref:
    return Ref(A, f"rows.0.{field}")


def _mark(name: str, status: str, extra: dict | None = None) -> TwinWrite:
    """Upsert de la acción con su nuevo estado (hay que repetir las columnas NOT NULL)."""
    values = {
        "id": ("uuid", a("id")),
        "incident_id": ("uuid", a("incident_id")),
        "kind": ("text", a("kind")),
        "status": ("text", status),
        "updated_at": ("timestamp", Ref("$time", "now_iso")),
    }
    values.update(extra or {})
    return TwinWrite(name, "actions", primary="id", values=values, outputs={"ok": True})


spec = WorkflowSpec(
    key="execute",
    name="SOS · Ejecución de acción",
    icon="bolt",
    description="Ejecuta una acción aprobada: llamada (web call), despacho de medios o notificación.",
    trigger=Trigger(T, "workflow_function_request", sample=SAMPLE).add(
        Python("sql_accion", SQL_ACCION, inputs={"action_id": Ref(T, "action_id")}, outputs={"sql": "SELECT 1"}).add(
            TwinSQL(
                A, Raw(Ref("sql_accion", "sql")), max_rows=1,
                outputs={"rows": [{"id": "00000000-0000-0000-0000-000000000003", "incident_id": "00000000-0000-0000-0000-000000000000",
                                   "kind": "evacuate_call", "status": "approved", "priority": 1, "payload": "{}",
                                   "contact_id": "", "resource_id": "", "contact_name": "María", "contact_role": "citizen",
                                   "contact_phone": "+34600000001", "resource_name": "", "resource_kind": "", "resource_lat": 0.0,
                                   "resource_lon": 0.0, "incident_type": "wildfire", "incident_summary": "s", "incident_lat": 39.7,
                                   "incident_lon": -0.47, "voice_channel": "webcall", "route": "voice"}]},
            ).add(
                Paths(
                    "rutas",
                    When(
                        "es_voz", a("route"), "text_equals", "voice",
                        Paths(
                            "canal_voz",
                            When(
                                "canal_webcall", a("voice_channel"), "text_equals", "webcall",
                                # La llamada la inicia el navegador (web call): dejamos la acción lista.
                                _mark("marcar_ready", "ready"),
                            ),
                            Otherwise(
                                "canal_phone",
                                # Adapter de teléfono real: pendiente de número/SIP en la organización.
                                Python("phone_no_disponible", "output={'error': 'canal phone no configurado: falta número/SIP en la org'}",
                                       outputs={"error": "x"}).add(_mark("marcar_failed_phone", "failed")),
                            ),
                        ),
                    ),
                    When(
                        "es_dispatch", a("route"), "text_equals", "dispatch",
                        TwinWrite(
                            "despachar_medio", "resources", primary="id",
                            values={
                                "id": ("uuid", a("resource_id")),
                                "name": ("text", a("resource_name")),
                                "kind": ("text", a("resource_kind")),
                                "lat": ("float8", a("resource_lat")),
                                "lon": ("float8", a("resource_lon")),
                                "status": ("text", "en_route"),
                                "assigned_incident_id": ("uuid", a("incident_id")),
                                "updated_at": ("timestamp", Ref("$time", "now_iso")),
                            },
                            outputs={"ok": True},
                        ).add(_mark("marcar_done_dispatch", "done", {"executed_at": ("timestamp", Ref("$time", "now_iso"))})),
                    ),
                    Otherwise(
                        "es_notify",
                        # Placeholder de notificación (Slack/email): se marca como hecha.
                        _mark("marcar_done_notify", "done", {"executed_at": ("timestamp", Ref("$time", "now_iso"))}),
                    ),
                )
            )
        )
    ),
)
