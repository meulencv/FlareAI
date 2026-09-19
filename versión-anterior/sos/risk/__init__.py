"""Función de riesgo determinista (cono de viento × activos). Corre igual en local y en el sandbox."""

from .engine import compute_risk, haversine_km, bearing_deg

__all__ = ["compute_risk", "haversine_km", "bearing_deg"]
