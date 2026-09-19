---
tags: [happyrobot, proyecto]
---

# Dashboard y simulador

## Retirada e informe rápidos (2026-09-20)

Petición: «una vez se apague el incendio, que nos dé el informe rápido», para una demo breve.
Se eliminaron 25 s hasta vigilancia y 45 s antes de retirada en ambos motores. Al alcanzar la
extinción ilustrativa, las unidades regresan inmediatamente, con animación de 5–15 s. Un traslado
sanitario ya iniciado termina primero; una carretera cortada sigue pudiendo impedir el regreso.

El informe se genera al iniciar la retirada, no al acabar todos los viajes. Declara cuántas unidades
siguen ocupadas en ese momento, sin fingir llegada a base ni alta del paciente. El cierre conserva
su significado de unidades ya liberadas y no genera un segundo PDF. Se mantienen los datos NASA.

Registro de sesión: primero fallaron tres regresiones con las esperas antiguas; después se cambió
el ciclo, se adaptaron sus pruebas y el verificador de presentación. Pasaron 123 pruebas Python,
36 JS, Ruff y el recorrido Chromium (Cerebro y PDF por HTTP, fixtures, sin llamadas reales).
Reproducir: `PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_presentation.py`.

## Editor manual del escenario (2026-09-20)

Petición: un lápiz rojo a la izquierda de Ajustes, con «Crear corte random», viento y potencia del fuego.
A diferencia de los ensayos visuales descritos más abajo, estos controles **sí cambian el motor local**.
Se reutilizó `/api/scenario` para conservar validación de origen, cerrojo, historial y persistencia.

- El corte se escoge al azar por delante de una unidad terrestre, sobre aristas reales y sin cortar.
  A* recalcula desde la posición interpolada de las unidades afectadas. Sin alternativa quedan detenidas;
  no se inventa un desvío visual ni se consulta OSRM ignorando la barrera. Hace falta una unidad en marcha.
- El selector de incendio delimita los sliders, no el corte compartido de carretera. Viento expresa
  dirección **hacia** 0–359°, no procedencia NOAA. La potencia negativa apaga progresivamente, cero devuelve
  la evolución normal y positiva aviva, manteniendo trabajo de medios y topes del simulador.
- Se permite reactivar un incendio contenido/en vigilancia, no uno en retirada/cerrado. No cambia
  observaciones NASA/NOAA ni workflows, contactos o telefonía. Los cambios constan como manuales/simulados.
- El panel usa el estilo de Ajustes, cierre por botón/Escape y confirmaciones accesibles. Serializa cambios
  al soltar el slider, no por cada píxel. Recupera foco tras guardar: desactivar el input durante el POST
  lo hacía perder en Chromium e impedía continuar ajustando con teclado.

### Registro de la sesión

Primero se añadieron regresiones que fallaban con el contrato anterior; después se conectaron panel y
motor y se probó el recorrido por HTTP en escritorio/móvil. El ensayo usa voz/LLM fixtures y la red local
cacheada, sin llamadas reales ni ejecuciones cloud. Comprueba corte, desvío/detención, viento, reducción y
avivado progresivos, teclado, errores y conservación de datos originales. Capturas en
`.local/scenario-editor-desktop.png` y `.local/scenario-editor-mobile.png`; el visor del agente no pudo
abrirlas por la política de archivos ignorados, aunque las comprobaciones DOM y de interacción pasaron.

```bash
.venv/bin/python -m unittest test_scene test_local_routes test_autodispatch test_director test_operations test_presentation
.local/node-v22.19.0-darwin-arm64/bin/node --test test_operations.mjs test_scene.mjs test_director.mjs
PLAYWRIGHT_BROWSERS_PATH="$PWD/.local/playwright-browsers" .venv/bin/python verify_presentation.py --editor
```

Para usar el contrato nuevo en un servidor que ya estaba ejecutándose hay que reiniciarlo y recargar
la web. No se reinició la sala activa ni se restableció ninguna base de datos durante esta sesión.

## FlareAI actual: recálculos visuales esporádicos (2026-09-20)

El usuario pidió dar algo de aleatoriedad al historial y representar visualmente algún recálculo,
no muchas rutas a la vez. Se añadió un ensayo puramente de frontend para no provocar cortes ni
modificar desplazamientos que ya están coordinados en el servidor.

- `static/director.js`: elige al azar una unidad terrestre en marcha con ruta visible y no aproximada.
  Primera oportunidad a los 12–24 s (hay trayectos acelerados de solo 45 s); después espera 45–90 s entre efectos. Seis segundos de resaltado
  violeta con trazo discontinuo en movimiento, seguido de «Ruta revisada · simulación».
- Motivos aleatorios: viento cambiado, vehículo averiado y acceso alternativo. Mensajes identificados
  como simulación; no representan observaciones NOAA, cálculos nuevos ni decisiones del LLM.
- `static/scene.js`: eventos visuales intercalados por fecha con el historial, separados de SQL/Twin,
  hasta 40 entradas locales. Desaparecen al recargar o cambiar sesión, no sobrescriben pasos reales.
- No añade llamadas HTTP, no mueve la cámara para mostrar el efecto y no altera rutas, ETA o viento.
  Los eventos reales tienen prioridad. Pausa, ocultación, desconexión y cambios de ruta cancelan el ensayo.
  Movimiento reducido mantiene el resaltado estático.
- Regresión: cadencia, elección aleatoria, rutas excluidas, cancelación e inmutabilidad. Suite JavaScript:
  `.local/node-v22.19.0-darwin-arm64/bin/node --test test_*.mjs`.
- Verificación de navegador: Chromium de escritorio y viewport móvil con movimiento reducido,
  sobre Leaflet real y estado fixture. Se comprobaron historial, un único trazo animado, finalización,
  pausa, prioridad de un evento real y limpieza al cambiar sesión, sin errores JavaScript ni llamadas
  externas. No es un ensayo live del director ni una nueva prueba de voz.

## Tráfico visual local (2026-09-20)

Petición: algo de movimiento junto a los camiones y las carreteras próximas, sin coches por todo el mapa;
un obstáculo puntual puede explicar un ensayo de recálculo, pero no debe inventarse una causa real.

Se conserva el aspecto de los coches. Aparecen progresivamente entre zoom 13 y 14, solo alrededor de
unidades terrestres visibles: ≤650 m y ≤220 px, máximo 24 tramos y 48 coches. La selección sigue el
marcador, también en pausa y con movimiento reducido. Barcelona usa cajas locales de su red preparada;
fuera de ella se reutiliza la geometría de las rutas disponibles, sin descargar ni fabricar calles.

El ensayo de tráfico muestra ahora un coche averiado y «Avería · simulación» durante seis segundos,
unos 80 m por delante de una unidad. Solo se ensaya en vista cercana; no cambia rutas, tiempos ni órdenes.
Los cortes reales del escenario siguen separados, con su identificador de tramo y el recálculo del servidor.

Verificación: regresiones Node de proximidad, presupuesto, vuelos/rutas aproximadas, pausa, respuesta tardía
y avería. Recorrido Chromium con Leaflet/director reales y estado fixture: 21 coches, avería, pausa, zoom,
zona vacía, móvil y retirada al terminar; sin errores JavaScript ni servicios externos. No es tráfico observado.

Los apartados siguientes describen el dashboard **anterior**, apartado en `versión-anterior/`.

## Dashboard (`web/server.py` + `web/static/index.html`)

Servidor stdlib (`ThreadingHTTPServer`), sin dependencias; frontend con Leaflet (mapa oscuro CARTO)
y `livekit-client` por CDN. `python web/server.py` → http://localhost:8000.

- Mapa: incidentes 🔥 con círculo por prioridad y **cono de trayectoria** (rumbo = viento+180,
  alcance del motor), activos ▲, medios ■ (ocupados), evidencias (puntos).
- Panel de incidentes: estado, confianza, riesgo, plan vigente, razonamiento del analista.
- **Acciones propuestas**: Aprobar/Rechazar (→ WF-Approve). Historial con resultados de llamada.
- **Sala de llamadas**: "Llamar al 112 virtual" (tú eres el ciudadano), "Descolgar" en acciones
  `ready` (tú eres la persona llamada), "Escuchar"/"Tomar el control" en `executing` (cloud, vía
  `voice/tokens` con `session_id`).
- Simulador integrado (botones): aviso 112, satélite + viento O, giro 180°, meteo real (Open-Meteo), reset.
- Config en caliente: `wind_shift_deg`, `cluster_radius_km`, `auto_approve_kinds`.
- API: `GET /api/state`, `/api/log`, `POST /api/actions/{id}/decide`, `/api/voice/token`,
  `/api/voice/finished` (local), `/api/sim/{paso}`, `/api/config`.
- La API key nunca llega al navegador. Modo `local`/`cloud` automático según Twin.
- En local, la voz usa el workflow básico **FlareAI Web Voice** (`HAPPYROBOT_VOICE_FALLBACK_WORKFLOW_ID`)
  porque los workflows SOS de voz fallan en su primer nodo Twin; el resultado de la llamada se marca
  con botones al colgar.

## Simulador (`main_simulation.py` → `sos/simulation/scenario_wind_shift.py`)

Guion en 5 pasos → [[Escenario demo - giro de viento]]. `--cloud` dispara los hooks reales (las
llamadas de voz quedan para el navegador), `--verbose` traza cada nodo, `--pause N` para presentar.

Relacionado: [[SOS Crisis Engine - arquitectura]] · [[Voice Tokens y LiveKit]] · [[Cómo arrancar todo]]
