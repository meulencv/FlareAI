---
tags: [happyrobot, concepto]
---

# Twin — la base de datos de HappyRobot

**Twin** es un **PostgreSQL gestionado por organización** (RDS aislado), integrado en la plataforma:
esquema visual, consola SQL, nodos de workflow, API REST, MCP server y un *API Gateway* opcional
para Apps externas. Es "la base de datos relacional de la plataforma" a la que se refiere el reto.

## Cómo se accede

| Vía | Qué permite | Auth |
|---|---|---|
| Nodos **Read from Twin / Write to Twin / Query Twin with SQL** | leer/insertar/upsert/SELECT desde un workflow | corren *como la org*, sin credenciales |
| `POST /api/v2/twin/sql` | **cualquier SQL** (DDL incluido) | API key con permiso `twin.manage` |
| `POST /twin/tables`, `/twin/tables/{t}/rows` (POST/PATCH/DELETE), `GET /twin/schema` | CRUD de tablas y filas | API key |
| `POST /twin/dump` | volcado automático de variables de runs a una tabla | API key |
| Polling tables (UI) | tabla sincronizada desde un endpoint HTTP con cursor | UI |
| Twin MCP (`mcp.platform.eu.happyrobot.ai/twin/mcp`) | explorar/consultar desde Claude Code, etc. | OAuth |

Tipos de columna: `int8 int4 float8 float4 text boolean timestamp uuid jsonb`. FK y vistas sí;
**sin PostGIS** (geometría en Python: haversine/rumbo, ver [[Motor de riesgo]]).
Límites: SELECT ≤ 500 filas / 1 MB; timeout 20 s (5 s vía MCP).

## Estado actual, revisión posterior del 19/09/2026

Twin ya responde a `GET /twin/schema`. La credencial habitual de voz permite leer el esquema pero
recibió 403 al ejecutar SQL; la credencial facilitada específicamente para Twin ejecutó `SELECT 1`
correctamente. No se guardan sus valores en el vault.

La decisión actual es **Twin para datos dinámicos; atlas, grafos y cachés en local**. `twin.py` crea
`flare_live_sessions`, `flare_live_calls`, `flare_live_state`, `flare_live_events`, `flare_live_settings`,
`flare_live_documents`, `flare_live_leases`, `flare_live_web_requests` y `flare_contacts`.
Se verificaron estado/eventos sin duplicados, contactos ordenados y reserva idempotente de webcalls.

Los `int8` llegan como strings y se normalizan por el tipo de columna. Una respuesta truncada obliga
a paginar; nunca se interpreta como un resultado completo. El endpoint rechazó una sentencia
`WITH … INSERT`: se usa una función PostgreSQL versionada para guardar estado y eventos atómicamente.
Una conexión HTTP no mantiene una transacción ni un advisory lock entre peticiones; el director usa
un lease renovable. Más detalles en [[2026-09-19#Presentación con testimonios, Twin y parte telefónico]].

## Estado inicial de la organización (histórico)

- Al principio del 2026-09-19 Twin **no estaba provisionado**: `GET /twin/schema` → `404 "Twin database
  not available"`. Se activa en la web: **Settings → Twin Database → Enable Twin** (permiso
  *Manage Twin database instance*), o pidiéndolo al soporte del hackathon.
- La API key actual **no tiene `twin.manage`**: `POST /twin/sql` → `403 "API key cannot perform
  action twin.manage"`. Hace falta una key con *Full Twin access* para `sos twin migrate` contra
  Twin. Los **nodos** de Twin dentro de los workflows no necesitan ese permiso.
- Mientras tanto usamos un **Postgres embebido local** con la misma interfaz → [[Base de datos local embebida]].

## Formatos de los nodos (descubiertos por prueba/error)

```json
// Write to Twin — upsert si alguna columna lleva isPrimary=true
{"tableName": "incidents", "columnValues": [
  {"columnName": "id", "type": "uuid", "isPrimary": true, "value": [PARAGRAPH]},
  {"columnName": "status", "type": "text", "isPrimary": false, "value": [PARAGRAPH]}]}

// Read from Twin
{"tableName": "assets", "filters": [{"column": "kind", "operator": "equals", "value": [PARAGRAPH]}],
 "limit": [PARAGRAPH], "orderByColumn": "name", "orderByDirection": "asc"}
// operadores: equals|not_equal|greater_than|less_than|greater_or_equal|less_or_equal|contains

// Query Twin with SQL (solo SELECT/WITH)
{"sql": "select * from incidents where id = '{{$var:<node_id>.incident_id}}'", "maxRows": 100}
```

Ojo con el upsert: `INSERT … ON CONFLICT` comprueba NOT NULL **antes** de resolver el conflicto,
así que al "actualizar" una fila con Write to Twin hay que repetir todas las columnas NOT NULL
(por eso nuestros upserts de `actions` llevan siempre `incident_id` y `kind`).

Relacionado: [[Base de datos local embebida]] · [[Esquema de datos SOS]] · [[Formato de nodos por API]] · [[Problemas y soluciones]]
