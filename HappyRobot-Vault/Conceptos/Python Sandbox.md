---
tags: [happyrobot, concepto]
---

# Python Sandbox (nodo de código)

- Contrato: las entradas configuradas (`input_data`, key-value con variables) llegan en el dict
  `input_data` **como strings**; el resultado se deja en `output` (JSON-serializable, mejor dict).
- **Sin acceso a red** ni instalación de paquetes. Toda I/O externa va por nodos Webhook/Twin.
- Perfiles: **standard** (Python 3.10, stdlib + dateutil/pytz) y **advanced** (3.12: pandas,
  numpy, shapely, pyproj, pydantic, jsonschema, rapidfuzz, Pillow…).
- Timeout de ejecución (no usar `time.sleep`); `Run python` legacy (RestrictedPython) retirado.
- Objetos anidados en `input_data` llegan como `map[...]` → pasar JSON strings (ver
  [[Formato de nodos por API]]).

Cómo lo usamos: el mismo código de cada nodo vive en el repo como texto (`sos/workflows/*.py`,
`sos/risk/engine.py` se embebe entero en el nodo `riesgo`) y se testea en local con `exec` bajo el
mismo contrato (`tests/test_sandbox_code.py`) y con el [[Intérprete local de workflows]].
Helper `sos/workflows/_sqlgen.py`: `q()` literal SQL seguro, `cfg_num()` lee config, `haversine_sql()`.

Relacionado: [[Formato de nodos por API]] · [[Motor de riesgo]]
