"""Carga de configuración desde variables de entorno y `.env` (sin dependencias)."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CONFIG_DIR = REPO_ROOT / "config"
STATE_FILE = REPO_ROOT / "deploy-state.json"


def load_dotenv(path: Path = REPO_ROOT / ".env") -> None:
    """Carga KEY=VALUE de .env en os.environ sin pisar lo ya definido."""
    if not path.exists():
        return
    for raw in path.read_text().splitlines():
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        os.environ.setdefault(key.strip(), value.strip().strip('"').strip("'"))


@dataclass(frozen=True)
class Settings:
    api_key: str
    api_base: str
    hooks_base: str
    firms_map_key: str | None
    environment: str  # production | staging | development

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        api_key = os.environ.get("HAPPYROBOT_API_KEY")
        if not api_key:
            raise SystemExit(
                "Falta HAPPYROBOT_API_KEY (ponla en .env o exporta la variable)."
            )
        return cls(
            api_key=api_key,
            api_base=os.environ.get(
                "HAPPYROBOT_API_BASE", "https://platform.eu.happyrobot.ai/api/v2"
            ).rstrip("/"),
            hooks_base=os.environ.get(
                "HAPPYROBOT_HOOKS_BASE", "https://platform.eu.happyrobot.ai/hooks"
            ).rstrip("/"),
            firms_map_key=os.environ.get("FIRMS_MAP_KEY") or None,
            environment=os.environ.get("HAPPYROBOT_ENV", "production"),
        )
