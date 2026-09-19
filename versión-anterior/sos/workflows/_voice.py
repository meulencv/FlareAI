"""Configuración común de los agentes de voz (idioma/voz en español)."""

from ._builder import P, static

VOICE_ANA = ("31hktsdrgix8", "Ana HR")  # es-ES, ver vault → Catálogo de voces


def voice_agent_config(name: str) -> dict:
    return {
        "agent": {
            "name": P(name),
            "voices": [static(*VOICE_ANA)],
            "languages": [static("es", "Spanish")],
            "language_accents": [static("es-es", "Spanish (Spain)")],
        },
        "business_hours_setting_name": "default",
    }
