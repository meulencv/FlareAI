# Traffic Lab — instrucciones del módulo aislado

Todo cambio de este prototipo debe quedar dentro de `traffic_lab/`. No importa módulos del proyecto padre y no modifica FlareAI, HappyRobot 112 ni los workflows de voz. No escribir claves en archivos: `HAPPYROBOT_API_KEY` vive en el entorno del proceso o se pide con getpass.

## Ejecutar

Desde la raíz de FlareAI:

```powershell
python traffic_lab/launch.py
```

Prepara el entorno virtual y el modelo si faltan, pide la clave de HappyRobot sin guardarla y abre `http://127.0.0.1:8790`. Enter sin clave permite modo local. `--local` omite HappyRobot y `--no-browser` evita abrir el navegador. No lanzar otra instancia mientras el puerto esté ocupado.

Desde esta carpeta, con el entorno instalado:

```powershell
.\.venv\Scripts\python.exe server.py
.\.venv\Scripts\python.exe -m unittest -v
node --check app.js
.\.venv\Scripts\python.exe verify.py
```

`verify.py` requiere el servidor arrancado. `--cloud` realiza tres ejecuciones reales de HappyRobot y consume uso de la plataforma. `--live` descarga imágenes recientes; sin esa opción usa las muestras guardadas. Los informes `verification-demo.json` y `verification-live.json` contienen evidencias y run IDs, nunca claves. Las pruebas unitarias no necesitan red ni modelo descargado.

## Arquitectura y contratos

- `prepare.py`: modelo ONNX de revisión fija y SHA-256 verificado; prepara tres muestras JPEG con evidencia HTTP. Si existen muestras válidas, no las refresca. Las muestras se descargaron el 19-09-2026, no son vídeo en directo.
- `traffic.py`: YOLOv8s sobre imagen completa y teselas solapadas (512 px en las cámaras de 1280 px, umbral 0,25); NMS fusiona duplicados y se descartan cajas cortadas por bordes internos de teselas. El conteo global incluye posibles aparcados y se identifica como detecciones parciales, no aforo. Solo las zonas cuyo encuadre coincide con una referencia calibrada producen métricas por calzada. Cero detecciones da densidad unknown, no vía despejada.
- `cameras.py`: catálogo cerrado de informo.madrid.es y SHA-256 explícito de cada referencia calibrada. ORB + homografía compara la escena y excluye las bandas de título/reloj: exige suficientes correspondencias distribuidas, inliers y desplazamiento de esquinas ≤1,5 %. Si no coincide, faltan rasgos o se modifica la referencia, los conteos por zona son null/unknown y no se dibujan esos polígonos. Es un guardarraíl conservador, no una prueba infalible de cámara inmóvil; puede abstenerse ante cambios de luz/follaje.
- `server.py`: servidor solo en loopback, estáticos permitidos explícitamente, control de Host/Origin, catálogo cerrado sin URLs aportadas por clientes, caché de 180 segundos y límite de descarga de 4 MB. No tiene endpoint para leer archivos arbitrarios. JSON/JPEG locales en `runtime/`; modelo y venv ignorados por Git.
- `POST /api/analyze`: `{"camera_id":"08301","mode":"demo"}`. Devuelve `observation_id`, `evidence` e imagen anotada base64.
- `POST /api/workflow`: `{"observation_id":"..."}`. Solo acepta observaciones producidas en esta sesión; devuelve `run_id`. Reenvíos de la misma observación reutilizan el run durante la vida del proceso.
- `GET /api/run?id=...`: resultado de un run iniciado por esta sesión. Nunca expone la API key.
- `cloud_steps.py`: Python de validación y guardarraíles, prompt del nodo Extract. El código Python desplegado se prueba localmente con el mismo texto.
- `happyrobot.py`: despliega un workflow nuevo si no existe estado local. Nunca busca ni modifica workflows ajenos por nombre. El estado local está en `runtime/happyrobot-state.json`; conservarlo para reutilizar el workflow existente. `publish-draft` solo acepta la última versión del workflow registrado en ese estado.

## Workflow de HappyRobot

Nombre: **FlareAI · Traffic Lab · revisión visual**.

- Workflow: `01a0b8eb-6bc9-7176-ba03-f7113b3bbaa7`.
- Slug: `bcuwz4ne4ot0`.
- Versión verificada: `01a0b8f0-4d83-7bd2-aa77-8e8e415dc144`.
- Entorno: production, sin cron, llamadas ni despachos. Trigger Workflow Function invocable mediante API autenticada o Call Workflow.
- Flujo: recibir `observation_json` (string JSON) → Python recalcula vigencia/calidad/densidad → AI Extract resume mediciones → Python emite `result_json` con revisión humana obligatoria.

La visión se ejecuta LOCALMENTE; el workflow de validación y resumen se ejecuta en HAPPYROBOT. La plataforma no está descargando ni procesando los JPEG. No anunciarlo como un modelo de visión alojado allí. Su sandbox Python no permite red ni instalar OpenCV; los schemas Generate/Extract consultados no exponen un campo de imagen. Solo se envían métricas a HappyRobot, no las fotografías.

Detalles de API comprobados en ejecuciones reales:

1. Extract devuelve campos bajo `response.summary` y `response.operator_check`, no en la raíz.
2. Al bifurcar una versión, los IDs físicos de los nodos cambian. Las variables usan `persistent_id` como `group_id`, mientras los endpoints de edición usan `id`. No sustituirlos indiscriminadamente.
3. Antes de publicar otra versión en production hay que despublicar la activa; la API lo exige. No borrar nodos ni versiones para resolverlo.
4. La publicación puede advertir `missing_variables` incluso cuando `available-vars` y los runs resuelven las rutas correctamente. La verificación válida es ejecutar y comprobar la evidencia y el resumen, no ignorar errores de ejecución.
5. Un nodo puede tener `output_id` mientras su salida aún está en ejecución; no interpretar `data: null` como fallo terminal.

## Límites y siguiente integración

Una foto permite estimar densidad VISIBLE, no velocidad, cola detenida, cierre ni transitabilidad. `speed_kmh`, `road_blocked` y `recommended_route` permanecen null. No detectar vehículos no demuestra vía libre; YOLO puede omitir vehículos oscuros, pequeños, tapados o desenfocados. No hay benchmark etiquetado: 23 pruebas de lógica y pruebas HTTP/cloud no equivalen a precisión de visión medida.

`usable_for_route_review` permanece false porque aún falta validar el encuadre y la cobertura vial. `current_visual_evidence` solo significa fecha del proveedor dentro de 15 minutos y controles básicos; no seguridad de la carretera. `dispatch_authorized` y `usable_for_automatic_routing` siempre false. El texto de IA es orientativo, no un permiso ni una regla de ejecución.

Próxima fase: cámaras georreferenciadas a tramos y sentidos, verificación del encuadre, vídeo o aforos para movimiento, cierres oficiales y alternativas de ruta con aprobación humana. No vincular izquierda/derecha en imagen con norte/sur ni inventar ETA a partir de cajas.

## Procedencia y licencia

Modelo local actual: Ultralytics YOLOv8s, COCO, AGPL-3.0; ONNX de `https://huggingface.co/Kalray/yolov8`, revisión `9e0af089be9c2f172e4fd9b724805f8b6514854e`, SHA-256 `1bd2afeed7a85188e295875b3936a6f08df5a7671457ece9077f3b9b8daee6d6` (44,9 MB). Sustituye al nano usado en las primeras evidencias, sin borrar aquellos informes. Revisar obligaciones AGPL/licencia comercial antes de redistribuir o convertirlo en servicio.

Imágenes: Ayuntamiento de Madrid, portal informo; URL exacta, Last-Modified y hash en cada muestra. Acceso público no equivale a permiso de reutilización ilimitada ni SLA. No analizar matrículas ni personas. Las métricas no acreditan que todas las cámaras estén disponibles en el futuro.

## Visión remota con Vercel (19-09-2026)

- `traffic_catalog.py` consulta en SOLO LECTURA `../data/espana-en-directo/data/catalog.json`, el catálogo que importa `database.py` en `flare_cameras`. No importa módulos del padre ni se conecta a PostgreSQL. Son 2.926 registros: 2.761 snapshots, 164 players y 1 link. El filtro inicial admite 2.600 candidatos HTTPS de tráfico: DGT 1.948, Madrid 357, Euskadi 295. Son candidatos, NO cámaras verificadas disponibles. Ejemplo: `python traffic_catalog.py --camera madrid-08301`.
- `gateway_vision.py` prepara peticiones con un adjunto `image_url` real, no una URL puesta como texto. Endpoint `https://ai-gateway.vercel.sh/v1/chat/completions`; modelo `openai/gpt-4.1-mini`. Visión y JSON Schema probados en tres runs. No tratar los resultados del VLM como conteos de YOLO ni como una validación estadística de precisión.
- `remote_setup.py` construye un workflow independiente: Workflow Function (camera_id, image_url) → Python valida la URL y prepara el cuerpo → Webhook llama a Vercel con autenticación Bearer nativa → Python valida la respuesta y fuerza revisión humana. Los scripts desplegados se generan desde las funciones probadas localmente; no importan el proyecto ni descargan modelos en el sandbox. Se ejecuta enteramente en HappyRobot/Vercel, sin consultar el servidor local.
- Publicado en production: **FlareAI · Traffic Vision · Vercel**, workflow `01a0b92b-35cd-78af-a37d-19bf9dce95c3`, slug `2kgsocnntmbo`, versión `01a0b92b-35db-7e9b-9166-88ddeae33b69`. Sin cron ni despachos. Estado en `runtime/vercel-workflow-state.json`. El usuario introdujo la clave y autorizó hasta 2 USD de pruebas en la ventana local; la clave solo se envió a la variable oculta de HappyRobot, no se guardó en archivos ni en el chat.
- `connect_gateway.py`: ventana local de entrada oculta y consentimiento. En este equipo funciona con `py -3.10 connect_gateway.py`; Python 3.13 tiene Tk importable pero falla al crear la ventana por falta de init.tcl. Requiere HAPPYROBOT_API_KEY en el proceso. No imprimir el cuerpo de la respuesta al actualizar la variable.
- Autenticación HTTP: usar `authType: bearer` y `token` como referencia a `use_case_variables.AI_GATEWAY_API_KEY`, no un header Authorization manual. Una prueba con una credencial ficticia confirmó que ese marcador no apareció en la salida del nodo. No imprimir ni guardar respuestas HTTP completas: pueden contener metadatos de petición. La prueba usa GET /v1/models, sin inferencia pagada, y restaura la configuración antes de publicar el nodo real.
- Un GET Webhook v2 requiere para quedar completo `headers: []`, `params: []` y body `{schemaVersion: 2, contentType: none, raw: ""}`. El endpoint /nodes/{id}/test devolvió Invalid body; se verificó con un run real de solo consulta y se despublicó el modo de prueba antes de restaurar la inferencia.
- Se han reservado las tres pruebas puntuales del CLI (máximo tres, reserva conservadora de 0,50 USD por intento). No hay reintentos automáticos. No se modificó el límite de la clave en Vercel: no confundir la autorización de pruebas con un tope global del proveedor. No activar cron ni barridos de miles de cámaras sin nuevo presupuesto.
- No ejecutar `npx vercel ai-gateway setup`: configura agentes de programación y sus credenciales, no despliega este workflow. No hace falta instalar Vercel CLI para hacer llamadas HTTP desde HappyRobot.
- Pruebas: `python -m unittest -v test_gateway.py` (13 sin red); suite completa en el venv: 36. `verify_remote.py --run-id ID [--run-id ID]` consulta runs existentes y escribe solo los resultados y uso numérico en `verification-remote.json`, sin generar inferencias. El informe de tres runs recoge un coste de inferencia Vercel de 0,0019968 USD: M-30 low/22 estimados, Plaza de Castilla low/3 estimados, O'Donnell unknown/null. No incluye otros posibles costes de HappyRobot.
- Runs verificados: `10635db2-5332-4fd4-9955-6c1da1c51265`, `cce9c7a5-3cf6-4f76-b1cf-f7104877b41e`, `5844c2c2-7dbe-4d31-abe1-6facd39a554e`.
- Se observó giro de la cámara 08301 en `preview-08301.jpg` (12:25:55 hora en imagen); las ROI del prototipo YOLO anterior ya no corresponden a esa vista. No comparar directamente sus conteos parciales con el conteo de toda la imagen del VLM. La visión remota no usa esas ROI fijas.
- Pendiente: verificar la hora de captura y vincular el fotograma exacto al resultado. El proveedor recibe una URL que cambia: no hay hash inmutable de la imagen procesada. `capture_time_verified` y `current_visual_evidence` siguen false. Las capturas periódicas no son vídeo continuo.
- Tener el catálogo local NO hace que PostgreSQL sea accesible desde HappyRobot; no prometer sincronización cloud ni monitorización de 2.600 cámaras. El invocador aporta camera_id + image_url (el CLI los resuelve en el catálogo de solo lectura). La interfaz local de YOLO no se ha sustituido ni desplegado en Vercel.

## Regresión por giro de cámara y revisión de la demo local

- La captura del usuario mostraba polígonos de una vista anterior sobre un encuadre PTZ nuevo; el filtro descartaba vehículos y mostraba falsos 0/1 con densidad baja. No solucionar moviendo polígonos a ciegas: validar contra referencias con hash antes de usarlos.
- Modelo actual YOLOv8s + teselas; umbral 0,25. Se probó 0,15 solo en `vision-candidate.*`, pero no se adoptó: añadió una caja parcial y no resolvió las omisiones. La detección de vehículos pequeños, oscuros u ocultos sigue siendo incompleta.
- La UI separa detecciones de toda la imagen (posibles aparcados) de detecciones por zonas validadas. Si el encuadre no coincide, no dibuja las zonas y devuelve null/unknown por calzada. El endpoint de resumen rechaza esas observaciones con HTTP 409 antes de llamar a HappyRobot; también rechaza cero detecciones en todas las zonas y actualización HTTP live >600 s o no verificable.
- La UI muestra hora de análisis y hora HTTP en Europe/Madrid, antigüedad actualizada cada segundo y aviso de captura NO VERIFICADA. El umbral HTTP local pasó de 900 a 600 s. Esto NO verifica la hora de captura del fotograma: la extracción/validación del reloj y el límite operativo real de diez minutos siguen pendientes. No se han cambiado los workflows remotos en esta corrección.
- `check_vision.py --stage after` usa el mismo fotograma congelado `samples/m30-front.jpg`; el nombre no garantiza orientación. `--capture` solo lo descarga si no existe. SHA-256 `690ae5dea8f09fd9565b47107a801516db7d6946e17c76a5beb5c1d38e4ab2e4`. La versión anterior devolvía 0/0 y low; ahora las zonas son unknown y se detectan tres vehículos en toda la imagen. Aún faltan vehículos: no es validación de precisión. `vision-before.*` y `vision-after.*` son comparables porque usan el mismo hash.
- `preview-08301.jpg` es OTRA captura de prueba con 20 detecciones, no una mejora de 0 a 20 sobre la misma foto. Las cámaras cambian de vista; nunca comparar conteos de fotogramas distintos para medir precisión.
- Pasan 46 tests Python y 5 de interfaz con `node --test test_ui.mjs`. Las pruebas HTTP con `verify.py` y `verify.py --live` no generan inferencias pagadas; guardan `verification-*-alignment.json` sin sobrescribir las evidencias iniciales. Se comprobaron muestras originales, vista nueva, iluminación, enmascarado del título, duplicados de teselas, caducidad en pantalla y bloqueo antes de llamadas cloud.
