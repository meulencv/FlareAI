"""Lista de workflows a desplegar. El deployer crea primero todos los workflows vacíos (para
poder referenciarse entre sí con Call Workflow) y luego construye sus nodos."""

from __future__ import annotations

from ._builder import WorkflowSpec


def all_specs() -> list[WorkflowSpec]:
    from . import approve, assess, citizen_inbound, execute, firms_feeder, ingest, outbound_voice, weather

    return [ingest.spec, assess.spec, execute.spec, approve.spec, outbound_voice.spec, citizen_inbound.spec,
            weather.inject, weather.feeder, firms_feeder.spec]


def by_key() -> dict[str, WorkflowSpec]:
    return {s.key: s for s in all_specs()}
