"""Esquema de la base de datos Twin (Postgres gestionado por HappyRobot).

Se declara en Python y se traduce a DDL idempotente (`CREATE TABLE IF NOT EXISTS`,
`CREATE OR REPLACE VIEW`). Sin PostGIS: lat/lon en float8 y geometría en Python.

Para añadir un tipo de desastre, sensor o canal NO hace falta tocar el esquema:
`incidents.type`, `evidence.source_type` y `actions.kind` son texto libre validado
por `config`.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Column:
    name: str
    type: str  # int8 | int4 | float8 | text | boolean | timestamp | uuid | jsonb
    primary: bool = False
    nullable: bool = True
    default: str | None = None
    references: str | None = None  # "tabla(columna)"

    def ddl(self) -> str:
        parts = [self.name, self.type]
        if self.primary:
            parts.append("PRIMARY KEY")
        if self.default is not None:
            parts.append(f"DEFAULT {self.default}")
        if not self.nullable and not self.primary:
            parts.append("NOT NULL")
        if self.references:
            parts.append(f"REFERENCES {self.references}")
        return " ".join(parts)


@dataclass(frozen=True)
class Table:
    name: str
    columns: list[Column]
    indexes: list[str] = field(default_factory=list)  # expresiones de columnas
    unique: list[str] = field(default_factory=list)  # índices únicos (idempotencia del seed)
    description: str = ""

    def ddl(self) -> list[str]:
        cols = ",\n  ".join(c.ddl() for c in self.columns)
        stmts = [f"CREATE TABLE IF NOT EXISTS {self.name} (\n  {cols}\n)"]
        for expr in self.indexes:
            stmts.append(f"CREATE INDEX IF NOT EXISTS {_idx(self.name, expr)} ON {self.name} ({expr})")
        for expr in self.unique:
            stmts.append(f"CREATE UNIQUE INDEX IF NOT EXISTS {_idx(self.name, expr, 'uq')} ON {self.name} ({expr})")
        return stmts


def _idx(table: str, expr: str, prefix: str = "idx") -> str:
    clean = expr.replace(",", "_").replace(" ", "").replace("(", "").replace(")", "")
    return f"{prefix}_{table}_{clean}"


@dataclass(frozen=True)
class View:
    name: str
    sql: str
    description: str = ""

    def ddl(self) -> list[str]:
        return [f"CREATE OR REPLACE VIEW {self.name} AS\n{self.sql}"]


def _uuid_pk() -> Column:
    return Column("id", "uuid", primary=True, default="gen_random_uuid()")


def _ts(name: str = "created_at") -> Column:
    return Column(name, "timestamp", nullable=False, default="now()")


TABLES: list[Table] = [
    Table(
        "config",
        [
            Column("key", "text", primary=True),
            Column("value", "jsonb", nullable=False),
            Column("description", "text"),
            _ts("updated_at"),
        ],
        description="Pesos, umbrales y reglas de negocio editables sin redeploy.",
    ),
    Table(
        "assets",
        [
            _uuid_pk(),
            Column("ref", "text"),  # clave estable del seed/simulador (p.ej. "serra")
            Column("name", "text", nullable=False),
            Column("kind", "text", nullable=False),  # town|hospital|school|plant|port|forest_reserve
            Column("lat", "float8", nullable=False),
            Column("lon", "float8", nullable=False),
            Column("population", "int8", default="0"),
            Column("insured_value", "float8", default="0"),
            Column("carbon_credit_value", "float8", default="0"),
            Column("hazard_class", "text"),  # forest|chemical|industrial|maritime
            Column("priority_weight", "float8", default="1"),
            Column("metadata", "jsonb", default="'{}'::jsonb"),
            _ts(),
        ],
        indexes=["kind"],
        unique=["ref"],
        description="Lo que hay que proteger: núcleos, infraestructuras, reservas.",
    ),
    Table(
        "contacts",
        [
            _uuid_pk(),
            Column("ref", "text"),  # clave estable del seed/simulador (p.ej. "serra")
            Column("name", "text", nullable=False),
            Column("role", "text", nullable=False),  # citizen|commander|police|mayor
            Column("phone", "text"),
            Column("asset_id", "uuid", references="assets(id)"),
            Column("language", "text", default="'es'"),
            Column("priority", "int8", default="100"),
            Column("notes", "text"),
            _ts(),
        ],
        indexes=["role", "asset_id"],
        unique=["ref"],
        description="A quién llamar y en qué orden.",
    ),
    Table(
        "resources",
        [
            _uuid_pk(),
            Column("ref", "text"),  # clave estable del seed/simulador (p.ej. "serra")
            Column("name", "text", nullable=False),
            Column("kind", "text", nullable=False),  # brigade|hydroplane|foam_unit|drone|police
            Column("capabilities", "jsonb", default="'[]'::jsonb"),  # ["water","foam","recon"]
            Column("lat", "float8", nullable=False),
            Column("lon", "float8", nullable=False),
            Column("status", "text", default="'available'"),  # available|en_route|deployed|refilling
            Column("assigned_incident_id", "uuid"),
            Column("eta_min", "float8"),
            Column("contact_id", "uuid", references="contacts(id)"),
            Column("metadata", "jsonb", default="'{}'::jsonb"),
            _ts("updated_at"),
        ],
        indexes=["status", "kind"],
        unique=["ref"],
        description="Medios operativos y su estado.",
    ),
    Table(
        "incidents",
        [
            _uuid_pk(),
            Column("type", "text", nullable=False, default="'unknown'"),
            Column("status", "text", nullable=False, default="'candidate'"),
            Column("lat", "float8", nullable=False),
            Column("lon", "float8", nullable=False),
            Column("confidence", "float8", default="0"),
            Column("risk_score", "float8", default="0"),
            Column("priority", "int8", default="0"),
            Column("summary", "text"),
            Column("ai_assessment", "jsonb", default="'{}'::jsonb"),
            Column("plan_id", "uuid"),
            _ts(),
            _ts("updated_at"),
        ],
        indexes=["status", "type"],
        description="El caso: candidato → verificado/descartado → activo → contenido → cerrado.",
    ),
    Table(
        "evidence",
        [
            _uuid_pk(),
            Column("incident_id", "uuid", references="incidents(id)"),
            Column("source_type", "text", nullable=False),  # call|firms|weather|drone|sensor|manual
            Column("source_ref", "text"),
            Column("lat", "float8"),
            Column("lon", "float8"),
            Column("observed_at", "timestamp", nullable=False, default="now()"),
            Column("reliability", "float8", default="0.5"),
            Column("payload", "jsonb", default="'{}'::jsonb"),
            Column("run_id", "text"),
            _ts(),
        ],
        indexes=["incident_id", "source_type", "observed_at"],
        description="Toda entrada cruda; se agrupa a un incidente por proximidad y tiempo.",
    ),
    Table(
        "weather_observations",
        [
            _uuid_pk(),
            Column("incident_id", "uuid", references="incidents(id)"),
            Column("lat", "float8", nullable=False),
            Column("lon", "float8", nullable=False),
            Column("wind_speed_kmh", "float8"),
            Column("wind_dir_deg", "float8"),
            Column("temp_c", "float8"),
            Column("humidity", "float8"),
            Column("observed_at", "timestamp", nullable=False, default="now()"),
            Column("source", "text", default="'open-meteo'"),
            _ts(),
        ],
        indexes=["incident_id, observed_at"],
        description="Serie meteorológica por incidente; base para detectar giros de viento.",
    ),
    Table(
        "plans",
        [
            _uuid_pk(),
            Column("incident_id", "uuid", nullable=False, references="incidents(id)"),
            Column("version", "int8", nullable=False, default="1"),
            Column("summary", "text"),
            Column("priorities", "jsonb", default="'[]'::jsonb"),
            Column("resource_plan", "jsonb", default="'[]'::jsonb"),
            Column("notification_order", "jsonb", default="'[]'::jsonb"),
            Column("status", "text", default="'current'"),  # current|superseded
            Column("created_by_run", "text"),
            _ts(),
        ],
        indexes=["incident_id, status"],
        description="Histórico de planes: cada recálculo crea una versión nueva.",
    ),
    Table(
        "actions",
        [
            _uuid_pk(),
            Column("incident_id", "uuid", nullable=False, references="incidents(id)"),
            Column("plan_id", "uuid", references="plans(id)"),
            Column("kind", "text", nullable=False),  # evacuate_call|coordination_call|dispatch|notify
            Column("status", "text", nullable=False, default="'proposed'"),
            Column("requires_approval", "boolean", nullable=False, default="true"),
            Column("contact_id", "uuid", references="contacts(id)"),
            Column("resource_id", "uuid", references="resources(id)"),
            Column("priority", "int8", default="100"),
            Column("rationale", "text"),
            Column("payload", "jsonb", default="'{}'::jsonb"),
            Column("run_id", "text"),
            Column("session_id", "text"),
            Column("result", "jsonb"),
            Column("decided_by", "text"),
            Column("decided_at", "timestamp"),
            Column("executed_at", "timestamp"),
            _ts(),
            _ts("updated_at"),
        ],
        indexes=["incident_id", "status", "kind"],
        description="Cola de acciones propuestas por la IA; el humano aprueba con 1 clic.",
    ),
]

VIEWS: list[View] = [
    View(
        "v_open_incidents",
        """
SELECT i.*,
       (SELECT count(*) FROM evidence e WHERE e.incident_id = i.id) AS evidence_count,
       (SELECT count(*) FROM actions a WHERE a.incident_id = i.id AND a.status = 'proposed') AS pending_actions
FROM incidents i
WHERE i.status NOT IN ('closed', 'dismissed')
ORDER BY i.priority DESC, i.risk_score DESC, i.created_at DESC
""",
        "Incidentes abiertos con contadores para el dashboard.",
    ),
    View(
        "v_pending_actions",
        """
SELECT a.*, i.type AS incident_type, i.summary AS incident_summary,
       c.name AS contact_name, c.role AS contact_role, c.phone AS contact_phone,
       r.name AS resource_name, r.kind AS resource_kind
FROM actions a
JOIN incidents i ON i.id = a.incident_id
LEFT JOIN contacts c ON c.id = a.contact_id
LEFT JOIN resources r ON r.id = a.resource_id
WHERE a.status IN ('proposed', 'approved', 'ready', 'executing')
ORDER BY a.priority ASC, a.created_at ASC
""",
        "Acciones pendientes de decisión o ejecución.",
    ),
    View(
        "v_latest_weather",
        """
SELECT DISTINCT ON (incident_id) *
FROM weather_observations
WHERE incident_id IS NOT NULL
ORDER BY incident_id, observed_at DESC
""",
        "Última observación meteorológica por incidente.",
    ),
    View(
        "v_active_calls",
        """
SELECT a.id AS action_id, a.kind, a.session_id, a.run_id, a.status, a.incident_id,
       c.name AS contact_name, c.role AS contact_role
FROM actions a
LEFT JOIN contacts c ON c.id = a.contact_id
WHERE a.status = 'executing' AND a.session_id IS NOT NULL
""",
        "Llamadas en curso (para escuchar/tomar el control desde el dashboard).",
    ),
]


def all_ddl() -> list[str]:
    stmts: list[str] = []
    for t in TABLES:
        stmts += t.ddl()
    for v in VIEWS:
        stmts += v.ddl()
    return stmts
