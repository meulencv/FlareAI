"""Cliente fino de la API pública v2 de HappyRobot (solo stdlib)."""

from .client import HappyRobotClient, HappyRobotError

__all__ = ["HappyRobotClient", "HappyRobotError"]
