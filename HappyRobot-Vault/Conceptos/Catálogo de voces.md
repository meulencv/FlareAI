---
tags: [happyrobot, concepto, api, voz]
---

# Catálogo de voces

```
GET /voices/?limit=100
```

Devuelve 141 voces (en la org de EU). Cada voz trae:

```json
{
  "id": "31hktsdrgix8",
  "name": "Ana HR",
  "provider": "happyrobot" | "elevenlabs",
  "provider_voice_id": "...",
  "model_id": "v2" | "v3",
  "model_family": "happyrobot" | "turbo",
  "language": "es-ES",
  "languages": ["es", "ar", "ca", ...],
  "locales": ["es-ES", "en-US", ...],
  "gender": "male" | "female"
}
```

Hay dos proveedores: voces propias `happyrobot` (sufijo "HR" en el nombre) y voces
`elevenlabs`. Muchas voces "HR" soportan multi-idioma (`languages` largo) aunque su `language`
por defecto sea otro — pero para fijar el idioma real de la conversación importa el campo del
**nodo del agente** (`agent.languages` / `agent.language_accents`), no solo elegir una voz
"que sepa español".

## Voces en español que encontramos (es-ES / es-MX / es-CO / es-AR)

| id | Nombre | Idioma | Proveedor | Género |
|---|---|---|---|---|
| `31hktsdrgix8` | **Ana HR** ⭐ (la que usamos) | es-ES | happyrobot | female |
| `idlhh2ukeldm` | Daniel HR | es-ES | happyrobot | male |
| `gjc70xusrf87` | Pablo Galvez HR | es-ES | happyrobot | male |
| `wfu3l7ejvhqb` | Angela HR | es-ES | happyrobot | female |
| `j6ijgb83x89l` | Damaris HR | es-ES | happyrobot | female |
| `gjwk98jhnhdu` | Alexandra HR | es-ES | happyrobot | female |
| `pdbhvdjto83v` | Yan HR | es-MX | happyrobot | — |
| `booezfxzw9dj` | Alejandra HR | es-MX | happyrobot | — |
| `8kjx9983xlp2` | Julieta HR | es-MX | happyrobot | — |
| `vtjy0pl8iwmh` | Angela HR | es-CO | happyrobot | — |
| `ijx8sbs6av90` | Emanuel HR | es-AR | happyrobot | — |
| `pablo-el` | Pablo | es-ES | elevenlabs | male |
| `zia88nk9ic3n` | Carolina Ruiz Turbo Multi | es-ES | elevenlabs | female |
| `vbyrsmCXWDCxDVgoPe5R7` | Andrea Turbo Multi | es-ES | elevenlabs | female |
| `kbpbjrrtxav4` | Carolina Turbo Multi | es-ES | elevenlabs | female |
| `rognws94ozyx-franco` | Franco | es-AR | elevenlabs | female |

> Nota: hay IDs duplicados de nombre (p. ej. "Daniel HR" aparece en `model_id: v2` y `v3` con
> distinto `id`) — siempre usar el `id` exacto de la fila, no el nombre.

Relacionado: [[FlareAI Web Voice - workflow]] (cómo se aplicó "Ana HR" al nodo del agente)
