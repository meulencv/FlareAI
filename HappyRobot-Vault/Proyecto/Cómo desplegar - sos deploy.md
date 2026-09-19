---
tags: [happyrobot, proyecto]
---

# Cómo desplegar — `python -m sos deploy`

`sos/workflows/deploy.py` (`Deployer`):

1. **ensure_workflow** para todos los specs: busca por id en `deploy-state.json`, si no por
   nombre, si no crea (`POST /workflows/` plano). Así los *Call Workflow* pueden referenciarse.
2. **build** por workflow: `unpublish` + `unlock` → crea nodos uno a uno en DFS (el trigger primero
   reemplaza todo) resolviendo `Ref` a ids reales; `custom-output` por nodo; para agentes edita el
   prompt hijo y añade signals; para tools `tool-call-result/generate` + `visibility`; borra los
   hijos por defecto de cada `path`.
3. **sync_variables**: `HAPPYROBOT_API_KEY` (oculta), `HAPPYROBOT_API_BASE` y las del spec.
4. `publish` (production) y guarda ids/slugs/hook en `deploy-state.json`.

```bash
python -m sos deploy                 # todos
python -m sos deploy assess execute  # solo algunos (por clave)
python -m sos destroy <clave>        # borrar (despublica todas las versiones antes; si no, 400 'live version')
python -m sos status                 # org, backend, workflows desplegados
```

Avisos `missing_variables` al publicar son inofensivos (los runs resuelven bien); nodos Twin
aparecen `is_complete=false` mientras Twin no exista pero publican igual.

Relacionado: [[Formato de nodos por API]] · [[Workflows SOS]] · [[IDs y recursos]]
