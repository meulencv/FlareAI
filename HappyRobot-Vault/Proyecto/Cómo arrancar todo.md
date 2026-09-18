---
tags: [happyrobot, proyecto, guía]
---

# Cómo arrancar todo (guía rápida)

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

Relacionado: [[SOS Crisis Engine - arquitectura]] · [[Dashboard y simulador]] · [[Base de datos local embebida]] · [[Cómo desplegar - sos deploy]]
