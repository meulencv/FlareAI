---
tags: [happyrobot, proyecto]
---

# Motor de riesgo (`sos/risk/engine.py`)

Función determinista `compute_risk(incident, weather, assets, resources, config)`; solo `math`
para poder embeberse tal cual en el nodo Python (perfil standard) de WF-Assess.

- El fuego avanza hacia `wind_dir_deg + 180` (dirección meteorológica = de dónde viene).
- Velocidad de avance = `max(min_spread_kmh, viento × spread_kmh_per_wind_kmh)`; alcance =
  velocidad × `horizon_hours` (3 h). Cono de `±cone_half_angle_deg` (30°) + perímetro de 1 km.
- Activo amenazado → ETA = distancia / velocidad; `score = (población×w + asegurado×w + carbono×w)
  × multiplicador por tipo (hospital 3, colegio 2.5…) × urgencia 1/(1+ETA)`.
- `priority` 1..4 por umbrales (`priority_thresholds`), `needed_capabilities` según
  `hazard_capabilities[type]` (agua vs espuma), `recommended_resources` = disponibles y compatibles
  ordenados por ETA (60 km/h tierra, 250 hidroavión).
- Todo parametrizado por `config.risk` (tabla config); tests en `tests/test_risk_engine.py`
  (viento O amenaza Serra/colegio/Segart; giro 180° → Olocau/Marines; sin viento → solo perímetro).

Relacionado: [[Esquema de datos SOS]] · [[Reasoning Agent y tools]] · [[Python Sandbox]]
