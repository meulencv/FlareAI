---
tags: [happyrobot, concepto]
---

# Signals — avisar a un agente en mitad de una llamada

Pub/sub por topics. Un agente suscrito recibe el `payload` del signal en su bucle de eventos y,
si `shouldRespondOnSignal`, habla de inmediato. Topics automáticos: `org.<org_id>`,
`usecase.<use_case_id>`, `session.<session_id>`; topics custom con patrones (`incident.*`).

```bash
# publicar
curl -X POST $BASE/signals/ -H "Authorization: Bearer $KEY" -H 'Content-Type: application/json' \
  -d '{"key": "incident.<id>", "env": "production", "payload": {"event": "wind_shift", "message": "El viento ha girado 180°…"}}'
# suscribir un nodo agente a un topic custom (lo hace sos deploy)
curl -X POST $BASE/signals/keys -H "Authorization: Bearer $KEY" -d '{"node_id": "<agent_node_id>", "key": "incident.*"}'
# programado
POST /signals/scheduled-signals {"key", "payload", "delay_seconds"}
```

En SOS: WF-Weather-Inject publica `incident.<id>` cuando detecta un giro de viento; el agente de
WF-Outbound-Voice está suscrito a `incident.*` y su prompt le indica interrumpir con tacto y
transmitir la nueva instrucción. En local el simulador registra los signals sin publicarlos.

Relacionado: [[Reasoning Agent y tools]] · [[Workflows SOS]] · [[Escenario demo - giro de viento]]
