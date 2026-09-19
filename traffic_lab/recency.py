import base64
import io
import re
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

MAX_AGE_SECONDS = 600
EMBEDDED_TZDATA = {}


def resolve_zone(name):
    try:
        return ZoneInfo(name)
    except ZoneInfoNotFoundError:
        data = EMBEDDED_TZDATA.get(name)
        if not data:
            raise
        return ZoneInfo.from_file(io.BytesIO(base64.b64decode(data)), key=name)


def parse_overlay_time(text, timezone_name):
    if not isinstance(text, str) or len(text) > 100 or timezone_name not in {"Europe/Madrid", "Atlantic/Canary"}:
        return None
    match = re.fullmatch(r"\s*(\d{2}|\d{4})[-/.](\d{2})[-/.](\d{2}|\d{4})[ T]+(\d{2}):(\d{2}):(\d{2})\s*", text)
    if not match:
        return None
    a, month, c, hour, minute, second = match.groups()
    if len(a) == 4 and len(c) == 2:
        year, day = a, c
    elif len(c) == 4 and len(a) == 2:
        year, day = c, a
    else:
        return None
    try:
        local = datetime(*map(int, (year, month, day, hour, minute, second)))
        zone = resolve_zone(timezone_name)
        first, second_fold = local.replace(tzinfo=zone, fold=0), local.replace(tzinfo=zone, fold=1)
        if first.utcoffset() != second_fold.utcoffset():
            return None
        utc = first.astimezone(timezone.utc)
        if utc.astimezone(zone).replace(tzinfo=None) != local:
            return None
        return utc
    except (ValueError, ZoneInfoNotFoundError):
        return None


def refresh_recency(result, now=None):
    now = now or datetime.now(timezone.utc)
    output = {**result}
    try:
        captured = datetime.fromisoformat(result["captured_at"])
        if captured.tzinfo is None:
            raise ValueError("Hora sin zona horaria")
        analyzed = datetime.fromisoformat(result["analyzed_at"])
        if analyzed.tzinfo is None:
            raise ValueError("Análisis sin zona horaria")
        age = (max(now, analyzed) - captured).total_seconds()
        status = "future" if captured > analyzed else "stale" if age > MAX_AGE_SECONDS else "recent"
    except (TypeError, ValueError, KeyError):
        age, status = None, "unknown"
    visual = result.get("visual_estimate", {})
    usable = status == "recent" and result.get("image_status") == "road_visible" and visual.get("vehicle_count_estimate") is not None
    output.update(freshness=status, age_seconds=round(age, 1) if age is not None else None,
                  density=visual.get("density", "unknown") if usable else "unknown",
                  vehicle_count_estimate=visual.get("vehicle_count_estimate") if usable else None,
                  usable_for_current_review=usable, recency_checked_at=now.isoformat(),
                  dispatch_authorized=False, requires_human_review=True, capture_time_verified=False)
    return output


def apply_recency(visual, timestamp_text, legible, timezone_name, now=None):
    now = now or datetime.now(timezone.utc)
    captured = parse_overlay_time(timestamp_text, timezone_name) if legible is True else None
    result = {**visual, "schema_version": "3.0", "analyzed_at": now.isoformat(),
              "visual_estimate": {"density": visual.get("density", "unknown"),
                                  "vehicle_count_estimate": visual.get("vehicle_count_estimate")},
              "timestamp_text": timestamp_text[:100] if isinstance(timestamp_text, str) else None,
              "timestamp_legible": legible is True, "capture_timezone": timezone_name,
              "captured_at": captured.isoformat() if captured else None,
              "expires_at": (captured + timedelta(seconds=MAX_AGE_SECONDS)).isoformat() if captured else None,
              "capture_time_source": "image_overlay_ai_transcription" if captured else "unknown",
              "max_age_seconds": MAX_AGE_SECONDS, "capture_time_verified": False,
              "current_visual_evidence": False, "dispatch_authorized": False, "requires_human_review": True}
    result["limitations"] = [*visual.get("limitations", []),
                             "Hora transcrita por IA del reloj de la imagen, no autenticada ni verificada independientemente."]
    return refresh_recency(result, now)
