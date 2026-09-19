# Simulador de llamada al 112 con HappyRobot

Aplicación independiente de FlareAI que simula una llamada de emergencia desde el navegador.
HappyRobot mantiene la conversación por voz y la página presenta una ficha breve obtenida del
transcript de la llamada.

> Esto es una demostración. No conecta con el 112 ni sustituye una llamada real. Ante una
> emergencia, llama al 112.

## Preparación

Requiere Python 3.10 o posterior. No instala dependencias.

```bash
cd happyrobot-112
cp .env.example .env
# Añade HAPPYROBOT_API_KEY a .env
python3 setup_happyrobot.py
```

`setup_happyrobot.py` crea y publica un workflow aislado llamado
`Simulador 112 · Asistente de voz`, configura español de España y guarda únicamente sus
identificadores no secretos en `workflow.json`. Es idempotente: si el workflow ya existe,
lo reutiliza.

## Arranque

```bash
python3 server.py
```

Abre <http://127.0.0.1:8112>, pulsa **Iniciar simulación** y permite el micrófono.

El backend conserva la API key. El navegador recibe solo un token LiveKit temporal. Durante
la llamada consulta el transcript de HappyRobot y extrae la última ficha pronunciada por el
agente:

- ubicación;
- tipo de emergencia;
- personas afectadas;
- riesgos inmediatos;
- teléfono de contacto.

No se guarda una copia local del audio ni del transcript. Las sesiones sí quedan registradas
en HappyRobot conforme a la configuración de la cuenta.

## Variables

| Variable | Valor por defecto |
|---|---|
| `HAPPYROBOT_API_KEY` | obligatoria |
| `HAPPYROBOT_API_BASE` | `https://platform.eu.happyrobot.ai/api/v2` |
| `HAPPYROBOT_WORKFLOW_ID` | se lee de `workflow.json` |
| `HOST` | `127.0.0.1` |
| `PORT` | `8112` |

## Pruebas

```bash
python3 test_server.py
```
