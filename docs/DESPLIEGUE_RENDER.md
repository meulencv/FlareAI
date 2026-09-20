# Despliegue del centro Python en Render

Guía para ejecutar en [Render](https://render.com) exactamente lo que hoy corre en local:
`app.py --presentation` con PostgreSQL, el marcador `/112/`, el receptor `/112/alerts/`, el director
HappyRobot y Twin. El Blueprint `render.yaml` de la raíz describe los dos recursos; esta guía cubre lo
que el Blueprint no puede hacer solo (secretos y estado local que no está en el repositorio).

Referencia consultada el 20/09/2026: [Blueprint spec](https://render.com/docs/blueprint-spec),
[Python version](https://render.com/docs/python-version), [Web services](https://render.com/docs/web-services),
[Health checks](https://render.com/docs/health-checks), [Deploys](https://render.com/docs/deploys),
[Render Postgres](https://render.com/docs/postgresql-creating-connecting), [Free tier](https://render.com/docs/free),
[Environment variables](https://render.com/docs/environment-variables), [Pricing](https://render.com/pricing).

## Qué se despliega

| Recurso | Blueprint | Motivo |
|---|---|---|
| Web service `flareai` | `runtime: python`, plan `1c-2g` (1 CPU, 2 GB, 25 $/mes), región `frankfurt` | El proceso en presentación ocupa ~650 MB de RSS en local: los planes de 512 MB (`free`, `0.5c-512mb`) no bastan. Frankfurt es la región europea; HappyRobot/Twin están en `platform.eu.happyrobot.ai`. |
| Render Postgres `flareai-db` | plan `0.1c-256mb` (6 $/mes), PostgreSQL 17, disco 5 GB | La base local ocupa ~1 GB (859 MB son la rejilla de 1 km² con el JSON completo de cada celda). 1 GB incluido; disco extra a 0,30 $/GB. |

Python: `.python-version` fija **3.13**. Todas las dependencias de `requirements.txt` tienen ruedas
binarias `manylinux` para 3.13 (numpy, shapely, Pillow, psycopg-binary, eccodeslib/eckitlib); con 3.14
(el intérprete local) numpy 2.2.6 y shapely 2.1.1 se compilarían desde fuente en Render. Se ha comprobado
que todos los módulos del proyecto importan y compilan con CPython 3.13.15 y esos paquetes.

El servicio se ejecuta en el mismo modo que el local: `python app.py --presentation --host 0.0.0.0 --port $PORT`.
Render exige escuchar en `0.0.0.0` y en el puerto de `PORT` (10000). El segundo servidor «móvil» (8112,
solo loopback) sigue arrancando pero no se publica: el puerto principal ya sirve `/112/` y `/112/alerts/`.

## Cambios en el código para Render (20/09/2026)

- `app.py`: `--port` toma por defecto `PORT` si existe; `FLAREAI_ALLOW_OUTBOUND=1` equivale a
  `--allow-outbound` (el comando de arranque de Render es fijo). `SIGTERM` se trata como Ctrl-C para
  cerrar ordenadamente: libera el lease de la sala en Twin, detiene el director y cierra la demo.
- `GET /healthz`: sonda HTTP para `healthCheckPath`. Responde `{"ok": true, "director": <estado>}` solo
  cuando el proceso ya sirve (datos, escenario y grafo cargados); Render espera hasta 15 minutos.
- `FLAREAI_PUBLIC_CONTROLS=1`: tras el proxy de Render la dirección del cliente nunca es loopback, así que
  `/api/scenario`, `/api/director/cancel-alert`, `/api/admin/reset` y `/api/demo/setup` se aceptan de
  cualquier cliente. Se mantiene la comprobación `Origin == Host`, que bloquea órdenes desde otros sitios,
  pero **cualquiera con la URL puede usar el editor del escenario y el reinicio de la demo**, igual que
  puede consumir cuota desde el marcador 112. No lo actives en un servidor expuesto que no sea la demo.
- `/api/demo/setup`: sin túnel ni App alojada, enlaza `/112/` y `/112/alerts/` sobre la URL pública del
  servicio (`RENDER_EXTERNAL_URL`, o `FLAREAI_PUBLIC_URL` en otra plataforma), de modo que los botones
  «Webcall demo» y «ES-Alert demo» del mapa apuntan al propio despliegue.
- `data/seed/assets.jsonl.gz` (17 MB, versionado) + `database.py seed` / `Database.import_seed()`: la red
  viaria de Barcelona, grafos, rutas y geocodificación cacheados viajan **dentro del repositorio** y
  `bootstrap()` los carga en cualquier base vacía. No hace falta copiar la base local.
- `database.py push --url <destino>`: opcional; copia además `flare_settings` (solo `--hackathon`) y las
  comprobaciones de cámaras vigentes.
- `requirements.txt`: `eccodeslib` pasa a `2.48.3.28`, la versión realmente instalada en `.venv`
  (`2.48.2.27` no tiene ruedas para macOS y no se instalaba en este equipo; ambas las tienen para Linux).

## Estado que no viaja en el repositorio

`preDeployCommand: python database.py import` ejecuta `bootstrap()` en cada despliegue: esquema, atlas
(rejilla y OSM desde `data/Espana_Datos_y_Mapas/output`), catálogo de cámaras, instantáneas FIRMS/GFS
de `data/`, cartografía y la semilla de activos. Es idempotente y tarda ~40 s en local (0,6 s si ya está hecho); en el plan mínimo de Render puede
llevar unos minutos la primera vez. Se ejecuta en una instancia aparte, antes de arrancar el servicio.

Lo que la base local tenía y el repositorio no, y cómo llega ahora a Render:

| Dato | Dónde vive en local | En Render |
|---|---|---|
| Red viaria de Barcelona `barcelona-demo-road-v1` | `flare_assets` (PostgreSQL local) | **Semilla del repositorio** `data/seed/assets.jsonl.gz`, cargada por `bootstrap()` en el pre-deploy. Sin ella `app.py --presentation` falla al iniciar («Falta precargar Barcelona»). Las 16 teselas de preparación no van (solo sirven para reanudar `--prepare-demo`). |
| Grafos, rutas, geocodificación y reproductores cacheados (`local_road_graph`, `director_route`, `geocoding`, `player`) | `flare_assets` | Misma semilla. Evitan pedir Nominatim/IGN y OSRM para «Sagrada Familia» y las demás ubicaciones ya verificadas. |
| `flare_settings` (`director-workflow` con `hook_key`, `firefighter-workflow`) | PostgreSQL local | **No van al repositorio** (credenciales). En presentación el director lee `flare_live_settings` de Twin, que ya existen; solo `--hackathon` los necesita: `database.py push`. |
| Comprobaciones de cámaras (`flare_camera_checks`) | PostgreSQL local | Caducan en horas y el servidor las regenera; `push` puede copiar las vigentes. |
| Teselas IGN, imágenes de cámaras, satélite (`data/territorial`, `data/satellite`) | disco | No se copian: se vuelven a descargar bajo demanda. El disco de Render es efímero; las cachés de `data/` se rehacen en cada despliegue. |
| Claves | `happyrobot-112/.env`, `.env.presentation` | Variables de entorno del servicio (abajo). |
| Reproductores de cámaras verificados con Playwright | `.local/playwright-browsers` | Playwright no está en `requirements.txt`; el bucle lo registra como «Verificación de cámaras pendiente» cada 10 min y sigue verificando imágenes. Las cámaras de vídeo dependen de las comprobaciones copiadas hasta que caduquen. |

La semilla se regenera desde la base local con `python database.py seed` (gzip reproducible, `mtime=0`:
mismo SHA-256 si no cambian los activos). `import_seed()` se ejecuta una sola vez por contenido (marca
`seed:<sha256>` en `flare_imports`) e inserta con `ON CONFLICT DO NOTHING`: una caché más reciente en la
base nunca se pisa. Rechaza semillas con activos fuera de `SEED_ASSET_KINDS` o con `path`.
Las filas de más de 4 MB (el grafo de Barcelona, 43 MB de JSON, y cinco grafos zonales) **no se insertan**:
parsearlas a `jsonb` agotó la memoria del plan `0.1c-256mb` en el primer despliegue real (`SSL error:
unexpected eof`). `get_asset()` las lee del archivo cuando la base no las tiene (índice de ids una vez por
proceso, ~1 s; carga del grafo ~0,6 s, luego cacheado por el router). La base sigue mandando si existe la fila.

`push` sigue disponible y es idempotente (upserts): `{"sources": 11, "settings": 3, "assets": 255,
"camera_checks": 2884}` en la prueba. Las filas grandes (14,6 MB del grafo) se envían con `statement_timeout=0`.

## Pasos

1. **Blueprint.** En el panel de Render: *New → Blueprint*, conectar el repositorio, rama `main`. Render
   lee `render.yaml`, crea `flareai-db` y `flareai`, y pide los valores de las variables `sync: false`:
   `HAPPYROBOT_API_KEY` (la de `happyrobot-112/.env`) y `FLAREAI_TWIN_API_KEY` (la de `.env.presentation`,
   con acceso SQL). Nunca se pegan en el repositorio ni en esta guía.
2. **Nada que copiar.** El pre-deploy importa atlas, catálogo, cartografía y la semilla de activos del
   repositorio; el primer arranque ya encuentra la red de Barcelona. Solo si quieres además los ajustes
   locales (modo `--hackathon`) o las comprobaciones de cámaras: copiar la *External Database URL* de
   `flareai-db` (Info de la base) y, desde este equipo, con el PostgreSQL local en marcha:
   ```bash
   .venv/bin/python database.py push --url 'postgresql://USUARIO:CLAVE@HOST.frankfurt-postgres.render.com/flareai?sslmode=require'
   ```
   Render rechaza `sslmode=disable`; `require` evita cualquier degradación a texto claro.
   Si cambias rutas o grafos en local y quieres que viajen con el código: `python database.py seed` y
   versionar `data/seed/assets.jsonl.gz`.
3. **Un único director.** El lease de la sala en Twin (`flare_live_leases`) admite un solo director: si el
   servidor local sigue en `--presentation`, el de Render queda en `standby` (y `/healthz` lo indica) hasta
   que el local se cierre; al revés, igual. Parar el local antes de presentar desde Render. En un
   redespliegue, la instancia nueva arranca en `standby` y adquiere el lease ~2 s después de que la antigua
   reciba `SIGTERM` (o a los 90 s si cayó de golpe).
4. **Llamadas reales.** `FLAREAI_ALLOW_OUTBOUND` está a `"0"`. Cambiarlo a `"1"` en *Environment* del
   servicio (Render reinicia) solo para el ensayo autorizado con los contactos de `flare_contacts`.
5. **Comprobar.** `https://<servicio>.onrender.com/healthz` → `{"ok": true, "director": "idle"}`;
   `/api/director` con `scenario.network.nodes` = 370215; el mapa muestra «Webcall demo ↗» apuntando a
   `https://<servicio>.onrender.com/112/`. La cookie del marcador se marca `Secure` porque Render envía
   `X-Forwarded-Proto: https`; el micrófono del navegador requiere HTTPS, que Render termina en su proxy.

Variables del servicio (todas las que lee el código):

| Variable | Valor en Render | Uso |
|---|---|---|
| `FLAREAI_DATABASE_URL` | URL interna de `flareai-db` (Blueprint) | PostgreSQL en lugar de `.local/pg`. |
| `HAPPYROBOT_API_KEY` | secreto | Voz 112, director, Twin de lectura, llamadas salientes. |
| `FLAREAI_TWIN_API_KEY` | secreto | SQL en Twin (`/twin/sql`). |
| `FLAREAI_PUBLIC_CONTROLS` | `1` | Editor del escenario, reinicio y enlace 112 tras el proxy. |
| `FLAREAI_ALLOW_OUTBOUND` | `0`/`1` | Llamadas telefónicas reales. |
| `HAPPYROBOT_API_BASE` | (por defecto EU) | Solo si cambia la plataforma. |
| `FLAREAI_DEMO_ACCESS_CODE` | opcional | Fragmento del enlace a una App 112 alojada (`flare_live_settings['phone-web']`). |
| `FLAREAI_NOMINATIM_URL` | opcional | Proveedor Nominatim propio; vacío desactiva OSM. |
| `FLAREAI_PUBLIC_URL` | no necesaria en Render | Render ya expone `RENDER_EXTERNAL_URL`. |

## Límites y decisiones

- **Sin disco persistente.** Un disco solo puede montarse en un directorio, y `data/` contiene archivos
  versionados que quedarían ocultos. Las cachés (FIRMS, GFS, GIBS, teselas, informes PDF en
  `.local/operation-reports`, memorias en `FlareAI-Memoria/`) se regeneran; el estado que importa vive
  en Twin (dinámico) y PostgreSQL (estático). Además un disco desactiva los despliegues sin corte.
- **Un solo proceso.** `numInstances` queda en 1 (por defecto): la caché compartida, los bucles de
  actualización y el director suponen un único escritor. No escalar horizontalmente.
- **Despliegue automático.** Sin `autoDeployTrigger`, Render despliega cada push a `main`; un despliegue
  reinicia el proceso y pierde el estado en memoria de la sesión. Poner `autoDeployTrigger: 'off'` y usar
  *Manual Deploy* si se prefiere controlar el momento (p. ej. durante una presentación).
- **Plan gratuito.** No sirve: 512 MB de RAM, apagado tras 15 min sin tráfico (el director y la actualización
  se detienen), sin `preDeployCommand`, y la base gratuita (1 GB) caduca a los 30 días.
- **Tamaño del repositorio.** Git contiene ~455 MB (+17 MB de la semilla) (atlas, evidencias GRIB, documentación de HappyRobot):
  la clonación alarga cada build. Si molesta, apartar de Git lo que el servidor no lee en ejecución
  (`data/evidence`, `data/Espana_Datos_y_Mapas/raw` y `*.parquet`, `happyrobot_documentation/`,
  `versión-anterior/`) es una decisión pendiente; nada de esto se ha tocado.
- **Rejilla en PostgreSQL.** `flare_grid.data` guarda las ~60 columnas del CSV aunque `nearby_atlas()`
  solo usa `GRID_FIELDS`. Reducirla bajaría la base de ~1 GB a ~200 MB; no se ha cambiado para no alterar
  `test_database` ni el formato existente.
- **Twin y sesiones.** Cada arranque crea una sesión nueva en Twin y conserva el histórico, como en local.
  `/api/admin/reset` sigue disponible (con `FLAREAI_PUBLIC_CONTROLS`) para vaciar la demo.

## Verificación realizada en local (sin Render)

Simulación del despliegue con una copia que contiene **solo los archivos versionados** (sin `.env`,
`.local`, `data/territorial`), CPython 3.13.15 y `requirements.txt` instalado desde ruedas, contra una
base PostgreSQL vacía del clúster local:

1. `python database.py import` (pre-deploy): 40 s con la semilla (239 activos, 295 en total); una segunda
   ejecución tarda 0,6 s y no repite nada. 511.226 celdas, 44.787 instalaciones, 2.926 cámaras.
2. `database.py push` (opcional) desde el repositorio principal, dos veces (idempotente), y también en orden
   inverso (push sobre base vacía → import → push).
3. `app.py --hackathon --host 0.0.0.0 --port 10000` con `PORT`, `FLAREAI_PUBLIC_CONTROLS=1` y
   `RENDER_EXTERNAL_URL`, sobre la base sembrada solo por `import` (sin push): `/healthz` 200, `/api/data`
   `ready` con 48 focos, `/api/director` con red de 370.215 nodos, `/api/demo/setup` enlazando `https://…/112/`, `/112/` y `/112/alerts/` 200, estáticos y
   `/api/webcams` 200, `POST /api/scenario` desde una IP de red local aceptado (400 de validación, no 404)
   y rechazado con `Origin` ajeno (403). `SIGTERM` cierra en ~2 s sin trazas.
4. Sin `FLAREAI_PUBLIC_CONTROLS`: desde red local 403/404 como antes; desde loopback, igual que antes.

No se usó `--presentation` en la simulación para no tocar Twin ni consumir cuota de HappyRobot desde un
segundo director; ese modo solo cambia la capa dinámica, que ya funciona en local con las mismas claves.
Queda pendiente el primer despliegue real en Render (tiempos del pre-deploy en el plan mínimo, memoria
efectiva en Linux y la URL definitiva).
