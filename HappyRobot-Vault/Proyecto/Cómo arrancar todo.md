---
tags: [happyrobot, proyecto, guía]
---

# Cómo arrancar todo (guía rápida)

## Simulador 112 aislado

```bash
cd /Users/meulencv/development/projects/FlareAI/happyrobot-112
# La key real solo en .env, que Git ignora.
python3 setup_happyrobot.py   # primera vez o para recuperar workflow.json
python3 server.py             # http://127.0.0.1:8112
```

Pulsa **Iniciar simulación**, permite el micrófono y habla. La ficha de ubicación, emergencia,
personas, riesgos y contacto se actualiza desde el transcript de HappyRobot. No llama al 112 real.
Detalles y límites en [[Simulador 112 con ficha en directo]].

## S.O.S. Crisis Engine (2026-09-19 en adelante)

```bash
cd /Users/meulencv/development/projects/FlareAI
# 1) entorno (todo dentro de la carpeta)
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env            # HAPPYROBOT_API_KEY=sk_live_... (nunca al repo)
# 2) base de datos local (Postgres embebido en .local/pg) + esquema + datos de demo
.venv/bin/python -m sos db start
.venv/bin/python -m sos twin migrate && .venv/bin/python -m sos twin seed
# 3) simulación completa (entregable del reto)
.venv/bin/python main_simulation.py            # añade --verbose para ver cada nodo
# 4) dashboard
.venv/bin/python web/server.py                 # http://localhost:8000
# 5) tests
.venv/bin/python -m pytest -q tests
```

En el dashboard: botones de simulación arriba (aviso 112 → satélite → giro de viento), aprobar
acciones con 1 clic, "Sala de llamadas" para hablar por voz (web call, micrófono).

## Cuando Twin esté provisionado (y la key tenga `twin.manage`)

```bash
.venv/bin/python -m sos status                 # debe decir backend twin
.venv/bin/python -m sos twin migrate && .venv/bin/python -m sos twin sync-to-twin
.venv/bin/python -m sos deploy                 # (re)publica los 9 workflows, incluidos los cron
.venv/bin/python main_simulation.py --cloud    # runs reales en la plataforma
.venv/bin/python web/server.py                 # detecta Twin → modo cloud, voz con los agentes SOS
```

## Legacy: FlareAI Web Voice (la web de voz simple de 2026-09-18)

```bash
cd voice && HAPPYROBOT_API_KEY=sk_live_... python3 server.py   # http://localhost:8000
```
El dashboard nuevo la reutiliza como agente de voz de reserva cuando no hay Twin.

## Dónde ver las cosas en HappyRobot

https://platform.eu.happyrobot.ai/hackspainteam3/workflows → 9 workflows "SOS · …". Cada
ejecución es un *run* con sus nodos; las llamadas tienen *session* con transcripción y audio.

## Prueba SMS independiente (2026-09-19)

La aplicación activa es ahora FlareAI; los comandos SOS anteriores corresponden al código
apartado en `versión-anterior/`. La prueba SMS se creó aparte para no alterar ese archivo
histórico ni el observatorio de incendios.

- Interfaz: `python sms_demo.py serve`, abrir `http://127.0.0.1:8091`.
- Credenciales: variables de proceso `HAPPYROBOT_API_KEY` y `HAPPYROBOT_SMS_HOOK_KEY`.
  La primera también admite el archivo autorizado `versión-anterior/.env`. No se guardó
  ninguna clave nueva en disco. Después de reiniciar hay que volver a proporcionar las variables.
- Remitente: `+15304471317`, número Telnyx de la organización, ID `3052288166032573735`.
- Workflow **FlareAI SMS Test**: `01a0b8d2-28d1-7e38-b7cf-7dded8edb333`.
  Version 3 publicada: `01a0b8e2-45aa-7727-b8f5-52300867d7c5`.
  Configuración local no secreta: `sms-workflow.json`.
- Flujo: solicitud predefinida con `to` y `message` → acción Send SMS
  (`019e3b65-e185-7c44-b042-67de4be40728`). Proveedor `use_existing_telnyx`;
  La selección inicial por ID interno dio 40013. En Version 4 se puso el número E.164 tanto
  en `telnyxPhoneNumber.static.id` como en `.name`; el error pasó a 40305. La asociación al
  perfil de mensajería sigue pendiente: no considerar esta configuración validada de extremo a extremo.
- Estado: **autenticación resuelta; entrega pendiente de prueba manual**. El endpoint de runs
  devolvió Cloudflare 502, por lo que se usa el webhook directo con `X-API-Key`, sin reintentar
  por otra ruta tras un fallo. La clave anterior devolvía 401 incluso coincidiendo con la UI;
  republicar Version 2 no bastó. El usuario regeneró la clave desde el botón de flechas circulares
  en Advanced configuration de una versión editable y publicó Version 3: así funcionó.
  Mantener Enhanced Security. Usar literalmente la clave del trigger, no la clave de cuenta ni
  su hash. La causa interna del rechazo anterior no se demostró.
- Verificación sin envío: run `2bf83087-a39b-4865-b1bb-1c4373eb6e41`, payload vacío de
  destinatario y mensaje. Trigger `succeeded`; Send SMS `failed` con `to is required`, esperado.
  No se ha probado la aceptación del proveedor ni la entrega con un destinatario real.
- El botón exige destinatario, mensaje y confirmación. Incluye CSRF, comprobación Host/Origin,
  límite de frecuencia y deduplicación por petición durante la sesión. Solo sirve en loopback;
  no debe exponerse públicamente como servicio de envío.

```bash
python -m unittest test_sms_demo -v
python -m py_compile sms_demo.py test_sms_demo.py
node --check static/sms.js
npx --yes --package eslint@9.33.0 eslint static/sms.js
```

Las 13 pruebas usan mocks: nunca contactan al proveedor. Abrir la página tampoco envía nada.
Un run completado no es un acuse de entrega del operador: verificar el móvil destinatario.

## Simulacro por Telegram (alternativa mientras se resuelven los SMS)

SMS quedó pendiente del mentor: el envío autorizado encontró Telnyx 40305 (remitente sin
asociación al perfil de mensajería). El número Twilio comprado en HappyRobot tampoco aparece
como toll-free utilizable en el selector gestionado. No se afirma haber conseguido entrega SMS.

Con `HAPPYROBOT_API_KEY` en el entorno:

```bash
python telegram_demo.py serve
python -m unittest test_sms_demo test_telegram_demo -v
python -m py_compile sms_demo.py telegram_demo.py test_sms_demo.py test_telegram_demo.py
npx --yes --package eslint@9.33.0 eslint static/sms.js static/telegram.js
```

Abrir `http://127.0.0.1:8092`:

1. Crear un bot dedicado con BotFather (`/newbot`). Introducir el token solo en el campo de
   contraseña local. Autorizar guardarlo como variable oculta del workflow y pulsar Conectar bot.
2. Abrir el enlace generado y pulsar Iniciar en Telegram. Volver a Comprobar vinculación.
   La vinculación exige el nonce actual, chat privado y fecha reciente; caduca a los 10 minutos.
3. Abrir `FlareAI Telegram Demo`, crear una versión editable, regenerar API Key del primer nodo
   mediante el botón de flechas circulares y publicar Production. Esto sigue pendiente al cierre:
   la clave inicialmente configurada por API devuelve 401.
4. Pulsar Comprobar HappyRobot sin enviar. El backend detecta la versión Live y lee la clave en
   memoria; no hace falta pegarla en el chat ni en la web. Usa `chat_id=0` para evitar entrega real.
5. Con bot, chat y webhook verificados, autorizar el texto y pulsar Enviar simulacro. El servidor
   añade siempre `SIMULACRO — No es una orden real de evacuación.`; no admite cambiar el destinatario
   desde el POST del navegador. Revisar la recepción real, no solo el estado del workflow.

Workflow `01a0b90b-bc5e-7b7c-b080-71f35f139200`, slug `qinusphyej9n`. Los IDs están en
`telegram-workflow.json`, sin secretos. El workflow recibe JSON serializado como texto y llama
mediante POST a Telegram sendMessage. La variable oculta `TELEGRAM_BOT_TOKEN` se interpola en
la URL; nunca se devuelve al navegador ni se guarda en archivos. No exportar diagnósticos remotos
sin revisar posibles URLs o cabeceras secretas.

La aplicación local consulta getMe/getWebhookInfo/getUpdates, pero los envíos pasan por HappyRobot.
Rechaza bots con webhook existente sin borrarlo. Reutiliza el servidor con Host/Origin/CSRF,
assets explícitos y deduplicación por petición. No hay broadcast ni suscripciones geográficas;
es una prueba de un único chat privado. Reiniciar exige conectar y vincular de nuevo.

27 pruebas con mocks pasan (15 SMS + 12 Telegram), además de compilación Python y ESLint.
Página local comprobada HTTP 200. Pendientes autenticación del webhook y prueba de entrega con el usuario.

Relacionado: [[Simulador 112 con ficha en directo]] · [[SOS Crisis Engine - arquitectura]] · [[Dashboard y simulador]] · [[Base de datos local embebida]] · [[Cómo desplegar - sos deploy]]
