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
`Simulador 112 · Asistente de voz`, configura español de España, el modelo
`gpt-5.6-sol-low`, transcripción avanzada y la tool silenciosa `actualizar_ficha`. Guarda
únicamente identificadores no secretos en `workflow.json`. Es idempotente: si el workflow
ya existe, actualiza su configuración y lo republica.

## Arranque

```bash
python3 server.py
```

Abre <http://127.0.0.1:8112>, marca `112`, pulsa llamar y permite el micrófono.

La interfaz imita una aplicación móvil de llamadas: marca `112` en el teclado y pulsa el botón
verde. Durante la llamada muestra contacto, estado, cronómetro y botón para colgar. La ficha está
oculta por defecto; **Datos recopilados** abre una hoja inferior con la información en directo.

El backend conserva la API key. El navegador recibe solo un token LiveKit temporal. Durante
la llamada consulta el transcript de HappyRobot y lee los argumentos estructurados de
`actualizar_ficha`; el agente no pronuncia etiquetas ni valores pendientes. Como respaldo,
el backend puede fusionar fichas antiguas interrumpidas e inferir señales urgentes básicas:

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
