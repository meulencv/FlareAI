"""WF-Approve: decisión humana (Human-in-the-loop) sobre una acción propuesta.

Entrada (hook): action_id, decision (approve | reject), operator, note.
Marca la acción y, si se aprueba, llama a WF-Execute.
"""

from ._builder import CallWorkflow, Otherwise, Paths, Python, Raw, Ref, Trigger, TwinSQL, TwinWrite, When, WorkflowSpec
from ._sqlgen import SQL_HELPERS

SAMPLE = {"action_id": "00000000-0000-0000-0000-000000000003", "decision": "approve", "operator": "operador-1", "note": ""}

SQL = SQL_HELPERS + r'''
aid = (input_data.get("action_id") or "").strip()
decision = (input_data.get("decision") or "").strip().lower()
status = "approved" if decision in ("approve", "approved", "yes", "ok") else "rejected"
output = {"sql": "SELECT id::text AS id, incident_id::text AS incident_id, kind, status FROM actions WHERE id = %s" % q(aid),
          "new_status": status, "approved": status == "approved"}
'''

T = "entrada"

spec = WorkflowSpec(
    key="approve",
    name="SOS · Aprobación humana",
    icon="check",
    description="El operador aprueba o rechaza una acción propuesta por la IA (1 clic en el dashboard).",
    trigger=Trigger(T, "incoming_hook", sample=SAMPLE).add(
        Python("preparar", SQL, inputs={"action_id": Ref(T, "action_id"), "decision": Ref(T, "decision")},
               outputs={"sql": "SELECT 1", "new_status": "approved", "approved": True}).add(
            TwinSQL("accion", Raw(Ref("preparar", "sql")), max_rows=1,
                    outputs={"rows": [{"id": "00000000-0000-0000-0000-000000000003", "incident_id": "00000000-0000-0000-0000-000000000000", "kind": "evacuate_call", "status": "proposed"}]}).add(
                TwinWrite(
                    "marcar", "actions", primary="id",
                    values={
                        "id": ("uuid", Ref("accion", "rows.0.id")),
                        "incident_id": ("uuid", Ref("accion", "rows.0.incident_id")),
                        "kind": ("text", Ref("accion", "rows.0.kind")),
                        "status": ("text", Ref("preparar", "new_status")),
                        "decided_by": ("text", Ref(T, "operator")),
                        "decided_at": ("timestamp", Ref("$time", "now_iso")),
                        "updated_at": ("timestamp", Ref("$time", "now_iso")),
                    },
                    outputs={"ok": True},
                ).add(
                    Paths(
                        "rutas",
                        When("aprobada", Ref("preparar", "approved"), "boolean_true", None,
                             CallWorkflow("ejecutar", "execute", data={"action_id": Ref(T, "action_id")}, fire_and_forget=True)),
                        Otherwise("rechazada", Python("fin", "output={'rejected': True}", outputs={"rejected": True})),
                    )
                )
            )
        )
    ),
)
