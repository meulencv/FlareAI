---
tags: [happyrobot, proyecto]
---

# Base de datos local embebida (mientras Twin no está provisionado)

Requisito del usuario: **nada instalado fuera de la carpeta del proyecto** (se deshizo un
`brew install postgresql@17` inicial). Solución: binarios de Postgres 17 de *zonky embedded-postgres*
(Maven Central, `embedded-postgres-binaries-darwin-arm64v8`) descomprimidos en `.local/pg/dist`,
datos en `.local/pg/data`, puerto `127.0.0.1:54329`, usuario `sos`, db `sos`. Todo en `.gitignore`.
Cliente: `psycopg[binary]` en el venv.

```bash
python -m sos db start|stop|status      # gestiona el servidor (pg_ctl)
python -m sos db which                  # backend activo según SOS_DB (auto|local|twin)
python -m sos twin migrate && python -m sos twin seed
python -m sos twin sql "select * from v_open_incidents"
```

`sos/db/base.py` expone la **misma interfaz que Twin** (`sql()` → `{command, rowCount, rows}`),
con dos backends: `LocalDatabase` (psycopg) y `TwinDatabase` (`POST /twin/sql`). `get_database()`
elige Twin si `POST /twin/sql` responde (necesita Twin provisionado **y** key con `twin.manage`).

## Pasar a Twin cuando esté disponible

```bash
python -m sos twin migrate            # SOS_DB=auto → Twin (mismo DDL)
python -m sos twin sync-to-twin       # copia config/assets/contacts/resources del local a Twin
python -m sos deploy weather_feeder firms_feeder   # republica los cron
python main_simulation.py --cloud
```

Si el bundle no está (`.local/pg/dist` vacío), descargarlo:
```bash
V=17.11.0; cd .local/pg && curl -sLO https://repo1.maven.org/maven2/io/zonky/test/postgres/embedded-postgres-binaries-darwin-arm64v8/$V/embedded-postgres-binaries-darwin-arm64v8-$V.jar \
 && unzip -o -q *.jar && mkdir -p dist && tar -xJf postgres-darwin-arm_64.txz -C dist
```
(El bundle no trae `psql`/`createdb`: la base `sos` se crea con psycopg.)

Relacionado: [[Twin - base de datos]] · [[Esquema de datos SOS]] · [[Intérprete local de workflows]]
