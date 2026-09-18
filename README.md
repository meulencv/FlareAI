# S.O.S. Agentic Crisis Engine — HackSpain 2026 · Reto HappyRobot

Agente autónomo de gestión de crisis (incendios y multi-riesgo) construido **sobre HappyRobot**:
Twin (Postgres gestionado) como fuente de verdad, workflows como módulos, un *Reasoning Agent*
como analista, agentes de voz para ciudadanos y mandos, y un dashboard con aprobación humana 1-clic.

Todo lo que vive en la plataforma se define como código en `sos/` y se despliega con un comando.

## Arranque rápido (local, sin Twin)

```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env          # pon tu HAPPYROBOT_API_KEY
.venv/bin/python -m sos db start && .venv/bin/python -m sos twin migrate && .venv/bin/python -m sos twin seed
.venv/bin/python main_simulation.py          # escenario completo con giro de viento
.venv/bin/python web/server.py               # dashboard → http://localhost:8000
```

Postgres embebido vive en `.local/pg` (no se instala nada fuera de la carpeta).

## Con Twin provisionado (HappyRobot)

```bash
.venv/bin/python -m sos twin migrate && .venv/bin/python -m sos twin seed   # SOS_DB=auto detecta Twin
.venv/bin/python -m sos deploy                                              # 9 workflows
.venv/bin/python main_simulation.py --cloud
```

Documentación completa (cómo funciona HappyRobot, decisiones, IDs, problemas resueltos) en el
vault de Obsidian `HappyRobot-Vault/` (empieza por `00 Índice.md`).

## Estructura

- `sos/happyrobot` cliente API · `sos/twin` esquema/migración/seed · `sos/workflows` los 9 workflows como código + deployer
- `sos/risk` motor de riesgo (cono de viento × activos) · `sos/runtime` intérprete local de los workflows · `sos/simulation` escenario demo
- `web/` dashboard (mapa, acciones, sala de llamadas) · `config/` pesos y escenario · `tests/`
