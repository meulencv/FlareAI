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
- `traffic.py`: YOLOv8n sobre imagen completa y recortes por zona; NMS fusiona duplicados; solo bicicleta/coche/moto/bus/camión. Selecciona por punto inferior central dentro de la ROI. Unión de cajas recortada a la ROI para calcular cobertura; niveles `<12 %`, `12–28 %`, `>=28 %`. No es ocupación vial oficial ni probabilidad calibrada.
- `cameras.py`: catálogo cerrado de cámaras de informo.madrid.es. ROI manuales normalizadas respecto al encuadre del 19-09-2026. Al cambiar cámara/zoom hay que revisar polígonos; el control de calidad básico NO detecta todos los giros, niebla ni carteles.
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

Modelo original: Ultralytics YOLOv8n, COCO, AGPL-3.0; export ONNX obtenido de `https://huggingface.co/inference4j/yolov8n`, revisión `66295110f9dd507498735446f4f9f05da3007073`, SHA-256 `65158dad735be799c2466fa15e260c09558080bd530b42a8d0c3d1b419afd8b5`. Revisar obligaciones AGPL/licencia comercial antes de redistribuir o convertirlo en servicio.

Imágenes: Ayuntamiento de Madrid, portal informo; URL exacta, Last-Modified y hash en cada muestra. Acceso público no equivale a permiso de reutilización ilimitada ni SLA. No analizar matrículas ni personas. Las métricas no acreditan que todas las cámaras estén disponibles en el futuro.
