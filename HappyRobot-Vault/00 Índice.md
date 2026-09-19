---
tags: [happyrobot, índice]
---

# 🧭 Índice — Vault HappyRobot / S.O.S. Agentic Crisis Engine

Este vault documenta todo lo descubierto y construido sobre **HappyRobot**: primero la web de voz
**FlareAI Web Voice** (2026-09-18) y después el **S.O.S. Agentic Crisis Engine** para el reto de
HackSpain 2026 (2026-09-19): gestión autónoma de crisis con Twin, workflows, Reasoning Agent, voz
y dashboard con aprobación humana.

> Objetivo del vault: que la próxima vez que se retome este trabajo (yo u otro asistente), se pueda
> leer aquí el contexto completo sin tener que redescubrir nada. Empieza por
> [[SOS Crisis Engine - arquitectura]] y [[Cómo arrancar todo]].

## Mapa de notas

### Conceptos (cómo funciona HappyRobot en general)
- [[Qué es HappyRobot]]
- [[Autenticación y hosts API]]
- [[Workflows y nodos]]
- [[Formato de nodos por API]] ← el JSON real de cada nodo (no está en la doc)
- [[Twin - base de datos]]
- [[Reasoning Agent y tools]]
- [[Signals]]
- [[Python Sandbox]]
- [[Templates de workflow]]
- [[Voice Tokens y LiveKit]]
- [[Catálogo de voces]]
- [[Apps y MCP]]

### Proyecto (lo que hemos construido)
- [[2026-09-19#Atlas nacional de infraestructura de emergencias|Atlas nacional de emergencias]] — SQLite/GeoJSON, extracción, calidad y consultas espaciales
- [[SOS Crisis Engine - arquitectura]]
- [[Workflows SOS]] (los 9 desplegados)
- [[Esquema de datos SOS]]
- [[Motor de riesgo]]
- [[Base de datos local embebida]]
- [[Intérprete local de workflows]]
- [[Dashboard y simulador]]
- [[Escenario demo - giro de viento]]
- [[Cómo desplegar - sos deploy]]
- [[Cómo arrancar todo]]
- [[Simulador 112 con ficha en directo]] (webcall integrada con mapa, sesión sin código y túnel móvil aislado)
- Legacy 2026-09-18: [[FlareAI Web Voice - workflow]] · [[Web app - server y frontend]]

### Referencia
- [[IDs y recursos]]
- [[Endpoints usados]]
- [[Catálogo de nodos]]
- [[Problemas y soluciones]] (18 problemas concretos y su solución)

### Bitácora
- [[2026-09-18]] — agente de voz web + vault
- [[2026-09-19]] — S.O.S. Crisis Engine; FlareAI con atlas SQL, instalaciones, webcams, carreteras y confirmaciones

## Estado actual (resumen rápido, 2026-09-20)
- **Tráfico local discreto:** solo con zoom cercano y junto a unidades terrestres, máximo 48 coches;
  avería puntual identificada como simulación para el ensayo visual de recálculo. No modifica rutas reales.
  [[Dashboard y simulador#Tráfico visual local (2026-09-20)|Criterios y verificación]].
- **Recálculos visuales esporádicos:** una ruta terrestre resaltada cada cierto tiempo, con motivos
  aleatorios de viento/tráfico/acceso y mensajes de simulación en el historial. Solo frontend;
  no cambia decisiones, rutas ni datos meteorológicos. [[Dashboard y simulador#FlareAI actual: recálculos visuales esporádicos (2026-09-20)|Detalles y límites]].
- **Presentación nueva:** centro y datos estáticos locales; dinámicos en Twin; solo 112 web, sin 123.
  Testimonios evaluados por el director, parte telefónico al llegar, refuerzos obligatorios, ES-Alert
  excepcional con veto, PDF y cerebro con Markdown local. Director original actualizado con autorización;
  24 testimonios evaluados por LLM real. Llamada real: principal no disponible y respaldo atendido.
  **Pendientes:** publicar la App 112, configuración privada persistente, confirmar experiencia de audio
  y ensayos live integrados. No se ha limpiado todavía la plataforma sin confirmación de IDs.
  [[2026-09-19#Presentación con testimonios, Twin y parte telefónico|Implementación y límites actuales]].
- **Estabilidad Barcelona:** eliminado el tope local de 30 runs/hora que impedía despachar tras
  varios avisos; no era agotamiento demostrado de HappyRobot. Despacho terrestre real verificado,
  pruebas backend/UI completas y aviso persistente de fallo del director. Helicóptero no garantizado
  por el LLM. [[2026-09-19#Revisión de estabilidad y desbloqueo del director|Resultados y límites]].
- **Macro simulador de sala:** `app.py --hackathon`; España completa y red Barcelona/Collserola/costa
  precargada (69.882 vías). Sensores sin llamada, hospitales/ambulancias, tráfico dibujado, cortes con
  desvíos locales, prioridad, supuesto invalidable y ciclo hasta cierre. Historial persistente y ES-Alert
  automático a los tres segundos con veto, solo al simulador. Director actualizado con autorización;
  run real movilizó dos camiones, dos ambulancias y policía. Voz intacta. Detalles y comandos en
  [[2026-09-19#Macro simulador de sala de hackathon|la bitácora de sala]].
- **Routing MVP revisado:** APIs OSM/OSRM con respaldo y caché, alternativas de parque libre e
  inventario disponible/ocupado. Sustituye Overpass durante el despacho tras un 504 en Barcelona;
  probado en seis localidades, incluida Las Palmas. [[2026-09-19#Rutas MVP y parques alternativos]].
- **112/123 simultáneos y llamadas breves:** límite local de 16 llamadas activas, polling independiente,
  OpenStreetMap + IGN con aproximación explícita si falla la dirección. Guiones breves publicados con
  autorización, voz/tools conservados. [[2026-09-19#Llamadas concurrentes y ubicación OSM|Pruebas y límites]].
- **Bomberos 123 y alertas móviles:** mismo marcador con dos números, workflow de voz separado,
  partes por incidente/unidad, confirmación o retirada, refuerzos y helicópteros ficticios.
  `/112/alerts/` recibe ES-Alert simulado con sonido tras activación. Probados LLM real y habla
  sintética sobre LiveKit; añadido control de altavoz, con límites de selección física en Safari.
  [[2026-09-19#Bomberos 123, alertas móviles y manos libres|Implementación y pruebas]].
- **Director autónomo FlareAI:** Reasoning Agent separado del marcador; contexto local, plan por tool,
  validación SQL y vehículos sobre rutas A* locales. Run real de Tarragona verificado: dos camiones,
  ruta de 2,08 km. Entrada de llamada fixture, no nueva prueba de audio. Mapa minimalista y borde de
  actividad; SMS fuera del flujo. Seguimiento cinematográfico entre avisos/camiones y panel automático
  de evidencias FIRMS/GFS, GIBS y cámaras verificadas: revisión visual, no visión artificial ni
  descarte de llamadas. Traffic Lab sigue aislado. Detalles en
  [[2026-09-19#Seguimiento cinematográfico y evidencias visuales|la revisión visual]] y correcciones
  de autenticación/variables en [[2026-09-19#Director autónomo con rutas locales|la bitácora del director]].
- **Atlas local de emergencias de FlareAI**: generados y verificados SQLite, GeoJSON y manifiesto;
  25.136 entidades, 22.575 georreferenciadas y presencia en las 52 provincias/ciudades autónomas.
  Pendientes 2.561 registros oficiales sin ubicación fiable; cobertura no exhaustiva ni
  disponibilidad operativa comprobada. Fuentes OSM, Sanidad, Madrid y DERA; 25 pruebas del
  módulo. Procedimiento, decisiones y limitaciones en
  [[2026-09-19#Atlas nacional de infraestructura de emergencias|la bitácora del atlas]].
- **Telegram como alternativa de prueba**: workflow `FlareAI Telegram Demo` creado, web en
  `http://127.0.0.1:8092`, bot dedicado, vinculación de un chat privado y prefijo obligatorio de
  simulacro. 27 pruebas SMS/Telegram con mocks pasan. Bot real conectado y chat vinculado:
  Telegram aceptó un mensaje directo de diagnóstico, pendiente confirmar recepción con el usuario.
  **El envío por HappyRobot sigue bloqueado por 401**; la prueba directa no ejecutó ese workflow.
- **SMS pendiente del mentor**: autenticación resuelta, pero un envío autorizado terminó en
  Telnyx 40305 por asociación al perfil de mensajería. El Twilio gestionado comprado no aparece
  como toll-free seleccionable. No hay entrega confirmada ni se compraron números desde el agente.
  Detalles en [[Cómo arrancar todo]] y [[2026-09-19]].

- **Activo: FlareAI**, observatorio Python + Leaflet en la raíz, servidor online en :8090.
  La implementación S.O.S. descrita en las notas anteriores vive en `versión-anterior/`.
- **Webcall 112 → mapa:** marcador `happyrobot-112/` servido por `app.py` en :8112, aislado del
  mapa en :8090. `demo.py publish` publica solo el marcador por HTTPS temporal. Sin código de
  vinculación; sesión limpia por arranque, avisos rojos etiquetados demo, sin Twin ni llamada al
  112 real. Véase [[Simulador 112 con ficha en directo]]. Workflow publicado/live y HTTPS con
  sesión segura verificados. **Webcall real de Tarragona → aviso confirmado demo en mapa**,
  con mensajes/tool de HappyRobot y selección automática comprobados; pendiente valoración
  humana de la escucha en móvil.
- **Datos activos en PostgreSQL local:** 511.226 celdas, 44.787 instalaciones OSM y 2.926 cámaras;
  fuentes, instantáneas FIRMS/GFS, focos, observaciones y metadatos de cartografía/medios en SQL.
  Esquema compatible en tipos con Twin, sin PostGIS; ninguna escritura remota. Véase [[2026-09-19]].
- **Mapa:** heatmap e instalaciones; cámaras ocultas hasta zoom 10. De los 2.926 registros
  auditados, 2.240 capturas integrables estaban disponibles al comprobar; se ocultan errores,
  plantillas y enlaces externos. La disponibilidad se revalida en SQL. El catálogo sigue siendo
  parcial y no se sincroniza automáticamente. Carreteras IGN con teselas retenidas durante zoom.
- **Fuego:** la misma animación en todas las escalas, con radio visual mínimo de 16 px, sin icono
  estático. Confirmado = rojo; sin confirmar = gris. No modifica la geometría medida y la confianza
  FIRMS no es confirmación. Véase [[2026-09-19]].
- **Verificación del proyecto activo:** 57 tests Python (incluyendo SQL), 6 del marcador,
  42 JavaScript, Ruff/mypy/ESLint y comprobaciones de navegador/HTTPS. Arquitectura y comandos
  actuales en `README.md`, `docs/IMPLEMENTACION.md` y `AGENTS.md` de la raíz.

### Estado histórico de HappyRobot (implementación apartada)
- 🧹 **Plataforma vaciada (2026-09-19, tarde)**: los 9 workflows SOS se **borraron** de HappyRobot a
  petición del usuario (sin Twin no servían). Siguen definidos como código: `python -m sos deploy`
  los vuelve a crear en una pasada cuando haya Twin. En la org solo quedan `FlareAI Web Voice`
  (lo usa el dashboard como voz de reserva) y `test`.
- ⚠️ **Twin no provisionado** (404) y API key sin `twin.manage` → **acción del usuario**:
  Settings → Twin Database → Enable + key con Full Twin access. Mientras: Postgres embebido en
  `.local/pg` con el mismo esquema, y `sos twin sync-to-twin` para migrar.
- ✅ `python main_simulation.py` funciona en local de punta a punta (aviso 112 → satélite →
  verificación IA → plan/acciones → aprobación → llamadas → giro de viento → re-plan + signal).
- ✅ Dashboard en `http://localhost:8000` (`python web/server.py`), voz por web call (agente básico
  hasta que haya Twin).
- ✅ 12 tests (`.venv/bin/python -m pytest -q tests`). Commit `be1bb86` + docs.
- 🔑 Secretos solo en `.env` / variables de workflow; nunca en repo ni vault.

Relacionado: [[2026-09-19]] · [[Cómo arrancar todo]] · [[SOS Crisis Engine - arquitectura]]
